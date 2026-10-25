# tests/test_wrap_up.py
# הודעת הסיום של הראיון.
#
# רגרסיה: הטקסט נהג להסתיים ב"האם יש לך שאלות לגבי התפקיד?",
# והפרונט נועל את תיבת הקלט מיד אחריו. מבחינת המשתמש המראיינת
# שאלה שאלה ואז חסמה אותו מלענות. (דווח ע"י משתמש, תוקן ב-20967d1)

import pytest

from agents import interview_agent


@pytest.mark.parametrize("language", ["en", "he"])
def test_closing_does_not_end_with_a_question(persona, language):
    """
    האינווריאנטה המדויקת: הודעה שמסתיימת בסימן שאלה מזמינה תשובה,
    וה-UI כבר לא מאפשר אחת. חייבת להיות הצהרה סוגרת.
    """
    result = interview_agent._wrap_up({"history": []}, persona, language)

    assert not result["message"].rstrip().endswith("?"), (
        f"הודעת הסיום ב-{language} מסתיימת בשאלה שהמשתמש לא יוכל לענות עליה"
    )


@pytest.mark.parametrize("language", ["en", "he"])
def test_closing_marks_the_interview_complete(persona, language):
    """זו הנקודה היחידה במערכת שמותר לה לקבוע is_complete=True"""
    result = interview_agent._wrap_up({"history": []}, persona, language)

    assert result["state"]["is_complete"] is True


@pytest.mark.parametrize("language", ["en", "he"])
def test_closing_is_appended_to_the_transcript(persona, language):
    """הודעת הסיום חייבת להישמר בהיסטוריה — היא חלק מהתמליל"""
    result = interview_agent._wrap_up({"history": []}, persona, language)
    history = result["state"]["history"]

    assert len(history) == 1
    assert history[0]["role"] == "interviewer"
    assert history[0]["content"] == result["message"]


def test_closing_is_written_in_hebrew_when_asked(persona):
    """בודק תווים עבריים ממשיים, לא רק שהפרמטר עבר"""
    result = interview_agent._wrap_up({"history": []}, persona, "he")

    assert any("֐" <= ch <= "ת" for ch in result["message"])


def test_closing_is_written_in_english_by_default(persona):
    result = interview_agent._wrap_up({"history": []}, persona, "en")

    assert not any("֐" <= ch <= "ת" for ch in result["message"])


@pytest.mark.parametrize("language", ["en", "he"])
def test_closing_names_the_company(persona, language):
    """הודעת הסיום אמורה להרגיש אישית לחברה, לא גנרית"""
    result = interview_agent._wrap_up({"history": []}, persona, language)

    assert persona["company_name"] in result["message"]
