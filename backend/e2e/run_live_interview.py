# test_agents.py
# בודק את כל ה-agents: 6 research agents + persona builder + interview engine
# הרצה: python test_agents.py (מתוך תיקיית backend עם venv פעיל)

import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.research import company_agent, glassdoor_agent
from agents.research import linkedin_agent, news_agent, tech_agent, neetcode_agent
from agents import persona_builder, interview_agent
from domains import domain_loader

# ---- הגדרות הבדיקה ----
TEST_COMPANY = "Wix"
TEST_JOB     = "Frontend Developer"

# תשובות מדומות של מועמד לבדיקת מנוע הראיון
MOCK_ANSWERS = [
    "I'm a frontend developer with 3 years of experience in React. I love building scalable UIs.",
    "In my last job I led a migration from class components to hooks, which improved performance by 30%.",
    "I'd structure it as a micro-frontend architecture with shared design tokens and a component registry.",
]


def run_research() -> dict:
    """מריץ את כל 5 ה-research agents"""
    results = {}
    agents_to_run = [
        ("🏢 Company",   company_agent,   "company"),
        ("📋 Glassdoor", glassdoor_agent, "glassdoor"),
        ("💼 LinkedIn",  linkedin_agent,  "linkedin"),
        ("📰 News",      news_agent,      "news"),
        ("💻 Tech",      tech_agent,      "tech"),
        ("🧩 NeetCode",  neetcode_agent,  "neetcode"),
    ]
    for label, agent, key in agents_to_run:
        print(f"\n{label} Agent — מחפש...")
        try:
            data = agent.run(TEST_COMPANY, TEST_JOB)
            results[key] = data
            print(f"   ✅ מפתחות: {list(data.keys())}")
        except Exception as e:
            print(f"   ❌ נכשל: {e}")
            results[key] = {}
    return results


def run_persona(research: dict) -> dict | None:
    """בונה פרסונת מראיין מהמחקר"""
    print("\n" + "=" * 55)
    print("🧠 Persona Builder — בונה מראיין...")
    print("=" * 55)
    try:
        persona = persona_builder.run(
            company_data=research.get("company",   {}),
            glassdoor_data=research.get("glassdoor", {}),
            linkedin_data=research.get("linkedin",  {}),
            news_data=research.get("news",      {}),
            neetcode_data=research.get("neetcode",  {}),  # ← חדש
        )
        print(f"   ✅ נוצר: {persona['name']} | {persona['title']}")
        return persona
    except Exception as e:
        print(f"   ❌ {e}")
        return None


def run_interview(persona: dict):
    """מדגים ראיון קצר של 3 תורות עם תשובות מדומות"""
    print("\n" + "=" * 55)
    print("🎤 Interview Agent — מתחיל ראיון (3 תורות)")
    print("=" * 55)

    try:
        # טוען את ה-domain config לפי שם התפקיד
        domain_config = domain_loader.load(TEST_JOB)
        total_q = sum(c for _, c in domain_config["question_flow"])
        print(f"   📂 Domain: {domain_config['name']} | סה\"כ שאלות: {total_q}")

        # פותח את הראיון עם domain_config
        result = interview_agent.start(persona, domain_config)
        print(f"\n🤵 {persona['name']}:\n   {result['message']}")
        state = result["state"]

        # מריץ 3 תורות עם תשובות מדומות
        for i, answer in enumerate(MOCK_ANSWERS, 1):
            print(f"\n👤 מועמד (תור {i}):\n   {answer}")
            result = interview_agent.next_turn(answer, state, persona, domain_config)
            print(f"\n🤵 {persona['name']}:\n   {result['message']}")
            state = result["state"]
            print(f"   [קטגוריה: {state['current_category']} | שאלות: {state['questions_asked']}/{total_q}]")

    except Exception as e:
        print(f"   ❌ {e}")


def main():
    print("=" * 55)
    print(f"🔍 בדיקה מלאה: {TEST_COMPANY} | {TEST_JOB}")
    print("=" * 55)

    research = run_research()
    persona  = run_persona(research)

    if persona:
        run_interview(persona)

    print("\n" + "=" * 55)
    print("✅ הבדיקה הסתיימה")


if __name__ == "__main__":
    main()
