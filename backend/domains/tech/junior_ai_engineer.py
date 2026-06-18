# junior_ai_engineer.py
# Domain config לתפקיד Junior AI Engineer
# לשינוי הראיון: ערוך רק את הקובץ הזה — אפס שינויים במנועים

DOMAIN_CONFIG = {
    "name": "Junior AI Engineer",

    # זרימת הראיון: 8 שאלות סה"כ
    # Technical מקבל יותר משקל — AI roles דורשות עומק
    "question_flow": [
        ("HR",         2),   # מוטיבציה ל-AI, background, learning mindset
        ("Behavioral", 2),   # עבודת צוות בפרויקטי AI/data, ambiguity handling
        ("Technical",  3),   # ML fundamentals, model evaluation, system design
        ("Coding",     1),   # Python, numpy/pandas, או ML pipeline implementation
    ],

    # כל 6 ה-agents רלוונטיים — neetcode מחזיר patterns של ML interviews
    "research_agents": [
        "company", "glassdoor", "linkedin",
        "news", "tech", "neetcode",
    ],

    # מנחה את Claude לגלם מראיין AI אמיתי
    "persona_style": (
        "Curious and research-oriented. Focuses on ML fundamentals, practical AI "
        "experience, and problem-solving approach. Asks about real projects the "
        "candidate worked on. Values intellectual curiosity and ability to explain "
        "complex concepts clearly. Comfortable with ambiguity."
    ),

    # קריטריוני ניקוד — ישמשו את feedback_agent (Step 8)
    "scoring_rubric": {
        "HR": [
            "genuine passion for AI/ML",
            "clear learning mindset",
            "realistic self-assessment",
        ],
        "Behavioral": [
            "handles ambiguity well",
            "cross-functional collaboration",
            "data-driven decision making",
        ],
        "Technical": [
            "ML fundamentals (bias/variance, overfitting, metrics)",
            "understands model lifecycle end-to-end",
            "practical deployment awareness",
        ],
        "Coding": [
            "Python proficiency",
            "data manipulation skills",
            "ML library familiarity (PyTorch/TensorFlow/sklearn)",
        ],
    },
}
