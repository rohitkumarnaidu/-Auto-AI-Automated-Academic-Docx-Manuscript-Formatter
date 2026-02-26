import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useDocumentMock, getPreviewMock } = vi.hoisted(() => ({
    useDocumentMock: vi.fn(),
    getPreviewMock: vi.fn(),
}));

vi.mock('../context/DocumentContext', () => ({
    useDocument: useDocumentMock,
}));

vi.mock('../services/api', () => ({
    submitEdit: vi.fn(),
    getPreview: getPreviewMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

import Edit from '../pages/Edit';

describe('Edit page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useDocumentMock.mockReturnValue({
            job: {
                id: 'job-edit-1',
                status: 'COMPLETED',
                originalFileName: 'custom-manuscript.docx',
                processedText: 'This content came from job data.',
                result: {
                    errors: [{ issue: 'Missing Title', message: 'Title section is required.' }],
                    warnings: [{ message: 'Use consistent heading styles.' }],
                },
            },
            setJob: vi.fn(),
        });
        getPreviewMock.mockResolvedValue({});
    });

    it('loads editable content from job data', async () => {
        render(
            <MemoryRouter>
                <Edit />
            </MemoryRouter>
        );

        const editor = screen.getByPlaceholderText(/start typing your manuscript/i);
        expect(editor).toHaveValue('This content came from job data.');
    });

    it('renders validation sections from job result', () => {
        render(
            <MemoryRouter>
                <Edit />
            </MemoryRouter>
        );

        expect(screen.getByText('Missing Title')).toBeInTheDocument();
        expect(screen.getByText('Title section is required.')).toBeInTheDocument();
        expect(screen.getByText('Use consistent heading styles.')).toBeInTheDocument();
    });
});
