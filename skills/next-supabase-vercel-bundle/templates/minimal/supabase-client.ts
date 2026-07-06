import { createClient } from '@supabase/supabase-js'

export const createSupabaseClient = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  return createClient(supabaseUrl, supabaseAnonKey)
}

export const supabase = createSupabaseClient()
