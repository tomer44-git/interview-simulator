// LoadingScreen.jsx — מסך טעינה בזמן שהresearch ובניית הפרסונה רצים
// מציג ספינר + הודעה דינמית שמתעדכנת מ-App.jsx
export default function LoadingScreen({ message }) {
  return (
    <div className="loading-screen">
      <div className="spinner" />
      <p className="loading-message">{message}</p>
      <p className="loading-hint">Searching the web in real time...</p>
    </div>
  )
}
