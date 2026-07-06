// ContextScreen.jsx — שלב אופציונלי: קונטקסט תהליך הגיוס + קבצים
// מופיע בין LandingPage ל-Loading — המשתמש יכול לדלג
import { useState, useRef } from 'react'
import { FileText, Upload, X } from 'lucide-react'

export default function ContextScreen({ onSubmit, onSkip }) {
  const [text,     setText]     = useState('')
  const [files,    setFiles]    = useState([])   // רשימת File objects
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  // ── טיפול בגרירת קבצים ──
  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    addFiles(Array.from(e.dataTransfer.files))
  }

  function handleFileInput(e) {
    addFiles(Array.from(e.target.files))
    e.target.value = ''  // מאפשר לבחור שוב את אותו קובץ
  }

  function addFiles(newFiles) {
    const allowed = newFiles.filter(f =>
      f.name.endsWith('.pdf') || f.name.endsWith('.doc') || f.name.endsWith('.docx')
    )
    setFiles(prev => [...prev, ...allowed])
  }

  function removeFile(idx) {
    setFiles(prev => prev.filter((_, i) => i !== idx))
  }

  function handleSubmit() {
    onSubmit(text, files)
  }

  const hasContent = text.trim() || files.length > 0

  return (
    <div className="context-page">
      <div className="context-card">
        <h2 className="context-title">Interview process so far</h2>
        <p className="context-subtitle">
          Optional — helps the interviewer tailor questions to where you are in the process.
        </p>

        {/* ── שדה טקסט חופשי ── */}
        <textarea
          className="context-textarea"
          placeholder="e.g. I had a screening call last week. They sent a home assignment about building a REST API. The interviewer mentioned they focus on system design..."
          value={text}
          onChange={e => setText(e.target.value)}
          rows={5}
        />

        {/* ── אזור גרירה / העלאת קבצים ── */}
        <div
          className={`drop-zone ${dragging ? 'drop-zone--active' : ''}`}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <Upload size={20} strokeWidth={1.5} />
          <span>Drag PDF or Word files here, or <u>click to browse</u></span>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.doc,.docx"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileInput}
          />
        </div>

        {/* ── רשימת קבצים שנוספו ── */}
        {files.length > 0 && (
          <ul className="file-list">
            {files.map((f, i) => (
              <li key={i} className="file-item">
                <FileText size={14} strokeWidth={1.5} />
                <span>{f.name}</span>
                <button className="file-remove" onClick={() => removeFile(i)} aria-label="הסר">
                  <X size={13} />
                </button>
              </li>
            ))}
          </ul>
        )}

        {/* ── כפתורים ── */}
        <div className="context-actions">
          <button className="btn-skip" onClick={onSkip}>Skip</button>
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={!hasContent}
          >
            Add Context & Start →
          </button>
        </div>
      </div>
    </div>
  )
}
