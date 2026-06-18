# persona_builder.md

## מה ה-agent עושה
Agent ראשון שמשתמש ב-Claude API. מקבל את כל נתוני המחקר מ-4 agents,
שולח פרומפט ל-claude-sonnet-4-20250514, ומחזיר דמות מראיין מציאותית כ-dict.

## קלט / פלט
**קלט:** 4 dicts — `company_data`, `glassdoor_data`, `linkedin_data`, `news_data`
**פלט:**
```python
{
  "name": str,                  # שם מלא של המראיין
  "title": str,                 # תפקידו בחברה
  "years_at_company": int,      # שנות ותק
  "interview_style": str,       # תיאור סגנון הראיון
  "personality_traits": [str],  # 3 תכונות אישיות
  "focus_areas": [str],         # 3 תחומים טכניים שמתמקד בהם
  "opening_statement": str,     # משפט פתיחה של הראיון
  "likely_questions": [str],    # 5 שאלות אופייניות
  "company_context": str,       # מה מייחד את החברה
  "company_name": str,
  "job_title": str
}
```

## תהליך הפעולה
```
1. בדיקת ANTHROPIC_API_KEY — זורק ValueError אם חסר
2. _prepare_summary() — מקצר את נתוני המחקר ל-snippet אחד לכל קטגוריה
3. בניית פרומפט עם הנתונים הקומפקטיים
4. קריאה ל-claude-sonnet-4-20250514 (max_tokens=1024)
5. פרסור JSON מהתשובה — עם fallback לניקוי markdown
6. הוספת metadata (company_name, job_title)
```

## תלויות
`anthropic>=0.60.0`, `python-dotenv` | משתנה: `ANTHROPIC_API_KEY`

## עלות משוערת לכל קריאה
~500-800 tokens = פחות מ-$0.01 לכל בניית פרסונה

## קשרים
- קורא לו: `orchestrator.py` (Step 6), `test_agents.py`
- מקבל קלט מ: `company_agent`, `glassdoor_agent`, `linkedin_agent`, `news_agent`
- מעביר פלט אל: `interview_agent.py` (Step 4)
