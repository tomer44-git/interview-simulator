// App.jsx — state מרכזי + ניווט בין מסכים
// כל ה-data חי כאן ומועבר למסכים כ-props
import { useState } from 'react'
import LandingPage     from './components/LandingPage'
import LoadingScreen   from './components/LoadingScreen'
import InterviewScreen from './components/InterviewScreen'
import FeedbackScreen  from './components/FeedbackScreen'
import * as api from './api'

const SCREENS = { LANDING: 'landing', LOADING: 'loading', INTERVIEW: 'interview', FEEDBACK: 'feedback' }

export default function App() {
  const [screen,   setScreen]   = useState(SCREENS.LANDING)
  const [persona,  setPersona]  = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [state,    setState]    = useState(null)
  const [messages, setMessages] = useState([])
  const [loading,  setLoading]  = useState('')
  const [feedback, setFeedback] = useState(null)  // תוצאות הניתוח מהfeedback_agent

  // ── מופעל כשהמשתמש שולח את הטופס ב-LandingPage ──
  async function handleStart(company, jobTitleInput) {
    setJobTitle(jobTitleInput)
    setScreen(SCREENS.LOADING)

    try {
      setLoading('Researching ' + company + ' across the web...')
      const research = await api.runResearch(company, jobTitleInput)

      setLoading('Building your interviewer persona...')
      const { persona: builtPersona } = await api.buildPersona(research, jobTitleInput)

      setLoading('Starting your interview...')
      const startResult = await api.startInterview(builtPersona, jobTitleInput)

      setPersona(builtPersona)
      setState(startResult.state)
      setMessages([{ role: 'interviewer', content: startResult.message }])
      setScreen(SCREENS.INTERVIEW)

    } catch (err) {
      alert('Something went wrong: ' + err.message)
      setScreen(SCREENS.LANDING)
    }
  }

  // ── מופעל בכל תשובה של המועמד ──
  async function handleTurn(userMessage) {
    setMessages(prev => [...prev, { role: 'candidate', content: userMessage }])

    try {
      const result = await api.sendTurn(userMessage, state, persona, jobTitle)
      setState(result.state)
      setMessages(prev => [...prev, { role: 'interviewer', content: result.message }])

      // ---- אם הראיון הסתיים — מבקשים פידבק ----
      if (result.is_complete) {
        setScreen(SCREENS.LOADING)
        setLoading('Analyzing your interview performance...')
        try {
          const fb = await api.getFeedback(result.state, persona, jobTitle)
          setFeedback(fb)
        } catch {
          // אם הפידבק נכשל — עדיין מציגים את מסך הסיום בלי ניקוד
          setFeedback(null)
        }
        setScreen(SCREENS.FEEDBACK)
      }

    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: 'Error: ' + err.message }])
    }
  }

  function handleRestart() {
    setScreen(SCREENS.LANDING)
    setPersona(null); setState(null); setMessages([])
    setJobTitle(''); setFeedback(null)
  }

  return (
    <div className="app">
      {screen === SCREENS.LANDING   && <LandingPage onStart={handleStart} />}
      {screen === SCREENS.LOADING   && <LoadingScreen message={loading} />}
      {screen === SCREENS.INTERVIEW && (
        <InterviewScreen
          messages={messages}
          persona={persona}
          state={state}
          onSend={handleTurn}
        />
      )}
      {screen === SCREENS.FEEDBACK  && (
        <FeedbackScreen
          feedback={feedback}
          persona={persona}
          onRestart={handleRestart}
        />
      )}
    </div>
  )
}
