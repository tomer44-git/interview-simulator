# tests/test_domains.py
# מערכת ה-domains — הטענה הארכיטקטונית המרכזית של הפרויקט:
# הוספת תחום חדש = הוספת קובץ config, בלי לגעת במנועים.
#
# אם ה-loader או ה-validator נשברים, כל התפקידים נופלים חזרה
# לברירת מחדל בשקט — והמשתמש מקבל ראיון לתפקיד הלא נכון בלי שום שגיאה.

import pytest

from domains import base_domain, domain_loader


# ------------------------------------------------- התאמת תפקיד

@pytest.mark.parametrize("job_title,expected", [
    ("Frontend Developer",  "Frontend Developer"),
    ("React Developer",     "Frontend Developer"),
    ("UI Developer",        "Frontend Developer"),
    ("Front-End Engineer",  "Frontend Developer"),
    ("Junior AI Engineer",  "Junior AI Engineer"),
    ("ML Engineer",         "Junior AI Engineer"),
    ("Machine Learning Engineer", "Junior AI Engineer"),
])
def test_job_title_maps_to_the_right_domain(job_title, expected):
    assert domain_loader.load(job_title)["name"] == expected


@pytest.mark.parametrize("job_title", [
    "frontend developer",
    "FRONTEND DEVELOPER",
    "  Frontend Developer  ",
])
def test_matching_ignores_case_and_whitespace(job_title):
    """משתמשים מקלידים איך שבא להם — ההתאמה חייבת לסלוח"""
    assert domain_loader.load(job_title)["name"] == "Frontend Developer"


def test_unknown_role_falls_back_instead_of_crashing():
    """
    נפילה לברירת מחדל עדיפה על קריסה — אבל כדאי לדעת שזה קורה.
    כרגע זה שקט מלבד print, וזו החלטה מודעת.
    """
    config = domain_loader.load("Pastry Chef")

    assert config == domain_loader.DEFAULT_CONFIG


def test_ai_role_is_matched_before_the_frontend_fallback():
    """
    סדר DOMAIN_MAP משמעותי. "Junior AI Engineer" מכיל גם "ai engineer"
    וגם מילים שעלולות להתנגש — הראשון שמתאים מנצח.
    """
    assert domain_loader.load("Junior AI Engineer")["name"] == "Junior AI Engineer"


def test_supported_titles_are_listed():
    supported = domain_loader.list_supported()

    assert "frontend" in supported
    assert "ml engineer" in supported


# ------------------------------------------------- תקינות ה-configs

ALL_CONFIGS = [cfg for _, cfg in domain_loader.DOMAIN_MAP]


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c["name"])
def test_every_shipped_config_is_valid(config):
    """כל config שמופה חייב לעבור את ה-validator"""
    assert base_domain.validate(config) is True


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c["name"])
def test_every_config_asks_eight_questions(config):
    """
    הפרונט מציג "Question N / 8". אם config כלשהו יסכום למספר אחר,
    המונה ישקר בלי ששום דבר ייכשל.
    """
    assert sum(count for _, count in config["question_flow"]) == 8


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c["name"])
def test_every_category_has_scoring_criteria(config):
    """
    חוזה בין question_flow ל-scoring_rubric: feedback_agent מנקד לפי
    ה-rubric. קטגוריה שנשאלת אך לא מנוקדת פשוט תיעלם מהדוח.
    """
    categories = {category for category, _ in config["question_flow"]}
    scored     = set(config["scoring_rubric"].keys())

    assert categories <= scored, f"קטגוריות ללא קריטריוני ניקוד: {categories - scored}"


@pytest.mark.parametrize("config", ALL_CONFIGS, ids=lambda c: c["name"])
def test_every_config_names_real_research_agents(config):
    """שם agent שגוי ב-config מדלג עליו בשקט ב-router"""
    known = {"company", "glassdoor", "linkedin", "news", "tech", "neetcode"}

    assert set(config["research_agents"]) <= known


# ------------------------------------------------- ה-validator עצמו

def test_validator_rejects_a_config_with_missing_keys():
    with pytest.raises(ValueError) as err:
        base_domain.validate({"name": "Broken"})

    assert "question_flow" in str(err.value)


def test_validator_rejects_a_malformed_question_flow():
    broken = {**base_domain.TEMPLATE, "question_flow": ["HR", "Behavioral"]}

    with pytest.raises(ValueError):
        base_domain.validate(broken)


def test_template_is_a_valid_starting_point():
    """התבנית היא מה שמעתיקים כדי ליצור תחום חדש — חייבת לעבור ולידציה"""
    assert base_domain.validate(base_domain.TEMPLATE) is True
