import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';

export default function ForgotPassword() {
    const { forgotPassword } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        setLoading(true);

        try {
            await forgotPassword(email);
            setMessage('OTP has been sent to your email.');
            // Navigate after a short delay so user can see success message
            setTimeout(() => {
                navigate('/verify-otp', { state: { email } });
            }, 1500);
        } catch (err) {
            setError(err.message || 'Failed to send OTP');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-background-light dark:bg-background-dark min-h-screen flex flex-col font-display transition-colors duration-300">
            <Navbar variant="auth" />

            {/* Main Content: Centered Card */}
            <main className="flex-grow flex items-center justify-center px-4 py-12">
                <div className="w-full max-w-[480px] bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-[#e7ecf3] dark:border-slate-800 p-8 md:p-10 flex flex-col">
                    {/* Icon Decoration */}
                    <div className="flex justify-center mb-6">
                        <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
                            <span className="material-symbols-outlined text-primary text-3xl">lock_reset</span>
                        </div>
                    </div>

                    {/* Headline Section */}
                    <div className="text-center mb-8">
                        <h1 className="text-[#0d131b] dark:text-white text-2xl md:text-3xl font-bold leading-tight mb-3">
                            Forgot your password?
                        </h1>
                        <p className="text-[#4c6c9a] dark:text-slate-400 text-base font-normal leading-relaxed px-2">
                            Enter your registered email address to receive a 6-digit OTP.
                        </p>
                    </div>

                    {message && (
                        <div className="mb-6 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 text-sm">
                            {message}
                        </div>
                    )}

                    {error && (
                        <div className="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Input Form Section */}
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="flex flex-col w-full">
                            <label className="flex flex-col gap-2">
                                <span className="text-[#0d131b] dark:text-slate-200 text-sm font-semibold">Email Address</span>
                                <div className="relative">
                                    <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#4c6c9a] text-xl">mail</span>
                                    <input
                                        className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/20 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 focus:border-primary h-14 placeholder:text-[#4c6c9a]/60 pl-12 pr-4 text-base font-normal transition-all"
                                        placeholder="Enter your registered email address"
                                        required
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>
                            </label>
                        </div>

                        {/* Action Button */}
                        <div className="pt-2">
                            <button
                                className="w-full flex cursor-pointer items-center justify-center rounded-lg h-14 px-5 bg-primary text-white text-base font-bold leading-normal tracking-wide transition-all hover:bg-primary/90 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
                                type="submit"
                                disabled={loading}
                            >
                                <span className="truncate">{loading ? 'Sending...' : 'Send OTP'}</span>
                            </button>
                        </div>
                    </form>

                    {/* Navigation Back Link */}
                    <div className="mt-8 text-center border-t border-[#e7ecf3] dark:border-slate-800 pt-6">
                        <Link
                            to="/login"
                            className="inline-flex items-center gap-2 text-primary hover:text-primary/80 text-sm font-semibold transition-colors"
                        >
                            <span className="material-symbols-outlined text-base">arrow_back</span>
                            Back to Sign in
                        </Link>
                    </div>
                </div>
            </main>

            {/* Abstract Decorative Background Elements (Visual Only) */}
            <div className="fixed top-0 left-0 w-full h-full -z-10 pointer-events-none overflow-hidden opacity-50 dark:opacity-20">
                <div className="absolute -top-[10%] -left-[5%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[120px]"></div>
                <div className="absolute top-[60%] -right-[10%] w-[35%] h-[50%] bg-primary/5 rounded-full blur-[100px]"></div>
            </div>
        </div>
    );
}
