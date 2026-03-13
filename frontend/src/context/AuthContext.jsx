'use client';
import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { supabase } from '../lib/supabaseClient';
import {
    signup as apiSignup,
    login as apiLogin,
    forgotPassword as apiForgotPassword,
    verifyOtp as apiVerifyOtp,
    resetPassword as apiResetPassword,
} from '@/src/services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);

    // Guard: prevents onAuthStateChange('SIGNED_OUT') from clearing state
    // while signIn/signUp is in progress (setSession fires SIGNED_OUT before SIGNED_IN)
    const signingInRef = useRef(false);

    const clearAppSessionStorage = () => {
        [
            'scholarform_currentJob',
            'scholarform_job',
            'scholarform_active_job',
        ].forEach((key) => sessionStorage.removeItem(key));
    };

    const debugAuthLog = (...args) => {
        if (process.env.NODE_ENV !== 'production') {
            console.log(...args);
        }
    };

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
                // Step 1: getSession() — fast local check. The JWT is cryptographically
                // signed, so access_token can be trusted even from localStorage.
                const { data: { session }, error } = await supabase.auth.getSession();

                if (error) {
                    debugAuthLog('Auth: getSession error', error);
                }

                if (session?.access_token && session?.user) {
                    // Set auth state immediately — don't block on getUser() network call.
                    // This ensures AuthGuard sees isLoggedIn=true before setLoading(false),
                    // preventing the redirect loop.
                    if (mounted) {
                        setUser(session.user);
                        setIsLoggedIn(true);
                    }

                    // Call getUser() in background to upgrade to server-verified user object.
                    // This silences the Supabase "session.user is insecure" warning and
                    // gives us authoritative user data (e.g. for admin role checks)
                    // without delaying the auth state resolution.
                    supabase.auth.getUser().then(({ data: { user: serverUser } }) => {
                        if (serverUser && mounted) {
                            setUser(serverUser);
                        }
                    }).catch(() => {
                        // Non-fatal — session.user from JWT is already in state
                    });
                } else {
                    if (mounted) {
                        setUser(null);
                        setIsLoggedIn(false);
                    }
                }
            } catch (err) {
                console.error('Auth: Initialization error', err);
                if (mounted) {
                    setUser(null);
                    setIsLoggedIn(false);
                }
            } finally {
                if (mounted) setLoading(false);
            }
        };

        initializeAuth();

        // Listener for SUBSEQUENT auth changes (login/logout/token refresh events)
        let subscription;
        if (supabase) {
            const { data } = supabase.auth.onAuthStateChange((event, session) => {
                debugAuthLog('[Auth] onAuthStateChange:', event, { hasSession: !!session, signingIn: signingInRef.current });

                if (event === 'SIGNED_OUT') {
                    // During signIn/signUp, setSession() can fire SIGNED_OUT before SIGNED_IN.
                    // Skip this event to prevent clearing user state mid-login.
                    if (signingInRef.current) {
                        debugAuthLog('[Auth] Ignoring SIGNED_OUT during active sign-in');
                        return;
                    }
                    setUser(null);
                    setIsLoggedIn(false);
                    clearAppSessionStorage();
                } else if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
                    // Keep this synchronous — no async getUser() here.
                    // Async getUser() inside onAuthStateChange creates a race where
                    // signingInRef.current is cleared before the promise resolves,
                    // allowing stale SIGNED_OUT events to slip through and cause a redirect loop.
                    if (session?.user && session?.access_token) {
                        setUser(session.user);
                        setIsLoggedIn(true);
                    } else {
                        setUser(null);
                        setIsLoggedIn(false);
                    }
                    signingInRef.current = false;
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
                    refresh_token: data.session.refresh_token,
                });

                if (sessionError) {
                    console.error('Auth: setSession failed during signup', sessionError);
                    signingInRef.current = false;
                } else {
                    const userToSet = data.user || data.session.user;
                    if (userToSet) {
                        setUser(userToSet);
                        setIsLoggedIn(true);
                    }
                }
            } else {
                signingInRef.current = false;
            }
            return { data, error: null };
        } catch (error) {
            signingInRef.current = false;
            return { data: null, error: error.message || String(error) };
        } finally {
            setLoading(false);
        }
    };

    const signIn = async (email, password) => {
        try {
            signingInRef.current = true;
            const data = await apiLogin({ email, password });

            if (!data?.session || !supabase) {
                signingInRef.current = false;
                return { data: data ?? null, error: null };
            }

            const { error: sessionError } = await supabase.auth.setSession({
                access_token: data.session.access_token,
                refresh_token: data.session.refresh_token,
            });

            if (sessionError) {
                console.error('Auth: setSession failed during signIn', sessionError);
                signingInRef.current = false;
                return { data: null, error: sessionError.message };
            }

            // Immediately update React state so AuthGuard sees isLoggedIn=true
            // before any navigation occurs — don't wait for onAuthStateChange.
            const userToSet = data.user || data.session.user;
            if (userToSet) {
                setUser(userToSet);
                setIsLoggedIn(true);
            }
            // signingInRef is cleared by onAuthStateChange SIGNED_IN event

            return { data, error: null };
        } catch (error) {
            signingInRef.current = false;
            return { data: null, error: error.message };
        }
    };

    const signInWithGoogle = async (redirectPath = '/dashboard') => {
        if (!supabase) throw new Error('Supabase client is not initialized');
        const safeRedirectPath = sanitizeRedirectPath(redirectPath);
        return await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(safeRedirectPath)}`,
            },
        });
    };

    const signOut = async ({ redirectToLogin = false } = {}) => {
        try {
            if (supabase) await supabase.auth.signOut();
        } catch (error) {
            console.error('Error signing out:', error);
        } finally {
            // Force local cleanup regardless of server response
            setUser(null);
            setIsLoggedIn(false);
            clearAppSessionStorage();

            if (redirectToLogin && typeof window !== 'undefined') {
                window.location.replace('/login');
            }
        }
    };

    const refreshSession = async () => {
        if (!supabase) return;
        const { data: { user: refreshedUser }, error } = await supabase.auth.getUser();
        if (refreshedUser && !error) {
            setUser(refreshedUser);
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
        loading,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
