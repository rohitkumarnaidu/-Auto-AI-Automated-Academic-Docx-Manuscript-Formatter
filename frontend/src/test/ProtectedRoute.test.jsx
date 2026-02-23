import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import React from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAuth } from '../context/AuthContext';

// Mock useAuth hook
vi.mock('../context/AuthContext', () => ({
    useAuth: vi.fn(),
}));

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

describe('ProtectedRoute', () => {
    it('renders children when user is logged in', () => {
        useAuth.mockReturnValue({ isLoggedIn: true });

        render(
            <MemoryRouter initialEntries={['/protected']} future={ROUTER_FUTURE_FLAGS}>
                <Routes>
                    <Route
                        path="/protected"
                        element={
                            <ProtectedRoute>
                                <div>Protected Content</div>
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('redirects to login when user is not logged in', () => {
        useAuth.mockReturnValue({ isLoggedIn: false });

        render(
            <MemoryRouter initialEntries={['/protected']} future={ROUTER_FUTURE_FLAGS}>
                <Routes>
                    <Route
                        path="/protected"
                        element={
                            <ProtectedRoute>
                                <div>Protected Content</div>
                            </ProtectedRoute>
                        }
                    />
                    <Route path="/login" element={<div>Login Page</div>} />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
        expect(screen.getByText('Login Page')).toBeInTheDocument();
    });
});
