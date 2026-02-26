import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useJobFromUrlMock, getComparisonMock } = vi.hoisted(() => ({
    useJobFromUrlMock: vi.fn(),
    getComparisonMock: vi.fn(),
}));

vi.mock('../hooks/useJobFromUrl', () => ({
    default: useJobFromUrlMock,
}));

vi.mock('../services/api', () => ({
    getComparison: getComparisonMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

import Compare from '../pages/Compare';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

const renderCompare = () => render(
    <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
        <Compare />
    </MemoryRouter>
);

describe('Compare page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useJobFromUrlMock.mockReturnValue({
            job: {
                id: 'job-compare-1',
                originalFileName: 'paper.docx',
                template: 'ieee',
            },
            isLoading: false,
            error: '',
        });
        getComparisonMock.mockResolvedValue({
            original: { raw_text: 'Original content' },
            formatted: { structured_data: { sections: { BODY: ['Updated content'] } } },
            html_diff: '',
        });
    });

    it('uses backend html_diff output when available', async () => {
        getComparisonMock.mockResolvedValue({
            original: { raw_text: 'Original content' },
            formatted: { structured_data: { sections: { BODY: ['Updated content'] } } },
            html_diff: '<html><body><div>Backend Diff</div></body></html>',
        });

        renderCompare();

        const iframe = await screen.findByTitle('Authoritative backend diff');
        expect(iframe).toHaveAttribute('srcdoc');
        expect(iframe.getAttribute('srcdoc')).toContain('Backend Diff');
        expect(screen.getByText('Backend HTML diff active')).toBeInTheDocument();
    });

    it('shows accurate pause/resume highlights label', async () => {
        renderCompare();
        await waitFor(() => expect(getComparisonMock).toHaveBeenCalledTimes(1));

        fireEvent.click(screen.getByRole('button', { name: /pause highlights/i }));
        expect(screen.getByRole('button', { name: /resume highlights/i })).toBeInTheDocument();
    });
});
