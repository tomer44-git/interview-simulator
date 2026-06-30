// App.jsx — state מרכזי + ניווט בין מסכים
// כל ה-data חי כאן ומועבר למסכים כ-props
import { useState } from 'react'
import LandingPage     from './components/LandingPage'
import LoadingScreen   from './components/LoadingScreen'
import InterviewScreen from './components/InterviewScreen'
import FeedbackScreen  from './components/FeedbackScreen'
import * as api from './api'

const SCREENS = { LANDING: 'landing', LOADING: 'loading', INTERVIEW: 'interview', FEEDBACK: 'feedback' }

// הודעות loading בשתי שפות
const MESSAGES = {
  en: {
    research:  (company) => `Researching ${company} across the web...`,
    persona:   'Building your interviewer persona...',
    starting:  'Starting your interview...',
    analyzing: 'Analyzing your interview performance...',
  },
  he: {
    research:  (company) => `חוקר את ${company} ברשת...`,
    persona:   'בונה את פרסונת המראיין שלך...',
    starting:  'מתחיל את הריאיון...',
    analyzing: 'מנתח את הביצועים שלך...',
  },
}

export default function App() {
  const [screen,   setScreen]   = useState(SCREENS.LANDING)
  const [persona,  setPersona]  = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [language, setLanguage] = useState('en')  // שפת הראיון — זורמת לכל ה-pipeline
  const [state,    setState]    = useState(null)
  const [messages, setMessages] = useState([])
  const [loading,  setLoading]  = useState('')
  const [feedback, setFeedback] = useState(null)

  // ── מופעל כשהמשתמש שולח את הטופס ב-LandingPage ──
  async function handleStart(company, jobTitleInput, lang) {
    setJobTitle(jobTitleInput)
    setLanguage(lang)
    setScreen(SCREENS.LOADING)

    const msg = MESSAGES[lang]

    try {
      setLoading(msg.research(company))
      const research = await api.runResearch(company, jobTitleInput)

      setLoading(msg.persona)
      const { persona: builtPersona } = await api.buildPersona(research, jobTitleInput, lang)

      setLoading(msg.starting)
      const startResult = await api.startInterview(builtPersona, jobTitleInput, lang)

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
      const result = await api.sendTurn(userMessage, state, persona, jobTitle, language)
      setState(result.state)
      setMessages(prev => [...prev, { role: 'interviewer', content: result.message }])

      if (result.is_complete) {
        setScreen(SCREENS.LOADING)
        setLoading(MESSAGES[language].analyzing)
        try {
          const fb = await api.getFeedback(result.state, persona, jobTitle, language)
          setFeedback(fb)
        } catch {
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
    setJobTitle(''); setFeedback(null); setLanguage('en')
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
          language={language}
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
