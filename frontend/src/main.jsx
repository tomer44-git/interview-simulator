// main.jsx — נקודת הכניסה של React
// מחבר את ה-App component לתוך ה-<div id="root"> שב-index.html
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './App.css'
import App from './App'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
