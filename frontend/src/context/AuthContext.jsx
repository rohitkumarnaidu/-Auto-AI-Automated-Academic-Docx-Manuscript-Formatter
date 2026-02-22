import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        const initializeAuth = async () => {
            try {
                // 1. Get the initial session
                const { data: { session } } = await supabase.auth.getSession();

                // 2. Strict validation: Must have session AND access_token
                if (!session || !session.access_token) {
                    if (mounted) {
                        setUser(null);
                        setIsLoggedIn(false);
                        setLoading(false);
                    }
                    return;
                }

                // 3. Server-side verification (getUser is the source of truth)
                const { data: { user }, error } = await supabase.auth.getUser();

                if (error || !user) {
                    // Token invalid/expired/revoked -> aggressive cleanup
                    console.warn("Auth: Invalid session detected, signing out.");
                    await supabase.auth.signOut();
                    sessionStorage.clear();
                    sessionStorage.removeItem('scholarform_currentJob');
                    if (mounted) {
                        setUser(null);
                        setIsLoggedIn(false);
                    }
                } else {
                    // Valid session confirmed
                    if (mounted) {
                        setUser(user);
                        setIsLoggedIn(true);
                    }
                }
            } catch (err) {
                console.error("Auth: Initialization error", err);
                if (mounted) {
                    setUser(null);
                    setIsLoggedIn(false);
                }
            } finally {
                if (mounted) setLoading(false);
            }
        };

        initializeAuth();

        // 4. Listener for SUBSEQUENT changes (login/logout events)
        const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
            // Only update state if we are NOT in the middle of initial loading
            // (Actually, checking if mounted handles unmounts, but we just update reactive state)

            if (event === 'SIGNED_OUT') {
                setUser(null);
                setIsLoggedIn(false);
                sessionStorage.clear();
                sessionStorage.removeItem('scholarform_currentJob');
            } else if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
                // For sign-in/refresh, we trust the session but access_token must exist
                if (session?.user && session?.access_token) {
                    setUser(session.user);
                    setIsLoggedIn(true);
                } else {
                    setUser(null);
                    setIsLoggedIn(false);
                }
            }
        });

        return () => {
            mounted = false;
            subscription.unsubscribe();
        };
    }, []);

    const signUp = async (signupData) => {
        const { signup: apiSignup } = await import('../services/api');
        try {
            setLoading(true);
            const data = await apiSignup(signupData);

            if (data?.session) {
                const { error: sessionError } = await supabase.auth.setSession({
                    access_token: data.session.access_token,
                    refresh_token: data.session.refresh_token
                });

                if (sessionError) {
                    console.error("Auth: setSession failed during signup", sessionError);
                    // We don't fail the whole signup if session set fails, but we can't auto-login
                } else {
                    const userToSet = data.user || data.session.user;
                    if (userToSet) {
                        setUser(userToSet);
                        setIsLoggedIn(true);
                    }
                }
            }
            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message || String(error) };
        } finally {
            setLoading(false);
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
        try {
            await supabase.auth.signOut();
        } catch (error) {
            console.error("Error signing out:", error);
        } finally {
            // Force local cleanup regardless of server response
            setUser(null);
            setIsLoggedIn(false);
            sessionStorage.clear();
            sessionStorage.removeItem('scholarform_currentJob');
        }
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
