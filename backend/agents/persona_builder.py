# persona_builder.py
# תפקיד: מקבל נתוני מחקר מכל ה-agents → בונה דמות מראיין עם Claude API
# קלט: 5 dicts ממחקר (כולל neetcode) | פלט: dict עם פרסונה מלאה

import os
import json
import time
from dotenv import load_dotenv
from anthropic import Anthropic

# טוען מפתחות מ-.env — override=True מבטיח שהערך מה-.env תמיד גובר
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"), override=True)


def _clean(obj):
    """cleans all non-ASCII from Tavily data before use"""
    if isinstance(obj, str):
        return obj.encode('ascii', errors='replace').decode('ascii')
    if isinstance(obj, list):
        return [_clean(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    return obj


def run(company_data: dict, glassdoor_data: dict,
        linkedin_data: dict, news_data: dict,
        neetcode_data: dict = None, language: str = "en") -> dict:
    """
    בונה פרסונת מראיין. neetcode_data אופציונלי.
    language: "en" לאנגלית, "he" לעברית — קובע את שפת הפרסונה.
    """

    # מנקה את כל הנתונים מTavily לפני שמשתמשים בהם —
    # U+2028 (LINE SEP) and U+2029 (PARA SEP) from Tavily web content break Railway ASCII stdout
    company_data   = _clean(company_data)
    glassdoor_data = _clean(glassdoor_data)
    linkedin_data  = _clean(linkedin_data)
    news_data      = _clean(news_data)
    if neetcode_data:
        neetcode_data = _clean(neetcode_data)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_anthropic_key_here":
        raise ValueError(
            "ANTHROPIC_API_KEY חסר ב-.env — הוסף מפתח אמיתי מ-console.anthropic.com"
        )

    client = Anthropic(api_key=api_key)

    # מכין תקציר מחקר — כולל NeetCode אם קיים
    research_summary = _prepare_summary(
        company_data, glassdoor_data, linkedin_data, news_data, neetcode_data
    )

    # הוראה ל-Claude: אם יש neetcode_data — השתמש בו לשאלות קידוד ספציפיות
    coding_instruction = ""
    if neetcode_data and neetcode_data.get("specific_problems"):
        coding_instruction = (
            "\nIMPORTANT: The NEETCODE DATA section contains real LeetCode problems "
            "and patterns asked at this company. Use specific problem names and patterns "
            "in the coding_question field — don't invent generic ones."
        )

    # הוראת שפה — שורה אחת שמספיקה לגרום ל-Claude לדבר בשפה הנכונה
    lang_instruction = "\nIMPORTANT: Generate ALL text fields in Hebrew." if language == "he" else ""

    prompt = f"""You are an expert at creating realistic job interview simulations.

Based on this company research, create a realistic interviewer persona.{coding_instruction}{lang_instruction}

=== RESEARCH DATA ===
{research_summary}
====================

Create a persona for someone who would interview a candidate for: {company_data['job_title']} at {company_data['company_name']}

Return ONLY valid JSON — no markdown, no explanation, just the JSON object:

{{
  "name": "realistic full name",
  "title": "their actual job title at the company",
  "years_at_company": <number 1-8>,
  "interview_style": "one sentence describing how they conduct interviews",
  "personality_traits": ["trait1", "trait2", "trait3"],
  "focus_areas": ["area 1", "area 2", "area 3"],
  "opening_statement": "Hi, I'm [name], [title] at [company]. [1-2 sentences intro]",
  "likely_questions": [
    "HR question specific to this company",
    "behavioral question",
    "technical/system design question",
    "technical/system design question",
    "coding question referencing a real pattern or problem from NeetCode data"
  ],
  "coding_question": "one specific coding problem or pattern from the NeetCode data",
  "company_context": "one sentence about what makes this company unique to interview at"
}}"""

    # [LATENCY] מודד את קריאת Claude API — זה ה-bottleneck של שלב הפרסונה
    _t = time.perf_counter()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    print(f"[LATENCY] claude/persona_builder  {time.perf_counter()-_t:.3f}s")

    raw_text = response.content[0].text.strip()

    try:
        persona = json.loads(raw_text)
    except json.JSONDecodeError:
        # Claude לפעמים עוטף ב-markdown — מנקה ומנסה שוב
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        persona = json.loads(cleaned)

    # מוסיף מטא-דאטה
    persona["company_name"] = company_data["company_name"]
    persona["job_title"]    = company_data["job_title"]

    return persona


def _prepare_summary(company_data: dict, glassdoor_data: dict,
                     linkedin_data: dict, news_data: dict,
                     neetcode_data: dict = None) -> str:
    """
    מכין תקציר קומפקטי. מוסיף סקציית NeetCode אם הנתונים קיימים.
    """

    def first(lst: list, max_chars: int = 400) -> str:
        """מחזיר snippet ראשון מרשימה, חתוך ל-max_chars, ומנקה תווי Unicode בעייתיים"""
        if not lst:
            return "No data found"
        text = str(lst[0])[:max_chars]
        # chr(0x2028)=LINE SEP, chr(0x2029)=PARA SEP -- strip these from Tavily content
        return text.replace(chr(0x2028), ' ').replace(chr(0x2029), ' ')

    summary = f"""
COMPANY: {company_data.get('company_name')} | ROLE: {company_data.get('job_title')}

COMPANY OVERVIEW: {first(company_data.get('overview', []))}

TECH STACK: {first(company_data.get('tech_stack', []))}

ENGINEERING CULTURE: {first(company_data.get('culture', []))}

RECENT NEWS: {first(news_data.get('new_products', []))} | {first(news_data.get('funding', []))}

JOB REQUIREMENTS: {first(linkedin_data.get('job_requirements', []))}

INTERVIEW QUESTIONS REPORTED: {first(glassdoor_data.get('reported_questions', []))}

INTERVIEW PROCESS: {first(glassdoor_data.get('interview_experiences', []))}"""

    # מוסיף סקציית NeetCode רק אם הנתונים קיימים
    if neetcode_data:
        summary += f"""

NEETCODE DATA — CODING PATTERNS AT THIS COMPANY:
{first(neetcode_data.get('patterns', []))}

SPECIFIC LEETCODE PROBLEMS ASKED:
{first(neetcode_data.get('specific_problems', []))}

DIFFICULTY PROFILE:
{first(neetcode_data.get('difficulty_profile', []))}"""

    return summary
