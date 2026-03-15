'use client';

import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
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
    const searchParams = useSearchParams();
    const router = useRouter();
    const { user } = useAuth();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const forceGuestMode = searchParams?.get('guest') === '1';
    const uiUser = forceGuestMode ? null : user;
    const guestParam = forceGuestMode ? '?guest=1' : '';

    const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));
    const isLandingRoute = pathname === '/';
    const isSimplePageRoute = pathname === '/terms' || pathname === '/privacy';
    const isUploadRoute = pathname === '/upload';

    const activeMode = section === 'generator'
        ? 'generator'
        : section === 'formatter'
            ? 'formatter'
            : pathname.startsWith('/generate')
                ? 'generator'
                : 'formatter';

    const navLinks = uiUser ? USER_LINKS_BY_MODE[activeMode] : APP_GUEST_LINKS;
    const showModeSwitch = !isAuthRoute;
    const logoHref = uiUser ? '/dashboard' : '/';

    const toggleMode = (mode) => {
        if (mode === activeMode) return;
        if (mode === 'generator') {
            router.push('/generate');
            return;
        }
        router.push(uiUser ? '/dashboard' : '/upload');
    };

    const actionHref = uiUser
        ? activeMode === 'generator'
            ? '/generate'
            : '/upload'
        : '/signup';

    const actionLabel = uiUser
        ? activeMode === 'generator'
            ? 'New Draft'
            : 'New Format'
        : 'Get Started';

    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [pathname]);

    // Reusable Logo Component
    const Logo = () => (
        <Link href={logoHref} className="flex items-center gap-2 sm:gap-3 shrink-0 group">
            <div className="flex items-center justify-center size-10 sm:size-12">
                <span className="material-symbols-outlined text-[32px] sm:text-[38px] text-blue-700 dark:text-blue-400">auto_stories</span>
            </div>
            <p className="text-[20px] sm:text-[24px] lg:text-[28px] font-black tracking-tight text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                ScholarForm AI
            </p>
        </Link>
    );

    // Reusable Mobile Menu Component
    const MobileNavMenu = () => (
        <div className="lg:hidden py-4 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 animate-in slide-in-from-top-4">
            <nav className="flex flex-col gap-2 px-2">
                {isLandingRoute && (
                    <>
                        {[{ h: '/#features', l: 'Features' }, { h: '/#templates', l: 'Templates' }, { h: '/#pricing', l: 'Pricing' }, { h: '/#about', l: 'About' }].map(link => (
                            <Link key={link.h} href={link.h} className="px-4 py-3 text-[15px] font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl transition-colors">
                                {link.l}
                            </Link>
                        ))}
                    </>
                )}
                {!isLandingRoute && !isAuthRoute && navLinks.map(({ href, label }) => (
                    <Link key={href} href={href} className="px-4 py-3 text-[15px] font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl transition-colors">
                        {label}
                    </Link>
                ))}
                
                <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col gap-2">
                    {uiUser ? (
                        <Link href="/dashboard" className="px-4 py-3 text-center text-[15px] font-bold text-white bg-primary hover:bg-primary-hover rounded-xl shadow-lg shadow-primary/20 transition-all">
                            Go to Dashboard
                        </Link>
                    ) : (
                        <>
                            <Link href={`/login${guestParam}`} className="px-4 py-3 text-center text-[15px] font-bold text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
                                Login
                            </Link>
                            <Link href={`/signup${guestParam}`} className="px-4 py-3 text-center text-[15px] font-bold text-white bg-primary hover:bg-primary-hover rounded-xl shadow-lg shadow-primary/20 transition-all">
                                Sign Up Free
                            </Link>
                        </>
                    )}
                </div>
            </nav>
        </div>
    );

    // Branch 1: Landing / Auth / Simple Pages
    if (isLandingRoute || isAuthRoute || isSimplePageRoute) {
        return (
            <header className="app-header sticky top-0 z-50 w-full">
                <div className="mx-auto max-w-[1240px] px-4 sm:px-6">
                    <div className="flex h-[72px] items-center justify-between gap-4">
                        <Logo />

                        {/* Desktop Mid Navigation */}
                        {isLandingRoute && (
                            <nav className="hidden lg:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
                                {['Features', 'Templates', 'Pricing', 'About'].map(item => (
                                    <Link key={item} href={`/#${item.toLowerCase()}`} className="text-[15px] font-semibold text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary transition-colors">
                                        {item}
                                    </Link>
                                ))}
                            </nav>
                        )}

                        <div className="ml-auto flex items-center gap-3 shrink-0">
                            <ThemeToggle />
                            
                            {/* Desktop Actions */}
                            <div className="hidden lg:flex items-center gap-4">
                                {uiUser ? (
                                    <>
                                        <Link href="/dashboard" className="text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Dashboard</Link>
                                        <button onClick={() => router.push('/settings')} className="h-10 w-10 rounded-full border border-slate-200 dark:border-white/10 surface-ladder-border-10 bg-white dark:bg-slate-800 hover:bg-slate-50 transition-all p-0.5" aria-label="Profile">
                                            <div className="w-full h-full rounded-full bg-violet-100 dark:bg-white/10 flex items-center justify-center text-slate-700 dark:text-slate-100">
                                                <span className="material-symbols-outlined text-[20px] leading-none">account_circle</span>
                                            </div>
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <Link href="/login" className="text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Login</Link>
                                        <Link href="/signup" className="h-10 px-5 inline-flex items-center justify-center rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-bold shadow-lg shadow-primary/20 transition-all">Sign Up</Link>
                                    </>
                                )}
                            </div>

                            {/* Mobile Hamburger */}
                            <button
                                type="button"
                                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                                className="lg:hidden flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                                aria-label="Toggle menu"
                            >
                                <span className="material-symbols-outlined text-[24px]">
                                    {isMobileMenuOpen ? 'close' : 'menu'}
                                </span>
                            </button>
                        </div>
                    </div>
                    {isMobileMenuOpen && <MobileNavMenu />}
                </div>
            </header>
        );
    }

    // Branch 2: Sidebar Layout (App Routes)
    if (isSidebarLayout) {
        return (
            <header className="app-header sticky top-0 z-50 w-full">
                <div className={isUploadRoute ? "mx-auto max-w-[1600px] px-4 xl:px-8" : "mx-auto max-w-[1240px] px-4 sm:px-6"}>
                    <div className="flex h-14 items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                            <button
                                type="button"
                                onClick={onOpenMobileSidebar}
                                className="h-10 w-10 inline-flex items-center justify-center rounded-xl hover:bg-slate-100 dark:hover:bg-white/10 active:scale-[0.98] transition-all text-slate-700 dark:text-slate-300 shrink-0"
                                aria-label="Toggle Sidebar"
                            >
                                <span className="material-symbols-outlined text-[24px]">menu</span>
                            </button>
                            <Link href={logoHref} className="flex items-center gap-2 group">
                                <span className="material-symbols-outlined text-[28px] text-primary">auto_stories</span>
                                <span className="font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors text-[17px] hidden sm:block">
                                    ScholarForm AI
                                </span>
                            </Link>
                        </div>

                        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
                            <ThemeToggle />
                            {uiUser ? (
                                <>
                                    <NotificationBell />
                                    <button onClick={() => router.push('/settings')} className="h-10 w-10 hidden sm:inline-flex items-center justify-center rounded-xl hover:bg-slate-100 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 transition-all" aria-label="Settings">
                                        <span className="material-symbols-outlined text-[22px]">settings</span>
                                    </button>
                                    <button onClick={() => router.push('/profile')} className="h-10 w-10 rounded-full border border-slate-200 dark:border-white/10 surface-ladder-border-10 bg-white dark:bg-slate-800 hover:bg-slate-50 transition-all p-0.5">
                                        <div className="w-full h-full rounded-full bg-violet-100 dark:bg-white/10 flex items-center justify-center text-slate-700 dark:text-slate-100">
                                            <span className="material-symbols-outlined text-[20px] leading-none">account_circle</span>
                                        </div>
                                    </button>
                                </>
                            ) : (
                                <div className="flex items-center gap-2 sm:gap-3">
                                    <Link href={`/login${guestParam}`} className="h-9 px-3 inline-flex items-center rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors">Login</Link>
                                    <Link href={`/signup${guestParam}`} className="h-9 px-4 inline-flex items-center rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-bold transition-opacity">Sign Up</Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </header>
        );
    }

    // Branch 3: Default Layout (App pages without sidebar layout)
    return (
        <header className="app-header sticky top-0 z-50 w-full">
            <div className="mx-auto max-w-[1240px] px-4 sm:px-6">
                <div className="flex h-[72px] items-center justify-between gap-4">
                    <Logo />

                    <div className="flex-1" />

                    <div className="ml-auto flex items-center gap-3 shrink-0">
                        <ThemeToggle />
                        
                        {/* Desktop Navigation Links */}
                        {!isAuthRoute && (
                            <nav className="hidden lg:flex items-center gap-4">
                                {navLinks.map(({ href, label }) => {
                                    const active = isInternalPath(href) ? pathname === href || pathname.startsWith(`${href}/`) : false;
                                    return (
                                        <Link key={href} href={href} className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${active ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10'}`}>
                                            {label}
                                        </Link>
                                    );
                                })}
                            </nav>
                        )}

                        <div className="hidden lg:flex items-center gap-3 ml-2">
                            {uiUser ? (
                                <>
                                    <NotificationBell />
                                    <button onClick={() => router.push('/settings')} className="h-10 w-10 rounded-full border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-800 hover:bg-slate-50 transition-all p-0.5">
                                        <div className="w-full h-full rounded-full bg-violet-100 dark:bg-white/10 flex items-center justify-center text-slate-700 dark:text-slate-100">
                                            <span className="material-symbols-outlined text-[20px] leading-none">account_circle</span>
                                        </div>
                                    </button>
                                </>
                            ) : (
                                <Link href="/signup" className="h-10 px-5 inline-flex items-center justify-center rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-bold shadow-lg shadow-primary/20 transition-all">Sign Up</Link>
                            )}
                        </div>

                        {/* Mobile Hamburger */}
                        <button
                            type="button"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="lg:hidden flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:bg-slate-50 transition-colors"
                            aria-label="Toggle menu"
                        >
                            <span className="material-symbols-outlined text-[24px]">
                                {isMobileMenuOpen ? 'close' : 'menu'}
                            </span>
                        </button>
                    </div>
                </div>
                {isMobileMenuOpen && <MobileNavMenu />}
            </div>
        </header>
    );
}
