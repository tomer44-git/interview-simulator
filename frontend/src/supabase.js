// supabase.js — client יחיד משותף לכל האפליקציה
// מאותחל עם VITE_SUPABASE_URL ו-VITE_SUPABASE_ANON_KEY שמוגדרים ב-Vercel
import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL     = import.meta.env.VITE_SUPABASE_URL
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY

// ה-anon key בטוח לשימוש בbrowser — מאפשר auth בלבד, לא גישה ישירה לDB
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
