import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useAuthMock, useDocumentsMock, navigateMock } = vi.hoisted(() => ({
    useAuthMock: vi.fn(),
    useDocumentsMock: vi.fn(),
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

vi.mock('../services/api', () => ({
    useDocuments: useDocumentsMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

import Dashboard from '../pages/Dashboard';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

describe('Dashboard page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useAuthMock.mockReturnValue({
            user: { user_metadata: { full_name: 'Ada' } },
        });
        useDocumentsMock.mockReturnValue({
            data: {
                documents: [
                    { id: 'job-a', status: 'COMPLETED', timestamp: '2026-01-01T10:00:00Z', originalFileName: 'A.docx' },
                    { id: 'job-b', status: 'COMPLETED', timestamp: '2026-01-03T10:00:00Z', originalFileName: 'B.docx' },
                    { id: 'job-c', status: 'COMPLETED_WITH_WARNINGS', timestamp: '2026-01-02T10:00:00Z', originalFileName: 'C.docx' },
                    { id: 'job-d', status: 'PROCESSING', timestamp: '2026-01-04T10:00:00Z', originalFileName: 'D.docx' },
                ],
            },
            isLoading: false,
            isFetching: false,
            refetch: vi.fn(),
        });
    });

    it('shows dynamic ready badge count (not hardcoded)', () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Dashboard />
            </MemoryRouter>
        );

        expect(screen.getByText('2 Ready')).toBeInTheDocument();
        expect(screen.queryByText('3 Ready')).not.toBeInTheDocument();
    });

    it('uses job-id download URL in row links and latest completed download action', () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <Dashboard />
            </MemoryRouter>
        );

        const downloadLinks = screen.getAllByRole('link', { name: 'Download' });
        expect(downloadLinks.some((link) => link.getAttribute('href') === '/jobs/job-a/download')).toBe(true);

        fireEvent.click(screen.getByRole('button', { name: /download results/i }));
        expect(navigateMock).toHaveBeenCalledWith('/jobs/job-b/download');
    });
});
