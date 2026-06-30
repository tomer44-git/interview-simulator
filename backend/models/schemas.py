# schemas.py
# מגדיר את צורת הנתונים לכל request ו-response ב-API
# Pydantic מאמת כל בקשה לפני שהקוד שלנו בכלל רץ

from pydantic import BaseModel


# ── /research ──────────────────────────────────────────
class ResearchRequest(BaseModel):
    # מה הfrontend שולח: שם חברה + תפקיד
    company:   str
    job_title: str

class ResearchResponse(BaseModel):
    # מה ה-API מחזיר: תוצאות כל 6 ה-agents
    company:   dict
    glassdoor: dict
    linkedin:  dict
    news:      dict
    tech:      dict
    neetcode:  dict


# ── /persona ───────────────────────────────────────────
class PersonaRequest(BaseModel):
    # מקבל את כל נתוני המחקר + שם התפקיד + שפה ("en" / "he")
    research:  dict
    job_title: str
    language:  str = "en"

class PersonaResponse(BaseModel):
    # מחזיר את הפרסונה שנבנתה
    persona: dict


# ── /interview/start ───────────────────────────────────
class InterviewStartRequest(BaseModel):
    # פותח ראיון חדש — צריך פרסונה, שם תפקיד ושפה
    persona:   dict
    job_title: str
    language:  str = "en"

class InterviewStartResponse(BaseModel):
    # מחזיר את משפט הפתיחה + ה-state הריק
    message: str
    state:   dict


# ── /interview/turn ────────────────────────────────────
class InterviewTurnRequest(BaseModel):
    # כל תור: תשובת המועמד + ה-state הנוכחי + הפרסונה + תפקיד + שפה
    user_message: str
    state:        dict
    persona:      dict
    job_title:    str
    language:     str = "en"

class InterviewTurnResponse(BaseModel):
    # מחזיר את תגובת המראיין + ה-state המעודכן + האם הסתיים
    message:     str
    state:       dict
    is_complete: bool


# ── /feedback ──────────────────────────────────────────
class FeedbackRequest(BaseModel):
    # מקבל את כל ה-state (כולל history) + פרסונה + תפקיד + שפה לניתוח
    state:     dict
    persona:   dict
    job_title: str
    language:  str = "en"

class CategoryScore(BaseModel):
    # ציון + פידבק לקטגוריה בודדת
    score:        float
    feedback:     str
    strengths:    list[str]
    improvements: list[str]

class FeedbackResponse(BaseModel):
    # תוצאת הניתוח המלא
    overall_score:        float
    categories:           dict[str, CategoryScore]
    summary:              str
    top_strengths:        list[str]
    areas_to_improve:     list[str]
    recommended_resources: list[str]
    session_id:           str | None = None  # מזהה Supabase אם נשמר
