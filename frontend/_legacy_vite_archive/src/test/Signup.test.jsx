import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const { useAuthMock, signUpMock } = vi.hoisted(() => ({
    useAuthMock: vi.fn(),
    signUpMock: vi.fn(),
}));

vi.mock('../context/AuthContext', () => ({
    useAuth: useAuthMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

import Signup from '../pages/Signup';

const ROUTER_FUTURE_FLAGS = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

const renderSignup = () => render(
    <MemoryRouter future={ROUTER_FUTURE_FLAGS}>
        <Signup />
    </MemoryRouter>
);

const fillRequiredFields = () => {
    fireEvent.change(screen.getByPlaceholderText(/e\.g\. jane doe/i), {
        target: { value: 'Jane Doe' },
    });
    fireEvent.change(screen.getByPlaceholderText(/enter your email address/i), {
        target: { value: 'jane@example.edu' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
        target: { value: 'Password1' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password again'), {
        target: { value: 'Password1' },
    });
    fireEvent.click(screen.getByRole('checkbox'));
};

describe('Signup page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        signUpMock.mockResolvedValue({ data: { user: { id: 'u1' }, session: null }, error: null });
        useAuthMock.mockReturnValue({
            signUp: signUpMock,
            signInWithGoogle: vi.fn(),
        });
    });

    it('updates password requirement hint color when password becomes valid', () => {
        renderSignup();

        expect(screen.getByText('radio_button_unchecked')).toHaveClass('text-slate-400');

        fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
            target: { value: 'Valid123' },
        });

        expect(screen.getByText('check_circle')).toHaveClass('text-green-500');
    });

    it('displays signup errors from auth context', async () => {
        signUpMock.mockResolvedValue({ data: null, error: 'Email already registered' });
        renderSignup();

        fillRequiredFields();
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        expect(await screen.findByText('Email already registered')).toBeInTheDocument();
    });

    it('submits the form and calls signUp with expected payload', async () => {
        renderSignup();

        fillRequiredFields();
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(signUpMock).toHaveBeenCalledWith({
                full_name: 'Jane Doe',
                email: 'jane@example.edu',
                institution: '',
                password: 'Password1',
                terms_accepted: true,
            });
        });
    });
});
