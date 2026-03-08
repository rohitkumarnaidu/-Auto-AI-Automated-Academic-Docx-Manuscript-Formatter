'use client';
import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { supabase } from '../lib/supabaseClient';
import {
    signup as apiSignup,
    login as apiLogin,
    forgotPassword as apiForgotPassword,
    verifyOtp as apiVerifyOtp,
    resetPassword as apiResetPassword,
} from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);

    // Guard: prevents onAuthStateChange('SIGNED_OUT') from clearing state
    // while signIn/signUp is in progress (setSession fires SIGNED_OUT before SIGNED_IN)
    const signingInRef = useRef(false);

    const sanitizeRedirectPath = (path) => {
        if (typeof path !== 'string') return '/dashboard';
        if (!path.startsWith('/') || path.startsWith('//')) return '/dashboard';
        return path;
    };

    useEffect(() => {
        let mounted = true;

        const initializeAuth = async () => {
            if (!supabase) {
                if (mounted) {
                    setUser(null);
                    setIsLoggedIn(false);
                    setLoading(false);
                }
                return;
            }
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
        let subscription;
        if (supabase) {
            const { data } = supabase.auth.onAuthStateChange(async (event, session) => {
                console.log('[Auth] onAuthStateChange:', event, { hasSession: !!session, signingIn: signingInRef.current });

                if (event === 'SIGNED_OUT') {
                    // During signIn/signUp, setSession() can fire SIGNED_OUT before SIGNED_IN.
                    // Skip this event to prevent clearing user state mid-login.
                    if (signingInRef.current) {
                        console.log('[Auth] Ignoring SIGNED_OUT during active sign-in');
                        return;
                    }
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
            subscription = data.subscription;
        }

        return () => {
            mounted = false;
            if (subscription) subscription.unsubscribe();
        };
    }, []);

    const signUp = async (signupData) => {
        try {
            setLoading(true);
            signingInRef.current = true;
            const data = await apiSignup(signupData);

            if (data?.session && supabase) {
                const { error: sessionError } = await supabase.auth.setSession({
                    access_token: data.session.access_token,
                    refresh_token: data.session.refresh_token
                });

                if (sessionError) {
                    console.error("Auth: setSession failed during signup", sessionError);
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
            signingInRef.current = false;
            setLoading(false);
        }
    };

    const signIn = async (email, password) => {
        try {
            signingInRef.current = true;
            const data = await apiLogin({ email, password });

            if (data?.session && supabase) {
                const { error: sessionError } = await supabase.auth.setSession({
                    access_token: data.session.access_token,
                    refresh_token: data.session.refresh_token
                });

                if (!sessionError) {
                    const userToSet = data.user || data.session.user;
                    if (userToSet) {
                        setUser(userToSet);
                        setIsLoggedIn(true);
                    }
                }
            }

            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        } finally {
            // Clear the guard AFTER a short delay so any pending
            // SIGNED_OUT events from setSession() are safely ignored
            setTimeout(() => { signingInRef.current = false; }, 1000);
        }
    };

    const signInWithGoogle = async (redirectPath = '/dashboard') => {
        if (!supabase) throw new Error('Supabase client is not initialized');
        const safeRedirectPath = sanitizeRedirectPath(redirectPath);
        return await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(safeRedirectPath)}`
            }
        });
    };

    const signOut = async ({ redirectToLogin = false } = {}) => {
        try {
            if (supabase) await supabase.auth.signOut();
        } catch (error) {
            console.error("Error signing out:", error);
        } finally {
            // Force local cleanup regardless of server response
            setUser(null);
            setIsLoggedIn(false);
            sessionStorage.clear();
            sessionStorage.removeItem('scholarform_currentJob');

            if (redirectToLogin && typeof window !== 'undefined') {
                window.location.replace('/login');
            }
        }
    };

    const refreshSession = async () => {
        if (!supabase) return;
        const { data: { user }, error } = await supabase.auth.getUser();
        if (user && !error) {
            setUser(user);
            setIsLoggedIn(true);
        }
    };

    const forgotPassword = async (email) => {
        try {
            const data = await apiForgotPassword({ email });
            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        }
    };

    const verifyOtp = async (email, otp) => {
        try {
            const data = await apiVerifyOtp({ email, otp });
            return { data, error: null };
        } catch (error) {
            return { data: null, error: error.message };
        }
    };

    const resetPassword = async (email, otp, newPassword) => {
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
        refreshSession,
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
