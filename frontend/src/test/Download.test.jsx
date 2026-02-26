import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

const { useDocumentMock, useAuthMock } = vi.hoisted(() => ({
    useDocumentMock: vi.fn(),
    useAuthMock: vi.fn(),
}));

vi.mock('../context/DocumentContext', () => ({
    useDocument: useDocumentMock,
}));

vi.mock('../context/AuthContext', () => ({
    useAuth: useAuthMock,
}));

vi.mock('../services/api', () => ({
    downloadExport: vi.fn(),
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

vi.mock('../components/ExportDialog', () => ({
    default: () => null,
}));

import Download from '../pages/Download';

describe('Download page actions', () => {
    const setJob = vi.fn();
    const completedJob = {
        id: 'job-123',
        status: 'COMPLETED',
        originalFileName: 'paper.docx',
        template: 'ieee',
        timestamp: new Date().toISOString(),
        flags: {},
    };

    beforeEach(() => {
        vi.clearAllMocks();
        sessionStorage.clear();
        useAuthMock.mockReturnValue({ isLoggedIn: false });
        useDocumentMock.mockReturnValue({ job: completedJob, setJob });
    });

    it('clears active job and navigates to upload when clicking Upload Another', () => {
        sessionStorage.setItem('scholarform_currentJob', JSON.stringify(completedJob));

        render(
            <MemoryRouter initialEntries={['/download']}>
                <Routes>
                    <Route path="/download" element={<Download />} />
                    <Route path="/upload" element={<div>Upload Page</div>} />
                </Routes>
            </MemoryRouter>
        );

        fireEvent.click(screen.getByText(/upload another/i));

        expect(setJob).toHaveBeenCalledWith(null);
        expect(sessionStorage.getItem('scholarform_currentJob')).toBeNull();
        expect(screen.getByText('Upload Page')).toBeInTheDocument();
    });
});
