import { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import NotificationBell from './NotificationBell';
import { useDocument } from '../context/DocumentContext';
import { isProcessing as checkProcessing } from '../constants/status';

export default function Navbar({ variant = 'app', activeTab = '' }) {
    const { isLoggedIn, signOut, loading, user } = useAuth();
    const { job } = useDocument();
    const isJobActive = Boolean(job?.id && job?.status && checkProcessing(job.status));
    const isAdminUser = Boolean(
        user?.is_admin
        || user?.app_metadata?.role === 'admin'
        || user?.user_metadata?.role === 'admin'
        || user?.role === 'admin'
    );
    const { theme, toggleTheme } = useTheme();
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const profileRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    const loggedInLinks = [
        { key: 'dashboard', to: '/dashboard', label: 'Dashboard' },
        { key: 'upload', to: '/upload', label: 'Upload' },
        { key: 'batch-upload', to: '/batch-upload', label: 'Batch Upload' },
        { key: 'templates', to: '/templates', label: 'Templates' },
        { key: 'template-editor', to: '/template-editor', label: 'Template Editor' },
        { key: 'feedback', to: '/feedback', label: 'Feedback' },
        { key: 'results', to: '/results', label: 'Validate Results' },
        { key: 'history', to: '/history', label: 'My Manuscripts' },
        { key: 'notifications', to: '/notifications', label: 'Notifications' },
        { key: 'settings', to: '/settings', label: 'Settings' },
        ...(isAdminUser ? [{ key: 'admin-dashboard', to: '/admin-dashboard', label: 'Admin Dashboard' }] : []),
    ];
    const guestLinks = [
        { key: 'dashboard', to: '/', label: 'Home' },
        { key: 'upload', to: '/upload', label: 'Upload' },
        { key: 'templates', to: '/templates', label: 'Templates' },
        { key: 'template-editor', to: '/template-editor', label: 'Template Editor' },
    ];
    const activeLinks = isLoggedIn ? loggedInLinks : guestLinks;

    const ThemeToggle = () => (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
            <span className="material-symbols-outlined">
                {theme === 'dark' ? 'light_mode' : 'dark_mode'}
            </span>
        </button>
    );

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

    useEffect(() => {
        setIsMobileMenuOpen(false);
        setIsProfileOpen(false);
    }, [location.pathname]);

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
                            <span className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                        </Link>
                        <nav className="hidden lg:flex items-center gap-8">
                            <a href="#features" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Features</a>
                            <a href="#templates" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Templates</a>
                            <a href="#pricing" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Pricing</a>
                            <a href="#about" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">About</a>
                        </nav>
                        <div className="flex items-center gap-3">
                            <ThemeToggle />
                            <div className="hidden sm:flex items-center gap-3">
                                <Link to="/login" className="text-sm font-semibold text-slate-700 dark:text-slate-200 px-4 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Sign In</Link>
                                <Link to="/signup" className="bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Sign Up</Link>
                            </div>
                            <button
                                type="button"
                                onClick={() => setIsMobileMenuOpen((current) => !current)}
                                className="sm:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                aria-label="Toggle menu"
                            >
                                <span className="material-symbols-outlined">
                                    {isMobileMenuOpen ? 'close' : 'menu'}
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
                {isMobileMenuOpen && (
                    <div className="sm:hidden border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-background-dark/95">
                        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-2">
                            <a href="#features" className="px-2 py-2 rounded-md text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">Features</a>
                            <a href="#templates" className="px-2 py-2 rounded-md text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">Templates</a>
                            <a href="#pricing" className="px-2 py-2 rounded-md text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">Pricing</a>
                            <a href="#about" className="px-2 py-2 rounded-md text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">About</a>
                            <div className="pt-2 flex flex-col gap-2">
                                <Link to="/login" className="w-full text-center text-sm font-semibold text-slate-700 dark:text-slate-200 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Sign In</Link>
                                <Link to="/signup" className="w-full text-center bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Sign Up</Link>
                            </div>
                        </div>
                    </div>
                )}
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
                            <span className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                        </Link>
                        <div className="flex items-center gap-3">
                            <ThemeToggle />
                            <Link to="/" className="hidden sm:inline-flex bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Home</Link>
                            <button
                                type="button"
                                onClick={() => setIsMobileMenuOpen((current) => !current)}
                                className="sm:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                aria-label="Toggle menu"
                            >
                                <span className="material-symbols-outlined">
                                    {isMobileMenuOpen ? 'close' : 'menu'}
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
                {isMobileMenuOpen && (
                    <div className="sm:hidden border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-background-dark/95">
                        <div className="max-w-7xl mx-auto px-4 py-3">
                            <Link to="/" className="w-full inline-flex items-center justify-center bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Home</Link>
                        </div>
                    </div>
                )}
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
        <header className="border-b border-solid border-slate-200 dark:border-slate-800 bg-white dark:bg-background-dark sticky top-0 z-50">
            <div className="max-w-[1600px] mx-auto flex items-center justify-between px-4 sm:px-6 lg:px-8 py-3 gap-3">
                <div className="flex items-center gap-4 text-primary min-w-0">
                    <Link to={isLoggedIn ? "/dashboard" : "/"} className="flex items-center gap-2 hover:opacity-80 transition-opacity min-w-0">
                        <div className="bg-primary text-white p-1.5 rounded-lg flex items-center justify-center shrink-0">
                            <span className="material-symbols-outlined text-xl">auto_stories</span>
                        </div>
                        <span className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-white truncate">ScholarForm AI</span>
                    </Link>
                </div>

                <div className="hidden xl:flex flex-1 justify-end gap-8 min-w-0">
                    <nav className="flex items-center gap-7">
                        {activeLinks.map((link) => (
                            <Link key={link.key} to={link.to} className={`${getTabClasses(link.key)} relative`}>
                                {link.label}
                                {link.key === 'upload' && isJobActive && (
                                    <span className="absolute -top-1 -right-3 flex h-2.5 w-2.5">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"></span>
                                    </span>
                                )}
                            </Link>
                        ))}
                    </nav>

                    {isLoggedIn ? (
                        <div className="flex items-center gap-4">
                            <ThemeToggle />
                            <div className="flex gap-2">
                                <NotificationBell />
                                <button
                                    onClick={() => navigate('/settings')}
                                    className="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                                    title="Settings"
                                >
                                    <span className="material-symbols-outlined">settings</span>
                                </button>
                            </div>
                            <div className="relative" ref={profileRef}>
                                <div
                                    className="flex items-center gap-2 cursor-pointer group"
                                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                                    role="button"
                                    tabIndex={0}
                                    aria-expanded={isProfileOpen}
                                    aria-label="Profile menu"
                                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setIsProfileOpen(!isProfileOpen); } }}
                                >
                                    <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border border-slate-200 dark:border-slate-700" style={{ backgroundImage: `url("${user?.user_metadata?.avatar_url || user?.user_metadata?.picture || 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBAnQke1dGWniClQX7rHZBtni1hbRlIpllATyD41NPPw3Br765F9F0vIWQH7I2SezfqlRBNZW0hgkDJ4Kl-Ekd0MVD60AqnPJe_Q0QkDvG2fqpVzmz_HTsQKFKkBIvfvFH26zii0uK7s11gs1bnXmlnWvG6LS6GTXhY6thfBqwRUWqvuAIMWQfqwnAs0DFEX2j3QBP0F7mG913xvhu2iMMo_MIgxF_nqEmviIbI0G3jFBvWtp3KPkAPAxfc4YVXlrDPh_tJJ5ZgnHP'}")` }}></div>
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
                                        <Link
                                            to="/settings"
                                            className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                                            onClick={() => setIsProfileOpen(false)}
                                        >
                                            Settings
                                        </Link>
                                        <div className="border-t border-slate-100 dark:border-slate-800 my-1"></div>
                                        <button
                                            onClick={async () => {
                                                await signOut();
                                                setIsProfileOpen(false);
                                                navigate('/');
                                            }}
                                            className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                        >
                                            Sign out
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center gap-4">
                            <span className="hidden 2xl:block text-xs text-slate-500 dark:text-slate-400 font-medium italic">
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

                <div className="xl:hidden flex items-center gap-2">
                    <ThemeToggle />
                    {isLoggedIn && <NotificationBell />}
                    <button
                        type="button"
                        onClick={() => setIsMobileMenuOpen((current) => !current)}
                        className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        aria-label="Toggle app menu"
                    >
                        <span className="material-symbols-outlined">
                            {isMobileMenuOpen ? 'close' : 'menu'}
                        </span>
                    </button>
                </div>
            </div>

            {isMobileMenuOpen && (
                <div className="xl:hidden border-t border-slate-200 dark:border-slate-800 px-4 sm:px-6 pb-4 pt-3 bg-white dark:bg-background-dark">
                    <nav className="flex flex-col gap-1">
                        {activeLinks.map((link) => (
                            <Link
                                key={link.key}
                                to={link.to}
                                className={`px-3 py-2 rounded-lg text-sm ${activeTab === link.key
                                    ? 'bg-primary/10 text-primary font-bold'
                                    : 'text-slate-700 dark:text-slate-300 font-medium hover:bg-slate-100 dark:hover:bg-slate-800'
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>

                    {isLoggedIn ? (
                        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 flex flex-col gap-2">
                            <Link to="/profile" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
                                My Account
                            </Link>
                            <Link to="/settings" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
                                Settings
                            </Link>
                            <button
                                onClick={async () => {
                                    await signOut();
                                    navigate('/');
                                }}
                                className="px-3 py-2 rounded-lg text-left text-sm font-bold text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                            >
                                Sign out
                            </button>
                        </div>
                    ) : (
                        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 flex flex-col gap-2">
                            <Link to="/login" className="w-full text-center text-sm font-semibold text-slate-700 dark:text-slate-300 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                Login
                            </Link>
                            <Link to="/signup" className="w-full text-center bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-700 shadow-sm transition-all active:scale-[0.98]">
                                Sign Up
                            </Link>
                        </div>
                    )}
                </div>
            )}
        </header>
    );
}
