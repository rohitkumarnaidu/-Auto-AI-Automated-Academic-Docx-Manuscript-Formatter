import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import DocumentGenerator from '../pages/DocumentGenerator';

// ─── Mocks ────────────────────────────────────────────────────────────────────

// Mock fetch globally
global.fetch = vi.fn();

// Mock usePageTitle hook
vi.mock('../hooks/usePageTitle', () => ({ default: () => { } }));

// ─── Helpers ──────────────────────────────────────────────────────────────────

const renderPage = () =>
    render(
        <MemoryRouter>
            <DocumentGenerator />
        </MemoryRouter>
    );

// ─── Step 1: Document Type Selector ──────────────────────────────────────────

describe('DocumentGenerator — Step 1: Document Type', () => {
    test('renders all 5 document type cards', () => {
        renderPage();
        expect(screen.getByText('Academic Paper')).toBeInTheDocument();
        expect(screen.getByText('Resume / CV')).toBeInTheDocument();
        expect(screen.getByText('Portfolio')).toBeInTheDocument();
        expect(screen.getByText('Technical Report')).toBeInTheDocument();
        expect(screen.getByText('Thesis Chapter')).toBeInTheDocument();
    });

    test('renders page heading', () => {
        renderPage();
        expect(screen.getByText('Choose Document Type')).toBeInTheDocument();
    });

    test('Next button is disabled before selecting a doc type', () => {
        renderPage();
        const nextBtn = screen.getByRole('button', { name: /continue/i });
        expect(nextBtn).toBeDisabled();
    });

    test('Next button becomes enabled after selecting a doc type', () => {
        renderPage();
        fireEvent.click(screen.getById ? document.getElementById('doc-type-academic_paper') : screen.getByText('Academic Paper'));
        const nextBtn = screen.getByRole('button', { name: /continue/i });
        expect(nextBtn).not.toBeDisabled();
    });

    test('clicking Academic Paper advances to Step 2', async () => {
        renderPage();
        const card = document.querySelector('#doc-type-academic_paper') || screen.getByText('Academic Paper').closest('button');
        fireEvent.click(card);
        const nextBtn = screen.getByRole('button', { name: /continue/i });
        fireEvent.click(nextBtn);
        await waitFor(() => {
            expect(screen.getByText('Choose a Template')).toBeInTheDocument();
        });
    });
});

// ─── Step 2: Template Picker ──────────────────────────────────────────────────

describe('DocumentGenerator — Step 2: Template Picker', () => {
    const goToStep2 = () => {
        renderPage();
        const card = document.querySelector('#doc-type-academic_paper') || screen.getByText('Academic Paper').closest('button');
        fireEvent.click(card);
        fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    };

    test('shows all 17 template cards', async () => {
        goToStep2();
        await waitFor(() => {
            expect(screen.getByText('IEEE')).toBeInTheDocument();
            expect(screen.getByText('APA (7th)')).toBeInTheDocument();
            expect(screen.getByText('Springer')).toBeInTheDocument();
            expect(screen.getByText('Nature')).toBeInTheDocument();
            expect(screen.getByText('Vancouver')).toBeInTheDocument();
        });
    });

    test('template search filter works', async () => {
        goToStep2();
        await waitFor(() => expect(screen.getByPlaceholderText('Search templates...')).toBeInTheDocument());
        fireEvent.change(screen.getByPlaceholderText('Search templates...'), { target: { value: 'spring' } });
        expect(screen.getByText('Springer')).toBeInTheDocument();
    });

    test('Next button disabled before template selection', async () => {
        goToStep2();
        await waitFor(() => {
            const btn = screen.getByRole('button', { name: /continue/i });
            expect(btn).toBeDisabled();
        });
    });
});

// ─── Step 3: Metadata Form ────────────────────────────────────────────────────

describe('DocumentGenerator — Step 3: Metadata Form', () => {
    const goToStep3 = async () => {
        renderPage();
        // Step 1: select doc type
        const cardEl = document.querySelector('#doc-type-academic_paper') || screen.getByText('Academic Paper').closest('button');
        fireEvent.click(cardEl);
        fireEvent.click(screen.getByRole('button', { name: /continue/i }));
        // Step 2: select template
        await waitFor(() => expect(screen.getByText('Choose a Template')).toBeInTheDocument());
        const ieeeCard = document.querySelector('#template-ieee') || screen.getByText('IEEE').closest('button');
        fireEvent.click(ieeeCard);
        fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    };

    test('shows title input for academic paper', async () => {
        await goToStep3();
        await waitFor(() => {
            expect(screen.getByText('Document Details')).toBeInTheDocument();
        });
    });

    test('Generate button is disabled without title', async () => {
        await goToStep3();
        await waitFor(() => {
            const btn = document.getElementById('btn-generate');
            expect(btn).toBeTruthy();
            expect(btn.disabled).toBe(true);
        });
    });

    test('Generate button enables after filling title', async () => {
        await goToStep3();
        await waitFor(() => expect(document.getElementById('meta-title')).toBeTruthy());
        fireEvent.change(document.getElementById('meta-title'), {
            target: { value: 'My Research Paper' },
        });
        await waitFor(() => {
            expect(document.getElementById('btn-generate').disabled).toBe(false);
        });
    });
});

// ─── Back Button ──────────────────────────────────────────────────────────────

describe('DocumentGenerator — Back navigation', () => {
    test('Back button returns from step 2 to step 1', async () => {
        renderPage();
        const card = document.querySelector('#doc-type-academic_paper') || screen.getByText('Academic Paper').closest('button');
        fireEvent.click(card);
        fireEvent.click(screen.getByRole('button', { name: /continue/i }));
        await waitFor(() => expect(screen.getByText('Choose a Template')).toBeInTheDocument());
        fireEvent.click(screen.getByRole('button', { name: /back/i }));
        await waitFor(() => expect(screen.getByText('Choose Document Type')).toBeInTheDocument());
    });
});

// ─── Step Indicator ────────────────────────────────────────────────────────────

describe('DocumentGenerator — Step indicator', () => {
    test('shows 4-step indicator', () => {
        renderPage();
        expect(screen.getByText('Document Type')).toBeInTheDocument();
        expect(screen.getByText('Template')).toBeInTheDocument();
        expect(screen.getByText('Details')).toBeInTheDocument();
        expect(screen.getByText('Generate')).toBeInTheDocument();
    });
});
