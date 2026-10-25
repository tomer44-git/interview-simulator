# tests/test_interview_flow.py
# בודק את מנוע הראיון עצמו — הלוגיקה, לא התשתית.
#
# הטסט המרכזי כאן הוא רגרסיה על באג אמיתי: is_complete נקבע True
# ברגע שהשאלה השמינית *נשאלה*, אז הפרונט קפץ לפידבק לפני שהמועמד
# הספיק לענות עליה. שאלת הקידוד נשארה ללא מענה וקיבלה ציון 0.0.
# שום חריגה לא נזרקה — רק מספר שגוי. (תוקן ב-ff97f6b)

from agents import interview_agent

TOTAL_QUESTIONS = 8  # HR 2 + Behavioral 2 + Technical 3 + Coding 1


def _ask_all_questions(claude, persona, domain_config):
    """
    מריץ ראיון עד שכל 8 השאלות נשאלו — אבל בלי לענות על האחרונה.
    מחזיר את ה-state בנקודה הקריטית שבה הבאג התרחש.
    """
    claude.set_responses([f"Question {i}?" for i in range(1, TOTAL_QUESTIONS + 1)])
    state = interview_agent.start(persona, domain_config)["state"]

    for i in range(1, TOTAL_QUESTIONS + 1):
        state = interview_agent.next_turn(
            f"Answer {i}", state, persona, domain_config
        )["state"]

    return state


# ------------------------------------------------- רגרסיה: שאלה 8

def test_interview_stays_open_after_the_last_question_is_asked(claude, persona, domain_config):
    """
    הבאג עצמו. אחרי שהשאלה האחרונה נשאלה המועמד עדיין חייב להיות
    מסוגל לענות — כלומר is_complete חייב להישאר False.
    """
    state = _ask_all_questions(claude, persona, domain_config)

    assert state["questions_asked"] == TOTAL_QUESTIONS
    assert state["is_complete"] is False, (
        "הראיון נסגר ברגע שהשאלה האחרונה נשאלה — "
        "המועמד לא יקבל הזדמנות לענות עליה"
    )


def test_is_complete_stays_false_through_every_question(claude, persona, domain_config):
    """לא רק בסוף — אף שאלה בדרך לא אמורה לסגור את הראיון"""
    claude.set_responses([f"Question {i}?" for i in range(1, TOTAL_QUESTIONS + 1)])
    state = interview_agent.start(persona, domain_config)["state"]

    for i in range(1, TOTAL_QUESTIONS + 1):
        state = interview_agent.next_turn(f"Answer {i}", state, persona, domain_config)["state"]
        assert state["is_complete"] is False, f"הראיון נסגר אחרי שאלה {i}"


def test_wrap_up_fires_only_after_the_final_answer(claude, persona, domain_config):
    """התור שאחרי השאלה האחרונה הוא זה שסוגר את הראיון"""
    state = _ask_all_questions(claude, persona, domain_config)

    final = interview_agent.next_turn(
        "My answer to the coding question.", state, persona, domain_config
    )

    assert final["state"]["is_complete"] is True


def test_every_question_receives_an_answer(claude, persona, domain_config):
    """
    מבנה התמליל ש-feedback_agent מסתמך עליו: כל תור של מראיין —
    חוץ מהודעת הסיום — מלווה בתשובת מועמד.

    הערה: הטסט הזה עובר גם עם באג שאלה 8, כי הוא מריץ את הלולאה
    ישירות ולא דרך ה-UI. הבאג היה בשכבה שמעל — הפרונט הפסיק לשאול
    תור אחד מוקדם מדי. הרגרסיה עצמה נבדקת בשני הטסטים שלמעלה.
    """
    state = _ask_all_questions(claude, persona, domain_config)
    state = interview_agent.next_turn("Final answer.", state, persona, domain_config)["state"]

    history = state["history"]
    for i, turn in enumerate(history[:-1]):      # ההודעה האחרונה היא הסיום
        if turn["role"] == "interviewer":
            assert history[i + 1]["role"] == "candidate", (
                f"שאלת המראיין בעמדה {i} נשארה ללא מענה"
            )


def test_coding_question_is_answered_before_scoring(claude, persona, domain_config):
    """
    ממוקד בתסמין המקורי: שאלת הקידוד היא האחרונה לפי ה-config,
    ולכן היא זו שנפגעה. התמליל חייב להכיל תשובה אחריה.
    """
    state = _ask_all_questions(claude, persona, domain_config)
    assert state["current_category"] == "Coding"

    state = interview_agent.next_turn("def solution(): ...", state, persona, domain_config)["state"]

    coding_answer = state["history"][-2]           # [-1] הוא הסיום
    assert coding_answer["role"] == "candidate"
    assert "def solution" in coding_answer["content"]


# ------------------------------------------------- ה-config מניע את הזרימה

def test_question_count_comes_from_the_domain_config(claude, persona, domain_config):
    """8 אינו מספר קשיח בקוד — הוא סכום ה-question_flow"""
    expected = sum(count for _, count in domain_config["question_flow"])
    state = _ask_all_questions(claude, persona, domain_config)

    assert expected == TOTAL_QUESTIONS
    assert state["questions_asked"] == expected


def test_categories_follow_the_configured_order(claude, persona, domain_config):
    """
    מוכיח את הטענה המרכזית של הארכיטקטורה: ה-config קובע את מבנה
    הראיון, לא הקוד. HR 2 ← Behavioral 2 ← Technical 3 ← Coding 1.
    """
    claude.set_responses([f"Question {i}?" for i in range(1, TOTAL_QUESTIONS + 1)])
    state = interview_agent.start(persona, domain_config)["state"]

    seen = []
    for i in range(1, TOTAL_QUESTIONS + 1):
        state = interview_agent.next_turn(f"Answer {i}", state, persona, domain_config)["state"]
        seen.append(state["current_category"])

    assert seen == [
        "HR", "HR",
        "Behavioral", "Behavioral",
        "Technical", "Technical", "Technical",
        "Coding",
    ]


# ------------------------------------------------- שפה ו-state

def test_a_non_tech_domain_runs_on_the_same_engine(claude, persona):
    """
    ההוכחה שהארכיטקטורה עומדת בטענה שלה: ראיון פיננסי מלא עובר
    במנוע שלא יודע שפיננסים קיימים, עם קטגוריות שלא מופיעות בשום
    מקום בקוד ("Case Study") ועם ארבעה סוכני מחקר במקום שישה.
    """
    from domains import domain_loader

    finance = domain_loader.load("Junior Financial Analyst")
    claude.set_responses([f"Finance question {i}?" for i in range(1, 9)])

    state = interview_agent.start(persona, finance)["state"]
    seen = []
    for i in range(1, 9):
        state = interview_agent.next_turn(f"Answer {i}", state, persona, finance)["state"]
        seen.append(state["current_category"])

    assert seen == [
        "HR", "HR",
        "Behavioral", "Behavioral",
        "Technical", "Technical",
        "Case Study", "Case Study",
    ]
    assert state["is_complete"] is False     # אותה הגנה על השאלה האחרונה

    closed = interview_agent.next_turn("Final answer.", state, persona, finance)
    assert closed["state"]["is_complete"] is True


def test_hebrew_instruction_reaches_the_system_prompt(claude, persona, domain_config):
    """בחירת השפה חייבת להגיע עד ל-system prompt, אחרת הראיון יהיה באנגלית"""
    state = interview_agent.start(persona, domain_config, language="he")["state"]
    interview_agent.next_turn("תשובה", state, persona, domain_config, language="he")

    assert "Hebrew" in claude.systems[0]


def test_state_is_self_contained(claude, persona, domain_config):
    """
    המנוע stateless — אין זיכרון בצד השרת. state שעבר סריאליזציה
    ובחזרה חייב להמשיך לעבוד, אחרת לא נוכל להריץ כמה instances.
    """
    import json

    state = interview_agent.start(persona, domain_config)["state"]
    round_tripped = json.loads(json.dumps(state))

    out = interview_agent.next_turn("answer", round_tripped, persona, domain_config)
    assert out["state"]["questions_asked"] == 1
