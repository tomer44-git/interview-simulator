// AuthScreen.jsx — מסך Login / Register
// שומר על אותה תמה לבנדר כמו שאר האפליקציה
import { useState } from 'react'
import { supabase } from '../supabase'
import { Mail, Lock } from 'lucide-react'

export default function AuthScreen() {
  const [mode,     setMode]     = useState('login')   // 'login' | 'register'
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [success,  setSuccess]  = useState('')
  const [busy,     setBusy]     = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setBusy(true)

    try {
      if (mode === 'login') {
        // התחברות עם אימייל + סיסמה
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        // הצלחה — App.jsx יזהה את ה-session ויעבור למסך הבית אוטומטית

      } else {
        // הרשמה — Supabase שולח מייל אימות
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) throw error
        setSuccess('Check your email and click the verification link to activate your account.')
      }
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Interview Simulator</h1>
        <p className="auth-subtitle">AI-powered interview practice</p>

        {/* טאבים: Login / Register */}
        <div className="auth-tabs">
          <button
            className={`auth-tab ${mode === 'login' ? 'auth-tab--active' : ''}`}
            onClick={() => { setMode('login'); setError(''); setSuccess('') }}
          >
            Sign In
          </button>
          <button
            className={`auth-tab ${mode === 'register' ? 'auth-tab--active' : ''}`}
            onClick={() => { setMode('register'); setError(''); setSuccess('') }}
          >
            Create Account
          </button>
        </div>

        <form className="landing-form" onSubmit={handleSubmit}>
          {/* שדה אימייל */}
          <div className="input-icon-wrap">
            <Mail size={16} strokeWidth={1.5} />
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>

          {/* שדה סיסמה */}
          <div className="input-icon-wrap">
            <Lock size={16} strokeWidth={1.5} />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {/* הודעת שגיאה */}
          {error   && <p className="auth-error">{error}</p>}

          {/* הודעת הצלחה אחרי הרשמה */}
          {success && <p className="auth-success">{success}</p>}

          <button className="btn-primary" type="submit" disabled={busy}>
            {busy
              ? 'Please wait...'
              : mode === 'login' ? 'Sign In →' : 'Create Account →'
            }
          </button>
        </form>
      </div>
    </div>
  )
}
