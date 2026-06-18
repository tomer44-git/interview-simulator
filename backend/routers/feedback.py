# routers/feedback.py
# POST /feedback — מנתח ראיון שהסתיים ומחזיר ציונים + שומר ל-Supabase

from fastapi import APIRouter, HTTPException
from models.schemas import FeedbackRequest, FeedbackResponse
from agents import feedback_agent
from domains import domain_loader
import supabase_client

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest):
    """
    מקבל: {"state": {...}, "persona": {...}, "job_title": "..."}
    מחזיר: ציונים מפורטים לפי קטגוריה + סיכום + משאבים מומלצים

    זרימה:
    1. טוען domain_config לפי job_title (כולל scoring_rubric)
    2. feedback_agent שולח תמליל + rubric לClaude → מקבל ציונים
    3. שומר session ל-Supabase (אם מוגדר)
    4. מחזיר תוצאות לfrontend
    """
    try:
        # ---- 1. טוען את ה-rubric מה-domain config ----
        domain_config = domain_loader.load(req.job_title)

        # ---- 2. מריץ את feedback_agent — קריאה לClaude ----
        scores = feedback_agent.run(req.state, req.persona, domain_config)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")

    # ---- 3. שומר ל-Supabase (לא קריטי — לא קורס אם נכשל) ----
    client     = supabase_client.get_client()
    session_id = supabase_client.save_session(
        client,
        company=req.persona.get("company_name", ""),
        job_title=req.job_title,
        persona=req.persona,
        state=req.state,
        feedback=scores,
    )

    # ---- 4. מחזיר תוצאות ----
    return FeedbackResponse(
        overall_score=scores["overall_score"],
        categories=scores["categories"],
        summary=scores["summary"],
        top_strengths=scores["top_strengths"],
        areas_to_improve=scores["areas_to_improve"],
        recommended_resources=scores["recommended_resources"],
        session_id=session_id,
    )
