# tech_agent.md

## מה ה-agent עושה
מחקר טכני ממוקד: דפוסי LeetCode, ריפוזים של החברה ב-GitHub, שאלות system design,
ואתגרים הנדסיים ייחודיים לחברה. מזין את interview_agent בחומר לשאלות טכניות.

## קלט / פלט
**קלט:** `company_name: str`, `job_title: str`
**פלט:**
```python
{
  "company_name":    str,
  "job_title":       str,
  "coding_patterns": [str, ...],   # 4 snippets — LeetCode/אלגוריתמים
  "github_stack":    [str, ...],   # 3 snippets — ריפוזים ו-tech stack
  "system_design":   [str, ...],   # 3 snippets — שאלות ארכיטקטורה
  "tech_challenges": [str, ...],   # 2 snippets — אתגרי הנדסה ייחודיים
}
```

## שאילתות Tavily
| שאילתה | depth | מטרה |
|--------|-------|-------|
| `{company} {job} coding interview leetcode patterns` | advanced | דפוסי קידוד |
| `{company} github open source repositories` | basic | tech stack אמיתי |
| `{company} {job} system design interview scalability` | advanced | ארכיטקטורה |
| `{company} engineering technical challenges blog` | basic | אתגרים ייחודיים |

## תלויות
`tavily-python`, `python-dotenv` | משתנה: `TAVILY_API_KEY`

## קשרים
- קורא לו: `orchestrator.py` (Step 6), `test_agents.py`
- פלט משמש: `interview_agent.py` (שאלות Technical ו-Coding)
- רץ במקביל עם: `company_agent`, `glassdoor_agent`, `linkedin_agent`, `news_agent`
