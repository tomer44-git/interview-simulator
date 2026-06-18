# neetcode_agent.md

## מה ה-agent עושה
מחפש ב-NeetCode וב-LeetCode בלבד (include_domains) — patterns ספציפיים לחברה,
בעיות שנשאלו בפועל, roadmap לתפקיד, ופרופיל קושי. מזין את persona_builder
לשאלות קידוד שמבוססות על נתונים אמיתיים ולא המצאות.

## מה מייחד agent זה
`include_domains=["neetcode.io", "leetcode.com"]` — Tavily מחפש רק באתרים
האלה, לא בגוגל הכללי. תוצאות הרבה יותר מדויקות ורלוונטיות.

## Domain Scope (Architecture Note)
This agent is intentionally hi-tech only. The system is domain-agnostic by design —
the domain config (Step 5) declares which agents run per domain.
neetcode_agent is listed under hi-tech domains only. When a law or finance domain
is added in the future, this agent simply won't be invoked — no code changes needed.

## קלט / פלט
**קלט:** `company_name: str`, `job_title: str`
**פלט:**
```python
{
  "company_name":       str,
  "job_title":          str,
  "patterns":           [str, ...],   # 5 snippets — arrays, graphs, DP וכו׳
  "specific_problems":  [str, ...],   # 5 snippets — בעיות LeetCode שנשאלו
  "roadmap_topics":     [str, ...],   # 3 snippets — NeetCode roadmap לתפקיד
  "difficulty_profile": [str, ...],   # 3 snippets — Easy/Medium/Hard distribution
}
```

## שאילתות Tavily
| שאילתה | include_domains | מטרה |
|--------|----------------|-------|
| `{company} interview coding patterns neetcode` | neetcode.io, leetcode.com | patterns |
| `{company} leetcode problems asked interview` | neetcode.io, leetcode.com | בעיות ספציפיות |
| `neetcode roadmap {job} study plan topics` | neetcode.io, leetcode.com | roadmap |
| `{company} interview difficulty easy medium hard` | neetcode.io, leetcode.com | פרופיל קושי |

## איך משפיע על הפרסונה
`persona_builder.py` כולל section של NEETCODE DATA בפרומפט.
שדה `coding_question` בפרסונה יכיל בעיה ספציפית מהנתונים — לא שאלה גנרית.

## תלויות
`tavily-python>=0.7.0`, `python-dotenv` | משתנה: `TAVILY_API_KEY`

## קשרים
- קורא לו: `orchestrator.py` (Step 6), `test_agents.py`
- פלט משמש: `persona_builder.py` → שדה `coding_question` + `likely_questions[-1]`
- רץ במקביל עם: כל שאר ה-research agents
