import { createBrowserClient } from '@supabase/ssr';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// B-FIX-11: Guard — do not call Supabase client factory with undefined args (crashes at runtime).
// Export null when env vars are missing; callers handle null gracefully.
if (!supabaseUrl || !supabaseAnonKey) {
    console.error('[Supabase] Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY. Auth and DB features will not work.');
}

export const supabase = (supabaseUrl && supabaseAnonKey)
    ? createBrowserClient(supabaseUrl, supabaseAnonKey)
    : null;
