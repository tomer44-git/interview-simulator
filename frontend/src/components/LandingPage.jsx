// LandingPage.jsx — מסך כניסה: טופס עם שם חברה + תפקיד
import { useState } from 'react'

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
          <input
            type="text"
            placeholder="e.g. Wix, Google, Startup XYZ"
            value={company}
            onChange={e => setCompany(e.target.value)}
            autoFocus
          />

          <label>Job Title</label>
          <input
            type="text"
            placeholder="e.g. Frontend Developer, Junior AI Engineer"
            value={jobTitle}
            onChange={e => setJobTitle(e.target.value)}
          />

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
