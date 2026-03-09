import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://fnpguxbnycsllvttttlk.supabase.co';
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const API_BASE = 'http://localhost:8000';

async function testApi() {
    if (!SUPABASE_ANON_KEY) {
        console.error("Please provide NEXT_PUBLIC_SUPABASE_ANON_KEY env var");
        return;
    }
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    console.log("1. Logging in...");
    const { data: authData, error: loginError } = await supabase.auth.signInWithPassword({
        email: "test401@example.com",
        password: "TestPassword123!@#"
    });

    // In case the user does not exist, we just sign up:
    if (loginError && loginError.message.includes("Invalid login")) {
        console.log("Signup instead...");
        const { data: signUpData, error: signupError } = await supabase.auth.signUp({
            email: "test401@example.com",
            password: "testpassword123"
        });
        if (signupError) {
            console.error("Signup error:", signupError);
            return;
        }
        console.log("Signup success!");
    } else if (loginError) {
        console.error("Login error:", loginError);
        return;
    } else {
        console.log("Login success!");
    }

    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    console.log("2. Session fetched:", !!session);

    if (session?.access_token) {
        console.log("3. Fetching /api/templates/custom with token...");
        const res = await fetch(`${API_BASE}/api/templates/custom`, {
            headers: {
                "Authorization": `Bearer ${session.access_token}`
            }
        });
        const json = await res.json();
        console.log("Status:", res.status);
        console.log("Response:", json);
    }
}

testApi();
