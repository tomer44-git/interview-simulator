# Multi-User Plan — Access Control, Attempts & Admin

Spec for turning the simulator from single-user into an invite-controlled
multi-user system. **Nothing here is built yet.** Written 2026-08-23.

Companion to `CLAUDE.md` — that file describes what exists, this one describes
what we agreed to build.

---

## 1. Goal

Tomer shares one public link. Access is controlled, each guest gets a limited
number of interviews, everyone keeps permanent access to their own results,
and Tomer has an admin panel to manage it all.

---

## 2. Decisions (locked)

| # | Decision |
|---|---|
| D1 | **Allowlist + pending hybrid.** Pre-approved emails get in automatically. Anyone else who signs up lands in `pending` and can run nothing until approved. |
| D2 | **3 attempts per user**, adjustable per-user by admin (reset to 0, or raise the cap). |
| D3 | **An attempt is consumed when `/interview/start` succeeds** — i.e. the moment the candidate is actually inside the interview. |
| D4 | **System failures never consume an attempt.** Research timeout, Celery crash, persona build error → nothing counted (start was never reached). |
| D5 | **User-caused abandonment does consume an attempt.** Closing the browser mid-interview is the user's responsibility. |
| D6 | **History is permanent and unconditional.** Available whether or not attempts remain. |
| D7 | **No email notifications.** Tomer checks the admin panel for the pending queue. |
| D8 | **Admin = `tomerbb98@gmail.com`**, set via `ADMIN_EMAIL` env var. Unlimited attempts, sees the admin panel. |
| D9 | **Admin can read full interview transcripts**, not only the scored report. Purpose is prompt iteration — seeing what the interviewer actually asked and what people actually answered. |
| D10 | **Automated tests are in scope**, targeting the two failure classes this project has already hit: silent flow bugs and non-ASCII breakage. |

### Why D3 and not "when research starts"

Research is the expensive, flaky stage (Tavily + 6 Celery tasks + 120s timeout).
Counting at `/interview/start` means a user is only charged once every fragile
step has already succeeded. This is the precise implementation of "an attempt
counts once you get your first question."

---

## 3. Registration flow

```
signup (Supabase Auth)
   │
   ├── email IS in allowlist  → status = 'approved'  → straight into the app
   │
   └── email NOT in allowlist → status = 'pending'   → PendingScreen
                                                        │
                                          admin approves / rejects
```

This is what protects against the "someone forwarded the link to 30 people"
case: those 30 can create accounts, but they sit in `pending`, consume zero
attempts, and cost zero API calls.

---

## 4. Data model (Supabase)

### New table: `profiles`

One row per registered user. Created automatically by a DB trigger on signup.

| column | type | notes |
|---|---|---|
| `id` | uuid PK | → `auth.users(id)` |
| `email` | text | copied at signup, used for the allowlist match |
| `status` | text | `pending` \| `approved` \| `rejected` |
| `attempts_used` | int | default 0 |
| `attempts_max` | int | default 3 — admin raises this to grant more |
| `is_admin` | bool | default false |
| `created_at` | timestamptz | |
| `approved_at` | timestamptz | nullable |

Two separate columns (`attempts_used` / `attempts_max`) are what make D2 easy:
**reset** = set `attempts_used = 0`; **grant more** = raise `attempts_max`.

### New table: `allowlist`

| column | type | notes |
|---|---|---|
| `email` | text PK | |
| `note` | text | optional — "colleague", "beta tester" |
| `added_at` | timestamptz | |

### Existing table: `sessions`

Add `user_id uuid` → `auth.users(id)`. Without it there is no way to show a
user their own history.

### Trigger

A Postgres trigger on `auth.users` insert creates the `profiles` row and sets
`status` by looking the email up in `allowlist`. Doing it in the DB rather than
the backend means it is atomic and cannot be bypassed by hitting the API
directly.

### RLS

Row Level Security on `profiles` and `sessions`: a user reads only their own
rows. Admin access goes through the backend using the service key.

---

## 5. Backend changes

### Gates

| Endpoint | Check |
|---|---|
| `/research` | `status == 'approved'` **and** `attempts_used < attempts_max` → else 403 |
| `/interview/start` | same check, then `attempts_used += 1` |

Checking at `/research` as well as `/interview/start` is deliberate: it fails
fast and avoids burning Tavily searches and Claude tokens on a user who could
never finish anyway.

### New endpoints

```
GET  /me                          → { status, attempts_used, attempts_max, is_admin }
GET  /history                     → the user's own sessions, full feedback payload

GET  /admin/users                 → all profiles + attempt counts
GET  /admin/stats                 → totals: users, interviews, top companies
GET  /admin/users/{id}/history    → any user's sessions (list)
GET  /admin/sessions/{sid}        → ONE session in full: transcript + feedback  (D9)
POST /admin/users/{id}/approve
POST /admin/users/{id}/reject
POST /admin/users/{id}/attempts   → { reset: true } | { attempts_max: 5 }
GET  /admin/allowlist
POST /admin/allowlist             → { email, note }
DELETE /admin/allowlist/{email}
```

The transcript already exists in the data — `sessions.state.history` holds every
turn. Nothing new needs to be stored; it only needs to be exposed and rendered.

All `/admin/*` routes sit behind a `require_admin` dependency that wraps the
existing `get_current_user` in `auth.py`.

### Files touched

- `backend/auth.py` — add `require_admin`, and load the profile alongside the user
- `backend/routers/research.py` — gate
- `backend/routers/interview.py` — gate + increment
- `backend/routers/feedback.py` — write `user_id` into the session row
- `backend/routers/me.py` — **new**
- `backend/routers/admin.py` — **new**
- `backend/supabase_client.py` — profile/allowlist/stats queries
- `backend/main.py` — register the new routers

---

## 6. Frontend changes

### New screens

| File | Purpose |
|---|---|
| `PendingScreen.jsx` | Shown when `status == 'pending'`. Waiting message + `tomerbb98@gmail.com`. |
| `HistoryScreen.jsx` | List of past interviews (company · role · date · score) → click opens the full feedback report. |
| `AdminScreen.jsx` | Tabs: Users · Pending · Stats · Allowlist. Clicking a user lists their sessions; clicking a session opens the **full transcript** beside the feedback report (D9). |
| `TranscriptView.jsx` | Renders a session's `state.history` as the Q&A it was — every interviewer question and candidate answer, in order. Admin-only. |

### Modified

- **`App.jsx`** — after login, call `/me` and route on `status`:
  `pending` → PendingScreen, `rejected` → rejection notice, `approved` → normal flow.
- **`LandingPage.jsx`** — attempts counter, Start disabled at zero,
  "My History" button, "Admin" button when `is_admin`.
- **`FeedbackScreen.jsx`** — reusable so HistoryScreen can render a past report
  without duplicating the layout.

### Reuse note

`HistoryScreen` must render **the exact same report** the user saw at the end of
the interview (D6), with company and job title added. So `FeedbackScreen` should
be refactored into a presentational component that takes a feedback object,
rather than being rewritten twice.

### Copy — exhausted attempts

Both languages are required; the app already has full EN/HE support and every
new string needs both.

**HE**
> כל הכבוד! השלמת 3 סימולציות ראיון — כל אחת מהן מקרבת אותך לעבודה הבאה שלך.
> תודה שהתנסית בסימולטור. אם תרצה ניסיונות נוספים או שיש לך משוב, אתה מוזמן לפנות אליי: tomerbb98@gmail.com

**EN**
> Well done! You've completed 3 interview simulations — each one brings you
> closer to your next role. Thanks for trying the simulator. If you'd like more
> attempts or have any feedback, reach out: tomerbb98@gmail.com

### Copy — pending approval

**HE**
> בקשת ההרשמה שלך התקבלה וממתינה לאישור. אשמח לעדכן אותך בקרוב — לשאלות: tomerbb98@gmail.com

**EN**
> Your registration has been received and is awaiting approval. For questions: tomerbb98@gmail.com

---

## 7. Tests (D10)

There are no automated tests today. Worth noting *why* that mattered: both bugs
that actually cost real time were invisible to a crash-based safety net.

- **The Q8 flow bug** returned HTTP 200, logged nothing, and produced a wrong score
- **The U+2028 bug** surfaced as the wrong error, because the error path itself threw

So the tests worth writing assert **behaviour and output shape**, not merely
"it did not raise".

### Priority 1 — guard what already broke

| Test | Asserts |
|---|---|
| Full interview loop | After the final turn the candidate answered **every** question. Catches the Q8 class directly. |
| Wrap-up is terminal | The closing message contains no question, and `is_complete` is True only after the last answer. |
| Non-ASCII survives | Hebrew text, em-dashes, smart quotes and U+2028 pass end-to-end with no encoding error. |
| Env var sanity | Every required key exists and is `.isascii()` at startup. Would have caught the pasted API key in one second. |

### Priority 2 — the new multi-user logic

| Test | Asserts |
|---|---|
| Attempt gate | The 4th attempt is refused with 403 |
| Pending gate | A `pending` user is refused on `/research` and `/interview/start` |
| Attempt accounting | A failed research run does **not** consume an attempt (D4) |
| Admin guard | A non-admin gets 403 on every `/admin/*` route |
| History isolation | A user can read only their own sessions |

### Open decision — the external APIs

Tests that really call Tavily and Anthropic are slow, cost money, and eat the
same 1,000/month Tavily quota that caps how many people can be invited.
Tests that mock them are fast and free but prove nothing about integration.

**Proposal:** mock by default, plus one opt-in end-to-end test behind a flag
(`RUN_LIVE_TESTS=1`) run by hand before a release. **Needs confirmation.**

---

## 8. Build order

1. **DB** — `profiles`, `allowlist`, `user_id` on `sessions`, trigger, RLS
2. **Backend** — `require_admin`, gates, `/me`
3. **Frontend** — PendingScreen, attempts counter, exhausted state
4. **History** — `/history` + HistoryScreen + FeedbackScreen refactor
5. **Admin** — `/admin/*` + AdminScreen + TranscriptView (D9)
6. **Tests** — Priority 1 then Priority 2 (§7)
7. **Manual pass** — full run with a second real email account

Steps 1–3 are what actually protect the account from cost. Steps 4–5 are
features. If time is short, do 1–3 first.

Priority-1 tests could reasonably be pulled forward to right after step 2 —
they cover the existing engine, not the new logic, and would then be in place
while the rest is built on top.

---

## 9. Explicitly out of scope

Discussed and deliberately **not** being built now — recorded so it isn't
re-litigated:

- `job_id` + polling instead of the blocking `.get(timeout=120)` in `research.py`
- Redis cache for research results keyed on `company + job_title`
- Raising Celery `--concurrency` / switching to `--pool=threads`
- Graceful degradation when a single research agent fails
- Retry with backoff on Anthropic/Tavily 429s
- Horizontal replicas, Redis HA, real monitoring

Current posture: **single user (Tomer), then a small invited group.** The system
handles roughly 5 simultaneous interview starts before the 120s timeout fires.
That is acceptable at this size. Revisit when the invited group grows past ~25.

### Known ceilings at current settings

| Limit | Value |
|---|---|
| Concurrent interview starts before timeout | ~5–6 |
| Tavily free tier | 1,000 searches/mo ÷ 24 per interview = **~41 interviews/mo** |
| Anthropic | ~$0.14 per interview |
| Railway Hobby | $5/mo minimum |

At 3 attempts each, Tavily caps the invited group at roughly **13 new users per
month** before the free tier runs out. This is the real constraint on how many
invitations to send.
