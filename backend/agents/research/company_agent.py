# company_agent.py
# תפקיד: מחפש מידע רשמי על החברה דרך Tavily ומחזיר dict מסודר
# קלט: שם חברה + תפקיד | פלט: dict עם מידע על החברה

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient

# טוען את המפתחות מקובץ .env שנמצא שתי תיקיות למעלה מהקובץ הזה
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


def run(company_name: str, job_title: str) -> dict:
    """
    מריץ את ה-agent: שולח שאילתות לטאווילי ומחזיר dict עם מידע על החברה.
    company_name — שם החברה (לדוגמה: "Google")
    job_title    — התפקיד המבוקש (לדוגמה: "Junior AI Engineer")
    """

    # [LATENCY] מדידת זמן כולל של ה-agent מתחילה כאן
    _t_agent = time.perf_counter()
    _ts_agent = datetime.now().isoformat(timespec='milliseconds')

    # מאתחל את לקוח Tavily עם המפתח מה-.env
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # ---- 4 שאילתות חיפוש ממוקדות ----
    # כל שאילתה מכוונת למידע ספציפי כדי שנקבל תוצאות רלוונטיות יותר

    # שאילתה 1: תיאור כללי של החברה
    _t = time.perf_counter()
    overview_results = client.search(
        query=f"{company_name} company overview mission products 2024 2025",
        max_results=3,
        search_depth="basic"
    )
    print(f"[LATENCY] tavily/company/overview  {time.perf_counter()-_t:.3f}s")

    # שאילתה 2: ה-tech stack שהחברה משתמשת בו
    _t = time.perf_counter()
    tech_results = client.search(
        query=f"{company_name} tech stack engineering technologies {job_title}",
        max_results=3,
        search_depth="basic"
    )
    print(f"[LATENCY] tavily/company/tech_stack  {time.perf_counter()-_t:.3f}s")

    # שאילתה 3: בלוג הנדסי / תרבות הצוות הטכני
    _t = time.perf_counter()
    culture_results = client.search(
        query=f"{company_name} engineering blog culture values team",
        max_results=2,
        search_depth="basic"
    )
    print(f"[LATENCY] tavily/company/culture  {time.perf_counter()-_t:.3f}s")

    # שאילתה 4: חדשות אחרונות על החברה
    _t = time.perf_counter()
    news_results = client.search(
        query=f"{company_name} latest news product launch funding 2024 2025",
        max_results=2,
        search_depth="basic"
    )
    print(f"[LATENCY] tavily/company/news  {time.perf_counter()-_t:.3f}s")

    # ---- מעבד את התוצאות לפורמט נקי ----
    # הפונקציה _extract_snippets מוציאה רק את טקסט התוצאות (בלי URLs ומטא-דאטה)
    result = {
        "company_name": company_name,
        "job_title": job_title,
        "overview": _extract_snippets(overview_results),
        "tech_stack": _extract_snippets(tech_results),
        "culture": _extract_snippets(culture_results),
        "recent_news": _extract_snippets(news_results),
    }

    # [LATENCY] מחזיר את זמן הריצה הכולל — יחולץ ע"י research router להשוואת מקביליות
    _duration = time.perf_counter() - _t_agent
    print(f"[LATENCY] {_ts_agent}  agent/company  {_duration:.3f}s  (total)")
    result["_timing"] = {"name": "company", "start": _ts_agent, "duration": _duration}
    return result


def _extract_snippets(search_response: dict) -> list[str]:
    """
    פונקציית עזר פנימית (לא נקראת מבחוץ).
    מוציאה רק את שדה ה-content מכל תוצאת חיפוש ומחזירה רשימת טקסטים.
    """
    results = search_response.get("results", [])
    # עוברים על כל תוצאה ומוציאים את התוכן, מסננים ערכים ריקים
    return [r.get("content", "") for r in results if r.get("content")]
