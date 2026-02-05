import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';

export default function VerifyOTP() {
    const navigate = useNavigate();
    const location = useLocation();
    const { verifyOtp, forgotPassword } = useAuth();
    const email = location.state?.email || '';

    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [resendLoading, setResendLoading] = useState(false);
    const inputRefs = [useRef(), useRef(), useRef(), useRef(), useRef(), useRef()];

    useEffect(() => {
        if (!email) {
            navigate('/forgot-password');
        }
    }, [email, navigate]);

    const handleChange = (index, value) => {
        if (value.length > 1) {
            // Handle paste
            const pasteData = value.slice(0, 6).split('');
            const newOtp = [...otp];
            pasteData.forEach((char, i) => {
                if (index + i < 6) newOtp[index + i] = char;
            });
            setOtp(newOtp);
            // Move focus to last filled or last box
            const lastIndex = Math.min(index + pasteData.length - 1, 5);
            inputRefs[lastIndex].current.focus();
            return;
        }

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        // Move to next field if value is entered
        if (value && index < 5) {
            inputRefs[index + 1].current.focus();
        }
    };

    const handleKeyDown = (index, e) => {
        // Move to previous field on backspace if empty
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs[index - 1].current.focus();
        }
    };

    const handleVerify = async (e) => {
        e.preventDefault();
        setError('');
        const otpString = otp.join('');

        if (otpString.length < 6) {
            setError('Please enter all 6 digits.');
            return;
        }

        setLoading(true);
        try {
            await verifyOtp(email, otpString);
            navigate('/reset-password', { state: { email, otp: otpString } });
        } catch (err) {
            setError(err.message || 'Verification failed. Please check the code.');
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setResendLoading(true);
        setError('');
        try {
            await forgotPassword(email);
            // Could show a "Code resent" toast here
        } catch (err) {
            setError('Failed to resend code.');
        } finally {
            setResendLoading(false);
        }
    };

    return (
        <div className="bg-background-light dark:bg-background-dark min-h-screen flex flex-col font-display transition-colors duration-300">
            <Navbar variant="auth" />

            <main className="flex-1 flex items-center justify-center p-4">
                <div className="layout-content-container flex flex-col w-full max-w-[480px] bg-white dark:bg-slate-900 shadow-xl rounded-xl p-8 border border-slate-100 dark:border-slate-800">
                    <div className="flex flex-col items-center">
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                            <span className="material-symbols-outlined !text-3xl">mark_email_read</span>
                        </div>
                        <h1 className="text-[#0d131b] dark:text-white tracking-tight text-[28px] md:text-[32px] font-bold leading-tight text-center pb-2">
                            Verify your email
                        </h1>
                        <p className="text-slate-600 dark:text-slate-400 text-base font-normal leading-normal pb-6 text-center">
                            Enter the 6-digit verification code sent to <span className="font-semibold text-primary">{email}</span>
                        </p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleVerify}>
                        <div className="flex justify-center py-3">
                            <fieldset className="relative flex gap-3 md:gap-4">
                                {otp.map((digit, i) => (
                                    <input
                                        key={i}
                                        ref={inputRefs[i]}
                                        className="flex h-14 w-11 md:w-12 text-center [appearance:textfield] focus:outline-0 focus:ring-2 focus:ring-primary/50 focus:border-primary border-0 border-b-2 border-[#cfd9e7] dark:border-slate-700 bg-transparent text-xl font-bold leading-normal text-primary dark:text-white"
                                        maxLength="6"
                                        type="text"
                                        value={digit}
                                        onChange={(e) => handleChange(i, e.target.value)}
                                        onKeyDown={(e) => handleKeyDown(i, e)}
                                        required
                                    />
                                ))}
                            </fieldset>
                        </div>

                        <div className="flex flex-col gap-4 py-6">
                            <button
                                className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 bg-primary text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 shadow-md transition-all active:scale-[0.98] disabled:opacity-70"
                                type="submit"
                                disabled={loading}
                            >
                                <span className="truncate">{loading ? 'Verifying...' : 'Verify Code'}</span>
                            </button>
                        </div>
                    </form>

                    <div className="flex flex-col items-center gap-6">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                            Didn't receive the code?
                            <button
                                onClick={handleResend}
                                disabled={resendLoading}
                                className="text-primary font-bold hover:underline ml-1 bg-transparent border-none p-0 cursor-pointer disabled:opacity-50"
                            >
                                {resendLoading ? 'Sending...' : 'Resend OTP'}
                            </button>
                        </p>
                        <div className="w-full h-[1px] bg-slate-100 dark:bg-slate-800"></div>
                        <Link
                            to="/login"
                            className="flex items-center gap-2 text-slate-500 dark:text-slate-400 hover:text-primary dark:hover:text-primary transition-colors text-sm font-medium"
                        >
                            <span className="material-symbols-outlined text-sm">arrow_back</span>
                            Back to Login
                        </Link>
                    </div>
                </div>
            </main>

            <div className="fixed top-0 left-0 -z-10 h-full w-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] h-[40%] w-[40%] rounded-full bg-primary/5 blur-[120px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-primary/5 blur-[120px]"></div>
            </div>
        </div>
    );
}
