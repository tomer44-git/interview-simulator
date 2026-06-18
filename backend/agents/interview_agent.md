# interview_agent.md

## מה ה-agent עושה
מנוע ראיון אדפטיבי stateless. מגלם את הפרסונה שנבנתה ב-persona_builder,
מנהל זרימת שאלות לפי קטגוריות, ומגיב בצורה חכמה לתשובות המועמד.

## ממשק (API)

### `start(persona) → dict`
פותח ראיון חדש. קורא לזה פעם אחת.
```python
result = interview_agent.start(persona)
# result = {"message": "פתיח...", "state": {...}}
```

### `next_turn(user_message, state, persona) → dict`
מעבד תשובה ומחזיר תגובה + state מעודכן. קורא לזה בכל תור.
```python
result = interview_agent.next_turn("My answer...", state, persona)
# result = {"message": "תגובה...", "state": {...}}
```

## מבנה ה-State
```python
{
  "history":          [{"role": "interviewer"/"candidate", "content": str}],
  "questions_asked":  int,        # 0 עד TOTAL_QUESTIONS (8)
  "current_category": str,        # HR / Behavioral / Technical / Coding
  "is_complete":      bool,       # True כשהגענו ל-8 שאלות
}
```

## זרימת קטגוריות
```
HR (2) → Behavioral (2) → Technical (3) → Coding (1) = 8 שאלות סה"כ
```

## למה stateless?
כי הוא יאוחסן ב-Supabase (Step 8) ויוגש דרך FastAPI (Step 6).
כל request מביא state, מעבד, ומחזיר state חדש — ללא זיכרון בין קריאות.

## תלויות
`anthropic>=0.60`, `python-dotenv` | משתנה: `ANTHROPIC_API_KEY`
מודל: `claude-sonnet-4-5-20250929`, max_tokens=300

## קשרים
- קורא לו: `orchestrator.py` (Step 6), `test_agents.py`, בעתיד FastAPI route `/interview`
- מקבל קלט מ: `persona_builder.py`
- מעביר data ל: `feedback_agent.py` (Step 8) — ה-history המלא
