# orchestrator.py
# תפקיד: מתזמר את הרצת סוכני המחקר במקביל ומרכיב את התוצאות
# קלט: שם חברה + תפקיד + domain_config | פלט: תוצאות כל הסוכנים + זמני ריצה
#
# הלוגיקה הזו ישבה קודם בתוך routers/research.py. היא הועברה לכאן כדי
# שה-router יטפל ב-HTTP בלבד, ושהתיזמור יהיה ניתן לבדיקה בלי שרת.

from celery import group

from tasks.research_tasks import AGENT_TASK_MAP

# כמה זמן לחכות לכל הסוכנים יחד.
# הסוכן האיטי קובע — הם רצים במקביל, לא בטור.
RESEARCH_TIMEOUT_SECONDS = 120


class OrchestrationError(Exception):
    """
    נזרקת כשהרצת המחקר המקבילה נכשלה — timeout, Redis שנפל,
    או סוכן שזרק חריגה.

    מכוונת לכך שה-router יתרגם אותה ל-HTTP. שכבת הסוכנים לא אמורה
    לדעת ש-HTTP קיים בכלל.
    """


def run_research(
    company: str,
    job_title: str,
    domain_config: dict,
    timeout: int = RESEARCH_TIMEOUT_SECONDS,
) -> dict:
    """
    מריץ את סוכני המחקר של הדומיין במקביל דרך Celery.

    מחזיר:
      {
        "results": {"company": {...}, "glassdoor": {...}, ...},
        "timings": [{"name": "company", "start": ..., "duration": ...}, ...],
      }

    זורק OrchestrationError אם ההרצה נכשלה.

    שים לב: אם סוכן אחד זורק, כל ה-group נכשל ושום תוצאה לא חוזרת.
    אין כרגע graceful degradation — זו החלטה מודעת שמתועדת
    ב-MULTI_USER_PLAN.md. כשנרצה להוסיף אותה, כאן המקום.
    """
    requested = domain_config["research_agents"]

    # מסנן שמות שאין להם task מתאים — config עם שגיאת כתיב לא יפיל את כולם
    agents_to_run = [name for name in requested if name in AGENT_TASK_MAP]

    unknown = [name for name in requested if name not in AGENT_TASK_MAP]
    if unknown:
        print(f"[orchestrator] שמות סוכנים לא מוכרים ב-config, מדלג: {unknown}")

    if not agents_to_run:
        raise OrchestrationError(
            f"אף סוכן מחקר תקין לא הוגדר עבור '{domain_config.get('name')}'"
        )

    # .s() בונה signature — מכין את ה-task עם הארגומנטים בלי להריץ עדיין
    tasks = [AGENT_TASK_MAP[name].s(company, job_title) for name in agents_to_run]

    try:
        # group() = הרץ את כולם במקביל | apply_async() = שלח ל-Redis
        results_list = group(tasks).apply_async().get(timeout=timeout)
    except Exception as exc:
        raise OrchestrationError(str(exc)) from exc

    # חשוב: מצמידים ל-agents_to_run (המסונן) ולא ל-requested המקורי.
    # צמידות לרשימה המקורית הייתה מזיזה את כל התוצאות במקום אחד
    # ברגע שסוכן אחד מסונן החוצה — ושיוך שקט של תוצאה לסוכן הלא נכון.
    results = dict(zip(agents_to_run, results_list))

    return {
        "results": results,
        "timings": _extract_timings(results, agents_to_run),
    }


def _extract_timings(results: dict, agent_names: list) -> list:
    """
    שולף את מפתח _timing מכל תוצאה ומסיר אותו ממנה.

    ההסרה חשובה: _timing הוא מטא-דאטה של מדידה ולא נתוני מחקר,
    והוא לא אמור להמשיך משם לסכמת התשובה או לפרומפט של הפרסונה.
    """
    timings = []
    for name in agent_names:
        timing = results[name].pop("_timing", None)
        if timing:
            timings.append(timing)
    return timings
