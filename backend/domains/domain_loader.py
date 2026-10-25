# domain_loader.py
# מקבל job_title ומחזיר את ה-domain config המתאים
# להוסיף domain חדש: 1) צור קובץ config, 2) הוסף שורה ל-DOMAIN_MAP

from domains.tech import frontend_developer, junior_ai_engineer
from domains.finance import junior_analyst
from domains import base_domain

# ---- מיפוי job titles ל-configs ----
# המפתח הוא substring — אם job_title מכיל את המפתח, נחזיר את ה-config
# חשוב: סדר הרשימה משנה — הראשון שמתאים מנצח
DOMAIN_MAP = [
    ("junior ai",         junior_ai_engineer.DOMAIN_CONFIG),
    ("ai engineer",       junior_ai_engineer.DOMAIN_CONFIG),
    ("ml engineer",       junior_ai_engineer.DOMAIN_CONFIG),
    ("machine learning",  junior_ai_engineer.DOMAIN_CONFIG),
    ("frontend",          frontend_developer.DOMAIN_CONFIG),
    ("front-end",         frontend_developer.DOMAIN_CONFIG),
    ("front end",         frontend_developer.DOMAIN_CONFIG),
    ("ui developer",      frontend_developer.DOMAIN_CONFIG),
    ("react developer",   frontend_developer.DOMAIN_CONFIG),

    # פיננסים — תחום לא-הייטק. הוספתו דרשה קובץ config ושורות כאן
    # בלבד; המנועים לא השתנו בכלל.
    ("financial analyst", junior_analyst.DOMAIN_CONFIG),
    ("finance analyst",   junior_analyst.DOMAIN_CONFIG),
    ("investment analyst", junior_analyst.DOMAIN_CONFIG),
    ("equity research",   junior_analyst.DOMAIN_CONFIG),
]

# ברירת מחדל — אם לא נמצא התאמה
DEFAULT_CONFIG = frontend_developer.DOMAIN_CONFIG


def load(job_title: str) -> dict:
    """
    מקבל job_title (לא case-sensitive) ומחזיר את ה-domain config המתאים.
    אם לא נמצאה התאמה — מחזיר את frontend_developer כברירת מחדל.

    דוגמאות:
      load("Frontend Developer")  → frontend_developer config
      load("Junior AI Engineer")  → junior_ai_engineer config
      load("React Developer")     → frontend_developer config
      load("אחר")                 → frontend_developer config (default)
    """
    normalized = job_title.lower().strip()

    # מחפש התאמה ראשונה ב-DOMAIN_MAP
    for keyword, config in DOMAIN_MAP:
        if keyword in normalized:
            # מאמת שה-config תקין לפני החזרה
            base_domain.validate(config)
            return config

    # לא נמצאה התאמה — מחזיר ברירת מחדל עם הודעה
    print(f"   ℹ️  לא נמצא domain עבור '{job_title}' — משתמש ב-Frontend Developer כברירת מחדל")
    return DEFAULT_CONFIG


def list_supported() -> list[str]:
    """מחזיר רשימה של כל ה-job titles הנתמכים כרגע"""
    return [keyword for keyword, _ in DOMAIN_MAP]
