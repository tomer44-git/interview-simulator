# tests/test_infrastructure.py
# בודק שרתמת הבדיקות עצמה עובדת — שה-mocks באמת תופסים
# ושאף טסט לא מסוגל להגיע ל-API אמיתי.
# אם הקובץ הזה נכשל, אין טעם להסתכל על שום טסט אחר.

import os

from agents import interview_agent, persona_builder
from agents.research import company_agent
from tests import sample_data


# ---------------------------------------------------------- רשת הביטחון

def test_real_api_keys_are_never_visible():
    """המפתחות האמיתיים מוחלפים במזויפים בכל טסט — אוטומטית"""
    assert os.getenv("ANTHROPIC_API_KEY") == "sk-ant-fake-key-for-tests"
    assert os.getenv("TAVILY_API_KEY")    == "tvly-fake-key-for-tests"


def test_fake_keys_are_ascii():
    """
    הבאג שעלה לנו שבעה commits: תו U+2028 בלתי נראה בתוך המפתח.
    אם המפתחות שלנו עצמם לא ASCII, הטסטים משקרים.
    """
    for key in ("ANTHROPIC_API_KEY", "TAVILY_API_KEY"):
        assert os.getenv(key).isascii()


# ---------------------------------------------------------- Claude

def test_claude_is_intercepted(claude, persona, domain_config):
    """next_turn קורא ל-Claude — הזיוף חייב לתפוס ולהחזיר את מה שקבענו"""
    claude.set_response("Tell me about a hard bug you fixed.")

    state = interview_agent.start(persona, domain_config)["state"]
    out   = interview_agent.next_turn("Three years of React.", state, persona, domain_config)

    assert out["message"] == "Tell me about a hard bug you fixed."
    assert len(claude.calls) == 1


def test_claude_returns_responses_in_order(claude, persona, domain_config):
    """set_responses מאפשר תשובה שונה לכל תור — נדרש לראיון של 8 שאלות"""
    claude.set_responses(["Question one?", "Question two?"])

    state = interview_agent.start(persona, domain_config)["state"]
    first  = interview_agent.next_turn("answer a", state, persona, domain_config)
    second = interview_agent.next_turn("answer b", first["state"], persona, domain_config)

    assert first["message"]  == "Question one?"
    assert second["message"] == "Question two?"


def test_claude_records_prompts(claude, persona, domain_config):
    """הפרומפטים נשמרים — כך אפשר לבדוק הזרקת שפה, קונטקסט וכו'"""
    state = interview_agent.start(persona, domain_config)["state"]
    interview_agent.next_turn("my answer", state, persona, domain_config, language="he")

    assert "my answer" in claude.prompts[0]
    assert "Hebrew" in claude.systems[0]


def test_start_does_not_call_claude(claude, persona, domain_config):
    """start() משתמש ב-opening_statement מהפרסונה ולא קורא ל-API"""
    result = interview_agent.start(persona, domain_config)

    assert result["message"] == persona["opening_statement"]
    assert claude.calls == []


# ---------------------------------------------------------- Tavily

def test_tavily_is_intercepted(tavily):
    """סוכן המחקר מקבל את מה שהזיוף מחזיר, בלי לגעת ברשת"""
    tavily.set_snippets(["Wix runs on React and TypeScript."])

    data = company_agent.run("Wix", "Frontend Developer")

    assert data["overview"] == ["Wix runs on React and TypeScript."]
    assert data["company_name"] == "Wix"


def test_tavily_records_queries(tavily):
    """company_agent שולח 4 שאילתות — נשמרות לבדיקה"""
    company_agent.run("Wix", "Frontend Developer")

    assert len(tavily.queries) == 4
    assert all("Wix" in q for q in tavily.queries)


# ---------------------------------------------------------- שילוב

def test_persona_builder_with_both_mocks(claude, tavily, research):
    """הצינור מחקר ← פרסונה עובד מקצה לקצה על זיופים בלבד"""
    claude.set_json(sample_data.PERSONA)

    built = persona_builder.run(
        company_data=research["company"],
        glassdoor_data=research["glassdoor"],
        linkedin_data=research["linkedin"],
        news_data=research["news"],
        neetcode_data=research["neetcode"],
    )

    assert built["name"] == "Maya Cohen"
    assert built["company_name"] == "Wix"   # נוסף ע"י הבילדר, לא ע"י Claude


# ---------------------------------------------------------- API

def test_app_boots_and_health_responds(api):
    """ה-FastAPI app נטען בתוך הטסטים בלי Redis ובלי Supabase"""
    res = api.get("/")

    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_protected_route_rejects_anonymous(api_anon):
    """בלי Authorization header — הבקשה נחסמת לפני שהיא נוגעת בלוגיקה"""
    res = api_anon.post("/persona", json={"research": {}, "job_title": "x"})

    assert res.status_code in (401, 422)


def test_protected_route_accepts_fake_user(api, claude, research):
    """עם המשתמש המזויף — אותו route עובר ומגיע ללוגיקה"""
    claude.set_json(sample_data.PERSONA)

    res = api.post("/persona", json={
        "research": research,
        "job_title": sample_data.JOB,
    })

    assert res.status_code == 200
    assert res.json()["persona"]["name"] == "Maya Cohen"
