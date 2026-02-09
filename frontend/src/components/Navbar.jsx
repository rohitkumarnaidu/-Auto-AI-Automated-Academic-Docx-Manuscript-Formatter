/* eslint-disable react/prop-types */
import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ variant = 'app', activeTab = '' }) {
    const { isLoggedIn, logout, loading } = useAuth();
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const profileRef = useRef(null);

    // Click-away listener for profile dropdown
    useEffect(() => {
        function handleClickOutside(event) {
            if (profileRef.current && !profileRef.current.contains(event.target)) {
                setIsProfileOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Prevent rendering while auth state is indeterminate
    if (loading) return null;

    if (variant === 'landing') {
        return (
            <header className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                            <div className="bg-primary text-white p-1.5 rounded-lg flex items-center justify-center">
                                <span className="material-symbols-outlined text-xl">auto_stories</span>
                            </div>
                            <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                        </Link>
                        <nav className="hidden md:flex items-center gap-8">
                            <a href="#features" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Features</a>
                            <a href="#templates" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Templates</a>
                            <a href="#pricing" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Pricing</a>
                            <a href="#about" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">About</a>
                        </nav>
                        <div className="flex items-center gap-3">
                            <Link to="/login" className="text-sm font-semibold text-slate-700 dark:text-slate-200 px-4 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Sign In</Link>
                            <Link to="/signup" className="bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Sign Up</Link>
                        </div>
                    </div>
                </div>
            </header>
        );
    }

    if (variant === 'auth') {
        return (
            <header className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                            <div className="bg-primary text-white p-1.5 rounded-lg flex items-center justify-center">
                                <span className="material-symbols-outlined text-xl">auto_stories</span>
                            </div>
                            <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                        </Link>
                        <div className="flex items-center">
                            <Link to="/" className="bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Home</Link>
                        </div>
                    </div>
                </div>
            </header>
        );
    }

    // App Navbar
    const getTabClasses = (tabName) => {
        const isActive = activeTab === tabName;
        return isActive
            ? "text-primary text-sm font-bold border-b-2 border-primary py-1"
            : "text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors";
    };

    return (
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-slate-800 bg-white dark:bg-background-dark px-10 py-3 sticky top-0 z-50">
            <div className="flex items-center gap-4 text-primary">
                <Link to={isLoggedIn ? "/dashboard" : "/"} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                    <div className="bg-primary text-white p-1.5 rounded-lg flex items-center justify-center">
                        <span className="material-symbols-outlined text-xl">auto_stories</span>
                    </div>
                    <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                </Link>
            </div>

            <div className="flex flex-1 justify-end gap-8">
                {/* Center Nav Links */}
                <nav className="flex items-center gap-9">
                    {isLoggedIn ? (
                        <>
                            <Link to="/dashboard" className={getTabClasses('dashboard')}>Dashboard</Link>
                            <Link to="/upload" className={getTabClasses('upload')}>Upload</Link>
                            <Link to="/templates" className={getTabClasses('templates')}>Templates</Link>
                            <Link to="/results" className={getTabClasses('results')}>Validate Results</Link>
                            <Link to="/history" className={getTabClasses('history')}>My Manuscripts</Link>
                        </>
                    ) : (
                        <>
                            <Link to="/" className={getTabClasses('dashboard')}>Home</Link>
                            <Link to="/upload" className={getTabClasses('upload')}>Upload</Link>
                            <Link to="/templates" className={getTabClasses('templates')}>Templates</Link>
                        </>
                    )}
                </nav>

                {/* Auth Actions */}
                {isLoggedIn ? (
                    <div className="flex items-center gap-4">
                        <div className="flex gap-2">
                            <button className="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200">
                                <span className="material-symbols-outlined">notifications</span>
                            </button>
                            <button className="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200">
                                <span className="material-symbols-outlined">settings</span>
                            </button>
                        </div>
                        <div className="relative" ref={profileRef}>
                            <div
                                className="flex items-center gap-2 cursor-pointer group"
                                onClick={() => setIsProfileOpen(!isProfileOpen)}
                            >
                                <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border border-slate-200 dark:border-slate-700" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCBAnQke1dGWniClQX7rHZBtni1hbRlIpllATyD41NPPw3Br765F9F0vIWQH7I2SezfqlRBNZW0hgkDJ4Kl-Ekd0MVD60AqnPJe_Q0QkDvG2fqpVzmz_HTsQKFKkBIvfvFH26zii0uK7s11gs1bnXmlnWvG6LS6GTXhY6thfBqwRUWqvuAIMWQfqwnAs0DFEX2j3QBP0F7mG913xvhu2iMMo_MIgxF_nqEmviIbI0G3jFBvWtp3KPkAPAxfc4YVXlrDPh_tJJ5ZgnHP")' }}></div>
                                <span className={`material-symbols-outlined text-slate-400 group-hover:text-primary transition-all duration-200 ${isProfileOpen ? 'rotate-180' : ''}`}>expand_more</span>
                            </div>

                            {isProfileOpen && (
                                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden py-1 z-50">
                                    <Link to="/profile" className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors" onClick={() => setIsProfileOpen(false)}>
                                        My Account
                                    </Link>
                                    <Link
                                        to="/history"
                                        className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                                        onClick={() => setIsProfileOpen(false)}
                                    >
                                        My Manuscripts
                                    </Link>
                                    <div className="border-t border-slate-100 dark:border-slate-800 my-1"></div>
                                    <button
                                        onClick={() => {
                                            logout();
                                            setIsProfileOpen(false);
                                        }}
                                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                    >
                                        Logout
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-4">
                        <span className="hidden xl:block text-xs text-slate-500 dark:text-slate-400 font-medium italic">
                            Login to save your documents and access history
                        </span>
                        <Link to="/login" className="text-sm font-semibold text-slate-700 dark:text-slate-300 hover:text-primary transition-colors">
                            Login
                        </Link>
                        <Link to="/signup" className="bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-700 shadow-sm transition-all active:scale-[0.98]">
                            Sign Up
                        </Link>
                    </div>
                )}
            </div>
        </header>
    );
}
