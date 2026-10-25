# routers/context.py
# POST /context — מקבל טקסט חופשי + קבצי PDF/Word ומחזיר סיכום לפרסונה
# משתמש ב-multipart/form-data כי מעביר קבצים בינאריים

import io
import logging

from fastapi import APIRouter, File, Form, UploadFile, Depends

from auth import get_current_user
from errors import server_error
from agents import context_agent

router = APIRouter()

logger = logging.getLogger("interview_simulator")


def _extract_pdf(data: bytes) -> str | None:
    """
    חולץ טקסט מ-PDF. מחזיר None אם הקובץ לא ניתן לקריאה.

    חשוב שזה יחזיר None ולא מחרוזת שגיאה: הערך הזה נכנס לתוכן שנשלח
    ל-Claude. קודם הוחזר כאן f"[PDF parse error: {e}]", כלומר קובץ פגום
    ייצר "תוכן מסמך" שהוא בעצם הודעת שגיאה, והפרסונה נבנתה עליו.
    """
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        logger.exception("PDF extraction failed")
        return None


def _extract_docx(data: bytes) -> str | None:
    """חולץ טקסט מ-Word. מחזיר None אם נכשל — מאותה סיבה כמו ב-PDF"""
    try:
        import docx
        doc = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception:
        logger.exception("DOCX extraction failed")
        return None


def _extract_plain(data: bytes) -> str | None:
    """קובץ טקסט רגיל — מנסה UTF-8"""
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        logger.exception("Plain text decode failed")
        return None


@router.post("/context")
async def process_context(
    text:  str              = Form(default=""),
    files: list[UploadFile] = File(default=[]),
    _user=Depends(get_current_user),
):
    """
    מקבל: multipart form עם text (חופשי) + files (PDF/Word, אופציונלי)
    מחזיר: {"context_summary": "...", "skipped_files": [...]}

    קובץ שלא ניתן לקריאה מדולג ושמו מוחזר — עדיף להודיע למשתמש
    מאשר לבנות פרסונה על תוכן שהוא בעצם הודעת שגיאה.
    """
    file_contents: list[str] = []
    skipped: list[str] = []

    for f in files:
        data = await f.read()
        name = (f.filename or "").lower()

        if name.endswith(".pdf"):
            extracted = _extract_pdf(data)
        elif name.endswith((".docx", ".doc")):
            extracted = _extract_docx(data)
        else:
            extracted = _extract_plain(data)

        # מדלגים גם על כישלון וגם על קובץ שהתברר כריק
        if extracted and extracted.strip():
            file_contents.append(extracted)
        else:
            skipped.append(f.filename or "unnamed file")

    try:
        summary = context_agent.run(text, file_contents)
    except Exception as e:
        raise server_error("Context processing failed", e)

    return {"context_summary": summary, "skipped_files": skipped}
