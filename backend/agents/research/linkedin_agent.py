# linkedin_agent.py
# תפקיד: מחפש מידע ציבורי מ-LinkedIn דרך Tavily
# קלט: שם חברה + תפקיד | פלט: dict עם דרישות, תרבות, וסיגנלים

import os
from dotenv import load_dotenv
from tavily import TavilyClient

# טוען מפתחות מ-.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


def run(company_name: str, job_title: str) -> dict:
    """
    מחפש מידע LinkedIn דרך Tavily.
    LinkedIn חוסם גישה ישירה, אך Tavily מוצא תוכן מאונדקס בגוגל.
    """

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # שאילתה 1: דרישות תפקיד אמיתיות ממשרות פתוחות ב-LinkedIn
    # חשוב: משרות פתוחות חושפות בדיוק מה החברה מחפשת
    job_results = client.search(
        query=f"{company_name} {job_title} linkedin job requirements skills responsibilities 2024 2025",
        max_results=4,
        search_depth="advanced"
    )

    # שאילתה 2: פוסטים של מהנדסים ועובדים על עבודה בחברה
    culture_results = client.search(
        query=f"linkedin {company_name} engineer working culture team experience post",
        max_results=3,
        search_depth="basic"
    )

    # שאילתה 3: מידע על הצוות הטכני — מנהלים, גודל צוות, מבנה
    team_results = client.search(
        query=f"{company_name} engineering team linkedin manager director {job_title} structure",
        max_results=3,
        search_depth="basic"
    )

    # שאילתה 4: סיגנלי גיוס — האם החברה מגייסת? כמה תפקידים פתוחים?
    hiring_results = client.search(
        query=f"{company_name} hiring {job_title} 2024 2025 open positions linkedin",
        max_results=2,
        search_depth="basic"
    )

    return {
        "company_name": company_name,
        "job_title": job_title,
        "job_requirements": _extract_snippets(job_results),
        "team_culture":     _extract_snippets(culture_results),
        "team_structure":   _extract_snippets(team_results),
        "hiring_signals":   _extract_snippets(hiring_results),
    }


def _extract_snippets(search_response: dict) -> list[str]:
    """מוציאה טקסט תוכן מתוצאות Tavily, מסננת ערכים ריקים"""
    results = search_response.get("results", [])
    return [r.get("content", "") for r in results if r.get("content")]
