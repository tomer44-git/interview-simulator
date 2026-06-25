# tech_agent.py
# תפקיד: מחקר טכני ממוקד — LeetCode patterns, GitHub, system design
# קלט: שם חברה + תפקיד | פלט: dict עם נושאים טכניים לראיון

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient

# טוען מפתחות מ-.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


def run(company_name: str, job_title: str) -> dict:
    """
    מחפש תוכן טכני שמכין את מנוע השאלות לשאלות קידוד ו-system design.
    התוצאות מוזנות ישירות ל-interview_agent ליצירת שאלות טכניות מדויקות.
    """

    # [LATENCY] מדידת זמן כולל של ה-agent
    _t_agent = time.perf_counter()
    _ts_agent = datetime.now().isoformat(timespec='milliseconds')

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # שאילתה 1: דפוסי LeetCode/קידוד שנשאלים לתפקיד הזה
    # חשוב: לא חיפוש גנרי אלא ספציפי לחברה + תפקיד
    leetcode_results = client.search(
        query=f"{company_name} {job_title} coding interview leetcode patterns algorithms data structures",
        max_results=4,
        search_depth="advanced"
    )

    # שאילתה 2: ריפוזים של החברה ב-GitHub — מגלה את הטכנולוגיות האמיתיות בשימוש
    github_results = client.search(
        query=f"{company_name} github open source repositories technologies stack",
        max_results=3,
        search_depth="basic"
    )

    # שאילתה 3: שאלות system design ספציפיות לתפקיד ולחברה
    system_design_results = client.search(
        query=f"{company_name} {job_title} system design interview questions scalability",
        max_results=3,
        search_depth="advanced"
    )

    # שאילתה 4: אתגרים טכניים ייחודיים לחברה — מה הם פתרו? מה הם בנו?
    # זה נותן חומר לשאלות "tell me about a technical challenge" ספציפיות לחברה
    challenges_results = client.search(
        query=f"{company_name} engineering technical challenges scale architecture blog",
        max_results=2,
        search_depth="basic"
    )

    result = {
        "company_name":    company_name,
        "job_title":       job_title,
        "coding_patterns": _extract_snippets(leetcode_results),
        "github_stack":    _extract_snippets(github_results),
        "system_design":   _extract_snippets(system_design_results),
        "tech_challenges": _extract_snippets(challenges_results),
    }
    _duration = time.perf_counter() - _t_agent
    print(f"[LATENCY] {_ts_agent}  agent/tech  {_duration:.3f}s")
    result["_timing"] = {"name": "tech", "start": _ts_agent, "duration": _duration}
    return result


def _extract_snippets(search_response: dict) -> list[str]:
    """מוציאה טקסט תוכן מתוצאות Tavily, מסננת ערכים ריקים"""
    results = search_response.get("results", [])
    return [r.get("content", "") for r in results if r.get("content")]
