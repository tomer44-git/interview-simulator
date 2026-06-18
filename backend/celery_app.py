# celery_app.py
# מגדיר את ה-Celery instance — מנהל המשימות המקבילות
# Redis משמש כ-broker (תור המשימות) וכ-backend (אחסון תוצאות)

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"), override=True)

# ---- כתובת Redis ----
# ברירת מחדל: Redis מקומי על פורט 6379
# בproduction (Railway) — ה-.env יכיל REDIS_URL אמיתי
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ---- יצירת ה-Celery app ----
# broker  = היכן Celery שם משימות חדשות לביצוע
# backend = היכן Celery שומר תוצאות שהסתיימו
celery = Celery(
    "interview_simulator",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# ---- הגדרות סידור נתונים ----
# JSON הוא פורמט קריא ובטוח לשמירת tasks ותוצאות
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # כמה זמן לשמור תוצאה ב-Redis אחרי שהסתיימה (שעה)
    result_expires=3600,
)
