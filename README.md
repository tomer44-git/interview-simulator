# Interview Simulator

Researches a company in real time, generates an interviewer persona grounded in
what it found, runs a role-specific mock interview, and scores the transcript.

**[Live demo →](https://interview-simulator-rose.vercel.app)**

Interviews run in English or Hebrew, with full RTL support.

---

## The problem

Generic interview practice tools ask generic questions. Interviewing at Wix is
not the same as interviewing at a seed-stage startup — different stack,
different process, different things the interviewer actually cares about.

This system reads up on the company first, then interviews you as someone who
works there would.

---

## How it works

```
   Company + Role
        │
        ▼
   Context (optional) ──── free text + PDF/Word about where you are
        │                  in the process so far
        ▼
   ┌─────────────────── Research ───────────────────┐
   │  6 agents in parallel via Celery               │
   │  company · glassdoor · linkedin                │
   │  news · tech · neetcode                        │
   └────────────────────┬───────────────────────────┘
                        ▼
                 Persona Builder
         a named interviewer with a real title,
         focus areas, and a coding question drawn
         from problems actually reported at that company
                        │
                        ▼
                Interview Engine
         8 questions, categories driven by config,
         stateless across turns
                        │
                        ▼
                 Feedback Agent
         per-category scores against the domain's
         rubric + study recommendations
```

**Stack:** React 19 + Vite on Vercel · FastAPI + Celery + Redis on Railway ·
Claude for generation · Tavily for search · Supabase for auth and storage.

---

## Design decisions

### The interview engine is stateless

The entire conversation state travels in every request. The server keeps
nothing between turns.

This costs bandwidth — the full transcript moves back and forth each turn — and
buys horizontal scaling for free. Adding instances needs no sticky sessions and
no shared session store. It is the decision I would make again.

### Domains are configuration, not code

Adding a sector means writing one file with four keys. Compare a tech domain
against the finance one:

```python
# domains/tech/frontend_developer.py
"question_flow":   [("HR", 2), ("Behavioral", 2), ("Technical", 3), ("Coding", 1)],
"research_agents": ["company", "glassdoor", "linkedin", "news", "tech", "neetcode"],

# domains/finance/junior_analyst.py
"question_flow":   [("HR", 2), ("Behavioral", 2), ("Technical", 2), ("Case Study", 2)],
"research_agents": ["company", "glassdoor", "linkedin", "news"],
```

The finance domain uses a category that exists nowhere in the codebase
(`Case Study`), drops the two agents that search GitHub and LeetCode because
they are meaningless for an analyst, and weights its questions differently.

The interview engine, persona builder, feedback agent and orchestrator contain
**zero references to any domain by name** — a grep for "finance" across every
engine, router and schema returns nothing. A full finance interview is covered
by a test that runs it through the unmodified engine.

### Celery + Redis was probably the wrong call

The six research agents only make HTTP calls — they are I/O-bound, and
`asyncio.gather()` would have achieved the same parallelism in one process
with no broker, no worker service, and no infrastructure bill.

Celery earns its place for CPU-bound work, jobs that must survive a restart, or
workers spread across machines. None of that applies here yet.

It was chosen for a scaling story rather than a present need. Kept for now
because the migration is not free and the architecture does genuinely extend;
recorded here because the reasoning matters more than the outcome.

### No LangChain

The agents are plain functions making direct API calls. LangChain would have
reduced boilerplate and brought LangSmith tracing, at the cost of abstraction
layers that obscure what is actually sent to the model — and an API that
changes shape between minor versions. For a pipeline this direct, the
abstraction did not pay for itself.

---

## Running locally

```bash
# backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env          # then fill in the keys
uvicorn main:app --reload

# worker (separate shell, needs Redis running)
celery -A celery_app worker --loglevel=info

# frontend
cd frontend && npm install && npm run dev
```

Required keys: `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`, `REDIS_URL`,
`SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`.

---

## Tests

```bash
cd backend && ./venv/bin/pytest
```

127 tests, well under a second, no network. Every external API is mocked, and
an autouse fixture swaps all real keys for fakes — so a missed mock fails
loudly instead of quietly spending money.

The suite is built around failures this project actually had, not coverage
targets:

| Test file | Guards against |
|---|---|
| `test_interview_flow.py` | The interview closing before the candidate answered the final question — which scored an unanswered coding question as 0.0 with no error anywhere |
| `test_encoding.py` | `U+2028` from scraped web content crashing Railway's ASCII stdout |
| `test_entry_points.py` | That fix being applied to one process entry point and forgotten in the other |
| `test_llm_parsing.py` | Claude returning JSON wrapped in markdown fences |
| `test_orchestrator.py` | Results being mapped onto the wrong agent |
| `test_domains.py` | A config whose categories have no scoring criteria |

`e2e/run_live_interview.py` runs the real pipeline against real APIs. It is
manual, deliberately excluded from pytest collection, and meant to be run
before a release.

---

## Known limitations

- **One failing research agent fails the whole research step.** There is no
  graceful degradation — the interview will not start rather than start with
  five sources instead of six.
- **`/research` blocks for up to 120 seconds.** FastAPI runs synchronous routes
  in a 40-thread pool, so concurrency is capped well before the hardware is.
  The fix is a job-id and polling pattern.
- **Roughly 5–6 simultaneous interview starts** before the Celery worker's
  queue pushes past that timeout.
- **No research caching.** Every interview re-researches the same companies,
  which caps the free Tavily tier at about 41 interviews per month.
- **Cost scales linearly with use** — roughly $0.14 per interview — and no
  architectural change removes that.

These are measured rather than guessed, and the reasoning for leaving each one
is recorded in [CLAUDE.md](CLAUDE.md).

---

## Repository

```
backend/
  agents/      orchestrator, persona builder, interview engine,
               feedback agent, context agent, 6 research agents
  domains/     config-driven domain system
  routers/     FastAPI endpoints
  tasks/       Celery task wrappers
  tests/       127 tests
  e2e/         manual pre-release run against real APIs
frontend/src/  React app — landing, auth, context, interview, feedback
```
