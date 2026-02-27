import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useAuthMock, useThemeMock, useDocumentMock, navigateMock } = vi.hoisted(() => ({
    useAuthMock: vi.fn(),
    useThemeMock: vi.fn(),
    useDocumentMock: vi.fn(),
    navigateMock: vi.fn(),
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

vi.mock('../context/DocumentContext', () => ({
    useDocument: useDocumentMock,
}));

import Navbar from '../components/Navbar';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

describe('Navbar app variant', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
        useAuthMock.mockReturnValue({
            isLoggedIn: true,
            loading: false,
            signOut: vi.fn(),
            user: { user_metadata: {} },
        });
        useThemeMock.mockReturnValue({
            theme: 'light',
            toggleTheme: vi.fn(),
        });
        useDocumentMock.mockReturnValue({
            job: { id: 'job-1', status: 'PROCESSING' },
        });
    });

    it('notification bell is clickable and opens notification menu', () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Navbar variant="app" />
            </MemoryRouter>
        );

        fireEvent.click(screen.getAllByRole('button', { name: /notifications/i })[0]);
        expect(screen.getByText(/view all notifications/i)).toBeInTheDocument();
    });

    it('settings button routes to settings page', () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Navbar variant="app" />
            </MemoryRouter>
        );

        fireEvent.click(screen.getByTitle('Settings'));
        expect(navigateMock).toHaveBeenCalledWith('/settings');
    });

    it('shows processing badge on upload link while job is processing', () => {
        const { container } = render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Navbar variant="app" />
            </MemoryRouter>
        );

        expect(container.querySelector('.animate-ping')).toBeInTheDocument();
    });
});
