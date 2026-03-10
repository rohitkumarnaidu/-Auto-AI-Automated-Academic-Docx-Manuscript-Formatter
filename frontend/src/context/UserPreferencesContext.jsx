'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { supabase } from '../lib/supabaseClient';

const UserPreferencesContext = createContext();

export const UserPreferencesProvider = ({ children }) => {
    const { user, isLoggedIn } = useAuth();
    const [preferences, setPreferencesState] = useState({
        fastMode: false,
        statusUpdates: true,
        newsletter: false,
    });

    // 1. Load preferences from Supabase metadata
    useEffect(() => {
        if (isLoggedIn && user?.user_metadata?.preferences) {
            setPreferencesState((prev) => ({
                ...prev,
                ...user.user_metadata.preferences,
            }));
        } else if (!isLoggedIn) {
            // Load from localStorage for guest users
            const saved = localStorage.getItem('scholarform_preferences');
            if (saved) {
                try {
                    setPreferencesState(JSON.parse(saved));
                } catch (e) {
                    console.error("Failed to parse preferences from localStorage", e);
                }
            }
        }
    }, [isLoggedIn, user]);

    // 2. Save preferences to local storage
    useEffect(() => {
        localStorage.setItem('scholarform_preferences', JSON.stringify(preferences));
    }, [preferences]);

    const setPreference = (key, value) => {
        setPreferencesState((prev) => {
            const next = { ...prev, [key]: value };

            // Sync to Supabase if logged in
            if (isLoggedIn && supabase) {
                supabase.auth.updateUser({
                    data: {
                        preferences: next
                    }
                }).catch(err => console.error("Failed to sync preferences to Supabase:", err));
            }

            return next;
        });
    };

    return (
        <UserPreferencesContext.Provider value={{ preferences, setPreference }}>
            {children}
        </UserPreferencesContext.Provider>
    );
};

export const useUserPreferences = () => useContext(UserPreferencesContext);
