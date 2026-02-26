import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { getBuiltinTemplatesMock, navigateMock } = vi.hoisted(() => ({
    getBuiltinTemplatesMock: vi.fn(),
    navigateMock: vi.fn(),
}));

vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => navigateMock,
    };
});

vi.mock('../services/api', () => ({
    getBuiltinTemplates: getBuiltinTemplatesMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

vi.mock('../components/Footer', () => ({
    default: () => <div data-testid="footer" />,
}));

import Templates from '../pages/Templates';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

const renderTemplates = () => render(
    <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
        <Templates />
    </MemoryRouter>
);

describe('Templates page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        getBuiltinTemplatesMock.mockResolvedValue([]);
    });

    it('updates search input on change', async () => {
        renderTemplates();
        await waitFor(() => expect(getBuiltinTemplatesMock).toHaveBeenCalledTimes(1));

        const searchInput = screen.getByPlaceholderText(/search for journal/i);
        fireEvent.change(searchInput, { target: { value: 'Nature' } });

        expect(searchInput).toHaveValue('Nature');
    });

    it('toggles filter chip active state', async () => {
        renderTemplates();
        await waitFor(() => expect(getBuiltinTemplatesMock).toHaveBeenCalledTimes(1));

        const engineeringChip = screen.getByRole('button', { name: /engineering/i });
        fireEvent.click(engineeringChip);

        expect(engineeringChip.className).toContain('bg-primary');
    });

    it('calls navigate when selecting a template', async () => {
        renderTemplates();

        const selectButtons = await screen.findAllByRole('button', { name: /select template/i });
        fireEvent.click(selectButtons[0]);

        expect(navigateMock).toHaveBeenCalledWith('/upload', {
            state: { preselectedTemplate: 'ieee' },
        });
    });
});
