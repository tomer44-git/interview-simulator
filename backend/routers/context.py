# routers/context.py
# POST /context — מקבל טקסט חופשי + קבצי PDF/Word ומחזיר סיכום לפרסונה
# משתמש ב-multipart/form-data כי מעביר קבצים בינאריים

import io
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from agents import context_agent

router = APIRouter()


def _extract_pdf(data: bytes) -> str:
    """חולץ טקסט מ-PDF בינארי — משתמש ב-pdfplumber"""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            # מאחד את הטקסט מכל הדפים
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as e:
        return f"[PDF parse error: {e}]"


def _extract_docx(data: bytes) -> str:
    """חולץ טקסט מ-Word בינארי — משתמש ב-python-docx"""
    try:
        import docx
        doc = docx.Document(io.BytesIO(data))
        # מאחד את כל הפסקאות
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"[DOCX parse error: {e}]"


@router.post("/context")
async def process_context(
    text:  str              = Form(default=""),
    files: list[UploadFile] = File(default=[]),
):
    """
    מקבל: multipart form עם text (חופשי) + files (PDF/Word, אופציונלי)
    מחזיר: {"context_summary": "..."} — ריק אם לא סופק קלט
    """
    file_contents = []

    for f in files:
        data = await f.read()
        name = (f.filename or "").lower()

        if name.endswith(".pdf"):
            file_contents.append(_extract_pdf(data))
        elif name.endswith(".docx") or name.endswith(".doc"):
            file_contents.append(_extract_docx(data))
        else:
            # קובץ טקסט רגיל — מנסה לקרוא כ-UTF-8
            try:
                file_contents.append(data.decode("utf-8", errors="replace"))
            except Exception:
                pass

    try:
        summary = context_agent.run(text, file_contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context processing failed: {e}")

    return {"context_summary": summary}
