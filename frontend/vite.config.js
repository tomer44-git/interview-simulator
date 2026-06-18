import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// vite.config.js — הגדרות שרת הפיתוח
// proxy מעביר בקשות API ל-FastAPI כדי לעקוף בעיות CORS בפיתוח
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // כל בקשה שמתחילה ב-/api תועבר ל-FastAPI על פורט 8000
      '/api': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
