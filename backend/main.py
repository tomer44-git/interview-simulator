# main.py
# נקודת הכניסה של ה-FastAPI app
# מאחד את כל ה-routers ומגדיר הגדרות גלובליות

import sys
import os

# מוסיף את תיקיית backend ל-path כדי שכל הimports יעבדו
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import research, persona, interview, feedback

# ---- יצירת ה-FastAPI app ----
app = FastAPI(
    title="Interview Simulator API",
    description="Multi-agent AI interview simulator",
    version="1.0.0",
)

# ---- CORS — מאפשר ל-React לדבר עם ה-backend ----
# בלי זה, הדפדפן יחסום כל בקשה מlocalhost:5173 ל-localhost:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # React dev server (Vite)
        "http://localhost:3000",   # React dev server (CRA — גיבוי)
    ],
    allow_credentials=True,
    allow_methods=["*"],           # GET, POST, OPTIONS וכו'
    allow_headers=["*"],
)

# ---- מחבר את כל ה-routers ל-app ----
# כל router מכיל קבוצת endpoints קשורים
app.include_router(research.router,  tags=["Research"])
app.include_router(persona.router,   tags=["Persona"])
app.include_router(interview.router, tags=["Interview"])
app.include_router(feedback.router,  tags=["Feedback"])


# ---- health check ----
# נשלח אליו כדי לוודא שהשרת עלה
@app.get("/")
def health_check():
    return {"status": "ok", "service": "Interview Simulator API"}
