# tests/test_error_handling.py
# שגיאות שרת לא דולפות פרטים פנימיים ללקוח.
#
# הרקע: ה-routers נהגו להחזיר f"...: {str(e)}". הטקסט הגולמי של חריגה
# יכול להכיל נתיבי קבצים, פנימיות של ספריות ומבנה DB — ובמקרה אחד
# בפרויקט הזה הוא הכיל קידומת של מפתח API שהוצגה בחלון שגיאה בדפדפן
# (commit 4fb59ad). הקוד ההוא הוסר, אבל הערוץ נשאר פתוח עד לתיקון הזה.

import re
from pathlib import Path

import pytest

from agents import orchestrator, persona_builder, interview_agent
from tests import sample_data

BACKEND = Path(__file__).resolve().parent.parent

ROUTERS = ["research.py", "persona.py", "interview.py", "feedback.py", "context.py"]

# מה שנראה כמו סוד בהודעת שגיאה
SECRET_SHAPED = "sk-ant-api03-SECRETVALUE /srv/app/secrets.env"


# ------------------------------------------------- אין str(e) בקוד

@pytest.mark.parametrize("router", ROUTERS)
def test_router_never_interpolates_the_raw_exception(router):
    """
    בדיקה בסגנון lint. אם מישהו יחזיר f"...{e}" ל-HTTPException בעתיד,
    הטסט ייפול כאן ולא אחרי שסוד כבר הוצג למשתמש.
    """
    source = (BACKEND / "routers" / router).read_text(encoding="utf-8")

    offenders = re.findall(r"HTTPException\([^)]*\{(?:str\()?e(?:xc)?\)?\}", source)

    assert not offenders, f"{router} מחזיר חריגה גולמית ללקוח: {offenders}"


# ------------------------------------------------- התנהגות בפועל

def _secret_bearing_failure(*args, **kwargs):
    raise RuntimeError(SECRET_SHAPED)


def test_persona_route_hides_the_internal_message(api, monkeypatch, research):
    monkeypatch.setattr(persona_builder, "run", _secret_bearing_failure)

    res = api.post("/persona", json={"research": research, "job_title": "Frontend Developer"})
    detail = res.json()["detail"]

    assert res.status_code == 500
    assert "sk-ant" not in detail
    assert "/srv/app" not in detail


def test_interview_route_hides_the_internal_message(api, monkeypatch, persona):
    monkeypatch.setattr(interview_agent, "start", _secret_bearing_failure)

    res = api.post("/interview/start", json={"persona": persona, "job_title": "Frontend Developer"})

    assert res.status_code == 500
    assert "sk-ant" not in res.json()["detail"]


def test_research_route_hides_the_internal_message(api, monkeypatch):
    def _boom(*args, **kwargs):
        raise orchestrator.OrchestrationError(SECRET_SHAPED)

    monkeypatch.setattr(orchestrator, "run_research", _boom)

    res = api.post("/research", json={"company": "Wix", "job_title": "Frontend Developer"})

    assert res.status_code == 500
    assert "sk-ant" not in res.json()["detail"]


@pytest.mark.parametrize("route,payload,target", [
    ("/persona", {"research": {}, "job_title": "Frontend Developer"}, None),
])
def test_client_still_gets_something_actionable(api, monkeypatch, route, payload, target):
    """
    הסתרה בלי מזהה הייתה הופכת כל תקלה לבלתי ניתנת לאבחון.
    המשתמש מצטט את ה-ref ואנחנו מוצאים את הרשומה המלאה בלוג.
    """
    monkeypatch.setattr(persona_builder, "run", _secret_bearing_failure)

    res = api.post(route, json=payload)
    detail = res.json()["detail"]

    assert "Persona build failed" in detail
    assert re.search(r"ref: [0-9a-f]{8}", detail), f"אין מזהה בהודעה: {detail}"


def test_each_failure_gets_its_own_reference(api, monkeypatch, research):
    """שני כשלים נפרדים = שני מזהים, אחרת אי אפשר לאתר אירוע ספציפי"""
    monkeypatch.setattr(persona_builder, "run", _secret_bearing_failure)
    body = {"research": research, "job_title": "Frontend Developer"}

    first  = api.post("/persona", json=body).json()["detail"]
    second = api.post("/persona", json=body).json()["detail"]

    assert first != second


def test_full_detail_reaches_the_server_log(api, monkeypatch, research, caplog):
    """מה שהוסתר מהלקוח חייב להופיע בלוג — אחרת איבדנו יכולת דיבאג"""
    monkeypatch.setattr(persona_builder, "run", _secret_bearing_failure)

    with caplog.at_level("ERROR", logger="interview_simulator"):
        api.post("/persona", json={"research": research, "job_title": "Frontend Developer"})

    assert SECRET_SHAPED in caplog.text
    assert "RuntimeError" in caplog.text


# ------------------------------------------------- שגיאות פענוח קבצים

def test_unreadable_pdf_does_not_become_document_content():
    """
    קודם הוחזר כאן f"[PDF parse error: {e}]", כלומר הודעת השגיאה נכנסה
    לפרומפט של בניית הפרסונה כאילו הייתה תוכן המסמך.
    """
    from routers import context

    result = context._extract_pdf(b"this is not a pdf at all")

    assert result is None


def test_unreadable_docx_does_not_become_document_content():
    from routers import context

    result = context._extract_docx(b"this is not a word document")

    assert result is None


def test_extractors_return_none_not_an_error_string():
    """
    None הוא המפתח: ה-route מדלג עליו. מחרוזת — כל מחרוזת — הייתה
    ממשיכה לצינור ומגיעה ל-Claude.
    """
    from routers import context

    for extractor in (context._extract_pdf, context._extract_docx):
        result = extractor(b"\x00\x01garbage")
        assert result is None or isinstance(result, str)
        assert result is None or "error" not in result.lower()
