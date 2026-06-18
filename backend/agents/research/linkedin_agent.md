# linkedin_agent.md

## מה ה-agent עושה
מחפש מידע ציבורי מ-LinkedIn דרך Tavily: דרישות תפקיד ממשרות פתוחות, תרבות צוות, מבנה ארגוני, וסיגנלי גיוס.

## קלט / פלט
**קלט:** `company_name: str`, `job_title: str`
**פלט:**
```python
{
  "company_name": str,
  "job_title": str,
  "job_requirements": [str, ...],   # 4 snippets — מה החברה מחפשת
  "team_culture":     [str, ...],   # 3 snippets — חוויות עובדים
  "team_structure":   [str, ...],   # 3 snippets — מבנה הצוות
  "hiring_signals":   [str, ...],   # 2 snippets — האם מגייסים?
}
```

## שאילתות Tavily
| שאילתה | depth | מטרה |
|--------|-------|-------|
| `{company} {job} linkedin job requirements skills` | advanced | דרישות אמיתיות |
| `linkedin {company} engineer culture experience post` | basic | תרבות |
| `{company} engineering team linkedin manager structure` | basic | מבנה |
| `{company} hiring {job} 2025 linkedin open positions` | basic | סיגנלי גיוס |

## תלויות
`tavily-python`, `python-dotenv` | משתנה: `TAVILY_API_KEY`

## קשרים
- קורא לו: `orchestrator.py` (Step 6), `test_agents.py`
- פלט משמש: `persona_builder.py`
- רץ במקביל עם: `company_agent`, `glassdoor_agent`, `news_agent`, `tech_agent`
