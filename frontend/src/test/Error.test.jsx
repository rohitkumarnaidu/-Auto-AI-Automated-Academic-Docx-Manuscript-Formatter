import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

import ErrorPage from '../pages/Error';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

describe('Error page', () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('renders current year dynamically in footer', () => {
        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <ErrorPage />
            </MemoryRouter>
        );

        const year = new Date().getFullYear();
        expect(screen.getByText(new RegExp(String(year)))).toBeInTheDocument();
    });

    it('wires Contact Support button handler', () => {
        const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null);

        render(
            <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
                <ErrorPage error={{ title: 'Processing Error', message: 'Custom failure' }} />
            </MemoryRouter>
        );

        fireEvent.click(screen.getByRole('button', { name: /contact support/i }));
        expect(openSpy).toHaveBeenCalledWith('mailto:support@scholarform.ai', '_self');
    });
});
