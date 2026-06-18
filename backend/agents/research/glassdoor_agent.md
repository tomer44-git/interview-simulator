# glassdoor_agent.md
> תיעוד מלא של ה-agent — קרא לפני כל שינוי בקוד

## מה ה-agent הזה עושה
מחפש חוויות ראיון אמיתיות, שאלות שנשאלו בעבר, ורמת קושי של תהליך הגיוס.
מחפש ב-Glassdoor, Reddit, Blind, LinkedIn — כל מה שנגיש ללא לוגין.

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
  "company_name": str,                  # שם החברה
  "job_title": str,                     # התפקיד
  "reported_questions": [str, ...],     # 4 snippets — שאלות שנשאלו בפועל
  "interview_experiences": [str, ...],  # 3 snippets — חוויות מועמדים (מ-Glassdoor/Reddit)
  "technical_topics": [str, ...],       # 3 snippets — נושאים טכניים, LeetCode patterns
  "difficulty_and_process": [str, ...]  # 2 snippets — דירוג קושי, שלבי התהליך
}
```

---

## שאילתות החיפוש שנשלחות ל-Tavily
| שאילתה | max_results | search_depth | מטרה |
|--------|-------------|--------------|-------|
| `{company} {job} interview questions asked 2024 2025` | 4 | **advanced** | שאלות אמיתיות |
| `{company} interview experience glassdoor {job} process` | 3 | **advanced** | חוויות מועמדים |
| `{company} technical interview coding questions {job} leetcode` | 3 | basic | נושאים טכניים |
| `{company} interview difficulty rating hiring process review` | 2 | basic | דירוג קושי |

**סה"כ קריאות Tavily לכל הרצה: 4**
> ⚠️ שתי השאילתות הראשונות הן `advanced` — כל אחת עולה יותר קרדיטים מ-`basic`

---

## מגבלה ידועה — תוכן מאחורי לוגין
Glassdoor מחביאה ביקורות שכר ופרטי ראיונות מאחורי לוגין.
הפתרון המתוכנן: **Step 2.5 — Playwright login** (ראה CLAUDE.md).
עד אז, ה-agent שולף מה שגוגל ממשיך לאנדקס + Reddit/Blind שהם פתוחים לגמרי.

---

## תלויות
```
tavily-python==0.5.0   # חיפוש אינטרנט
python-dotenv==1.1.0   # טעינת .env
```
משתנה סביבה נדרש: `TAVILY_API_KEY`

---

## איך לשנות בבטחה
- **להוסיף מקור** — הוסף את שם האתר לשאילתה (לדוגמה: `"site:blind.com {company} interview"`)
- **לשנות עומק** — `advanced` מחזיר תוצאות טובות יותר מ-Glassdoor, אבל עולה יותר
- **לא לשנות** את שם הפונקציה `run()` — ה-orchestrator קורא לה ישירות
- **שדרוג עתידי** — כשמוסיפים Playwright, `run()` תבדוק קודם אם יש cookies שמורים

---

## קשרים עם agents אחרים
- **קורא לו:** `orchestrator.py`
- **מעביר פלט אל:** `persona_builder.py` (ב-Step 3) — השאלות האמיתיות הן הבסיס לפרסונה
- **רץ במקביל עם:** `company_agent`, `linkedin_agent`, `news_agent`, `tech_agent`

---

## Step 2.5 — תוכנית Playwright (עתידי)
```
כשיממשו:
1. glassdoor_agent.run() יבדוק אם קיים קובץ glassdoor_cookies.json
2. אם כן — יטען cookies וישלח requests ישירות לגלאסדור
3. אם לא — יפתח Playwright, יבקש מהמשתמש להתחבר ידנית, ישמור cookies
4. יחזיר מידע עשיר יותר: שכר, דירוגים, פרטי ראיון מלאים
```
