// api.js — כל הקריאות ל-FastAPI backend במקום אחד
// בפיתוח: /api עובר דרך vite proxy ל-localhost:8000
// בproduction: VITE_API_URL מכיל את ה-URL האמיתי של Railway

const BASE = import.meta.env.VITE_API_URL || '/api'

// ה-JWT token של המשתמש המחובר — מוגדר ע"י App.jsx מיד אחרי login
let _token = null
export function setAuthToken(token) { _token = token }

// שולח POST ומחזיר JSON — מוסיף Authorization header אוטומטית
async function post(path, body) {
  const headers = { 'Content-Type': 'application/json' }
  if (_token) headers['Authorization'] = `Bearer ${_token}`

  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers,
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

// שולח טקסט + קבצים ל-context agent — מחזיר context_summary
// משתמש ב-FormData כי יש קבצים בינאריים
export async function sendContext(text, files) {
  const formData = new FormData()
  formData.append('text', text)
  for (const file of files) {
    formData.append('files', file)
  }
  // גם כאן מוסיפים את ה-token — FormData לא מקבל Content-Type ידני
  const headers = {}
  if (_token) headers['Authorization'] = `Bearer ${_token}`

  const res = await fetch(`${BASE}/context`, { method: 'POST', body: formData, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Context request failed')
  }
  return res.json()  // { context_summary: "..." }
}

// בונה פרסונת מראיין — language + context_summary
export const buildPersona = (research, jobTitle, language = 'en', contextSummary = '') =>
  post('/persona', { research, job_title: jobTitle, language, context_summary: contextSummary })

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
