// api.js — כל הקריאות ל-FastAPI backend במקום אחד
// בפיתוח: /api עובר דרך vite proxy ל-localhost:8000
// בproduction: VITE_API_URL מכיל את ה-URL האמיתי של Railway

const BASE = import.meta.env.VITE_API_URL || '/api'

// שולח POST ומחזיר JSON — פונקציה פנימית משותפת
async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

// מריץ את כל 6 ה-research agents במקביל דרך Celery
// language לא נדרש כאן — המחקר הוא אנגלי תמיד (תוכן מהאינטרנט)
export const runResearch = (company, jobTitle) =>
  post('/research', { company, job_title: jobTitle })

// בונה פרסונת מראיין — language קובע את שפת הפרסונה
export const buildPersona = (research, jobTitle, language = 'en') =>
  post('/persona', { research, job_title: jobTitle, language })

// פותח ראיון חדש — language זורם לagent כדי להגדיר שפת שיחה
export const startInterview = (persona, jobTitle, language = 'en') =>
  post('/interview/start', { persona, job_title: jobTitle, language })

// מעבד תשובה של מועמד — language מוזרק לכל תור
export const sendTurn = (userMessage, state, persona, jobTitle, language = 'en') =>
  post('/interview/turn', {
    user_message: userMessage,
    state,
    persona,
    job_title: jobTitle,
    language,
  })

// מנתח את הראיון המלא — language מעביר לfeedback agent
export const getFeedback = (state, persona, jobTitle, language = 'en') =>
  post('/feedback', { state, persona, job_title: jobTitle, language })
