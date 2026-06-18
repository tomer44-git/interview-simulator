# neetcode_agent.py
# תפקיד: שולף patterns ובעיות קידוד מ-NeetCode ו-LeetCode ספציפית לחברה
# קלט: שם חברה + תפקיד | פלט: dict עם patterns, בעיות, ורמת קושי מומלצת

import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

# אתרים ממוקדים — Tavily יחפש רק בהם
CODING_SITES = ["neetcode.io", "leetcode.com"]


def run(company_name: str, job_title: str) -> dict:
    """
    מחפש ב-NeetCode וב-LeetCode בלבד, ספציפית לחברה ולתפקיד.
    include_domains מגביל את Tavily לאתרים האלה בלבד — תוצאות הרבה יותר מדויקות.
    """

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # שאילתה 1: אילו patterns מ-NeetCode נשאלים בחברה הזו
    # include_domains = חיפוש רק ב-neetcode.io ו-leetcode.com
    patterns_results = client.search(
        query=f"{company_name} interview coding patterns topics neetcode",
        max_results=5,
        search_depth="advanced",
        include_domains=CODING_SITES
    )

    # שאילתה 2: בעיות LeetCode ספציפיות שנשאלו בחברה
    problems_results = client.search(
        query=f"{company_name} leetcode problems asked interview questions list",
        max_results=5,
        search_depth="advanced",
        include_domains=CODING_SITES
    )

    # שאילתה 3: roadmap של NeetCode לתפקיד הזה
    # NeetCode מארגן את הבעיות לפי תפקיד — מידע זהב לפרסונה
    roadmap_results = client.search(
        query=f"neetcode roadmap {job_title} study plan topics",
        max_results=3,
        search_depth="basic",
        include_domains=CODING_SITES
    )

    # שאילתה 4: רמת קושי — Easy/Medium/Hard המומלצים לחברה הזו
    difficulty_results = client.search(
        query=f"{company_name} interview difficulty easy medium hard leetcode frequency",
        max_results=3,
        search_depth="basic",
        include_domains=CODING_SITES
    )

    return {
        "company_name":        company_name,
        "job_title":           job_title,
        "patterns":            _extract_snippets(patterns_results),
        "specific_problems":   _extract_snippets(problems_results),
        "roadmap_topics":      _extract_snippets(roadmap_results),
        "difficulty_profile":  _extract_snippets(difficulty_results),
    }


def _extract_snippets(search_response: dict) -> list[str]:
    """מוציאה טקסט תוכן מתוצאות Tavily, מסננת ערכים ריקים"""
    results = search_response.get("results", [])
    return [r.get("content", "") for r in results if r.get("content")]
