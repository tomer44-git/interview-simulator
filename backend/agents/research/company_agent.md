# company_agent.md
> תיעוד מלא של ה-agent — קרא לפני כל שינוי בקוד

## מה ה-agent הזה עושה
מחפש מידע רשמי ועדכני על חברה יעד דרך Tavily.
מחזיר dict מסודר עם overview, tech stack, תרבות הנדסית, וחדשות אחרונות.

---

## קלט (Input)
| פרמטר | סוג | דוגמה |
|--------|-----|--------|
| `company_name` | string | `"Wix"` |
| `job_title` | string | `"Frontend Developer"` |

---

## פלט (Output)
```python
{
  "company_name": str,       # שם החברה כפי שהוזן
  "job_title": str,          # התפקיד כפי שהוזן
  "overview": [str, ...],    # 3 snippets — תיאור כללי, מוצרים, מיזיון
  "tech_stack": [str, ...],  # 3 snippets — טכנולוגיות, frameworks, כלים
  "culture": [str, ...],     # 2 snippets — בלוג הנדסי, ערכים, צוות
  "recent_news": [str, ...]  # 2 snippets — גיוסי הון, מוצרים חדשים, כיוון
}
```

---

## שאילתות החיפוש שנשלחות ל-Tavily
| שאילתה | max_results | search_depth | מטרה |
|--------|-------------|--------------|-------|
| `{company} company overview mission products 2024 2025` | 3 | basic | תיאור כללי |
| `{company} tech stack engineering technologies {job_title}` | 3 | basic | טכנולוגיות |
| `{company} engineering blog culture values team` | 2 | basic | תרבות הנדסית |
| `{company} latest news product launch funding 2024 2025` | 2 | basic | חדשות |

**סה"כ קריאות Tavily לכל הרצה: 4**

---

## תלויות
```
tavily-python==0.5.0   # חיפוש אינטרנט
python-dotenv==1.1.0   # טעינת .env
```
משתנה סביבה נדרש: `TAVILY_API_KEY`

---

## איך לשנות בבטחה
- **להוסיף שאילתה** — הוסף בלוק `client.search(...)` ומפתח חדש לה-dict המוחזר
- **לשנות מספר תוצאות** — שנה `max_results` (מקסימום 10 בחינם, כל תוצאה = 1 קרדיט)
- **לשנות עומק חיפוש** — `"basic"` מהיר וזול, `"advanced"` עמוק ויקר יותר
- **לא לשנות** את שם הפונקציה `run()` — ה-orchestrator קורא לה ישירות

---

## דוגמת פלט אמיתית (Wix, Frontend Developer)
```json
{
  "company_name": "Wix",
  "job_title": "Frontend Developer",
  "overview": [
    "The core mission of Wix is to empower individuals and businesses to create, grow, and run their desired ventures online...",
    "The company's mission is to empower everyone to create, connect, and grow. Its vision is to enable anyone to succeed online..."
  ],
  "tech_stack": ["React, Node.js, TypeScript — Wix platform engineering..."],
  "culture": ["Wix engineering blog covers topics from performance to accessibility..."],
  "recent_news": ["Wix announced new AI-powered site builder features in 2024..."]
}
```

---

## קשרים עם agents אחרים
- **קורא לו:** `orchestrator.py`
- **מעביר פלט אל:** `persona_builder.py` (ב-Step 3)
- **רץ במקביל עם:** `glassdoor_agent`, `linkedin_agent`, `news_agent`, `tech_agent`
