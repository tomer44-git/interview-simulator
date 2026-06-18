# base_domain.py
# תבנית + validator לכל domain config במערכת
# כשמוסיפים domain חדש — מעתיקים את TEMPLATE ומתאימים. לא נוגעים במנועים.

# ---- השדות החובה בכל domain config ----
REQUIRED_KEYS = [
    "name",             # שם התפקיד/דומיין
    "question_flow",    # רשימה של (קטגוריה, מספר שאלות) — מגדיר את מבנה הראיון
    "research_agents",  # אילו agents רצים לדומיין הזה
    "persona_style",    # הנחיה ל-Claude על אופי המראיין
    "scoring_rubric",   # קריטריוני הערכה לכל קטגוריה
]


def validate(config: dict) -> bool:
    """
    מוודא שה-domain config כולל את כל השדות הנדרשים.
    נקרא על ידי domain_loader בעת טעינת config.
    זורק ValueError עם הסבר ברור אם משהו חסר.
    """
    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        raise ValueError(
            f"Domain config '{config.get('name', 'unknown')}' "
            f"חסר שדות חובה: {missing}"
        )

    # בדיקה שה-question_flow הוא רשימה של tuples תקינים
    for item in config["question_flow"]:
        if not (isinstance(item, tuple) and len(item) == 2):
            raise ValueError(
                f"question_flow חייב להיות רשימה של (category, count) tuples"
            )
    return True


# ---- תבנית להעתקה בעת יצירת domain חדש ----
TEMPLATE = {
    "name": "Role Name",

    # מגדיר את סדר וכמות השאלות לכל קטגוריה
    "question_flow": [
        ("HR",         2),
        ("Behavioral", 2),
        ("Technical",  3),
        ("Coding",     1),
    ],

    # אילו research agents ירוצו לדומיין הזה
    # hi-tech כולל neetcode, תחומים אחרים לא
    "research_agents": [
        "company", "glassdoor", "linkedin",
        "news", "tech", "neetcode",
    ],

    # הנחיה ל-Claude על אופי ונטייה של המראיין
    "persona_style": "Describe interviewer style here",

    # קריטריוני הערכה — ישמשו את feedback_agent בשלב 8
    "scoring_rubric": {
        "HR":         ["clarity", "motivation", "culture fit"],
        "Behavioral": ["STAR structure", "impact", "ownership"],
        "Technical":  ["depth", "trade-offs", "system thinking"],
        "Coding":     ["correctness", "efficiency", "communication"],
    },
}
