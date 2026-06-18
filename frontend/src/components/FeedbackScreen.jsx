// FeedbackScreen.jsx — מסך תוצאות הראיון
// מציג ציון כולל, ציונים לפי קטגוריה, חוזקות, ונקודות לשיפור

export default function FeedbackScreen({ feedback, persona, onRestart }) {
  if (!feedback) return null

  const { overall_score, categories, summary,
          top_strengths, areas_to_improve, recommended_resources } = feedback

  return (
    <div className="feedback-screen">

      {/* ── כותרת ── */}
      <div className="feedback-header">
        <h2>Interview Complete</h2>
        <p className="feedback-subtitle">
          Feedback from {persona?.name} · {persona?.company_name}
        </p>
      </div>

      {/* ── ציון כולל ── */}
      <div className="overall-score-card">
        <div className="score-circle">
          <span className="score-number">{overall_score.toFixed(1)}</span>
          <span className="score-denom">/10</span>
        </div>
        <p className="score-summary">{summary}</p>
      </div>

      {/* ── ציונים לפי קטגוריה ── */}
      <div className="categories-grid">
        {Object.entries(categories).map(([cat, data]) => (
          <div key={cat} className="category-card">
            <div className="category-header">
              <span className="category-name">{cat}</span>
              <span className="category-score">{data.score.toFixed(1)}</span>
            </div>
            {/* פס התקדמות חזואלי */}
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${data.score * 10}%` }} />
            </div>
            <p className="category-feedback">{data.feedback}</p>
            <div className="tags">
              {data.strengths.map((s, i) => (
                <span key={i} className="tag tag-green">✓ {s}</span>
              ))}
              {data.improvements.map((imp, i) => (
                <span key={i} className="tag tag-orange">↑ {imp}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* ── משאבים מומלצים ── */}
      {recommended_resources?.length > 0 && (
        <div className="resources-section">
          <h3>Recommended Resources</h3>
          <ul>
            {recommended_resources.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
      )}

      <button className="btn-restart" onClick={onRestart}>
        Start New Interview
      </button>
    </div>
  )
}
