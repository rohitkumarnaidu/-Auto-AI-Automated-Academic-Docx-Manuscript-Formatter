import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function VerifyOTP() {
    const navigate = useNavigate();

    const handleVerify = (e) => {
        e.preventDefault();
        // UI logic: navigate to reset-password
        navigate('/reset-password');
    };

    return (
        <div className="bg-background-light dark:bg-background-dark min-h-screen flex flex-col font-display transition-colors duration-300">
            <Navbar variant="auth" />

            {/* Main Content Area */}
            <main className="flex-1 flex items-center justify-center p-4">
                <div className="layout-content-container flex flex-col w-full max-w-[480px] bg-white dark:bg-slate-900 shadow-xl rounded-xl p-8 border border-slate-100 dark:border-slate-800">
                    {/* Headline Section */}
                    <div className="flex flex-col items-center">
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                            <span className="material-symbols-outlined !text-3xl">mark_email_read</span>
                        </div>
                        <h1 className="text-[#0d131b] dark:text-white tracking-tight text-[28px] md:text-[32px] font-bold leading-tight text-center pb-2">
                            Verify your email
                        </h1>
                        <p className="text-slate-600 dark:text-slate-400 text-base font-normal leading-normal pb-6 text-center">
                            Enter the 6-digit verification code sent to your email.
                        </p>
                    </div>

                    {/* OTP Input Section */}
                    <form onSubmit={handleVerify}>
                        <div className="flex justify-center py-3">
                            <fieldset className="relative flex gap-3 md:gap-4">
                                {/* Input boxes for OTP */}
                                {[...Array(6)].map((_, i) => (
                                    <input
                                        key={i}
                                        className="flex h-14 w-11 md:w-12 text-center [appearance:textfield] focus:outline-0 focus:ring-2 focus:ring-primary/50 focus:border-primary border-0 border-b-2 border-[#cfd9e7] dark:border-slate-700 bg-transparent text-xl font-bold leading-normal text-primary dark:text-white"
                                        max="9"
                                        maxLength="1"
                                        min="0"
                                        placeholder="·"
                                        type="text"
                                        required
                                    />
                                ))}
                            </fieldset>
                        </div>

                        {/* Action Button */}
                        <div className="flex flex-col gap-4 py-6">
                            <button
                                className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 bg-primary text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 shadow-md transition-all active:scale-[0.98]"
                                type="submit"
                            >
                                <span className="truncate">Verify Code</span>
                            </button>
                        </div>
                    </form>

                    {/* Secondary Links */}
                    <div className="flex flex-col items-center gap-6">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                            Didn't receive the code?
                            <button className="text-primary font-bold hover:underline ml-1 bg-transparent border-none p-0 cursor-pointer">
                                Resend OTP
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

            {/* Subtle background elements for aesthetic */}
            <div className="fixed top-0 left-0 -z-10 h-full w-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] h-[40%] w-[40%] rounded-full bg-primary/5 blur-[120px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-primary/5 blur-[120px]"></div>
            </div>
        </div>
    );
}
