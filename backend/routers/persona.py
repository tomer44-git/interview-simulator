# routers/persona.py
# POST /persona — מקבל נתוני מחקר ומחזיר פרסונת מראיין
# route פשוט — אין Celery כאן, Claude API רץ ישירות

import time
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import PersonaRequest, PersonaResponse
from agents import persona_builder
from latency import _record

router = APIRouter()


@router.post("/persona", response_model=PersonaResponse)
def build_persona(req: PersonaRequest):
    """
    מקבל: {"research": {...כל נתוני המחקר...}, "job_title": "Frontend Developer"}
    מחזיר: {"persona": {...פרסונת המראיין...}}

    קורא ל-Claude API ובונה מראיין בעל שם ואישיות ספציפית
    """
    try:
        # [LATENCY] מדידת שלב הפרסונה
        _t = time.perf_counter()
        _ts = datetime.now().isoformat(timespec='milliseconds')

        # ---- מוציא כל סוג מחקר מהdictionary ----
        persona = persona_builder.run(
            company_data=req.research.get("company",   {}),
            glassdoor_data=req.research.get("glassdoor", {}),
            linkedin_data=req.research.get("linkedin",  {}),
            news_data=req.research.get("news",      {}),
            neetcode_data=req.research.get("neetcode",  {}),
        )
        _record("stage/persona", _ts, time.perf_counter() - _t)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Persona build failed: {str(e)}")

    return PersonaResponse(persona=persona)
