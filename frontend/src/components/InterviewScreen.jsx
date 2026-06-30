// InterviewScreen.jsx — מסך הצ'אט הראשי
// מציג היסטוריית הודעות + input לתשובות המועמד
import { useState, useEffect, useRef } from 'react'
import { User, Briefcase, MessageSquare, Send } from 'lucide-react'
import ChatBubble from './ChatBubble'

export default function InterviewScreen({ messages, persona, state, language = 'en', onSend }) {
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
    // dir="rtl" כשהשפה עברית — מטפל בכל היישור והכיוון אוטומטית
    <div className="interview-wrapper" dir={language === 'he' ? 'rtl' : 'ltr'}>
      <div className="interview-screen">

        {/* ── header ── */}
        <div className="interview-header">
          <div className="interviewer-info">
            {/* User icon ליד שם המראיין */}
            <span className="interviewer-name">
              <User size={15} strokeWidth={2} />
              {persona?.name}
            </span>
            {/* Briefcase icon ליד תפקיד + חברה */}
            <span className="interviewer-title">
              <Briefcase size={13} strokeWidth={2} />
              {persona?.title} · {persona?.company_name}
            </span>
          </div>
          {/* MessageSquare icon ליד מונה השאלות */}
          <div className="progress">
            <MessageSquare size={13} strokeWidth={2} />
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
              <div className="avatar">
                <User size={18} strokeWidth={1.5} />
              </div>
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
            placeholder={language === 'he' ? 'כתוב את תשובתך...' : 'Type your answer...'}
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={busy}
            autoFocus
          />
          {/* Send icon במקום טקסט "Send" */}
          <button type="submit" className="btn-send" disabled={busy || !input.trim()}>
            <Send size={16} strokeWidth={2} />
          </button>
        </form>

      </div>
    </div>
  )
}
