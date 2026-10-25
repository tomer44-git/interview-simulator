# tests/sample_data.py
# נתוני דמה בצורה המדויקת שה-agents האמיתיים מחזירים.
# מופרד מ-conftest.py כדי שהפיקסצ'רים יישארו קריאים.
#
# חשוב: תווי Unicode בעייתיים נכתבים כ-chr(0x2028) ולא כתו ממשי.
# תו ממשי בקוד מקור הוא בדיוק הבאג מ-commit d626234 — כש-Python בונה
# traceback שכולל את שורת המקור הזו, כתיבתו ל-stdout של Railway קורסת.

LINE_SEP = chr(0x2028)  # U+2028 LINE SEPARATOR
PARA_SEP = chr(0x2029)  # U+2029 PARAGRAPH SEPARATOR

COMPANY = "Wix"
JOB     = "Frontend Developer"


# ---------- פלט של 6 ה-research agents ----------

COMPANY_DATA = {
    "company_name": COMPANY,
    "job_title":    JOB,
    "overview":     ["Wix is a cloud-based web development platform serving millions of users."],
    "tech_stack":   ["React, TypeScript, Node.js, and a custom component library."],
    "culture":      ["Engineering teams own their services end to end."],
    "recent_news":  ["Launched a new AI site builder this quarter."],
}

GLASSDOOR_DATA = {
    "company_name":           COMPANY,
    "job_title":              JOB,
    "reported_questions":     ["Explain the virtual DOM and when it helps."],
    "interview_experiences":  ["Three rounds: screening, technical, team fit."],
    "technical_topics":       ["React internals, CSS layout, performance budgets."],
    "difficulty_and_process": ["Moderate difficulty, roughly two weeks end to end."],
}

LINKEDIN_DATA = {
    "company_name":    COMPANY,
    "job_title":       JOB,
    "job_requirements": ["3+ years with React, strong CSS, accessibility awareness."],
    "team_culture":     ["Small autonomous squads with weekly design reviews."],
    "team_structure":   ["Frontend guild of about forty engineers."],
    "hiring_signals":   ["Actively hiring across frontend this quarter."],
}

NEWS_DATA = {
    "company_name":  COMPANY,
    "job_title":     JOB,
    "funding":       ["Public company, steady revenue growth reported."],
    "new_products":  ["AI-assisted site generation released recently."],
    "strategy":      ["Moving upmarket toward larger business customers."],
    "challenges":    ["Competition from newer no-code platforms."],
}

TECH_DATA = {
    "company_name":    COMPANY,
    "job_title":       JOB,
    "coding_patterns": ["Heavy use of hooks and memoization patterns."],
    "github_stack":    ["Public repos show TypeScript, Jest, and Playwright."],
    "system_design":   ["Micro-frontend architecture with shared design tokens."],
    "tech_challenges": ["Rendering performance at very large page counts."],
}

NEETCODE_DATA = {
    "company_name":       COMPANY,
    "job_title":          JOB,
    "patterns":           ["Two pointers, sliding window, hash maps."],
    "specific_problems":  ["Valid Parentheses, Group Anagrams, LRU Cache."],
    "roadmap_topics":     ["Arrays and hashing, then stack, then trees."],
    "difficulty_profile": ["Mostly easy to medium for this role level."],
}

ALL_RESEARCH = {
    "company":   COMPANY_DATA,
    "glassdoor": GLASSDOOR_DATA,
    "linkedin":  LINKEDIN_DATA,
    "news":      NEWS_DATA,
    "tech":      TECH_DATA,
    "neetcode":  NEETCODE_DATA,
}


# ---------- אותו מחקר, אבל עם התווים ששברו לנו את Railway ----------
# משמש ב-test_encoding.py כדי לוודא שהצינור שורד תוכן web מלוכלך

DIRTY_COMPANY_DATA = {
    **COMPANY_DATA,
    "overview":   [f"Wix is a platform{LINE_SEP}serving millions{PARA_SEP}of users."],
    "tech_stack": ["React — TypeScript, “smart quotes”, and em‑dashes everywhere."],
    "culture":    ["צוותי הנדסה בוויקס אחראים על השירותים שלהם מקצה לקצה."],
}


# ---------- פרסונה בדיוק בסכמה ש-persona_builder מחזיר ----------

PERSONA = {
    "name":               "Maya Cohen",
    "title":              "Senior Frontend Engineer",
    "years_at_company":   4,
    "interview_style":    "Conversational but probing on real trade-offs.",
    "personality_traits": ["curious", "direct", "collaborative"],
    "focus_areas":        ["React architecture", "performance", "accessibility"],
    "opening_statement":  "Hi, I'm Maya, a Senior Frontend Engineer at Wix. Let's get started.",
    "likely_questions": [
        "What draws you to Wix specifically?",
        "Tell me about a time a project went sideways.",
        "How would you architect a page builder's component tree?",
        "How do you approach rendering performance?",
        "Implement an LRU cache.",
    ],
    "coding_question":  "Implement an LRU cache with O(1) get and put.",
    "company_context":  "Wix engineers own their services end to end.",
    "company_name":     COMPANY,
    "job_title":        JOB,
}


# ---------- פידבק בדיוק בסכמה ש-feedback_agent מחזיר ----------

FEEDBACK = {
    "overall_score": 7.5,
    "categories": {
        "HR":         {"score": 8.0, "feedback": "Clear and genuine.",
                       "strengths": ["clarity"], "improvements": ["more specifics"]},
        "Behavioral": {"score": 7.0, "feedback": "Good structure, light on outcomes.",
                       "strengths": ["STAR structure"], "improvements": ["quantify impact"]},
        "Technical":  {"score": 7.5, "feedback": "Solid React depth.",
                       "strengths": ["hooks knowledge"], "improvements": ["accessibility"]},
        "Coding":     {"score": 7.0, "feedback": "Correct solution, quiet while coding.",
                       "strengths": ["correctness"], "improvements": ["think out loud"]},
    },
    "summary":               "A capable frontend candidate with room to grow on impact storytelling.",
    "top_strengths":         ["React depth", "clear communication", "ownership"],
    "areas_to_improve":      ["quantifying impact", "accessibility", "verbalizing reasoning"],
    "recommended_resources": ["Inclusive Components by Heydon Pickering", "web.dev performance course"],
}
