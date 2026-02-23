import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useAuthMock, useDocumentMock, useDocumentStatusMock } = vi.hoisted(() => ({
    useAuthMock: vi.fn(),
    useDocumentMock: vi.fn(),
    useDocumentStatusMock: vi.fn(),
}));

vi.mock('../context/AuthContext', () => ({
    useAuth: useAuthMock,
}));

vi.mock('../context/DocumentContext', () => ({
    useDocument: useDocumentMock,
}));

vi.mock('../services/api', () => ({
    CHUNK_UPLOAD_THRESHOLD_BYTES: 10 * 1024 * 1024,
    uploadChunked: vi.fn(),
    uploadDocumentWithProgress: vi.fn(),
    useDocumentStatus: useDocumentStatusMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

vi.mock('../components/upload/CategoryTabs', () => ({
    default: () => <div data-testid="category-tabs" />,
}));

vi.mock('../components/upload/TemplateSelector', () => ({
    default: () => <div data-testid="template-selector" />,
}));

vi.mock('../components/upload/FormattingOptions', () => ({
    default: () => <div data-testid="formatting-options" />,
}));

vi.mock('../components/upload/ProcessingStepper', () => ({
    default: () => <div data-testid="processing-stepper" />,
}));

import Upload from '../pages/Upload';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

describe('Upload page validation', () => {
    beforeEach(() => {
        useAuthMock.mockReturnValue({ isLoggedIn: false });
        useDocumentMock.mockReturnValue({ job: null, setJob: vi.fn() });
        useDocumentStatusMock.mockReturnValue({ data: null, error: null });
    });

    const renderUpload = () => render(
        <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
            <Upload />
        </MemoryRouter>
    );

    it('sets file input accept filter to supported formats', () => {
        const { container } = renderUpload();
        const input = container.querySelector('input[type="file"]');

        expect(input).toBeInTheDocument();
        expect(input).toHaveAttribute('accept', '.docx,.pdf,.tex,.txt,.html,.htm,.md,.markdown,.doc');
    });

    it('shows validation error for unsupported file formats', () => {
        const { container } = renderUpload();
        const input = container.querySelector('input[type="file"]');
        const invalidFile = new File(['bad'], 'malware.exe', { type: 'application/octet-stream' });

        fireEvent.change(input, { target: { files: [invalidFile] } });

        expect(screen.getByText(/unsupported file format/i)).toBeInTheDocument();
    });

    it('accepts valid file formats and displays selected file', () => {
        const { container } = renderUpload();
        const input = container.querySelector('input[type="file"]');
        const validFile = new File(['hello'], 'paper.docx', {
            type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        });

        fireEvent.change(input, { target: { files: [validFile] } });

        expect(screen.getByText(/file: paper\.docx/i)).toBeInTheDocument();
        expect(screen.queryByText(/unsupported file format/i)).not.toBeInTheDocument();
    });
});
