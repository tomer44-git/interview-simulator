# routers/interview.py
# POST /interview/start — פותח ראיון ומחזיר משפט פתיחה + state ריק
# POST /interview/turn  — מעבד תשובה ומחזיר תגובת מראיין + state מעודכן

import time
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import (
    InterviewStartRequest, InterviewStartResponse,
    InterviewTurnRequest,  InterviewTurnResponse,
)
from agents import interview_agent
from domains import domain_loader
from latency import _record

router = APIRouter()


@router.post("/interview/start", response_model=InterviewStartResponse)
def start_interview(req: InterviewStartRequest):
    """
    מקבל: {"persona": {...}, "job_title": "Frontend Developer"}
    מחזיר: {"message": "Hi, I'm David...", "state": {...}}

    טוען את ה-domain_config לפי job_title — כך מבנה הראיון מגיע מה-config,
    לא מקוד hardcoded
    """
    try:
        # ---- טוען domain config לפי שם התפקיד ----
        domain_config = domain_loader.load(req.job_title)

        # ---- פותח ראיון — מחזיר פתיחה + state ריק ----
        result = interview_agent.start(req.persona, domain_config, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview start failed: {str(e)}")

    return InterviewStartResponse(
        message=result["message"],
        state=result["state"],
    )


@router.post("/interview/turn", response_model=InterviewTurnResponse)
def interview_turn(req: InterviewTurnRequest):
    """
    מקבל: {"user_message": "...", "state": {...}, "persona": {...}, "job_title": "..."}
    מחזיר: {"message": "...", "state": {...}, "is_complete": false}

    ה-state מגיע מהfrontend בכל תור — הbackend לא שומר כלום בין בקשות (stateless)
    """
    try:
        # ---- טוען domain config — זהה לזה שנטען ב-start ----
        domain_config = domain_loader.load(req.job_title)

        # ---- מעבד את תגובת המועמד ומחזיר תגובת מראיין ----
        _t = time.perf_counter()
        _ts = datetime.now().isoformat(timespec='milliseconds')
        result = interview_agent.next_turn(
            req.user_message,
            req.state,
            req.persona,
            domain_config,
            language=req.language,
        )
        _record("stage/interview_turn", _ts, time.perf_counter() - _t)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview turn failed: {str(e)}")

    return InterviewTurnResponse(
        message=result["message"],
        state=result["state"],
        is_complete=result["state"]["is_complete"],
    )
