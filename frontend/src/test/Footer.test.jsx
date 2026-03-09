import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import Footer from '../components/Footer';

describe('Footer', () => {
    it('renders app footer with policy and support links', () => {
        render(<Footer variant="app" />);

        expect(screen.getByRole('link', { name: /terms of service/i })).toHaveAttribute('href', '/terms');
        expect(screen.getByRole('link', { name: /privacy policy/i })).toHaveAttribute('href', '/privacy');
        expect(screen.getByRole('link', { name: /support/i })).toHaveAttribute('href', 'mailto:support@scholarform.ai');
    });

    it('renders landing footer core navigation links', () => {
        render(<Footer variant="landing" />);

        expect(screen.getByRole('link', { name: /^templates$/i })).toHaveAttribute('href', '/templates');
        expect(screen.getByRole('link', { name: /^pricing$/i })).toHaveAttribute('href', '/#pricing');
        expect(screen.getByRole('link', { name: /privacy policy/i })).toHaveAttribute('href', '/privacy');
    });
});
