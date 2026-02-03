import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function ResetPassword() {
    const navigate = useNavigate();

    const handleReset = (e) => {
        e.preventDefault();
        // UI logic: navigate to login
        navigate('/login');
    };

    return (
        <div className="bg-background-light dark:bg-background-dark min-h-screen flex flex-col font-display transition-colors duration-300">
            <Navbar variant="auth" />

            {/* Main Content */}
            <main className="flex-1 flex items-center justify-center p-4">
                <div className="w-full max-w-[480px] bg-white dark:bg-slate-900 shadow-xl rounded-xl overflow-hidden border border-[#e7ecf3] dark:border-slate-800">
                    <div className="px-8 pt-10 pb-4">
                        {/* HeadlineText */}
                        <h1 className="text-[#0d131b] dark:text-slate-100 tracking-tight text-[28px] md:text-[32px] font-bold leading-tight text-center">Reset your password</h1>
                        {/* BodyText */}
                        <p className="text-[#4c6c9a] dark:text-slate-400 text-base font-normal leading-normal pt-2 text-center">
                            Create a new password for your account.
                        </p>
                    </div>

                    <form className="px-8 pb-10 space-y-5" onSubmit={handleReset}>
                        {/* TextField: New Password */}
                        <div className="flex flex-col gap-1.5">
                            <label className="flex flex-col w-full">
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium leading-normal pb-1">New Password</p>
                                <div className="flex w-full items-stretch rounded-lg shadow-sm">
                                    <input
                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg rounded-r-none border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 text-[#0d131b] dark:text-slate-100 focus:outline-0 focus:ring-1 focus:ring-primary focus:border-primary h-12 placeholder:text-[#94a3b8] p-[15px] border-r-0 text-base font-normal leading-normal"
                                        placeholder="Enter your new password"
                                        type="password"
                                        required
                                    />
                                    <div className="text-[#4c6c9a] flex border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 items-center justify-center pr-[15px] rounded-r-lg border-l-0 cursor-pointer hover:text-primary transition-colors">
                                        <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>visibility</span>
                                    </div>
                                </div>
                            </label>
                            {/* MetaText */}
                            <p className="text-[#64748b] dark:text-slate-500 text-xs font-normal leading-normal">At least 8 characters with a number</p>
                        </div>

                        {/* TextField: Confirm Password */}
                        <div className="flex flex-col gap-1.5">
                            <label className="flex flex-col w-full">
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium leading-normal pb-1">Confirm Password</p>
                                <div className="flex w-full items-stretch rounded-lg shadow-sm">
                                    <input
                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg rounded-r-none border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 text-[#0d131b] dark:text-slate-100 focus:outline-0 focus:ring-1 focus:ring-primary focus:border-primary h-12 placeholder:text-[#94a3b8] p-[15px] border-r-0 text-base font-normal leading-normal"
                                        placeholder="Enter your new password again"
                                        type="password"
                                        required
                                    />
                                    <div className="text-[#4c6c9a] flex border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 items-center justify-center pr-[15px] rounded-r-lg border-l-0 cursor-pointer hover:text-primary transition-colors">
                                        <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>visibility</span>
                                    </div>
                                </div>
                            </label>
                        </div>

                        {/* Primary Action Button */}
                        <div className="pt-4">
                            <button
                                className="w-full flex items-center justify-center rounded-lg h-12 bg-primary text-white text-base font-bold leading-normal tracking-wide hover:bg-primary/90 transition-all shadow-md active:scale-[0.98]"
                                type="submit"
                            >
                                Reset Password
                            </button>
                        </div>

                        {/* Footer Link */}
                        <div className="text-center pt-2">
                            <Link
                                to="/login"
                                className="text-primary hover:text-primary/80 text-sm font-medium transition-colors inline-flex items-center gap-1"
                            >
                                <span className="material-symbols-outlined text-sm">arrow_back</span>
                                Back to Login
                            </Link>
                        </div>
                    </form>
                </div>
            </main>

            {/* Visual Element Background (Optional/Aesthetic) */}
            <div className="fixed inset-0 -z-10 h-full w-full bg-white dark:bg-background-dark pointer-events-none">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
                <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary opacity-5 blur-[100px]"></div>
            </div>
        </div>
    );
}
