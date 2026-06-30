# Interview Simulator — Project Context

## Vision
A multi-agent AI system that researches a target company in real time (Glassdoor, LinkedIn, company site, news) and generates a personalized interviewer persona to simulate role-specific job interviews. Currently focused on tech/AI roles, built with a domain-agnostic architecture designed to scale to any industry (law, finance, medicine, etc).

## Owner
Tomer Ben Bassat — Computer Science student, 3.5 years cloud operations experience. Beginner-level coder. Every explanation should be simple. Every code block must have comments explaining what each part does. Before writing any code, explain in 2 sentences what we are about to build. If something can break, warn me before it happens.

## Tech Stack
- Frontend: React + Vite + lucide-react (icons)
- Backend: Python FastAPI
- Task Queue: Celery + Redis (manages parallel agents efficiently)
- AI: Claude API (claude-sonnet-4-5-20250929)
- Web Search: Tavily API
- Database: Supabase (PostgreSQL)
- Deploy: Vercel (frontend) + Railway (backend + Redis)

## Agent Architecture (6 layers)
1. Input Agent — collects company name, job title, experience level
2. Orchestrator Agent — coordinates all research agents, decides when enough data is collected
3. Research Agents (run in parallel via Celery) — 6 agents:
   - Company Agent: official site, tech blog, recent news
   - Glassdoor Agent: real interview Q&A and reviews
   - LinkedIn Agent: team members, tech stack, culture posts
   - Tech Agent: GitHub repos, system design, engineering challenges
   - News Agent: funding rounds, new products, company direction
   - NeetCode Agent: coding patterns + LeetCode problems from neetcode.io/leetcode.com (hi-tech only)
4. Persona Builder — correlates all research into a named interviewer character
5. Interview Agent — manages real-time conversation, adaptive difficulty, question categories
6. Feedback Agent — scores each answer, generates final report with study recommendations

## Key Architectural Decisions
- Every agent is an isolated Python file — can be modified independently without touching others
- Orchestrator only cares about output format, not internal agent logic
- Domain system is config-based — adding a new sector = adding one config file, engine unchanged
- Celery + Redis handle parallel agent execution — system stays fast as agents and users scale
- Domain-specific agents (e.g. neetcode_agent) are intentionally scoped — the domain config (Step 5) defines which agents run per domain. neetcode_agent runs for hi-tech roles, not for law or finance. Adding a new domain never requires touching the engine, only adding a config file that maps which agents to invoke.

## Domain System (Expandable)
All domains live in a domains/ folder. Each domain is a config file that defines:
- Which sources to search
- Question categories (HR, Technical, Behavioral, Coding)
- Scoring rubric
- Persona style

Current domains: Junior AI Engineer, Frontend Developer, Data Analyst
Placeholder domains: Law (Junior Associate), Finance (Analyst)

## Project Structure
```
interview-simulator/
├── CLAUDE.md
├── frontend/
│   └── src/
├── backend/
│   ├── main.py                      (empty — Step 6)
│   ├── celery_app.py                (empty — Step 6)
│   ├── requirements.txt             ✅ all latest versions
│   ├── test_agents.py               ✅ full end-to-end test
│   ├── agents/
│   │   ├── orchestrator.py          (empty — Step 6)
│   │   ├── persona_builder.py       ✅ + .md
│   │   ├── interview_agent.py       ✅ + .md
│   │   ├── feedback_agent.py        (empty — Step 8)
│   │   └── research/
│   │       ├── company_agent.py     ✅ + .md
│   │       ├── glassdoor_agent.py   ✅ + .md
│   │       ├── linkedin_agent.py    ✅ + .md
│   │       ├── news_agent.py        ✅ + .md
│   │       ├── tech_agent.py        ✅ + .md
│   │       └── neetcode_agent.py    ✅ + .md
│   └── domains/
│       ├── base_domain.py           ✅ validate() + TEMPLATE
│       ├── domain_loader.py         ✅ load(job_title) → DOMAIN_CONFIG
│       ├── tech/
│       │   ├── frontend_developer.py ✅ question_flow + rubric
│       │   └── junior_ai_engineer.py ✅ question_flow + rubric
│       └── finance/
│           └── junior_analyst.py    (empty — future)
└── .env                             ✅ ANTHROPIC + TAVILY keys set
```

## Environment Variables
```
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
REDIS_URL=your_redis_url_here
```

## 10-Step Build Plan
- ✅ Step 1:   Setup — project folder structure + CLAUDE.md + .env placeholders (DONE — 2026-05-24)
- ✅ Step 2:   Tavily web search — Company Agent + Glassdoor Agent + agent .md files (DONE — 2026-05-24)
- ✅ Step 3:   LinkedIn Agent + News Agent + Persona Builder + agent .md files (DONE — 2026-06-02)
- ✅ Step 4:   Tech Agent + adaptive interview engine (DONE — 2026-06-02)
- ✅ Step 4.5: NeetCode Agent — coding patterns from neetcode.io/leetcode.com (DONE — 2026-06-02)
- ✅ Step 5:   Domain config system — hi-tech roles only for now (DONE — 2026-06-18)
- ✅ Step 6:   FastAPI + Celery + Redis backend — 4 routes: /research /persona /interview /feedback (DONE — 2026-06-18)
- ✅ Step 7:   Full React frontend — landing, loading, interview, feedback screens (DONE — 2026-06-18)
- ✅ Step 8:   Feedback Agent + Supabase session storage (DONE — 2026-06-18)
- ✅ Step 9:   Deploy — Vercel (frontend) + Railway (backend + Redis + Celery worker) (DONE — 2026-06-25)
- ✅ Step 9.5: Latency instrumentation — time.perf_counter() on all API calls + pipeline stages (DONE — 2026-06-25)
- 🔜 Step 10:  Testing, polish, README, demo

## Live URLs
- Frontend: https://interview-simulator-rose.vercel.app
- Backend:  https://interview-simulator-production-b88c.up.railway.app
- GitHub:   https://github.com/tomer44-git/interview-simulator.git

## Infrastructure
- Vercel: frontend deployed, VITE_API_URL → Railway backend
- Railway: interview-simulator (FastAPI, Online) + Redis (Online) + perceptive-compassion (Celery worker, Online)
- Supabase: https://ckthaweepviqodmqkrip.supabase.co

## Current Status
**Step 9 + 9.5 — COMPLETE ✅**
Last updated: 2026-06-25

### What was done in Step 1:
- Full project folder structure + CLAUDE.md + .env with placeholders

### What was done in Step 2:
- `company_agent.py` + `glassdoor_agent.py` — Tavily web search (4 queries each)
- `requirements.txt` — all packages at latest versions
- `test_agents.py` — end-to-end test script

### What was done in Step 3:
- `linkedin_agent.py` + `news_agent.py` — Tavily (4 queries each, news uses `time_range`)
- `persona_builder.py` — first Claude API call, builds named interviewer from all research
- All packages upgraded (anthropic 0.105.2, tavily 0.7.25, etc.)

### What was done in Step 4:
- `tech_agent.py` — GitHub, system design, engineering challenges (4 queries)
- `interview_agent.py` — stateless conversation engine, HR→Behavioral→Technical→Coding (8 questions)
- All 5 research agents + persona builder + interview engine verified working end-to-end ✅

### What was done in Step 4.5:
- `neetcode_agent.py` — searches neetcode.io + leetcode.com only via `include_domains`
- `persona_builder.py` updated — accepts neetcode_data, generates specific `coding_question` field
- All 6 research agents + full interview flow verified ✅

### What was done in Step 5:
- `domains/base_domain.py` — REQUIRED_KEYS, validate(), TEMPLATE
- `domains/tech/frontend_developer.py` — full DOMAIN_CONFIG (question_flow, research_agents, persona_style, scoring_rubric)
- `domains/tech/junior_ai_engineer.py` — full DOMAIN_CONFIG for AI/ML role
- `domains/domain_loader.py` — maps job_title string → correct DOMAIN_CONFIG (substring matching, graceful default)
- `interview_agent.py` updated — hardcoded QUESTION_FLOW removed; accepts domain_config param in start() and next_turn()
- `test_agents.py` updated — loads domain_config via domain_loader and passes to interview_agent

### What was done in Step 9 (Deploy):
- `.gitignore` — excludes .env, venv, node_modules, dist
- `backend/Procfile` — Railway start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- `frontend/src/api.js` — `VITE_API_URL` env var for production backend URL
- Vercel: frontend deployed, env var set, CORS URLs configured in main.py
- Railway: FastAPI service (Root Directory = `backend`), Redis service, Celery worker service
  - Celery start command: `celery -A celery_app worker --loglevel=info --concurrency=2`
  - C_FORCE_ROOT=1 added to Celery worker (Railway runs as root)
  - All API keys added as Railway environment variables

### What was done in Step 9.5 (Latency Instrumentation):
- `backend/latency.py` (NEW) — `measure_latency()` decorator (sync+async), `_measurements` list, `print_research_summary()`, `print_full_summary()`
- All 6 research agents — agent-level timing + `_timing` key returned in dict for parallelism proof
- `company_agent.py` specifically — per-call Tavily timing on all 4 individual searches
- `persona_builder.py`, `interview_agent.py`, `feedback_agent.py` — Claude API call timing
- All 4 routers — stage-level timing recorded to `_measurements`
- `routers/research.py` — extracts `_timing` from each agent result, calls `print_research_summary()`
- `routers/feedback.py` — calls `print_full_summary()` at end of complete pipeline run
- Logs appear in Railway Console: per-call logs in perceptive-compassion, stage logs in interview-simulator

### Up Next — Step 10:
End-to-end test via https://interview-simulator-rose.vercel.app, then polish + README

## Rules
- Always add Hebrew comments inside code blocks explaining what each part does
- Never skip explaining why a decision was made
- Before writing code, explain in 2 sentences what we are about to build
- If something can break, warn about it before it happens
- Keep every file under 150 lines — split into smaller files if needed
- Each agent file is self-contained and independently modifiable
