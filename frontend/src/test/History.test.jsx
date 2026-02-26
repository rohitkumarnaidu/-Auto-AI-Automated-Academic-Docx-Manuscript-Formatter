import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useDocumentMock, useDocumentsMock, deleteDocumentMock, refetchMock } = vi.hoisted(() => ({
    useDocumentMock: vi.fn(),
    useDocumentsMock: vi.fn(),
    deleteDocumentMock: vi.fn(),
    refetchMock: vi.fn(),
}));

vi.mock('../context/DocumentContext', () => ({
    useDocument: useDocumentMock,
}));

vi.mock('../services/api', () => ({
    useDocuments: useDocumentsMock,
    deleteDocument: deleteDocumentMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

import History from '../pages/History';

describe('History page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        deleteDocumentMock.mockResolvedValue({ success: true });
        refetchMock.mockResolvedValue({});
        useDocumentMock.mockReturnValue({
            setJob: vi.fn(),
        });
        useDocumentsMock.mockReturnValue({
            data: {
                documents: [
                    { id: 'doc-1', filename: 'PrimaryName.docx', template: 'ieee', status: 'COMPLETED', timestamp: '2026-01-01T10:00:00Z', result: {} },
                    { id: 'doc-2', original_file_name: 'SnakeName.docx', template: 'ieee', status: 'COMPLETED', timestamp: '2026-01-02T10:00:00Z', result: {} },
                    { id: 'doc-3', originalFileName: 'CamelName.docx', template: 'ieee', status: 'COMPLETED', timestamp: '2026-01-03T10:00:00Z', result: {} },
                    { id: 'doc-4', template: 'ieee', status: 'FAILED', timestamp: '2026-01-04T10:00:00Z', result: {} },
                ],
            },
            isLoading: false,
            refetch: refetchMock,
        });
    });

    it('shows delete controls and calls delete API after confirmation', async () => {
        render(
            <MemoryRouter>
                <History />
            </MemoryRouter>
        );

        fireEvent.click(screen.getAllByTitle('Delete')[0]);
        fireEvent.click(screen.getByRole('button', { name: /^Delete$/ }));

        await waitFor(() => {
            expect(deleteDocumentMock).toHaveBeenCalledWith('doc-4');
        });
    });

    it('uses filename fallback chain for manuscript display', () => {
        render(
            <MemoryRouter>
                <History />
            </MemoryRouter>
        );

        expect(screen.getByText('PrimaryName.docx')).toBeInTheDocument();
        expect(screen.getByText('SnakeName.docx')).toBeInTheDocument();
        expect(screen.getByText('CamelName.docx')).toBeInTheDocument();
        expect(screen.getByText('Untitled')).toBeInTheDocument();
    });
});
