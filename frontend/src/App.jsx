// App.jsx — state מרכזי + ניווט בין מסכים
import { useState, useEffect } from 'react'
import { supabase }     from './supabase'
import { setAuthToken } from './api'
import LandingPage     from './components/LandingPage'
import AuthScreen      from './components/AuthScreen'
import ContextScreen   from './components/ContextScreen'
import LoadingScreen   from './components/LoadingScreen'
import InterviewScreen from './components/InterviewScreen'
import FeedbackScreen  from './components/FeedbackScreen'
import * as api from './api'

const SCREENS = {
  LANDING:  'landing',
  CONTEXT:  'context',
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
    skipped:  'These files could not be read and were left out:',
    continue: 'Continue without them →',
  },
  he: {
    context:  'מעבד את היסטוריית הראיונות שלך...',
    research: (c) => `חוקר את ${c} ברשת...`,
    persona:  'בונה את פרסונת המראיין שלך...',
    starting: 'מתחיל את הריאיון...',
    analyzing:'מנתח את הביצועים שלך...',
    skipped:  'לא הצלחנו לקרוא את הקבצים הבאים והם לא נכללו:',
    continue: 'המשך בלעדיהם →',
  },
}

export default function App() {
  // ── Auth state ──
  const [session,     setSession]     = useState(null)
  const [authLoading, setAuthLoading] = useState(true)  // true בזמן בדיקת session קיים

  // ── Interview state ──
  const [screen,   setScreen]   = useState(SCREENS.LANDING)
  const [persona,  setPersona]  = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [company,  setCompany]  = useState('')
  const [language, setLanguage] = useState('en')
  const [state,    setState]    = useState(null)
  const [messages, setMessages] = useState([])
  const [loading,  setLoading]  = useState('')
  const [feedback, setFeedback] = useState(null)
  // { skipped: [שמות קבצים], summary: "..." } כשקבצים לא נקראו
  const [contextWarning, setContextWarning] = useState(null)

  // ── בדיקת session בטעינה + האזנה לשינויים ──
  useEffect(() => {
    // בודק אם יש session שמור (ממש בטעינה הראשונה)
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session) setAuthToken(session.access_token)
      setAuthLoading(false)
    })

    // מאזין לLogin / Logout — מעדכן session ו-token אוטומטית
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, session) => {
      setSession(session)
      setAuthToken(session?.access_token ?? null)
    })

    // ניקוי listener כשהקומפוננטה מתפרקת
    return () => subscription.unsubscribe()
  }, [])

  async function handleSignOut() {
    await supabase.auth.signOut()
    handleRestart()
  }

  // ── שלב 1: LandingPage → שומר נתונים ועובר לContextScreen ──
  function handleStart(companyInput, jobTitleInput, lang) {
    setCompany(companyInput)
    setJobTitle(jobTitleInput)
    setLanguage(lang)
    setScreen(SCREENS.CONTEXT)
  }

  // ── מחקר → פרסונה → פתיחת ראיון ──
  // מופרד כי נקראים אליו משני מקומות: הגשה רגילה, והמשך אחרי אזהרת קבצים
  async function runPipeline(contextSummary) {
    const msg = MESSAGES[language]
    setScreen(SCREENS.LOADING)

    try {
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

  // ── שלב 2: ContextScreen → מעבד קונטקסט ומריץ את ה-pipeline ──
  async function handleContextSubmit(contextText, contextFiles) {
    setScreen(SCREENS.LOADING)
    setContextWarning(null)

    try {
      let contextSummary = ''
      if (contextText.trim() || contextFiles.length > 0) {
        setLoading(MESSAGES[language].context)
        const ctxResult = await api.sendContext(contextText, contextFiles)
        contextSummary = ctxResult.context_summary || ''

        // קבצים שה-backend לא הצליח לקרוא — עוצרים ומיידעים.
        // המשתמש העלה אותם כי רצה שיילקחו בחשבון; להמשיך בשקט
        // יהפוך את הראיון לכזה שמתעלם מהם בלי שידע למה.
        const skipped = ctxResult.skipped_files || []
        if (skipped.length > 0) {
          // שומרים את הסיכום כדי לא לשלם שוב על אותה קריאה אם ימשיך
          setContextWarning({ skipped, summary: contextSummary })
          setScreen(SCREENS.CONTEXT)
          return
        }
      }

      await runPipeline(contextSummary)

    } catch (err) {
      alert('Something went wrong: ' + err.message)
      setScreen(SCREENS.LANDING)
    }
  }

  // המשתמש בחר להמשיך למרות שקבצים דולגו — משתמשים בסיכום שכבר חושב
  function handleContinueAnyway() {
    const summary = contextWarning?.summary || ''
    setContextWarning(null)
    runPipeline(summary)
  }

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
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: 'Error: ' + err.message }])
    }
  }

  // ── שלב 4: המשתמש לחץ "View Results" אחרי הודעת הסיום ──
  async function handleViewResults() {
    setScreen(SCREENS.LOADING)
    setLoading(MESSAGES[language].analyzing)
    try {
      const fb = await api.getFeedback(state, persona, jobTitle, language)
      setFeedback(fb)
    } catch { setFeedback(null) }
    setScreen(SCREENS.FEEDBACK)
  }

  function handleRestart() {
    setScreen(SCREENS.LANDING)
    setPersona(null); setState(null); setMessages([])
    setJobTitle(''); setCompany(''); setFeedback(null); setLanguage('en')
  }

  // ── בזמן בדיקת session ── (מניעת ריצוד עם AuthScreen)
  if (authLoading) return <div className="app"><LoadingScreen message="Loading..." /></div>

  // ── לא מחובר → מסך Login/Register ──
  if (!session) return <div className="app"><AuthScreen /></div>

  return (
    <div className="app">
      {screen === SCREENS.LANDING   && (
        <LandingPage onStart={handleStart} onSignOut={handleSignOut} />
      )}
      {screen === SCREENS.CONTEXT   && (
        <ContextScreen
          onSubmit={handleContextSubmit}
          onSkip={handleContextSkip}
          warning={contextWarning}
          warningText={MESSAGES[language].skipped}
          continueText={MESSAGES[language].continue}
          onContinueAnyway={handleContinueAnyway}
        />
      )}
      {screen === SCREENS.LOADING   && <LoadingScreen message={loading} />}
      {screen === SCREENS.INTERVIEW && (
        <InterviewScreen
          messages={messages}
          persona={persona}
          state={state}
          language={language}
          onSend={handleTurn}
          onViewResults={handleViewResults}
        />
      )}
      {screen === SCREENS.FEEDBACK  && (
        <FeedbackScreen feedback={feedback} persona={persona} onRestart={handleRestart} />
      )}
    </div>
  )
}
