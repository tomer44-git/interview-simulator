# interview_agent.py
# תפקיד: מנוע ראיון אדפטיבי stateless — מנהל שיחה עם המועמד בזמן אמת
# קלט: תשובת מועמד + state נוכחי | פלט: תגובת מראיין + state מעודכן

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"), override=True)

def start(persona: dict, domain_config: dict) -> dict:
    """
    פותח את הראיון: מחזיר משפט הפתיחה של הפרסונה ו-state ריק.
    קורא לזה פעם אחת בתחילת כל ראיון.
    """
    # קטגוריה ראשונה לפי ה-domain config
    first_category = domain_config["question_flow"][0][0]

    # state ראשוני — ריק, מוכן לתור הראשון
    initial_state = {
        "history":          [],               # היסטוריית כל השיחה
        "questions_asked":  0,                # כמה שאלות נשאלו עד כה
        "current_category": first_category,  # קטגוריה ראשונה מה-config
        "is_complete":      False,            # האם הראיון הסתיים
    }

    # הוספת משפט הפתיחה של המראיין להיסטוריה
    opening = persona.get("opening_statement", f"Hi, I'm {persona.get('name')}. Let's get started.")
    initial_state["history"].append({"role": "interviewer", "content": opening})

    return {"message": opening, "state": initial_state}


def next_turn(user_message: str, state: dict, persona: dict, domain_config: dict) -> dict:
    """
    מעבד תשובה של מועמד ומחזיר את תגובת המראיין + state מעודכן.
    זה ה-function המרכזי שנקרא בכל תור בשיחה.

    user_message  — מה המועמד אמר
    state         — המצב הנוכחי של הראיון (מה שהוחזר מהתור הקודם)
    persona       — הפרסונה שנבנתה ב-persona_builder
    domain_config — config הדומיין (מגדיר question_flow)
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # סך השאלות נגזר מה-domain config — לא hardcoded
    question_flow   = domain_config["question_flow"]
    total_questions = sum(count for _, count in question_flow)

    # מוסיף את תשובת המועמד להיסטוריה
    state["history"].append({"role": "candidate", "content": user_message})

    # ---- קובע באיזו קטגוריה אנחנו ----
    current_category = _get_current_category(state["questions_asked"], question_flow)
    state["current_category"] = current_category

    # בדיקה האם הראיון הסתיים
    if state["questions_asked"] >= total_questions:
        return _wrap_up(state, persona, client)

    # ---- בונה את הפרומפט ל-Claude ----
    # Claude מגלם את הפרסונה ומגיב בהתאם לקטגוריה ולתשובה
    system_prompt = f"""You are {persona['name']}, {persona['title']} at {persona['company_name']}.
Your interview style: {persona['interview_style']}
Personality: {', '.join(persona['personality_traits'])}
Focus areas: {', '.join(persona['focus_areas'])}

You are conducting a {current_category} interview segment.
Rules:
- Respond naturally to the candidate's last answer (1-2 sentences max)
- Then ask ONE clear question appropriate for {current_category}
- Keep total response under 4 sentences
- Be specific to {persona['company_name']} context when relevant
- Do NOT number questions or use bullet points"""

    # ממיר את ההיסטוריה לפורמט שה-API מצפה לו
    messages = _history_to_messages(state["history"])

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=300,   # תגובות קצרות — ראיון, לא נאום
        system=system_prompt,
        messages=messages
    )

    interviewer_reply = response.content[0].text.strip()

    # מעדכן state
    state["history"].append({"role": "interviewer", "content": interviewer_reply})
    state["questions_asked"] += 1
    state["is_complete"] = state["questions_asked"] >= total_questions

    return {"message": interviewer_reply, "state": state}


def _get_current_category(questions_asked: int, question_flow: list) -> str:
    """מחשב באיזו קטגוריה אנחנו לפי מספר השאלות שנשאלו ו-question_flow מה-config"""
    count = 0
    for category, limit in question_flow:
        count += limit
        if questions_asked < count:
            return category
    return "Wrap-up"


def _wrap_up(state: dict, persona: dict, client: Anthropic) -> dict:
    """מסיים את הראיון בנימוס ומחזיר הודעת סיום"""
    closing = (
        f"Thank you so much for your time today. "
        f"It was great getting to know you. "
        f"We'll be in touch soon with next steps. "
        f"Do you have any questions for me about the role or {persona['company_name']}?"
    )
    state["history"].append({"role": "interviewer", "content": closing})
    state["is_complete"] = True
    return {"message": closing, "state": state}


def _history_to_messages(history: list) -> list:
    """ממיר היסטוריה פנימית לפורמט messages של Anthropic API"""
    messages = []
    for turn in history:
        role = "assistant" if turn["role"] == "interviewer" else "user"
        messages.append({"role": role, "content": turn["content"]})
    return messages
