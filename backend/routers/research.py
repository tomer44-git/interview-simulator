# routers/research.py
# POST /research — מריץ את כל ה-research agents במקביל דרך Celery
# מחכה לכל התוצאות ומחזיר אותן יחד

from fastapi import APIRouter, HTTPException
from celery import group

from models.schemas import ResearchRequest, ResearchResponse
from tasks.research_tasks import AGENT_TASK_MAP
from domains import domain_loader

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest):
    """
    מקבל: {"company": "Wix", "job_title": "Frontend Developer"}
    מחזיר: תוצאות כל 6 ה-agents

    השלבים:
    1. טוען domain_config לפי job_title → יודע אילו agents להריץ
    2. בונה group של Celery tasks — כולם יוזנקו במקביל
    3. מחכה לכולם (עד 120 שניות)
    4. מרכיב את התוצאות ומחזיר
    """
    # ---- 1. אילו agents מריצים לתפקיד הזה? ----
    domain_config    = domain_loader.load(req.job_title)
    agents_to_run    = domain_config["research_agents"]  # למשל: ["company","glassdoor",...]

    # ---- 2. בונה רשימת Celery tasks למקביליות ----
    # .s() = "signature" — מכין את הtask עם הארגומנטים בלי להריץ עדיין
    tasks = [
        AGENT_TASK_MAP[agent_name].s(req.company, req.job_title)
        for agent_name in agents_to_run
        if agent_name in AGENT_TASK_MAP
    ]

    try:
        # ---- 3. מזניק את כולם במקביל ומחכה לתוצאות ----
        # group() = "הרץ את כל אלה במקביל"
        # .apply_async() = שלח לRedis
        # .get(timeout=120) = חכה לכולם, עד 120 שניות
        results_list = group(tasks).apply_async().get(timeout=120)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

    # ---- 4. ממפה תוצאות לשמות ה-agents ----
    # results_list מגיע כרשימה — agent_name[0] מקביל לresult[0]
    results = dict(zip(agents_to_run, results_list))

    # מוודא שכל שדה קיים (agents שלא רצו = dict ריק)
    return ResearchResponse(
        company=results.get("company",   {}),
        glassdoor=results.get("glassdoor", {}),
        linkedin=results.get("linkedin",  {}),
        news=results.get("news",      {}),
        tech=results.get("tech",      {}),
        neetcode=results.get("neetcode",  {}),
    )
