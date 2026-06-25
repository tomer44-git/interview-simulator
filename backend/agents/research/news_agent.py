# news_agent.py
# תפקיד: מחפש חדשות עדכניות על החברה — גיוסי הון, מוצרים, כיוון אסטרטגי
# קלט: שם חברה + תפקיד | פלט: dict עם funding, מוצרים, ואסטרטגיה

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient

# טוען מפתחות מ-.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


def run(company_name: str, job_title: str) -> dict:
    """
    מחפש חדשות עדכניות שמראיין אמיתי יזכיר בשיחה.
    משתמש ב-time_range של Tavily לסינון תוצאות עדכניות בלבד.
    """

    # [LATENCY] מדידת זמן כולל של ה-agent
    _t_agent = time.perf_counter()
    _ts_agent = datetime.now().isoformat(timespec='milliseconds')

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # שאילתה 1: גיוסי הון והשקעות — מאיפה מגיע הכסף?
    funding_results = client.search(
        query=f"{company_name} funding round investment valuation 2024 2025",
        max_results=3,
        search_depth="basic",
        time_range="year"   # חדש ב-Tavily 0.7+ — מסנן לשנה האחרונה בלבד
    )

    # שאילתה 2: מוצרים חדשים שהושקו לאחרונה
    product_results = client.search(
        query=f"{company_name} new product feature launch announcement 2024 2025",
        max_results=3,
        search_depth="basic",
        time_range="year"
    )

    # שאילתה 3: כיוון אסטרטגי — AI, expansion, שינויים גדולים
    strategy_results = client.search(
        query=f"{company_name} strategy roadmap AI expansion plans 2025",
        max_results=3,
        search_depth="basic"
    )

    # שאילתה 4: אתגרים ותחרות — מה לחצים על החברה?
    # חשוב: מראיין אמיתי רוצה לדעת שאתה מבין את הסביבה התחרותית
    challenges_results = client.search(
        query=f"{company_name} competition challenges market 2024 2025",
        max_results=2,
        search_depth="basic"
    )

    result = {
        "company_name": company_name,
        "job_title":    job_title,
        "funding":      _extract_snippets(funding_results),
        "new_products": _extract_snippets(product_results),
        "strategy":     _extract_snippets(strategy_results),
        "challenges":   _extract_snippets(challenges_results),
    }
    _duration = time.perf_counter() - _t_agent
    print(f"[LATENCY] {_ts_agent}  agent/news  {_duration:.3f}s")
    result["_timing"] = {"name": "news", "start": _ts_agent, "duration": _duration}
    return result


def _extract_snippets(search_response: dict) -> list[str]:
    """מוציאה טקסט תוכן מתוצאות Tavily, מסננת ערכים ריקים"""
    results = search_response.get("results", [])
    return [r.get("content", "") for r in results if r.get("content")]
