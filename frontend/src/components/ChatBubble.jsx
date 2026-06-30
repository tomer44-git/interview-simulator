// ChatBubble.jsx — בועת הודעה בודדת בצ'אט
// role קובע צד (שמאל = מראיין, ימין = מועמד) ועיצוב
import { User, UserRound } from 'lucide-react'

export default function ChatBubble({ role, content }) {
  const isInterviewer = role === 'interviewer'
  const isError       = role === 'error'

  return (
    <div className={`bubble-row ${isInterviewer ? 'left' : 'right'}`}>
      {/* אייקון User בצד שמאל למראיין */}
      {isInterviewer && (
        <div className="avatar">
          <User size={18} strokeWidth={1.5} />
        </div>
      )}

      <div className={`bubble ${isInterviewer ? 'bubble-interviewer' : 'bubble-candidate'} ${isError ? 'bubble-error' : ''}`}>
        {content}
      </div>

      {/* אייקון UserRound בצד ימין למועמד */}
      {!isInterviewer && !isError && (
        <div className="avatar">
          <UserRound size={18} strokeWidth={1.5} />
        </div>
      )}
    </div>
  )
}
