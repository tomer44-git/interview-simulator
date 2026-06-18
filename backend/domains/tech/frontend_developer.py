# frontend_developer.py
# Domain config לתפקיד Frontend Developer
# לשינוי הראיון: ערוך רק את הקובץ הזה — אפס שינויים במנועים

DOMAIN_CONFIG = {
    "name": "Frontend Developer",

    # זרימת הראיון: 8 שאלות סה"כ
    "question_flow": [
        ("HR",         2),   # מוטיבציה, רקע, מה מחפש
        ("Behavioral", 2),   # STAR — עבודת צוות, להתמודד עם קשיים
        ("Technical",  3),   # React, CSS, performance, accessibility
        ("Coding",     1),   # DOM manipulation, algorithm, או live coding
    ],

    # כל 6 ה-agents רלוונטיים לתפקיד טכנולוגי
    "research_agents": [
        "company", "glassdoor", "linkedin",
        "news", "tech", "neetcode",
    ],

    # מנחה את Claude לגלם מראיין frontend אמיתי
    "persona_style": (
        "Technical and collaborative. Focuses on UI architecture, component design, "
        "performance optimization, and code quality. Asks about real trade-offs "
        "(e.g. SSR vs CSR, hooks vs class components). Values clear communication "
        "about technical decisions."
    ),

    # קריטריוני ניקוד — ישמשו את feedback_agent (Step 8)
    "scoring_rubric": {
        "HR": [
            "clarity of self-presentation",
            "genuine motivation for the role",
            "cultural fit signals",
        ],
        "Behavioral": [
            "uses STAR structure",
            "demonstrates ownership",
            "shows collaboration skills",
        ],
        "Technical": [
            "depth of React/JS knowledge",
            "understands performance trade-offs",
            "awareness of accessibility and browser APIs",
        ],
        "Coding": [
            "correct solution",
            "considers edge cases",
            "communicates while coding",
        ],
    },
}
