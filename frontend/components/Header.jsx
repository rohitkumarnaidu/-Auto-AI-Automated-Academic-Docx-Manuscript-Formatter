'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import ModeSwitcher from '@/components/header/ModeSwitcher';
import ThemeToggle from '@/components/header/ThemeToggle';
import { useAuth } from '@/src/context/AuthContext';
import NotificationBell from '@/src/components/NotificationBell';

const AUTH_ROUTES = ['/login', '/signup', '/forgot-password', '/verify-otp', '/reset-password', '/auth/callback'];

const APP_GUEST_LINKS = [
    { href: '/', label: 'Home' },
    { href: '/upload', label: 'Upload' },
    { href: '/templates', label: 'Templates' },
    { href: '/template-editor', label: 'Template Editor' },
];

const USER_LINKS_BY_MODE = {
    formatter: [
        { href: '/dashboard', label: 'Dashboard' },
        { href: '/upload', label: 'Upload' },
        { href: '/history', label: 'History' },
        { href: '/templates', label: 'Templates' },
    ],
    generator: [
        { href: '/generate', label: 'Generator' },
        { href: '/dashboard', label: 'Dashboard' },
        { href: '/history', label: 'History' },
        { href: '/templates', label: 'Templates' },
    ],
};

const isInternalPath = (value) => value.startsWith('/') && !value.startsWith('//');

export default function Header({ section = 'shared', isSidebarLayout = false, onOpenMobileSidebar }) {
    const pathname = usePathname();
    const router = useRouter();
    const { user, signOut } = useAuth();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));
    const isLandingRoute = pathname === '/';
    const isUploadRoute = pathname === '/upload';

    const activeMode = section === 'generator'
        ? 'generator'
        : section === 'formatter'
            ? 'formatter'
            : pathname.startsWith('/generate')
                ? 'generator'
                : 'formatter';

    const navLinks = user ? USER_LINKS_BY_MODE[activeMode] : APP_GUEST_LINKS;
    const showModeSwitch = !isAuthRoute;
    const logoHref = user ? '/dashboard' : '/';

    const toggleMode = (mode) => {
        if (mode === activeMode) return;
        if (mode === 'generator') {
            router.push('/generate');
            return;
        }
        router.push(user ? '/dashboard' : '/upload');
    };

    const actionHref = user
        ? activeMode === 'generator'
            ? '/generate'
            : '/upload'
        : '/signup';

    const actionLabel = user
        ? activeMode === 'generator'
            ? 'New Draft'
            : 'New Format'
        : 'Get Started';

    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [pathname]);

    if (!user && (isLandingRoute || isAuthRoute)) {
        return (
            <header className="sticky top-0 z-50 w-full bg-white/60 dark:bg-slate-950/60 backdrop-blur-2xl pt-2 pb-1">
                <div className="mx-auto max-w-[1240px] px-4 sm:px-6">
                    <div className="flex h-[72px] items-center justify-between gap-4">
                        <Link href="/" className="flex items-center gap-2 sm:gap-3 shrink-0 group">
                            <div className="flex items-center justify-center size-10 sm:size-12">
                                <span className="material-symbols-outlined text-[32px] sm:text-[38px] text-blue-700 dark:text-blue-400">auto_stories</span>
                            </div>
                            <p className="text-[22px] sm:text-[28px] font-black tracking-tight text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                                ScholarForm AI
                            </p>
                        </Link>

                        {/* Desktop Navigation */}
                        {!isAuthRoute && (
                            <nav className="hidden lg:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
                                <Link href="/#features" className="text-[15px] font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                    Features
                                </Link>
                                <Link href="/#templates" className="text-[15px] font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                    Templates
                                </Link>
                                <Link href="/#pricing" className="text-[15px] font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                    Pricing
                                </Link>
                                <Link href="/#about" className="text-[15px] font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                    About
                                </Link>
                            </nav>
                        )}

                        <div className="ml-auto flex items-center gap-3 shrink-0">
                            <ThemeToggle />
                            {isAuthRoute && (
                                <Link href="/" className="h-10 px-3 hidden sm:inline-flex items-center text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                    Home
                                </Link>
                            )}
                            {pathname !== '/login' && (
                                <Link href="/login" className="h-10 px-3 inline-flex items-center text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                    Login
                                </Link>
                            )}
                            {pathname !== '/signup' && (
                                <Link href="/signup" className="h-10 px-3 inline-flex items-center text-sm font-bold text-slate-900 dark:text-white hover:text-primary dark:hover:text-primary transition-colors">
                                    Sign Up
                                </Link>
                            )}
                        </div>
                    </div>
                </div>
            </header>
        );
    }

    if (isSidebarLayout) {
        const sidebarHeaderClassName = isUploadRoute
            ? 'sticky top-0 z-50 w-full bg-white/60 dark:bg-slate-950/60 backdrop-blur-2xl pt-2 pb-1'
            : 'app-header sticky top-0 z-40 w-full bg-white/60 backdrop-blur-2xl border-b border-slate-200/50 shadow-sm dark:bg-slate-950/60 dark:border-white/[0.06]';

        return (
            <header className={sidebarHeaderClassName}>
                <div className={`flex xl:px-8 ${isUploadRoute ? 'h-[72px]' : 'h-14'} items-center px-4 gap-4 max-w-[1600px] mx-auto`}>
                    {/* Left: Hamburger & Logo */}
                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            onClick={onOpenMobileSidebar}
                            className="h-10 w-10 inline-flex items-center justify-center rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-700 dark:text-slate-300 shrink-0"
                            aria-label="Toggle Sidebar"
                        >
                            <span className="material-symbols-outlined text-[24px]">menu</span>
                        </button>
                        <Link href={logoHref} className="flex items-center gap-2 group">
                            <span className="material-symbols-outlined text-[28px] text-primary">auto_stories</span>
                            <span className="font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors text-[17px]">
                                ScholarForm AI
                            </span>
                        </Link>
                    </div>

                    <div className="flex-1" />

                    {/* Right: Controls */}
                    <div className="flex items-center gap-2 sm:gap-3 shrink-0">
                        <ThemeToggle />
                        {user ? (
                            <>
                                <NotificationBell />
                                <button
                                    onClick={() => router.push('/profile')}
                                    className="h-9 w-9 rounded-full overflow-hidden border border-slate-300 dark:border-slate-700 hover:border-primary transition-colors"
                                >
                                    <div className="w-full h-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-slate-700 dark:text-slate-100 font-bold text-sm">
                                        {user.email?.charAt(0).toUpperCase() || 'U'}
                                    </div>
                                </button>
                            </>
                        ) : (
                            <div className="flex items-center gap-2">
                                <Link href="/" className="hidden sm:inline-flex h-9 px-3 items-center rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                    Home
                                </Link>
                                <Link href="/login" className="h-9 px-3 inline-flex items-center rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                    Login
                                </Link>
                                <Link href="/signup" className="h-9 px-4 inline-flex items-center rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-bold transition-opacity">
                                    Sign Up
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </header>
        );
    }

    return (
        <header className="sticky top-0 z-50 w-full px-3 sm:px-4 pt-3">
            <div className="mx-auto max-w-[1240px] rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white/90 dark:bg-[#101114]/90 backdrop-blur-xl shadow-[0_14px_40px_rgba(0,0,0,0.06)] dark:shadow-[0_22px_56px_rgba(0,0,0,0.45)]">
                <div className="flex h-[68px] items-center gap-3 px-3 sm:px-4">
                    <Link href={logoHref} className="flex items-center gap-2 shrink-0 group">
                        <div className="flex items-center justify-center size-10">
                            <span className="material-symbols-outlined text-[32px] text-primary">auto_stories</span>
                        </div>
                        <div className="hidden sm:block">
                            <p className="text-[18px] font-bold tracking-tight text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                                ScholarForm AI
                            </p>
                        </div>
                    </Link>

                    <div className="flex-1" />

                    <div className="ml-auto flex items-center gap-2 sm:gap-3 shrink-0">
                        <ThemeToggle />

                        {user ? (
                            <>
                                <NotificationBell />
                                <button
                                    onClick={() => router.push('/profile')}
                                    className="h-9 w-9 rounded-full overflow-hidden border border-slate-300 dark:border-slate-700 hover:border-primary transition-colors"
                                    aria-label="User Profile"
                                >
                                    <div className="w-full h-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-slate-700 dark:text-slate-100 font-bold text-sm">
                                        {user.email?.charAt(0).toUpperCase() || 'U'}
                                    </div>
                                </button>
                            </>
                        ) : !isAuthRoute ? (
                            <div className="hidden sm:flex items-center gap-2">
                                <Link href="/login" className="h-9 px-3 inline-flex items-center rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                    Login
                                </Link>
                                <Link href="/signup" className="h-9 px-4 inline-flex items-center rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-bold transition-opacity">
                                    Sign Up
                                </Link>
                            </div>
                        ) : (
                            <Link href="/" className="hidden sm:inline-flex h-9 px-3 items-center rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                Home
                            </Link>
                        )}

                        <button
                            type="button"
                            onClick={() => setIsMobileMenuOpen((current) => !current)}
                            className="md:hidden h-9 w-9 inline-flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                            aria-label="Toggle menu"
                            aria-expanded={isMobileMenuOpen}
                        >
                            <span className="material-symbols-outlined text-[20px]">
                                {isMobileMenuOpen ? 'close' : 'menu'}
                            </span>
                        </button>
                    </div>
                </div>

                {!isAuthRoute && (
                    <div className="border-t border-slate-200/90 dark:border-white/10 px-3 sm:px-4 py-2.5">
                        <div className="flex flex-col gap-2">
                            {showModeSwitch && (
                                <div className="w-full overflow-x-auto custom-scrollbar pb-1">
                                    <ModeSwitcher activeMode={activeMode} onChange={toggleMode} />
                                </div>
                            )}

                            <div className="flex items-center justify-between gap-3">
                                <nav className="flex items-center gap-2 overflow-x-auto custom-scrollbar">
                                    {navLinks.map(({ href, label }) => {
                                        const active = isInternalPath(href)
                                            ? pathname === href || pathname.startsWith(`${href}/`)
                                            : false;

                                        return (
                                            <Link
                                                key={href}
                                                href={href}
                                                className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition-colors ${active
                                                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold'
                                                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 hover:bg-slate-100 dark:hover:text-white dark:hover:bg-slate-800'
                                                    }`}
                                            >
                                                {label}
                                            </Link>
                                        );
                                    })}
                                </nav>

                                {user ? (
                                    <button
                                        onClick={() => router.push(actionHref)}
                                        className="h-9 px-4 inline-flex items-center rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-semibold active:scale-[0.98] transition-all shadow-lg shadow-primary/20"
                                    >
                                        {actionLabel}
                                    </button>
                                ) : (
                                    <Link href={actionHref} className="h-9 px-4 inline-flex items-center rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-semibold active:scale-[0.98] transition-all shadow-lg shadow-primary/20">
                                        {actionLabel}
                                    </Link>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {isMobileMenuOpen && (
                    <div className="md:hidden border-t border-slate-200/90 dark:border-white/10 px-3 pb-3 pt-3">
                        {!isAuthRoute && (
                            <nav className="flex flex-col gap-1">
                                {navLinks.map(({ href, label }) => {
                                    const active = pathname === href || pathname.startsWith(`${href}/`);
                                    return (
                                        <Link
                                            key={href}
                                            href={href}
                                            className={`px-3 py-2 rounded-lg text-sm transition-colors ${active
                                                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold'
                                                : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                                                }`}
                                        >
                                            {label}
                                        </Link>
                                    );
                                })}
                            </nav>
                        )}

                        <div className="mt-3 flex flex-col gap-2">
                            {user ? (
                                <>
                                    <button
                                        onClick={() => router.push('/profile')}
                                        className="h-10 rounded-lg border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                    >
                                        Profile
                                    </button>
                                    <button
                                        onClick={async () => {
                                            await signOut();
                                            router.push('/');
                                        }}
                                        className="h-10 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-semibold transition-colors"
                                    >
                                        Sign Out
                                    </button>
                                </>
                            ) : isAuthRoute ? (
                                <Link href="/" className="h-10 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-semibold inline-flex items-center justify-center transition-colors">
                                    Home
                                </Link>
                            ) : (
                                <>
                                    <Link href="/login" className="h-10 rounded-lg border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-700 dark:text-slate-200 inline-flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                        Login
                                    </Link>
                                    <Link href="/signup" className="h-10 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-semibold inline-flex items-center justify-center transition-colors">
                                        Sign Up
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
}
