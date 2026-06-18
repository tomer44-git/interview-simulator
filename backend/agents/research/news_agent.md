# news_agent.md

## מה ה-agent עושה
מחפש חדשות עדכניות על החברה: גיוסי הון, השקות מוצרים, אסטרטגיה, ותחרות.
משתמש ב-`time_range="year"` של Tavily 0.7+ לסינון תוצאות מהשנה האחרונה.

## קלט / פלט
**קלט:** `company_name: str`, `job_title: str`
**פלט:**
```python
{
  "company_name": str,
  "job_title":    str,
  "funding":      [str, ...],   # 3 snippets — גיוסי הון
  "new_products": [str, ...],   # 3 snippets — מוצרים חדשים
  "strategy":     [str, ...],   # 3 snippets — כיוון אסטרטגי
  "challenges":   [str, ...],   # 2 snippets — תחרות ואתגרים
}
```

## שאילתות Tavily
| שאילתה | time_range | מטרה |
|--------|------------|-------|
| `{company} funding round investment 2024 2025` | year | גיוסי הון |
| `{company} new product feature launch 2024 2025` | year | מוצרים |
| `{company} strategy roadmap AI expansion 2025` | — | אסטרטגיה |
| `{company} competition challenges market 2025` | — | תחרות |

## תלויות
`tavily-python>=0.7.0` (נדרש עבור `time_range`), `python-dotenv` | משתנה: `TAVILY_API_KEY`

## קשרים
- קורא לו: `orchestrator.py` (Step 6), `test_agents.py`
- פלט משמש: `persona_builder.py`
- רץ במקביל עם: `company_agent`, `glassdoor_agent`, `linkedin_agent`, `tech_agent`
