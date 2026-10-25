# tests/test_entry_points.py
# שתי נקודות כניסה לתהליכים נפרדים: main.py (FastAPI) ו-celery_app.py (worker).
# שתיהן חייבות להגדיר stdout ל-UTF-8 לפני כל import אחר.
#
# הרקע: קוד המקור שלנו מכיל עברית בהערות. אם תהליך זורק חריגה,
# Python בונה traceback שכולל את שורות המקור — וכתיבתו ל-stdout של
# Railway (ASCII כברירת מחדל) קורסת בעצמה ומסתירה את השגיאה האמיתית.
#
# ההגנה הוחלה על main.py ב-eb016a1 אבל נשכחה ב-celery_app.py,
# כלומר ה-worker נשאר חשוף — נמצא ע"י הטסטים האלה.

from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent

ENTRY_POINTS = ["main.py", "celery_app.py"]

# מודולים שרצים ב-worker ומכילים עברית בקוד המקור
WORKER_MODULES = [
    "tasks/research_tasks.py",
    "agents/research/company_agent.py",
    "agents/research/glassdoor_agent.py",
    "agents/research/linkedin_agent.py",
    "agents/research/news_agent.py",
    "agents/research/tech_agent.py",
    "agents/research/neetcode_agent.py",
]


@pytest.mark.parametrize("entry", ENTRY_POINTS)
def test_entry_point_configures_utf8_output(entry):
    """שני התהליכים, אותה הגנה — לא רק זה שבמקרה טופל"""
    source = (BACKEND / entry).read_text(encoding="utf-8")

    assert "sys.stdout.reconfigure(encoding='utf-8')" in source, (
        f"{entry} לא מגדיר stdout ל-UTF-8 — traceback עם עברית יפיל אותו"
    )
    assert "sys.stderr.reconfigure(encoding='utf-8')" in source, (
        f"{entry} לא מגדיר stderr ל-UTF-8"
    )


@pytest.mark.parametrize("entry", ENTRY_POINTS)
def test_utf8_guard_runs_before_heavy_imports(entry):
    """
    הסדר הוא כל העניין. אם ההגדרה רצה אחרי ייבוא המודולים, חריגה
    שתתרחש *במהלך* הייבוא עדיין תיכשל בכתיבה.
    """
    source = (BACKEND / entry).read_text(encoding="utf-8")
    guard = source.index("sys.stdout.reconfigure")

    for later_import in ("from celery import", "from routers import",
                         "from fastapi import", "from dotenv import"):
        if later_import in source:
            assert source.index(later_import) > guard, (
                f"ב-{entry} השורה '{later_import}' רצה לפני הגדרת UTF-8"
            )


@pytest.mark.parametrize("module", WORKER_MODULES)
def test_worker_source_really_would_break_ascii_output(module):
    """
    מתעד *למה* ההגנה נחוצה ולא רק שהיא קיימת.
    אם מישהו ינקה את ההערות לאנגלית בעתיד, הטסט הזה ייכשל ויזכיר
    שההגנה אולי כבר מיותרת — וזה מידע שימושי, לא רעש.
    """
    source = (BACKEND / module).read_text(encoding="utf-8")

    with pytest.raises(UnicodeEncodeError):
        source.encode("ascii")


def test_both_entry_points_use_identical_protection():
    """
    הגנה שונה בין שני התהליכים היא בדיוק איך שהפער הזה נוצר
    מלכתחילה — תוקן באחד, נשכח בשני.
    """
    blocks = []
    for entry in ENTRY_POINTS:
        source = (BACKEND / entry).read_text(encoding="utf-8")
        lines = [ln.strip() for ln in source.splitlines() if "reconfigure" in ln]
        blocks.append(lines)

    assert blocks[0] == blocks[1], "main.py ו-celery_app.py מגינים על עצמם אחרת"
