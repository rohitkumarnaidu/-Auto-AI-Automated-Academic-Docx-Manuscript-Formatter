'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import ModeSwitcher from '@/components/header/ModeSwitcher';
import ThemeToggle from '@/components/header/ThemeToggle';
import { useAuth } from '@/src/context/AuthContext';

const AUTH_ROUTES = ['/login', '/signup', '/forgot-password', '/verify-otp', '/reset-password', '/auth/callback'];

const GUEST_LINKS = [
    { href: '/', label: 'Home' },
    { href: '/templates', label: 'Templates' },
    { href: '/#pricing', label: 'Pricing' },
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

export default function Header({ section = 'shared' }) {
    const pathname = usePathname();
    const router = useRouter();
    const { user } = useAuth();

    const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));
    const activeMode = section === 'generator'
        ? 'generator'
        : section === 'formatter'
            ? 'formatter'
            : pathname.startsWith('/generate')
                ? 'generator'
                : 'formatter';
    const navLinks = user ? USER_LINKS_BY_MODE[activeMode] : GUEST_LINKS;

    const toggleMode = (mode) => {
        if (mode === activeMode) return;
        router.push(mode === 'generator' ? '/generate' : '/dashboard');
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
    const actionIcon = user
        ? activeMode === 'generator'
            ? 'auto_awesome'
            : 'add'
        : null;

    const canShowModeSwitch = Boolean(user) && !isAuthRoute;
    const logoHref = user ? '/dashboard' : '/';

    return (
        <header className="sticky top-0 z-50 glass-nav w-full animate-in slide-in-from-top-2 duration-300">
            <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                <Link href={logoHref} className="flex items-center gap-3 cursor-pointer">
                    <div className="flex items-center justify-center size-10 rounded-xl bg-gradient-to-br from-primary to-blue-600 text-white shadow-lg shadow-primary/20">
                        <span className="material-symbols-outlined text-[24px]">school</span>
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white hidden sm:block">
                        ScholarFormat
                    </h1>
                </Link>

                {canShowModeSwitch ? (
                    <div className="flex justify-center flex-1">
                        <div className="glass-panel p-1.5 rounded-2xl md:inline-flex hidden relative shadow-xl focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2 focus-within:ring-offset-background-dark transition-all">
                            <ModeSwitcher activeMode={activeMode} onChange={toggleMode} />
                        </div>
                    </div>
                ) : (
                    <div className="flex-1"></div>
                )}

                <div className="flex items-center gap-4">
                    <ThemeToggle />
                    {user ? (
                        <>
                            <nav className="hidden lg:flex items-center gap-6 mr-4">
                                {navLinks.map(({ href, label }) => {
                                    const active = isInternalPath(href)
                                        ? pathname === href || pathname.startsWith(`${href}/`)
                                        : false;
                                    return (
                                        <Link
                                            key={href}
                                            href={href}
                                            className={`text-sm font-medium transition-colors ${active
                                                ? 'text-primary dark:text-white'
                                                : 'text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-white'
                                                }`}
                                        >
                                            {label}
                                        </Link>
                                    );
                                })}
                            </nav>

                            <button
                                onClick={() => router.push(actionHref)}
                                className="hidden sm:flex items-center justify-center h-10 px-5 rounded-lg bg-primary hover:bg-primary-hover active:scale-95 text-white text-sm font-semibold transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40 focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900"
                            >
                                {actionIcon && <span className="material-symbols-outlined text-[20px] mr-2">{actionIcon}</span>}
                                {actionLabel}
                            </button>

                            <button onClick={() => router.push('/profile')} className="h-10 w-10 shrink-0 rounded-full overflow-hidden border-2 border-slate-700 cursor-pointer hover:border-primary focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors active:scale-95" aria-label="User Profile">
                                <div className="w-full h-full bg-surface-dark flex items-center justify-center text-primary font-bold">
                                    {user.email?.charAt(0).toUpperCase() || 'U'}
                                </div>
                            </button>
                        </>
                    ) : (
                        <div className="flex items-center gap-3">
                            <nav className="hidden lg:flex items-center gap-6 mr-2">
                                {GUEST_LINKS.map(({ href, label }) => (
                                    <Link key={href} href={href} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">
                                        {label}
                                    </Link>
                                ))}
                            </nav>
                            <Link href="/login" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Sign In</Link>
                            <Link href={actionHref} className="flex items-center justify-center h-10 px-5 rounded-lg bg-primary hover:bg-primary-hover active:scale-95 text-white text-sm font-semibold transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40 focus:ring-2 focus:ring-primary focus:ring-offset-2">
                                {actionLabel}
                            </Link>
                        </div>
                    )}
                </div>
            </div>

            {canShowModeSwitch && (
                <div className="md:hidden flex justify-center py-2 px-4 border-t border-glass-border">
                    <ModeSwitcher activeMode={activeMode} onChange={toggleMode} compact />
                </div>
            )}
        </header>
    );
}
