import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const {
    refreshSessionMock,
    useAuthMock,
    navigateMock,
    exchangeCodeForSessionMock,
    setSessionMock,
    getSessionMock,
} = vi.hoisted(() => ({
    refreshSessionMock: vi.fn(),
    useAuthMock: vi.fn(),
    navigateMock: vi.fn(),
    exchangeCodeForSessionMock: vi.fn(),
    setSessionMock: vi.fn(),
    getSessionMock: vi.fn(),
}));

vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => navigateMock,
    };
});

vi.mock('../context/AuthContext', () => ({
    useAuth: useAuthMock,
}));

vi.mock('../lib/supabaseClient', () => ({
    supabase: {
        auth: {
            exchangeCodeForSession: exchangeCodeForSessionMock,
            setSession: setSessionMock,
            getSession: getSessionMock,
        },
    },
}));

import AuthCallback from '../pages/AuthCallback';

describe('AuthCallback page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useAuthMock.mockReturnValue({
            refreshSession: refreshSessionMock,
        });
        exchangeCodeForSessionMock.mockResolvedValue({ error: null });
        setSessionMock.mockResolvedValue({ error: null });
        getSessionMock.mockResolvedValue({
            data: { session: { access_token: 'token' } },
            error: null,
        });
    });

    afterEach(() => {
        window.history.replaceState({}, '', '/');
    });

    it('handles OAuth callback and redirects on success', async () => {
        window.history.replaceState({}, '', '/auth/callback?code=oauth-code-123');

        render(
            <MemoryRouter>
                <AuthCallback />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(exchangeCodeForSessionMock).toHaveBeenCalledWith('oauth-code-123');
            expect(refreshSessionMock).toHaveBeenCalled();
            expect(navigateMock).toHaveBeenCalledWith('/dashboard', { replace: true });
        });
    });

    it('shows error state and does not redirect on callback errors', async () => {
        window.history.replaceState({}, '', '/auth/callback?error=Access+Denied');

        render(
            <MemoryRouter>
                <AuthCallback />
            </MemoryRouter>
        );

        expect(await screen.findByText('Access Denied')).toBeInTheDocument();
        expect(navigateMock).not.toHaveBeenCalled();
    });
});
