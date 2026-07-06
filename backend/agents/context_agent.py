# context_agent.py
# תפקיד: מקבל טקסט חופשי + תוכן קבצים → מחזיר סיכום קצר לפרסונה
# הסיכום מוזרק לפרומפט של persona_builder כדי לדייק את הראיון

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"), override=True)


def run(free_text: str, file_contents: list[str]) -> str:
    """
    מקבל טקסט חופשי על תהליך הגיוס + תוכן קבצים (מטלות בית וכו').
    מחזיר סיכום קצר (עד 300 מילים) שיוזרק לפרסונת המראיין.
    אם אין קלט — מחזיר מחרוזת ריקה (context אופציונלי).
    """
    # אם אין שום קלט — אין טעם לקרוא ל-Claude
    combined = free_text.strip()
    if file_contents:
        combined += "\n\n" + "\n\n---\n\n".join(file_contents)

    if not combined.strip():
        return ""

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # מגביל את גודל הקלט כדי לא לבזבז tokens
    if len(combined) > 8000:
        combined = combined[:8000] + "\n[content truncated]"

    prompt = f"""You are analyzing a job candidate's interview history to help an interviewer tailor their questions.

The candidate provided the following context about their interview process so far:

---
{combined}
---

Extract and summarize ONLY what is useful for an interviewer to know:
- How many interview rounds have already happened
- What home assignments or take-home tasks were given (summarize key requirements)
- What topics were already covered or tested
- Any feedback the candidate received
- What stage of the process this interview is at

Return a concise summary (under 200 words). If something is not mentioned, skip it.
Focus on process facts, not the candidate's personal qualities."""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()
