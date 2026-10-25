# tests/test_llm_parsing.py
# פענוח ה-JSON שחוזר מ-Claude.
#
# שני ה-agents האלה מבקשים JSON ומקבלים טקסט חופשי. מודלים עוטפים
# לפעמים ב-```json, לפעמים ב-``` בלבד, ולפעמים מחזירים JSON נקי.
# אם הפענוח נשבר, השלב הבא בצינור מקבל זבל — ולכן זה מקום שחייב כיסוי.

import json

import pytest

from agents import persona_builder, feedback_agent
from tests import sample_data


def _build(claude, research, raw_text):
    """מכריח את Claude המזויף להחזיר טקסט גולמי ומריץ את בניית הפרסונה"""
    claude.set_response(raw_text)
    return persona_builder.run(
        company_data=research["company"],
        glassdoor_data=research["glassdoor"],
        linkedin_data=research["linkedin"],
        news_data=research["news"],
        neetcode_data=research["neetcode"],
    )


# ------------------------------------------------- persona_builder

def test_persona_parses_bare_json(claude, research):
    built = _build(claude, research, json.dumps(sample_data.PERSONA))

    assert built["name"] == "Maya Cohen"


def test_persona_parses_json_fenced_as_markdown(claude, research):
    """המקרה הנפוץ ביותר — המודל עוטף למרות ההוראה המפורשת"""
    raw = "```json\n" + json.dumps(sample_data.PERSONA) + "\n```"
    built = _build(claude, research, raw)

    assert built["name"] == "Maya Cohen"


def test_persona_parses_fence_without_a_language_tag(claude, research):
    raw = "```\n" + json.dumps(sample_data.PERSONA) + "\n```"
    built = _build(claude, research, raw)

    assert built["name"] == "Maya Cohen"


def test_persona_tolerates_surrounding_whitespace(claude, research):
    raw = "\n\n  " + json.dumps(sample_data.PERSONA) + "  \n\n"
    built = _build(claude, research, raw)

    assert built["name"] == "Maya Cohen"


def test_persona_carries_every_field_the_interview_engine_needs(claude, research):
    """
    חוזה בין שני שלבים: interview_agent קורא opening_statement,
    וה-UI קורא name ו-title. אם אחד מהם חסר, הראיון נשבר בהמשך.
    """
    built = _build(claude, research, json.dumps(sample_data.PERSONA))

    for field in ("name", "title", "opening_statement", "interview_style",
                  "personality_traits", "focus_areas"):
        assert field in built, f"הפרסונה חסרה את {field}"


def test_persona_gets_company_and_role_from_the_builder_not_the_model(claude, research):
    """
    שני השדות האלה נוספים בקוד ולא מגיעים מ-Claude — כך הם תמיד נכונים
    גם אם המודל ימציא שם חברה אחר.
    """
    model_output = {**sample_data.PERSONA, "company_name": "WRONG", "job_title": "WRONG"}
    built = _build(claude, research, json.dumps(model_output))

    assert built["company_name"] == research["company"]["company_name"]
    assert built["job_title"] == research["company"]["job_title"]


def test_persona_raises_on_unparseable_output(claude, research):
    """כישלון רועש עדיף על פרסונה חצי-בנויה שתישבר בשלב מאוחר יותר"""
    with pytest.raises(json.JSONDecodeError):
        _build(claude, research, "I'm sorry, I can't help with that.")


# ------------------------------------------------- feedback_agent

def _score(claude, persona, domain_config, raw_text):
    claude.set_response(raw_text)
    state = {"history": [
        {"role": "interviewer", "content": "Tell me about yourself."},
        {"role": "candidate",   "content": "Three years of React."},
    ]}
    return feedback_agent.run(state, persona, domain_config)


def test_feedback_parses_bare_json(claude, persona, domain_config):
    scores = _score(claude, persona, domain_config, json.dumps(sample_data.FEEDBACK))

    assert scores["overall_score"] == 7.5


def test_feedback_parses_json_fenced_as_markdown(claude, persona, domain_config):
    raw = "```json\n" + json.dumps(sample_data.FEEDBACK) + "\n```"
    scores = _score(claude, persona, domain_config, raw)

    assert scores["overall_score"] == 7.5


def test_feedback_returns_every_field_the_ui_renders(claude, persona, domain_config):
    """FeedbackScreen קורא את כל אלה — חסר אחד והמסך קורס"""
    scores = _score(claude, persona, domain_config, json.dumps(sample_data.FEEDBACK))

    for field in ("overall_score", "categories", "summary",
                  "top_strengths", "areas_to_improve", "recommended_resources"):
        assert field in scores, f"הפידבק חסר את {field}"


def test_feedback_receives_the_full_transcript(claude, persona, domain_config):
    """
    הניקוד טוב רק כמו התמליל שהוא מקבל. ציון 0.0 בקודינג נבע מכך
    שהתמליל נקטע — אז שווה לוודא שהתשובות באמת מגיעות לפרומפט.
    """
    _score(claude, persona, domain_config, json.dumps(sample_data.FEEDBACK))

    assert "Three years of React." in claude.prompts[0]
