// InterviewScreen.jsx — מסך הצ'אט הראשי
// מציג היסטוריית הודעות + input לתשובות המועמד
import { useState, useEffect, useRef } from 'react'
import ChatBubble from './ChatBubble'

export default function InterviewScreen({ messages, persona, state, onSend }) {
  const [input, setInput]   = useState('')
  const [busy,  setBusy]    = useState(false)  // true בזמן שממתינים לתגובת המראיין
  const bottomRef = useRef(null)

  // גלילה אוטומטית לתחתית בכל פעם שמגיעה הודעה חדשה
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || busy) return

    const text = input.trim()
    setInput('')
    setBusy(true)
    await onSend(text)   // App.jsx מטפל בקריאה ל-API
    setBusy(false)
  }

  // חישוב התקדמות — מה מספר השאלות שנשאלו
  const asked = state?.questions_asked ?? 0
  const total = 8  // לפי question_flow ברירת מחדל

  return (
    <div className="interview-screen">

      {/* ── header ── */}
      <div className="interview-header">
        <div className="interviewer-info">
          <span className="interviewer-name">🤵 {persona?.name}</span>
          <span className="interviewer-title">{persona?.title} · {persona?.company_name}</span>
        </div>
        <div className="progress">
          Question {Math.min(asked + 1, total)} / {total}
        </div>
      </div>

      {/* ── רשימת הודעות ── */}
      <div className="messages-list">
        {messages.map((msg, i) => (
          <ChatBubble key={i} role={msg.role} content={msg.content} />
        ))}
        {/* ספינר בזמן המתנה לתגובת המראיין */}
        {busy && (
          <div className="bubble-row left">
            <div className="avatar">🤵</div>
            <div className="bubble bubble-interviewer typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── input ── */}
      <form className="input-row" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Type your answer..."
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={busy}
          autoFocus
        />
        <button type="submit" className="btn-send" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>

    </div>
  )
}
