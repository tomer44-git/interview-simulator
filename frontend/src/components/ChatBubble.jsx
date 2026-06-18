// ChatBubble.jsx — בועת הודעה בודדת בצ'אט
// role קובע צד (שמאל = מראיין, ימין = מועמד) ועיצוב
export default function ChatBubble({ role, content }) {
  const isInterviewer = role === 'interviewer'
  const isError       = role === 'error'

  return (
    <div className={`bubble-row ${isInterviewer ? 'left' : 'right'}`}>
      {isInterviewer && <div className="avatar">🤵</div>}
      <div className={`bubble ${isInterviewer ? 'bubble-interviewer' : 'bubble-candidate'} ${isError ? 'bubble-error' : ''}`}>
        {content}
      </div>
      {!isInterviewer && !isError && <div className="avatar">👤</div>}
    </div>
  )
}
