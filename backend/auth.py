# auth.py
# מאמת שכל בקשה ל-API מגיעה ממשתמש מחובר
# מוגדר כ-FastAPI Dependency — מוסיפים אותו לכל route שצריך הגנה

import os
from fastapi import Header, HTTPException
from supabase import create_client, Client

# client יחיד לכל חיי השרת — יעיל יותר מיצירה מחדש בכל בקשה
_client: Client = None


def _get_client() -> Client:
    """מחזיר את ה-Supabase client, יוצר אותו פעם אחת (lazy init)"""
    global _client
    if _client is None:
        _client = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_KEY", ""),
        )
    return _client


def get_current_user(authorization: str = Header(...)):
    """
    FastAPI Dependency — רץ לפני כל route שמשתמש ב-Depends(get_current_user)

    מה הוא עושה:
    1. מוציא את ה-JWT token מה-Authorization header
    2. שולח אותו ל-Supabase לאימות
    3. אם תקין → מחזיר את פרטי המשתמש (אפשר להשתמש בהם בroute)
    4. אם לא תקין → זורק שגיאת 401 Unauthorized
    """
    # בדיקה שה-header מגיע בפורמט הנכון: "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must be: Bearer <token>")

    token = authorization[7:]  # חותך את "Bearer " ולוקח רק את ה-token

    try:
        # Supabase מאמת את ה-token ומחזיר את פרטי המשתמש
        resp = _get_client().auth.get_user(token)
        return resp.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
