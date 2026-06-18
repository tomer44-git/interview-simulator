# supabase_client.py
# מאתחל חיבור ל-Supabase לשמירת sessions
# אם המפתחות חסרים ב-.env — מחזיר None ולא קורס (Supabase אופציונלי בפיתוח)

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/Users/tomerbenbassat/Desktop/interview-simulator/.env", override=True)


def get_client():
    """
    מחזיר Supabase client אם המפתחות קיימים, אחרת None.
    כך אפשר לפתח ולבדוק בלי Supabase מוגדר.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    # ---- אם אחד מהמפתחות חסר או הוא placeholder — עוקפים Supabase ----
    # בודק שה-URL מתחיל ב-https:// (כתובת Supabase אמיתית תמיד מתחילה כך)
    if not url or not key or not url.startswith("https://"):
        return None

    from supabase import create_client
    return create_client(url, key)


def save_session(client, company: str, job_title: str,
                 persona: dict, state: dict, feedback: dict) -> str | None:
    """
    שומר session ל-Supabase ומחזיר את ה-ID שנוצר.
    מחזיר None אם client=None (Supabase לא מוגדר).

    טבלה נדרשת ב-Supabase:
    create table sessions (
      id          uuid primary key default gen_random_uuid(),
      company     text,
      job_title   text,
      persona_name text,
      transcript  jsonb,
      feedback    jsonb,
      created_at  timestamptz default now()
    );
    """
    if client is None:
        return None

    try:
        result = client.table("sessions").insert({
            "company":      company,
            "job_title":    job_title,
            "persona_name": persona.get("name"),
            "transcript":   state.get("history", []),
            "feedback":     feedback,
        }).execute()

        # מחזיר את ה-UUID שנוצר לrow החדש
        return result.data[0]["id"] if result.data else None

    except Exception as e:
        # שגיאת Supabase לא תקרוס את הAPI — רק נרשום ונמשיך
        print(f"   ⚠️  Supabase save failed: {e}")
        return None
