import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Footer from '../components/Footer';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

const renderFooter = (variant) => render(
    <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
        <Footer variant={variant} />
    </MemoryRouter>
);

describe('Footer links', () => {
    it('contains no href="#" placeholder links', () => {
        const { container } = renderFooter('landing');
        const anchors = Array.from(container.querySelectorAll('a'));

        expect(anchors.length).toBeGreaterThan(0);
        anchors.forEach((anchor) => {
            expect(anchor.getAttribute('href')).not.toBe('#');
        });
    });

    it('ensures all link destinations are valid', () => {
        const { container } = renderFooter('app');
        const anchors = Array.from(container.querySelectorAll('a'));

        expect(anchors.length).toBeGreaterThan(0);
        anchors.forEach((anchor) => {
            const href = anchor.getAttribute('href');
            expect(href).toBeTruthy();
            expect(href.trim()).not.toBe('');
        });
    });
});
