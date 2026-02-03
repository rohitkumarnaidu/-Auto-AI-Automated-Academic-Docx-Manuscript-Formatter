import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function Login() {
    return (
        <div className="bg-background-light dark:bg-background-dark min-h-screen flex flex-col transition-colors duration-300">
            <Navbar variant="auth" />

            {/* Main Login Content */}
            <main className="flex flex-1 items-center justify-center py-12 px-4">
                <div className="layout-content-container flex flex-col w-full max-w-[480px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-8">
                    {/* Headline */}
                    <h1 className="text-[#0d131b] dark:text-slate-100 tracking-light text-[32px] font-bold leading-tight text-center pb-2 pt-4 font-display">Welcome back</h1>
                    <p className="text-[#4c6c9a] dark:text-slate-400 text-center text-base pb-8 font-normal">Please enter your details to sign in.</p>

                    {/* Form Section (REQUIRED FIRST) */}
                    <form className="flex flex-col gap-4" onSubmit={(e) => e.preventDefault()}>
                        {/* Email Field */}
                        <div className="flex flex-col">
                            <label className="flex flex-col w-full">
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium leading-normal pb-2">Email Address</p>
                                <input
                                    className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/20 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-900 focus:border-primary h-12 placeholder:text-[#4c6c9a] px-4 text-sm font-normal leading-normal transition-all"
                                    placeholder="Enter your registered email address"
                                    type="email"
                                    required
                                />
                            </label>
                        </div>
                        {/* Password Field */}
                        <div className="flex flex-col">
                            <label className="flex flex-col w-full">
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium leading-normal pb-2">Password</p>
                                <input
                                    className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/20 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-900 focus:border-primary h-12 placeholder:text-[#4c6c9a] px-4 text-sm font-normal leading-normal transition-all"
                                    placeholder="Enter your password"
                                    type="password"
                                    required
                                />
                            </label>
                            <div className="flex justify-end pt-1">
                                <Link to="/forgot-password" title="Go to Forgot Password Page" className="text-primary text-xs font-medium hover:underline">Forgot password?</Link>
                            </div>
                        </div>
                        {/* Login Button */}
                        <div className="pt-4">
                            <button
                                className="flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 bg-primary text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 shadow-md transition-all active:scale-[0.98]"
                                type="submit"
                            >
                                Login
                            </button>
                        </div>
                    </form>

                    <div className="relative flex items-center py-8">
                        <div className="flex-grow border-t border-[#e7ecf3] dark:border-slate-800"></div>
                        <span className="flex-shrink mx-4 text-sm text-[#4c6c9a] dark:text-slate-500 font-normal uppercase tracking-wider">or continue with</span>
                        <div className="flex-grow border-t border-[#e7ecf3] dark:border-slate-800"></div>
                    </div>

                    {/* Social Login Section (REQUIRED SECOND) */}
                    <div className="flex flex-col gap-3">
                        <button className="flex w-full items-center justify-center gap-3 rounded-lg border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800/50 px-4 py-3 text-sm font-medium text-[#0d131b] dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                            <svg className="h-5 w-5" viewBox="0 0 24 24">
                                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"></path>
                                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                            </svg>
                            Continue with Google
                        </button>
                    </div>

                    {/* Signup Link */}
                    <p className="text-center text-sm text-[#4c6c9a] dark:text-slate-400 mt-8">
                        Don't have an account? <Link to="/signup" className="text-primary font-bold hover:underline">Sign up</Link>
                    </p>
                </div>
            </main>
        </div>
    );
}
