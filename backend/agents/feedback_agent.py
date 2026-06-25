# feedback_agent.py
# מנתח את תמליל הראיון המלא ומחזיר ציונים לפי ה-scoring_rubric מה-domain config
# קלט: state (היסטוריה מלאה) + persona + domain_config | פלט: dict עם ציונים מפורטים

import os
import json
import time
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"), override=True)


def run(state: dict, persona: dict, domain_config: dict) -> dict:
    """
    מנתח ראיון שהסתיים ומחזיר ציונים מפורטים.

    state         — המצב הסופי של הראיון (כולל history המלאה)
    persona       — פרסונת המראיין (שם חברה, תפקיד וכו')
    domain_config — config הדומיין (כולל scoring_rubric)
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # ---- מכין את תמליל הראיון בפורמט קריא ----
    transcript = _format_transcript(state.get("history", []))

    # ---- מכין את קריטריוני הניקוד בפורמט קריא ----
    rubric = _format_rubric(domain_config.get("scoring_rubric", {}))

    # ---- בונה את הפרומפט לClaude ----
    prompt = f"""You are a professional interview evaluator. Below is a transcript of an interview at {persona.get('company_name', 'the company')} for the role of {domain_config.get('name', 'the position')}.

Evaluate ONLY the CANDIDATE's answers against these criteria:
{rubric}

Return a JSON object with EXACTLY this structure (no other text):
{{
  "overall_score": <float 1-10>,
  "categories": {{
    "<category_name>": {{
      "score": <float 1-10>,
      "feedback": "<2-3 sentence honest assessment>",
      "strengths": ["<strength>", "<strength>"],
      "improvements": ["<specific area to improve>", "<specific area>"]
    }}
  }},
  "summary": "<3-4 sentence overall assessment of the candidate>",
  "top_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "areas_to_improve": ["<area 1>", "<area 2>", "<area 3>"],
  "recommended_resources": ["<specific book/course/topic to study>", "<resource 2>"]
}}

INTERVIEW TRANSCRIPT:
{transcript}"""

    # [LATENCY] מודד את קריאת Claude — הקריאה הארוכה ביותר (max_tokens=1500)
    _t = time.perf_counter()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    print(f"[LATENCY] claude/feedback_agent  {time.perf_counter()-_t:.3f}s")

    # ---- מפרסר את ה-JSON שחזר מClaude ----
    raw = response.content[0].text.strip()
    # מנקה markdown code blocks אם Claude עטף בהם
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _format_transcript(history: list) -> str:
    """ממיר את ה-history לתמליל קריא לClaude"""
    lines = []
    for turn in history:
        role = "Interviewer" if turn["role"] == "interviewer" else "Candidate"
        lines.append(f"{role}: {turn['content']}")
    return "\n\n".join(lines)


def _format_rubric(rubric: dict) -> str:
    """ממיר את ה-scoring_rubric לרשימה קריאה"""
    lines = []
    for category, criteria in rubric.items():
        lines.append(f"{category}:")
        for criterion in criteria:
            lines.append(f"  - {criterion}")
    return "\n".join(lines)
