import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useAuthMock, useThemeMock, navigateMock, updateUserMock } = vi.hoisted(() => ({
    useAuthMock: vi.fn(),
    useThemeMock: vi.fn(),
    navigateMock: vi.fn(),
    updateUserMock: vi.fn(),
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

vi.mock('../context/ThemeContext', () => ({
    useTheme: useThemeMock,
}));

vi.mock('../lib/supabaseClient', () => ({
    supabase: {
        auth: {
            updateUser: updateUserMock,
        },
        storage: {
            from: () => ({
                upload: vi.fn(),
                getPublicUrl: vi.fn(() => ({ data: { publicUrl: 'https://cdn.example/avatar.png' } })),
            }),
        },
    },
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

import Profile from '../pages/Profile';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

describe('Profile page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        updateUserMock.mockResolvedValue({ error: null });
        useThemeMock.mockReturnValue({ theme: 'light', toggleTheme: vi.fn() });
        useAuthMock.mockReturnValue({
            user: {
                id: 'user-12345678',
                email: 'researcher@example.edu',
                created_at: '2026-01-01T00:00:00Z',
                user_metadata: {
                    full_name: 'Ada Lovelace',
                    institution: 'Analytical University',
                },
            },
            signOut: vi.fn(),
            refreshSession: vi.fn(),
            forgotPassword: vi.fn(),
        });
    });

    it('displays profile data', () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Profile />
            </MemoryRouter>
        );

        expect(screen.getByText('Ada Lovelace')).toBeInTheDocument();
        expect(screen.getByText('researcher@example.edu')).toBeInTheDocument();
        expect(screen.getByText('Analytical University')).toBeInTheDocument();
    });

    it('wires action buttons with working handlers', async () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Profile />
            </MemoryRouter>
        );

        fireEvent.click(screen.getByRole('button', { name: /verify institution/i }));
        await waitFor(() => {
            expect(updateUserMock).toHaveBeenCalledWith({
                data: { institution_verified: false, institution_verify_requested: true },
            });
        });

        fireEvent.click(screen.getByRole('button', { name: /change password/i }));
        expect(screen.getByPlaceholderText('New Password (min 8 chars)')).toBeInTheDocument();

        fireEvent.click(screen.getByRole('button', { name: /manage subscription/i }));
        expect(navigateMock).toHaveBeenCalledWith('/settings');

        fireEvent.click(screen.getByRole('button', { name: /edit profile/i }));
        expect(screen.getByRole('button', { name: /save changes/i })).toBeInTheDocument();
    });
});
