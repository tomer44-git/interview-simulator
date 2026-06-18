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
export const runResearch = (company, jobTitle) =>
  post('/research', { company, job_title: jobTitle })

// בונה פרסונת מראיין מנתוני המחקר
export const buildPersona = (research, jobTitle) =>
  post('/persona', { research, job_title: jobTitle })

// פותח ראיון חדש — מחזיר משפט פתיחה + state ריק
export const startInterview = (persona, jobTitle) =>
  post('/interview/start', { persona, job_title: jobTitle })

// מעבד תשובה של מועמד — מחזיר תגובת מראיין + state מעודכן
export const sendTurn = (userMessage, state, persona, jobTitle) =>
  post('/interview/turn', {
    user_message: userMessage,
    state,
    persona,
    job_title: jobTitle,
  })

// מנתח את הראיון המלא ומחזיר ציונים מפורטים
export const getFeedback = (state, persona, jobTitle) =>
  post('/feedback', { state, persona, job_title: jobTitle })
