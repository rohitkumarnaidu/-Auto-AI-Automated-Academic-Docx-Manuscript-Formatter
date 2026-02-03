import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [user, setUser] = useState(null);

    // Persist auth state for development convenience
    useEffect(() => {
        const savedAuth = localStorage.getItem('isLoggedIn');
        const savedUser = localStorage.getItem('user');
        if (savedAuth === 'true') {
            setIsLoggedIn(true);
            setUser(JSON.parse(savedUser));
        }
    }, []);

    const login = (userData) => {
        setIsLoggedIn(true);
        setUser(userData || { name: 'Researcher', email: 'researcher@example.com' });
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('user', JSON.stringify(userData || { name: 'Researcher', email: 'researcher@example.com' }));
    };

    const logout = () => {
        setIsLoggedIn(false);
        setUser(null);
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('user');
    };

    return (
        <AuthContext.Provider value={{ isLoggedIn, user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
