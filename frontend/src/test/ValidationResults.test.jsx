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
    getPreview: getPreviewMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

vi.mock('../components/ValidationCard', () => ({
    default: ({ title, description }) => (
        <div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    ),
}));

import ValidationResults from '../pages/ValidationResults';

describe('ValidationResults page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('loads validation data from preview when job.result is missing', async () => {
        const setJob = vi.fn();
        useDocumentMock.mockReturnValue({
            job: {
                id: 'job-1',
                status: 'COMPLETED',
                originalFileName: 'sample.docx',
                template: 'ieee',
                result: null,
                flags: {},
            },
            setJob,
        });

        getPreviewMock.mockResolvedValue({
            validation_results: {
                errors: [{ issue: 'Missing Abstract', message: 'Abstract section is required.' }],
                warnings: [],
                advisories: [],
            },
        });

        render(
            <MemoryRouter>
                <ValidationResults />
            </MemoryRouter>
        );

        expect(getPreviewMock).toHaveBeenCalledWith('job-1', { debounceMs: 0 });
        expect(await screen.findByText('Missing Abstract')).toBeInTheDocument();
        expect(screen.getByText('Abstract section is required.')).toBeInTheDocument();
        expect(setJob).toHaveBeenCalled();
    });
});
