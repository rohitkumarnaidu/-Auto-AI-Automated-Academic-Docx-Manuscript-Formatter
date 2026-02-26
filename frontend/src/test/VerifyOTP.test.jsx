import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

const { useAuthMock, verifyOtpMock, forgotPasswordMock } = vi.hoisted(() => ({
    useAuthMock: vi.fn(),
    verifyOtpMock: vi.fn(),
    forgotPasswordMock: vi.fn(),
}));

vi.mock('../context/AuthContext', () => ({
    useAuth: useAuthMock,
}));

vi.mock('../components/Navbar', () => ({
    default: () => <div data-testid="navbar" />,
}));

import VerifyOTP from '../pages/VerifyOTP';

const renderVerifyOtp = () => render(
    <MemoryRouter initialEntries={[{ pathname: '/verify-otp', state: { email: 'otp@example.com' } }]}>
        <Routes>
            <Route path="/verify-otp" element={<VerifyOTP />} />
            <Route path="/reset-password" element={<div>Reset Password</div>} />
        </Routes>
    </MemoryRouter>
);

describe('VerifyOTP page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        verifyOtpMock.mockResolvedValue({ data: { verified: true }, error: null });
        forgotPasswordMock.mockResolvedValue({ data: {}, error: null });
        useAuthMock.mockReturnValue({
            verifyOtp: verifyOtpMock,
            forgotPassword: forgotPasswordMock,
        });
    });

    it('sets loading state during OTP verification', () => {
        verifyOtpMock.mockImplementation(() => new Promise(() => {}));
        renderVerifyOtp();

        const inputs = screen.getAllByRole('textbox');
        ['1', '2', '3', '4', '5', '6'].forEach((digit, index) => {
            fireEvent.change(inputs[index], { target: { value: digit } });
        });
        fireEvent.click(screen.getByRole('button', { name: /verify code/i }));

        expect(verifyOtpMock).toHaveBeenCalledWith('otp@example.com', '123456');
        expect(screen.getByRole('button', { name: /verifying/i })).toBeDisabled();
    });

    it('moves focus to the next OTP field while typing', () => {
        renderVerifyOtp();

        const inputs = screen.getAllByRole('textbox');
        fireEvent.change(inputs[0], { target: { value: '7' } });

        expect(document.activeElement).toBe(inputs[1]);
    });

    it('handles paste across OTP inputs', () => {
        renderVerifyOtp();

        const inputs = screen.getAllByRole('textbox');
        fireEvent.change(inputs[0], { target: { value: '123456' } });

        expect(inputs.map((input) => input.value)).toEqual(['1', '2', '3', '4', '5', '6']);
        expect(document.activeElement).toBe(inputs[5]);
    });
});
