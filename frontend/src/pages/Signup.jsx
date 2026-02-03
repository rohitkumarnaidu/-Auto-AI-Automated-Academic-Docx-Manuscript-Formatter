import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function Signup() {
    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-[#0d131b] dark:text-slate-50 min-h-screen flex flex-col">
            <Navbar variant="auth" />

            {/* Main Content */}
            <main className="flex-grow flex items-center justify-center py-12 px-4">
                <div className="max-w-[540px] w-full bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-[#e7ecf3] dark:border-slate-800 p-8 md:p-10">
                    {/* Headline & Intro */}
                    <div className="text-center mb-8">
                        <h1 className="text-[#0d131b] dark:text-slate-50 tracking-tight text-[32px] font-bold leading-tight pb-2">Create your account</h1>
                        <p className="text-[#4c6c9a] dark:text-slate-400 text-base font-normal">Join thousands of researchers formatting with ease.</p>
                    </div>

                    {/* Signup Form (REQUIRED FIRST) */}
                    <form action="#" className="space-y-4" method="POST" onSubmit={(e) => e.preventDefault()}>
                        {/* Full Name */}
                        <div className="flex flex-col">
                            <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium pb-2">Full Name</p>
                            <div className="relative">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#4c6c9a] text-[20px]">person</span>
                                <input
                                    className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-slate-50 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 h-12 pl-12 pr-4 placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 focus:border-primary focus:ring-1 focus:ring-primary transition-all text-sm"
                                    placeholder="e.g. Jane Doe"
                                    required
                                    type="text"
                                />
                            </div>
                        </div>
                        {/* Email */}
                        <div className="flex flex-col">
                            <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium pb-2">Institutional Email</p>
                            <div className="relative">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#4c6c9a] text-[20px]">alternate_email</span>
                                <input
                                    className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-slate-50 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 h-12 pl-12 pr-4 placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 focus:border-primary focus:ring-1 focus:ring-primary transition-all text-sm"
                                    placeholder="Enter your email address"
                                    required
                                    type="email"
                                />
                            </div>
                        </div>
                        {/* Institution */}
                        <div className="flex flex-col">
                            <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium pb-2">Institution / University <span className="text-xs text-[#4c6c9a] font-normal ml-1">(Optional)</span></p>
                            <div className="relative">
                                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#4c6c9a] text-[20px]">school</span>
                                <input
                                    className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-slate-50 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 h-12 pl-12 pr-4 placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 focus:border-primary focus:ring-1 focus:ring-primary transition-all text-sm"
                                    placeholder="Enter your institution name"
                                    type="text"
                                />
                            </div>
                        </div>
                        {/* Password Group */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex flex-col">
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium pb-2">Password</p>
                                <div className="relative">
                                    <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#4c6c9a] text-[20px]">lock</span>
                                    <input
                                        className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-slate-50 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 h-12 pl-12 pr-4 placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 focus:border-primary focus:ring-1 focus:ring-primary transition-all text-sm"
                                        placeholder="Enter your password"
                                        required
                                        type="password"
                                    />
                                </div>
                            </div>
                            <div className="flex flex-col">
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium pb-2">Confirm Password</p>
                                <div className="relative">
                                    <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#4c6c9a] text-[20px]">lock_reset</span>
                                    <input
                                        className="form-input flex w-full rounded-lg text-[#0d131b] dark:text-slate-50 border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 h-12 pl-12 pr-4 placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 focus:border-primary focus:ring-1 focus:ring-primary transition-all text-sm"
                                        placeholder="Enter your password again"
                                        required
                                        type="password"
                                    />
                                </div>
                            </div>
                        </div>
                        {/* Requirements hint */}
                        <div className="flex items-center gap-2 px-1">
                            <span className="material-symbols-outlined text-green-500 text-[14px]">check_circle</span>
                            <span className="text-xs text-[#4c6c9a] dark:text-slate-400">At least 8 characters with a number</span>
                        </div>
                        {/* Terms */}
                        <div className="flex items-start gap-2 pt-2 px-1">
                            <input className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary" id="terms" required type="checkbox" />
                            <label className="text-xs text-[#4c6c9a] dark:text-slate-400 leading-relaxed" htmlFor="terms">
                                I agree to the <a className="text-primary hover:underline" href="#">Terms of Service</a> and <a className="text-primary hover:underline" href="#">Privacy Policy</a>.
                            </label>
                        </div>
                        {/* Submit Button */}
                        <button className="flex w-full items-center justify-center rounded-lg h-14 bg-primary text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 transition-all mt-4 shadow-lg shadow-primary/20" type="submit">
                            Create Account
                        </button>
                    </form>

                    <div className="relative flex items-center my-6">
                        <div className="flex-grow border-t border-[#e7ecf3] dark:border-slate-800"></div>
                        <span className="flex-shrink mx-4 text-xs font-medium text-[#4c6c9a] dark:text-slate-500 uppercase tracking-wider">or sign up with</span>
                        <div className="flex-grow border-t border-[#e7ecf3] dark:border-slate-800"></div>
                    </div>

                    {/* Social Signup (REQUIRED SECOND) */}
                    <button className="flex w-full items-center justify-center gap-3 rounded-lg border border-[#cfd9e7] dark:border-slate-700 bg-white dark:bg-slate-800 h-12 px-4 text-[#0d131b] dark:text-slate-50 text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all mb-6">
                        <svg className="h-5 w-5" viewBox="0 0 24 24">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"></path>
                            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                        </svg>
                        <span>Continue with Google</span>
                    </button>

                    {/* Footer Link */}
                    <div className="mt-8 text-center">
                        <p className="text-sm text-[#4c6c9a] dark:text-slate-400">
                            Already have an account?
                            <Link to="/login" className="text-primary font-bold hover:underline ml-1">Login</Link>
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}
