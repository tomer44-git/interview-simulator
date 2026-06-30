// LandingPage.jsx — מסך כניסה: טופס עם שם חברה + תפקיד
import { useState } from 'react'
import { Building2, Briefcase } from 'lucide-react'

export default function LandingPage({ onStart }) {
  const [company,  setCompany]  = useState('')
  const [jobTitle, setJobTitle] = useState('')

  function handleSubmit(e) {
    e.preventDefault()  // מונע רענון דף ברגיל
    if (!company.trim() || !jobTitle.trim()) return
    onStart(company.trim(), jobTitle.trim())
  }

  return (
    <div className="landing">
      <div className="landing-card">
        <h1>Interview Simulator</h1>
        <p className="subtitle">
          Real-time AI research · Personalized interviewer · Role-specific questions
        </p>

        <form onSubmit={handleSubmit} className="landing-form">
          <label>Company Name</label>
          {/* עטיפת אייקון Building2 + שדה קלט */}
          <div className="input-icon-wrap">
            <Building2 size={16} strokeWidth={2} />
            <input
              type="text"
              placeholder="e.g. Wix, Google, Startup XYZ"
              value={company}
              onChange={e => setCompany(e.target.value)}
              autoFocus
            />
          </div>

          <label>Job Title</label>
          {/* עטיפת אייקון Briefcase + שדה קלט */}
          <div className="input-icon-wrap">
            <Briefcase size={16} strokeWidth={2} />
            <input
              type="text"
              placeholder="e.g. Frontend Developer, Junior AI Engineer"
              value={jobTitle}
              onChange={e => setJobTitle(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={!company.trim() || !jobTitle.trim()}
          >
            Start Interview →
          </button>
        </form>

        <p className="hint">Research takes ~20 seconds. The wait is worth it.</p>
      </div>
    </div>
  )
}
