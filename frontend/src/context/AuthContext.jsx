import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check active session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
            setIsLoggedIn(!!session);
            setLoading(false);
        });

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
            setIsLoggedIn(!!session);
            setLoading(false);

            if (!session) {
                // Clear app-specific storage on logout
                sessionStorage.clear();
                localStorage.removeItem('scholarform_job'); // Assuming job might be stored here too, mostly session
            }
        });

        return () => subscription.unsubscribe();
    }, []);

    const signUp = async (signupData) => {
        const { signup: apiSignup } = await import('../services/api');
        try {
            const data = await apiSignup(signupData);
            return { data, error: null };
        } catch (error) {
            return { data: null, error };
        }
    };

    const signIn = async (email, password) => {
        const { login: apiLogin } = await import('../services/api');
        try {
            const data = await apiLogin({ email, password });

            if (data?.session) {
                await supabase.auth.setSession({
                    access_token: data.session.access_token,
                    refresh_token: data.session.refresh_token
                });
            }

            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        }
    };

    const signInWithGoogle = async () => {
        return await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: `${window.location.origin}/dashboard`, // Redirect back to dashboard
            }
        });
    };

    const signOut = async () => {
        return await supabase.auth.signOut();
    };

    const forgotPassword = async (email) => {
        const { forgotPassword: apiForgotPassword } = await import('../services/api');
        try {
            const data = await apiForgotPassword({ email });
            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        }
    };

    const verifyOtp = async (email, otp) => {
        const { verifyOtp: apiVerifyOtp } = await import('../services/api');
        try {
            const data = await apiVerifyOtp({ email, otp });
            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        }
    };

    const resetPassword = async (email, otp, newPassword) => {
        const { resetPassword: apiResetPassword } = await import('../services/api');
        try {
            const data = await apiResetPassword({ email, otp, new_password: newPassword });
            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        }
    };

    const value = {
        user,
        isLoggedIn,
        signUp,
        signIn,
        signInWithGoogle,
        signOut,
        forgotPassword,
        verifyOtp,
        resetPassword,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
