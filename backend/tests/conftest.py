# tests/conftest.py
# פיקסצ'רים משותפים לכל הטסטים — pytest טוען את הקובץ הזה אוטומטית.
#
# עיקרון מנחה: שום טסט לא פונה ל-API אמיתי. כל קריאה ל-Claude ול-Tavily
# מוחלפת בזיוף שמחזיר תוכן נשלט, ובנוסף המפתחות האמיתיים מוחלפים במזויפים —
# כך שאם שכחנו למקם mock איפשהו, הטסט ייכשל בקול במקום לשרוף מכסה בשקט.

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from tests import sample_data

# המודולים שבהם צריך להחליף את הקונסטרקטור.
# מחליפים את השם *במקום שבו הוא נקרא*, לא במקום שבו הוא מוגדר —
# כי כל מודול עשה "from anthropic import Anthropic" לעצמו.
CLAUDE_MODULES = [
    "agents.persona_builder",
    "agents.interview_agent",
    "agents.feedback_agent",
    "agents.context_agent",
]

TAVILY_MODULES = [
    "agents.research.company_agent",
    "agents.research.glassdoor_agent",
    "agents.research.linkedin_agent",
    "agents.research.news_agent",
    "agents.research.tech_agent",
    "agents.research.neetcode_agent",
]


# ---------------------------------------------------------------- env

@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    """
    רץ לפני כל טסט אוטומטית ומחליף את כל המפתחות במזויפים.
    זו רשת הביטחון: אם mock כלשהו יפספס, הקריאה תצא עם מפתח לא תקין
    ותיכשל מיד — במקום להצליח בשקט ולחייב אותנו בכסף אמיתי.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY",   "sk-ant-fake-key-for-tests")
    monkeypatch.setenv("TAVILY_API_KEY",      "tvly-fake-key-for-tests")
    monkeypatch.setenv("SUPABASE_URL",        "https://fake.supabase.test")
    monkeypatch.setenv("SUPABASE_KEY",        "fake-anon-key")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.setenv("REDIS_URL",           "redis://localhost:6379/15")
    monkeypatch.setenv("ADMIN_EMAIL",         "admin@test.local")


# ---------------------------------------------------------------- Claude

class FakeClaude:
    """
    מחליף את Anthropic. שומר כל פרומפט שנשלח (ל-assertions)
    ומחזיר טקסט שהטסט קובע מראש.
    """

    def __init__(self):
        self._queue   = []                        # תשובות לפי סדר, נצרכות אחת-אחת
        self._default = "Mock interviewer reply."  # מה שמוחזר כשהתור ריק
        self.calls    = []                        # כל ה-kwargs של כל קריאה

    # --- הגדרת התנהגות ע"י הטסט ---
    def set_response(self, text):
        """תשובה קבועה לכל הקריאות"""
        self._default = text
        self._queue = []

    def set_responses(self, texts):
        """תשובות שונות לפי סדר — לראיון מלא עם 8 שאלות שונות"""
        self._queue = list(texts)

    def set_json(self, obj):
        """נוחות: פרסונה או פידבק שחוזרים כ-JSON"""
        self.set_response(json.dumps(obj))

    # --- בדיקה ע"י הטסט ---
    @property
    def prompts(self):
        """
        כל תוכן ההודעות של כל קריאה, משורשר.
        חשוב: persona_builder שולח הודעה אחת, אבל interview_agent שולח את
        כל השיחה — לכן משרשרים, אחרת "X in prompts[0]" יבדוק רק את ההודעה
        הראשונה ויחמיץ את התשובה האחרונה של המועמד.
        """
        return ["\n".join(m["content"] for m in c["messages"]) for c in self.calls]

    @property
    def systems(self):
        """ה-system prompt של כל קריאה (None אם לא היה)"""
        return [c.get("system") for c in self.calls]

    # --- פנימי ---
    def _next_text(self):
        return self._queue.pop(0) if self._queue else self._default

    def _build_client(self, *args, **kwargs):
        """מה שמוחזר במקום Anthropic(api_key=...)"""
        def create(**kw):
            self.calls.append(kw)
            return SimpleNamespace(content=[SimpleNamespace(text=self._next_text())])
        return SimpleNamespace(messages=SimpleNamespace(create=create))


@pytest.fixture
def claude():
    """מחליף את Claude בכל המודולים שמשתמשים בו"""
    fake = FakeClaude()
    with _patch_all(CLAUDE_MODULES, "Anthropic", fake._build_client):
        yield fake


# ---------------------------------------------------------------- Tavily

class FakeTavily:
    """מחליף את TavilyClient. שומר כל שאילתה ומחזיר snippets נשלטים."""

    def __init__(self):
        self.queries   = []
        self._snippets = ["Default web snippet for testing."]

    def set_snippets(self, snippets):
        self._snippets = list(snippets)

    def _build_client(self, *args, **kwargs):
        """מה שמוחזר במקום TavilyClient(api_key=...)"""
        def search(**kw):
            self.queries.append(kw.get("query", ""))
            return {
                "results": [
                    {"content": s, "title": "Test result", "url": "https://example.test"}
                    for s in self._snippets
                ]
            }
        return SimpleNamespace(search=search)


@pytest.fixture
def tavily():
    """מחליף את Tavily בכל 6 סוכני המחקר"""
    fake = FakeTavily()
    with _patch_all(TAVILY_MODULES, "TavilyClient", fake._build_client):
        yield fake


# ---------------------------------------------------------------- API

FAKE_USER = SimpleNamespace(
    id="00000000-0000-0000-0000-000000000001",
    email="tester@test.local",
)


@pytest.fixture
def api():
    """TestClient של FastAPI עם משתמש מחובר מזויף"""
    from fastapi.testclient import TestClient
    import main
    from auth import get_current_user

    main.app.dependency_overrides[get_current_user] = lambda: FAKE_USER
    with TestClient(main.app) as client:
        yield client
    main.app.dependency_overrides.clear()


@pytest.fixture
def api_anon():
    """TestClient ללא אימות — לבדיקה שה-routes באמת חוסמים"""
    from fastapi.testclient import TestClient
    import main

    main.app.dependency_overrides.clear()
    with TestClient(main.app) as client:
        yield client


# ---------------------------------------------------------------- נתונים

@pytest.fixture
def persona():
    """פרסונה תקינה, עותק טרי לכל טסט"""
    return json.loads(json.dumps(sample_data.PERSONA))


@pytest.fixture
def research():
    """תוצאות 6 סוכני המחקר, עותק טרי"""
    return json.loads(json.dumps(sample_data.ALL_RESEARCH))


@pytest.fixture
def domain_config():
    """ה-config האמיתי — נתונים סטטיים, אין בו קריאות רשת"""
    from domains import domain_loader
    return domain_loader.load(sample_data.JOB)


# ---------------------------------------------------------------- עזר

class _patch_all:
    """
    Context manager שמחליף שם אחד במספר מודולים בבת אחת.
    משמש כי כל agent עשה import נפרד של אותו קונסטרקטור.
    """

    def __init__(self, modules, attr, replacement):
        self._patchers = [patch(f"{m}.{attr}", replacement) for m in modules]

    def __enter__(self):
        for p in self._patchers:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patchers:
            p.stop()
        return False
