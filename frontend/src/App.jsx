// App.jsx — state מרכזי + ניווט בין מסכים
import { useState } from 'react'
import LandingPage     from './components/LandingPage'
import ContextScreen   from './components/ContextScreen'
import LoadingScreen   from './components/LoadingScreen'
import InterviewScreen from './components/InterviewScreen'
import FeedbackScreen  from './components/FeedbackScreen'
import * as api from './api'

const SCREENS = {
  LANDING:  'landing',
  CONTEXT:  'context',   // שלב חדש — קונטקסט תהליך הגיוס
  LOADING:  'loading',
  INTERVIEW:'interview',
  FEEDBACK: 'feedback',
}

const MESSAGES = {
  en: {
    context:  'Processing your interview history...',
    research: (c) => `Researching ${c} across the web...`,
    persona:  'Building your interviewer persona...',
    starting: 'Starting your interview...',
    analyzing:'Analyzing your interview performance...',
  },
  he: {
    context:  'מעבד את היסטוריית הראיונות שלך...',
    research: (c) => `חוקר את ${c} ברשת...`,
    persona:  'בונה את פרסונת המראיין שלך...',
    starting: 'מתחיל את הריאיון...',
    analyzing:'מנתח את הביצועים שלך...',
  },
}

export default function App() {
  const [screen,   setScreen]   = useState(SCREENS.LANDING)
  const [persona,  setPersona]  = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [company,  setCompany]  = useState('')
  const [language, setLanguage] = useState('en')
  const [state,    setState]    = useState(null)
  const [messages, setMessages] = useState([])
  const [loading,  setLoading]  = useState('')
  const [feedback, setFeedback] = useState(null)

  // ── שלב 1: LandingPage → שומר נתונים ועובר לContextScreen ──
  function handleStart(companyInput, jobTitleInput, lang) {
    setCompany(companyInput)
    setJobTitle(jobTitleInput)
    setLanguage(lang)
    setScreen(SCREENS.CONTEXT)
  }

  // ── שלב 2: ContextScreen → מריץ את כל ה-pipeline ──
  async function handleContextSubmit(contextText, contextFiles) {
    setScreen(SCREENS.LOADING)
    const msg = MESSAGES[language]

    try {
      // שלב קונטקסט — אופציונלי, רק אם יש תוכן
      let contextSummary = ''
      if (contextText.trim() || contextFiles.length > 0) {
        setLoading(msg.context)
        const ctxResult = await api.sendContext(contextText, contextFiles)
        contextSummary = ctxResult.context_summary || ''
      }

      setLoading(msg.research(company))
      const research = await api.runResearch(company, jobTitle)

      setLoading(msg.persona)
      const { persona: builtPersona } = await api.buildPersona(
        research, jobTitle, language, contextSummary
      )

      setLoading(msg.starting)
      const startResult = await api.startInterview(builtPersona, jobTitle, language)

      setPersona(builtPersona)
      setState(startResult.state)
      setMessages([{ role: 'interviewer', content: startResult.message }])
      setScreen(SCREENS.INTERVIEW)

    } catch (err) {
      alert('Something went wrong: ' + err.message)
      setScreen(SCREENS.LANDING)
    }
  }

  // דילוג על שלב הקונטקסט — מריץ pipeline ללא context
  function handleContextSkip() {
    handleContextSubmit('', [])
  }

  // ── שלב 3: כל תור בראיון ──
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
        } catch { setFeedback(null) }
        setScreen(SCREENS.FEEDBACK)
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: 'Error: ' + err.message }])
    }
  }

  function handleRestart() {
    setScreen(SCREENS.LANDING)
    setPersona(null); setState(null); setMessages([])
    setJobTitle(''); setCompany(''); setFeedback(null); setLanguage('en')
  }

  return (
    <div className="app">
      {screen === SCREENS.LANDING   && <LandingPage onStart={handleStart} />}
      {screen === SCREENS.CONTEXT   && (
        <ContextScreen onSubmit={handleContextSubmit} onSkip={handleContextSkip} />
      )}
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
        <FeedbackScreen feedback={feedback} persona={persona} onRestart={handleRestart} />
      )}
    </div>
  )
}
