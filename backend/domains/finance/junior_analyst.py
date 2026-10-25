# junior_analyst.py
# Domain config לתפקיד Junior Financial Analyst
# לשינוי הראיון: ערוך רק את הקובץ הזה — אפס שינויים במנועים
#
# הקובץ הזה הוא ההוכחה שהמערכת באמת domain-agnostic. שים לב לשלושה
# הבדלים מתחומי ההייטק, שאף אחד מהם לא דרש שורת קוד במנוע:
#
#   1. קטגוריה בשם "Case Study" במקום "Coding" — שמות הקטגוריות הם
#      מחרוזות חופשיות שזורמות לפרומפט ול-rubric, לא enum קשיח
#   2. ארבעה סוכני מחקר במקום שישה — tech ו-neetcode מחפשים GitHub
#      ו-LeetCode, שאין להם שום משמעות לאנליסט פיננסי
#   3. חלוקת משקל אחרת — שני Case Studies, כי בראיונות פיננסיים
#      המקרה הוא עיקר הראיון ולא נספח לו

DOMAIN_CONFIG = {
    "name": "Junior Financial Analyst",

    # זרימת הראיון: 8 שאלות סה"כ
    # Case Study מקבל משקל כפול לעומת תחומי ההייטק
    "question_flow": [
        ("HR",         2),   # מוטיבציה לפיננסים, מסלול הסמכה, שאיפות
        ("Behavioral", 2),   # עמידה בלחץ דדליין, עבודה מול לקוח, דיוק
        ("Technical",  2),   # מודלים פיננסיים, דוחות כספיים, הערכת שווי
        ("Case Study", 2),   # ניתוח מקרה — DCF, השוואת חברות, המלצת השקעה
    ],

    # ארבעה סוכנים בלבד — tech ו-neetcode לא רלוונטיים לתחום הזה
    "research_agents": [
        "company", "glassdoor", "linkedin", "news",
    ],

    # מנחה את Claude לגלם מראיין פיננסי אמיתי
    "persona_style": (
        "Precise and detail-oriented. Focuses on analytical rigour, comfort with "
        "financial statements, and the ability to defend an assumption under "
        "pressure. Asks the candidate to walk through their reasoning out loud "
        "rather than jump to an answer. Values intellectual honesty about what "
        "they do not know over a confident guess."
    ),

    # קריטריוני ניקוד — feedback_agent מנקד לפי אלה
    "scoring_rubric": {
        "HR": [
            "genuine interest in financial markets",
            "awareness of the certification path (CPA/CFA)",
            "realistic understanding of the role's day-to-day",
        ],
        "Behavioral": [
            "performs accurately under deadline pressure",
            "communicates clearly with non-financial stakeholders",
            "takes ownership of errors",
        ],
        "Technical": [
            "fluency with the three financial statements and how they link",
            "valuation fundamentals (DCF, comparables, precedent transactions)",
            "Excel and financial modelling proficiency",
        ],
        "Case Study": [
            "states assumptions explicitly before building",
            "structures the analysis before computing",
            "defends conclusions with numbers rather than intuition",
        ],
    },
}
