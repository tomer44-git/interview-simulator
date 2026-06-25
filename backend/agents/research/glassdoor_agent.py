# glassdoor_agent.py
# תפקיד: מחפש שאלות ראיון אמיתיות וחוויות מועמדים דרך Tavily
# קלט: שם חברה + תפקיד | פלט: dict עם שאלות, תהליך, ורמת קושי

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient

# טוען את המפתחות מקובץ .env שנמצא שתי תיקיות למעלה
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


def run(company_name: str, job_title: str) -> dict:
    """
    מריץ את ה-agent: מחפש חוויות ראיון מהאינטרנט ומחזיר dict מסודר.
    company_name — שם החברה (לדוגמה: "Wix")
    job_title    — התפקיד המבוקש (לדוגמה: "Frontend Developer")
    """

    # [LATENCY] מדידת זמן כולל של ה-agent
    _t_agent = time.perf_counter()
    _ts_agent = datetime.now().isoformat(timespec='milliseconds')

    # מאתחל את לקוח Tavily עם המפתח מה-.env
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # ---- 4 שאילתות ממוקדות לחוויות ראיון ----

    # שאילתה 1: שאלות ראיון ספציפיות לחברה ולתפקיד
    questions_results = client.search(
        query=f"{company_name} {job_title} interview questions asked 2024 2025",
        max_results=4,
        search_depth="advanced"   # advanced = חיפוש עמוק יותר, שווה את הזמן כאן
    )

    # שאילתה 2: חוויות ראיון מ-Glassdoor ומאתרים דומים (Reddit, Blind, וכו׳)
    glassdoor_results = client.search(
        query=f"{company_name} interview experience glassdoor {job_title} process",
        max_results=3,
        search_depth="advanced"
    )

    # שאילתה 3: שאלות טכניות / קידוד ספציפיות
    technical_results = client.search(
        query=f"{company_name} technical interview coding questions {job_title} leetcode",
        max_results=3,
        search_depth="basic"
    )

    # שאילתה 4: רמת קושי ופידבק על תהליך הגיוס
    difficulty_results = client.search(
        query=f"{company_name} interview difficulty rating hiring process review",
        max_results=2,
        search_depth="basic"
    )

    # ---- מחזיר dict מסודר ----
    result = {
        "company_name": company_name,
        "job_title": job_title,
        "reported_questions":     _extract_snippets(questions_results),
        "interview_experiences":  _extract_snippets(glassdoor_results),
        "technical_topics":       _extract_snippets(technical_results),
        "difficulty_and_process": _extract_snippets(difficulty_results),
    }
    # [LATENCY] מחזיר timing לroutr להשוואת מקביליות
    _duration = time.perf_counter() - _t_agent
    print(f"[LATENCY] {_ts_agent}  agent/glassdoor  {_duration:.3f}s")
    result["_timing"] = {"name": "glassdoor", "start": _ts_agent, "duration": _duration}
    return result


def _extract_snippets(search_response: dict) -> list[str]:
    """
    פונקציית עזר פנימית.
    מוציאה את טקסט התוכן מכל תוצאת חיפוש של Tavily, מסננת ערכים ריקים.
    """
    results = search_response.get("results", [])
    return [r.get("content", "") for r in results if r.get("content")]
