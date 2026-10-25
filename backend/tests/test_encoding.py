# tests/test_encoding.py
# רגרסיה על הבאג היקר ביותר בפרויקט.
#
# תווי U+2028/U+2029 מגיעים בתוכן web ש-Tavily גורד. stdout של Railway
# הוא ASCII כברירת מחדל, אז כתיבת תוכן כזה הפילה את בניית הפרסונה.
# לקח שבעה commits למצוא, כי ה-traceback עצמו הכיל את התווים והפיל
# את הדפסת השגיאה — כלומר מנגנון הדיווח הסתיר את השגיאה.
#
# הסיבה הסופית הייתה U+2028 שהודבק לתוך ANTHROPIC_API_KEY ב-Railway.

from agents import persona_builder
from tests import sample_data
from tests.sample_data import LINE_SEP, PARA_SEP


def _build(claude, company_data, **extra):
    claude.set_json(sample_data.PERSONA)
    return persona_builder.run(
        company_data=company_data,
        glassdoor_data=sample_data.GLASSDOOR_DATA,
        linkedin_data=sample_data.LINKEDIN_DATA,
        news_data=sample_data.NEWS_DATA,
        neetcode_data=sample_data.NEETCODE_DATA,
        **extra,
    )


# ------------------------------------------------- הצינור שורד קלט מלוכלך

def test_separator_characters_do_not_break_persona_building(claude):
    """תוכן web עם U+2028 חייב לעבור בלי לקרוס"""
    built = _build(claude, sample_data.DIRTY_COMPANY_DATA)

    assert built["name"] == "Maya Cohen"


def test_separators_never_reach_the_prompt(claude):
    """
    הלב של התיקון: הניקוי קורה *לפני* שהנתונים נכנסים לפרומפט,
    לא אחרי שמשהו כבר קרס.
    """
    _build(claude, sample_data.DIRTY_COMPANY_DATA)

    prompt = claude.prompts[0]
    assert LINE_SEP not in prompt
    assert PARA_SEP not in prompt


def test_web_content_is_flattened_to_ascii(claude):
    """
    מה שמנוקה הוא *הקלט החיצוני* — לא תבנית הפרומפט שלנו.
    (לתבנית עצמה יש em-dashes, וזה תקין: היא נשלחת ב-UTF-8 ל-API
    ולא נכתבת ל-stdout של Railway.)

    הסניטייזר אגרסיבי — encode('ascii', errors='replace') — ולכן
    גרשיים חכמים ועברית מתוכן web אמיתי נמחקים גם הם. חוב מודע,
    והטסט מתעד את ההתנהגות בפועל ולא את הרצויה.
    """
    _build(claude, sample_data.DIRTY_COMPANY_DATA)
    prompt = claude.prompts[0]

    assert chr(0x201C) not in prompt          # “ שהגיע מהרשת
    assert chr(0x201D) not in prompt          # ” שהגיע מהרשת
    assert "צוותי" not in prompt              # עברית שהגיעה מהרשת
    assert "Wix is a platform?serving millions?of users." in prompt


def test_hebrew_research_content_does_not_crash(claude):
    """DIRTY_COMPANY_DATA מכיל עברית — תוכן web אמיתי מהאזור"""
    built = _build(claude, sample_data.DIRTY_COMPANY_DATA)

    assert built["title"] == "Senior Frontend Engineer"


def test_separators_nested_deep_are_cleaned(claude):
    """
    _clean רקורסיבי. התיקון הראשון ניקה רק את האיבר הראשון של כל
    רשימה והבאג שרד — ולכן הטסט מכניס את התו עמוק במבנה.
    """
    nested = {
        **sample_data.COMPANY_DATA,
        "overview": [
            "clean first item",
            f"second item with{LINE_SEP}a separator",
            f"third{PARA_SEP}item",
        ],
    }
    _build(claude, nested)

    assert LINE_SEP not in claude.prompts[0]
    assert PARA_SEP not in claude.prompts[0]


# ------------------------------------------------- שפה ממשיכה לעבוד

def test_hebrew_interview_instruction_survives_sanitising(claude):
    """
    הסניטייזר פועל על נתוני המחקר, לא על הוראת השפה.
    ראיון בעברית חייב להמשיך לעבוד.
    """
    _build(claude, sample_data.DIRTY_COMPANY_DATA, language="he")

    assert "Hebrew" in claude.prompts[0]


def test_context_summary_is_injected_when_present(claude):
    """הקונטקסט מהמשתמש מגיע לפרומפט — ולא נמחק בדרך"""
    _build(claude, sample_data.COMPANY_DATA,
           context_summary="Candidate already passed a screening call.")

    assert "screening call" in claude.prompts[0]


def test_context_block_is_absent_when_not_provided(claude):
    """בלי קונטקסט — אין סקציה ריקה שמבלבלת את המודל"""
    _build(claude, sample_data.COMPANY_DATA)

    assert "CANDIDATE'S INTERVIEW HISTORY" not in claude.prompts[0]
