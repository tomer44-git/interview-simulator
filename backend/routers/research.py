# routers/research.py
# POST /research — מריץ את סוכני המחקר ומחזיר את התוצאות
#
# ה-router אחראי על HTTP בלבד: אימות, תרגום שגיאות, מדידת שלב, ועיצוב
# התשובה. התיזמור עצמו — בניית ה-group, ההמתנה, שיוך התוצאות —
# יושב ב-agents/orchestrator.py.

import time
from datetime import datetime

from fastapi import APIRouter, Depends

from auth import get_current_user
from errors import server_error
from models.schemas import ResearchRequest, ResearchResponse
from agents import orchestrator
from domains import domain_loader
from latency import _record, clear_measurements, print_research_summary

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest, _user=Depends(get_current_user)):
    """
    מקבל: {"company": "Wix", "job_title": "Frontend Developer"}
    מחזיר: תוצאות כל סוכני המחקר של הדומיין
    """
    # [LATENCY] מאפס מדידות ומתחיל מדידת שלב
    clear_measurements()
    _t_stage = time.perf_counter()
    _ts_stage = datetime.now().isoformat(timespec="milliseconds")

    # ה-config קובע אילו סוכנים רצים לתפקיד הזה
    domain_config = domain_loader.load(req.job_title)

    try:
        outcome = orchestrator.run_research(req.company, req.job_title, domain_config)
    except orchestrator.OrchestrationError as exc:
        # תרגום שגיאת תיזמור לשגיאת HTTP — הגבול בין השכבות.
        # ההודעה המלאה נרשמת בלוג; הלקוח מקבל מזהה בלבד.
        raise server_error("Research failed", exc)

    results = outcome["results"]

    # [LATENCY] רושם את זמן השלב ומדפיס טבלת השוואת מקביליות
    stage_duration = time.perf_counter() - _t_stage
    _record("stage/research", _ts_stage, stage_duration)
    if outcome["timings"]:
        print_research_summary(stage_duration, outcome["timings"])

    # סוכן שלא רץ לדומיין הזה מוחזר כ-dict ריק
    return ResearchResponse(
        company=results.get("company",   {}),
        glassdoor=results.get("glassdoor", {}),
        linkedin=results.get("linkedin",  {}),
        news=results.get("news",      {}),
        tech=results.get("tech",      {}),
        neetcode=results.get("neetcode",  {}),
    )
