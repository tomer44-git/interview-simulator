# tests/test_orchestrator.py
# שכבת התיזמור, מבודדת מ-Celery ומ-Redis.
#
# עד להעברה הזו הלוגיקה ישבה בתוך ה-router, כלומר הדרך היחידה
# לבדוק אותה הייתה להרים שרת HTTP ו-Redis. עכשיו אפשר פשוט לקרוא לה.

from types import SimpleNamespace

import pytest

from agents import orchestrator


@pytest.fixture
def fake_group(monkeypatch):
    """
    מחליף את group() של Celery. הטסט קובע מה יחזור או איזו שגיאה תיזרק,
    ובודק אחר כך כמה משימות נשלחו ובאיזה timeout.
    """
    state = SimpleNamespace(tasks=None, timeout=None, results=[], error=None)

    class _Group:
        def __init__(self, tasks):
            state.tasks = list(tasks)

        def apply_async(self):
            return self

        def get(self, timeout=None):
            state.timeout = timeout
            if state.error:
                raise state.error
            return state.results

    monkeypatch.setattr(orchestrator, "group", _Group)
    return state


def _config(agents, name="Test Domain"):
    return {"name": name, "research_agents": agents}


def _result(label):
    return {"data": label, "_timing": {"name": label, "duration": 1.0}}


# ------------------------------------------------- המסלול הרגיל

def test_results_are_keyed_by_agent_name(fake_group):
    fake_group.results = [_result("company"), _result("news")]

    out = orchestrator.run_research("Wix", "Frontend", _config(["company", "news"]))

    assert out["results"]["company"]["data"] == "company"
    assert out["results"]["news"]["data"] == "news"


def test_only_the_configured_agents_are_dispatched(fake_group):
    """
    זו הטענה הארכיטקטונית: ה-config קובע מי רץ. תחום משפטי לא
    אמור להריץ את סוכן ה-NeetCode.
    """
    fake_group.results = [_result("company"), _result("glassdoor")]

    orchestrator.run_research("Wix", "Frontend", _config(["company", "glassdoor"]))

    assert len(fake_group.tasks) == 2


def test_timing_metadata_is_separated_from_research_data(fake_group):
    """
    _timing הוא מדידה, לא מחקר. הוא חייב לצאת מהתוצאה כדי שלא ימשיך
    לסכמת התשובה ולפרומפט של בניית הפרסונה.
    """
    fake_group.results = [_result("company")]

    out = orchestrator.run_research("Wix", "Frontend", _config(["company"]))

    assert "_timing" not in out["results"]["company"]
    assert out["timings"][0]["name"] == "company"


def test_results_without_timing_are_handled(fake_group):
    """לא כל סוכן בהכרח מחזיר _timing — היעדרו לא אמור להפיל כלום"""
    fake_group.results = [{"data": "company"}]

    out = orchestrator.run_research("Wix", "Frontend", _config(["company"]))

    assert out["timings"] == []


def test_timeout_is_applied(fake_group):
    fake_group.results = [_result("company")]

    orchestrator.run_research("Wix", "Frontend", _config(["company"]), timeout=30)

    assert fake_group.timeout == 30


def test_default_timeout_matches_the_documented_constant(fake_group):
    fake_group.results = [_result("company")]

    orchestrator.run_research("Wix", "Frontend", _config(["company"]))

    assert fake_group.timeout == orchestrator.RESEARCH_TIMEOUT_SECONDS


# ------------------------------------------------- שמות סוכנים שגויים

def test_unknown_agent_names_are_skipped(fake_group):
    """שגיאת כתיב ב-config לא אמורה להפיל את כל המחקר"""
    fake_group.results = [_result("company")]

    out = orchestrator.run_research(
        "Wix", "Frontend", _config(["company", "no_such_agent"])
    )

    assert len(fake_group.tasks) == 1
    assert "no_such_agent" not in out["results"]


def test_unknown_name_in_the_middle_does_not_shift_results(fake_group):
    """
    באג שתוקן בזמן ההעברה. הקוד הישן הצמיד את התוצאות לרשימת
    הסוכנים *המקורית* בעוד שהמשימות נבנו מהרשימה *המסוננת* — אז שם
    לא מוכר באמצע הזיז את כל התוצאות במקום אחד, ושייך בשקט את
    תוצאת LinkedIn לסוכן החדשות.
    """
    fake_group.results = [_result("company"), _result("linkedin")]

    out = orchestrator.run_research(
        "Wix", "Frontend", _config(["company", "typo_here", "linkedin"])
    )

    assert out["results"]["company"]["data"] == "company"
    assert out["results"]["linkedin"]["data"] == "linkedin"


def test_config_with_no_valid_agents_raises(fake_group):
    """כישלון מפורש עדיף על מחקר ריק שייראה כמו הצלחה"""
    with pytest.raises(orchestrator.OrchestrationError):
        orchestrator.run_research("Wix", "Frontend", _config(["nope", "also_nope"]))


# ------------------------------------------------- טיפול בכשלים

def test_celery_failure_becomes_an_orchestration_error(fake_group):
    """
    שכבת הסוכנים לא מכירה HTTP. היא זורקת שגיאה משלה,
    וה-router הוא שמתרגם אותה ל-500.
    """
    fake_group.error = TimeoutError("timed out waiting for workers")

    with pytest.raises(orchestrator.OrchestrationError) as err:
        orchestrator.run_research("Wix", "Frontend", _config(["company"]))

    assert "timed out" in str(err.value)


def test_original_error_is_preserved_as_the_cause(fake_group):
    """השגיאה המקורית נשמרת ב-__cause__ כדי שלא נאבד אותה בדיבאג"""
    original = ConnectionError("redis is down")
    fake_group.error = original

    with pytest.raises(orchestrator.OrchestrationError) as err:
        orchestrator.run_research("Wix", "Frontend", _config(["company"]))

    assert err.value.__cause__ is original


# ------------------------------------------------- גבול ה-HTTP

def test_router_translates_orchestration_error_to_500(api, monkeypatch):
    """ה-router חייב לתרגם — לא לתת לחריגה לדלוף כ-500 גנרי של FastAPI"""
    def _boom(*args, **kwargs):
        raise orchestrator.OrchestrationError("workers unavailable")

    monkeypatch.setattr(orchestrator, "run_research", _boom)

    res = api.post("/research", json={"company": "Wix", "job_title": "Frontend Developer"})

    assert res.status_code == 500
    assert "workers unavailable" in res.json()["detail"]


def test_router_passes_the_domain_config_through(api, monkeypatch):
    """התפקיד נפתר ל-config *לפני* התיזמור — ה-config הוא שקובע מי רץ"""
    seen = {}

    def _capture(company, job_title, domain_config, **kwargs):
        seen["name"] = domain_config["name"]
        return {"results": {}, "timings": []}

    monkeypatch.setattr(orchestrator, "run_research", _capture)

    api.post("/research", json={"company": "Wix", "job_title": "Junior AI Engineer"})

    assert seen["name"] == "Junior AI Engineer"
