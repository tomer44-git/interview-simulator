# Interview Simulator — Project Context

Working context for AI tooling. For a human introduction to the project, see [README.md](README.md).

---

## What this is

A multi-agent system that researches a company in real time and runs a
role-specific mock interview against a generated interviewer persona, then
scores the transcript. Built tech-first, with a config-driven domain layer
intended to extend to other industries.

**Live:** https://interview-simulator-rose.vercel.app

---

## Working conventions

- **Comments in Hebrew inside code blocks**, explaining what each part does
- **Explain why a decision was made**, not just what was done
- **Before writing code, state in two sentences what is about to be built**
- **Warn before anything that can break** — deploys, migrations, API cost
- **Keep every file under 150 lines**; split rather than let one grow
- **Each agent is self-contained** and independently modifiable
- **Non-ASCII characters never appear literally in source** — use `chr(0x2028)`.
  A literal breaks tracebacks on Railway's ASCII stdout (see Known debt)
- **Never return a raw exception to the client.** Use `errors.server_error()`,
  which logs the full traceback server-side and returns only a short reference
  id. A raw `str(e)` once put an API key prefix into a browser dialog.

---

## Stack

| Layer | Choice |
|---|---|
| Frontend | React 19 + Vite + lucide-react, deployed on Vercel |
| Backend | FastAPI, deployed on Railway |
| Queue | Celery + Redis |
| LLM | Claude (`claude-sonnet-4-5-20250929`) |
| Search | Tavily |
| Auth + DB | Supabase (Postgres + Auth) |

---

## Architecture

```
Landing  →  Context (optional)  →  Research  →  Persona  →  Interview  →  Feedback
```

**Six research agents** run in parallel through Celery: `company`, `glassdoor`,
`linkedin`, `news`, `tech`, `neetcode`. Which of them run is decided by the
domain config, not by the engine.

**Orchestrator** (`agents/orchestrator.py`) builds the Celery group, waits,
and maps results back to agent names. Routers handle HTTP only.

**Interview engine** is stateless — the full conversation state travels in
every request, so instances can be added without sticky sessions.

**Domain configs** define four things and nothing else is needed to add a
sector: `question_flow`, `research_agents`, `persona_style`, `scoring_rubric`.

Three domains ship: two tech, one finance. The finance config is the proof —
it uses a category name no tech domain has (`Case Study`), runs four research
agents instead of six, and weights its questions differently. The engines
contain zero references to it.

---

## Project structure

Line counts as of 2026-10-25.

```
backend/
├── main.py                     58   FastAPI entry, CORS, routers
├── celery_app.py               48   Celery entry — UTF-8 stdout guard
├── auth.py                     45   JWT verification via Supabase
├── latency.py                  93   perf_counter instrumentation
├── supabase_client.py          63   session persistence
├── agents/
│   ├── orchestrator.py         94   parallel research coordination
│   ├── persona_builder.py     179   research → interviewer persona
│   ├── interview_agent.py     137   stateless conversation engine
│   ├── feedback_agent.py       91   transcript → scores
│   ├── context_agent.py        56   free text + PDF/Word → summary
│   └── research/                    6 agents, 73–93 lines each
├── domains/
│   ├── base_domain.py          66   REQUIRED_KEYS, validate(), TEMPLATE
│   ├── domain_loader.py        62   job title → config
│   ├── tech/                        frontend_developer 53, junior_ai_engineer 54
│   └── finance/junior_analyst.py 64  non-tech domain, 4 agents, "Case Study"
├── routers/                         research, context, persona, interview, feedback
├── tasks/research_tasks.py     60   Celery task wrappers + AGENT_TASK_MAP
├── tests/                   1454   166 tests, fully mocked
└── e2e/run_live_interview.py  116   manual pre-release check, real APIs

frontend/src/                 1,279   App + 7 screens + api + supabase client
```

---

## Environment variables

```
ANTHROPIC_API_KEY      TAVILY_API_KEY       REDIS_URL
SUPABASE_URL           SUPABASE_KEY         SUPABASE_SERVICE_KEY
```

Frontend (Vercel): `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`

---

## Tests

```bash
cd backend && ./venv/bin/pytest          # 166 tests, ~0.7s, no network
```

All external APIs are mocked. An autouse fixture replaces every real key
with a fake one, so a missed mock fails loudly rather than spending money.

`e2e/run_live_interview.py` is the only thing that calls real APIs. It is
manual and deliberately not collected by pytest.

---

## Status

| Area | State |
|---|---|
| Research → persona → interview → feedback | working in production |
| Hebrew interviews (full pipeline + RTL) | working |
| Context agent (free text + PDF/Word) | working |
| Supabase auth | working |
| Test suite | 166 tests |
| Multi-user: invites, attempt limits, admin | specced, not built — see [MULTI_USER_PLAN.md](MULTI_USER_PLAN.md) |

---

## Known debt

Deliberate, with reasons. Do not "fix" these without discussing cost.

- **No graceful degradation in research.** One agent raising fails the whole
  `group().get()`. Acceptable at current scale; `orchestrator.py` is where it
  would go.
- **`/research` blocks for up to 120s.** FastAPI runs sync routes in a 40-thread
  pool, so ~40 concurrent research calls stall the server. The fix is a
  `job_id` + polling pattern.
- **Celery `--concurrency=2`.** Roughly 5–6 simultaneous interview starts
  before the 120s timeout fires.
- **No research caching.** Every interview re-researches the same companies.
  Tavily's free tier is 1,000 searches/month and one interview costs ~24, so
  this caps usage at ~41 interviews/month.
- **ASCII sanitizer is blunt.** `encode('ascii', errors='replace')` in
  `persona_builder` destroys em-dashes and smart quotes in real content.
- **Missing-token errors return 422, not 401.** FastAPI validation artifact.
