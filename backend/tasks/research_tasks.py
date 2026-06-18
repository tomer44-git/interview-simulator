# research_tasks.py
# עוטף כל research agent ב-@celery.task
# כך Celery יכול להפעיל את כולם במקביל על workers שונים

import sys
import os

# מוסיף את תיקיית backend ל-path כדי שהimports יעבדו גם בתוך ה-worker
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from celery_app import celery
from agents.research import (
    company_agent,
    glassdoor_agent,
    linkedin_agent,
    news_agent,
    tech_agent,
    neetcode_agent,
)


# ---- כל @celery.task = משימה שרצה ב-worker נפרד ----
# הסימן .s() בקריאה מאוחר יותר = "signature" — מאפשר לשלב tasks בgroup

@celery.task(name="tasks.run_company")
def run_company(company: str, job_title: str) -> dict:
    return company_agent.run(company, job_title)

@celery.task(name="tasks.run_glassdoor")
def run_glassdoor(company: str, job_title: str) -> dict:
    return glassdoor_agent.run(company, job_title)

@celery.task(name="tasks.run_linkedin")
def run_linkedin(company: str, job_title: str) -> dict:
    return linkedin_agent.run(company, job_title)

@celery.task(name="tasks.run_news")
def run_news(company: str, job_title: str) -> dict:
    return news_agent.run(company, job_title)

@celery.task(name="tasks.run_tech")
def run_tech(company: str, job_title: str) -> dict:
    return tech_agent.run(company, job_title)

@celery.task(name="tasks.run_neetcode")
def run_neetcode(company: str, job_title: str) -> dict:
    return neetcode_agent.run(company, job_title)


# ---- מיפוי שם agent לfunction ----
# domain_config["research_agents"] מכיל רשימת שמות כמו ["company","glassdoor",...]
# המיפוי הזה מאפשר להפעיל רק את ה-agents הרלוונטיים לדומיין
AGENT_TASK_MAP = {
    "company":   run_company,
    "glassdoor": run_glassdoor,
    "linkedin":  run_linkedin,
    "news":      run_news,
    "tech":      run_tech,
    "neetcode":  run_neetcode,
}
