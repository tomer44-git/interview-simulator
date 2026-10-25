# routers/persona.py
# POST /persona — מקבל נתוני מחקר ומחזיר פרסונת מראיין

import time
from datetime import datetime
from fastapi import APIRouter, Depends
from auth import get_current_user
from errors import server_error
from models.schemas import PersonaRequest, PersonaResponse
from agents import persona_builder
from latency import _record

router = APIRouter()


@router.post("/persona", response_model=PersonaResponse)
def build_persona(req: PersonaRequest, _user=Depends(get_current_user)):
    """
    מקבל: {"research": {...}, "job_title": "...", "language": "en"/"he", "context_summary": "..."}
    מחזיר: {"persona": {...פרסונת המראיין...}}
    """
    try:
        _t = time.perf_counter()
        _ts = datetime.now().isoformat(timespec='milliseconds')

        persona = persona_builder.run(
            company_data=req.research.get("company",   {}),
            glassdoor_data=req.research.get("glassdoor", {}),
            linkedin_data=req.research.get("linkedin",  {}),
            news_data=req.research.get("news",      {}),
            neetcode_data=req.research.get("neetcode",  {}),
            language=req.language,
            context_summary=req.context_summary,
        )
        _record("stage/persona", _ts, time.perf_counter() - _t)
    except Exception as e:
        raise server_error("Persona build failed", e)

    return PersonaResponse(persona=persona)
