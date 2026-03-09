'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/src/context/AuthContext';

const APP_GUEST_LINKS = [
    { href: '/upload', label: 'Upload', icon: 'upload_file' },
    { href: '/templates', label: 'Templates', icon: 'grid_view' },
    { href: '/template-editor', label: 'Template Editor', icon: 'edit_document' },
];

const USER_MAIN_LINKS_BY_MODE = {
    formatter: [
        { href: '/dashboard', label: 'Dashboard', icon: 'space_dashboard' },
        { href: '/upload', label: 'Upload', icon: 'upload_file' },
        { href: '/history', label: 'History', icon: 'history' },
        { href: '/templates', label: 'Templates', icon: 'grid_view' },
    ],
    generator: [
        { href: '/dashboard', label: 'Dashboard', icon: 'space_dashboard' },
        { href: '/generate', label: 'Generator', icon: 'magic_button' },
        { href: '/history', label: 'History', icon: 'history' },
        { href: '/templates', label: 'Templates', icon: 'grid_view' },
    ],
};

const USER_SECONDARY_LINKS = [
    { href: '/batch-upload', label: 'Batch Upload', icon: 'upload' },
    { href: '/template-editor', label: 'Template Editor', icon: 'edit_document' },
    { href: '/results', label: 'Validation Results', icon: 'fact_check' },
    { href: '/feedback', label: 'Feedback', icon: 'chat' },
];

const isInternalPath = (value) => value.startsWith('/') && !value.startsWith('//');
const RESULTS_ALIAS_PREFIXES = ['/compare', '/preview', '/edit', '/download'];

const isLinkActive = (pathname, href) => {
    if (!isInternalPath(href)) {
        return false;
    }

    if (href === '/results') {
        return pathname === '/results'
            || pathname.startsWith('/results/')
            || RESULTS_ALIAS_PREFIXES.some((prefix) => pathname.startsWith(prefix));
    }

    return pathname === href || pathname.startsWith(`${href}/`);
};

export default function Sidebar({ section = 'shared', onClose, isCollapsed = false }) {
    const pathname = usePathname();
    const router = useRouter();
    const { user, signOut } = useAuth();
    const isAdminUser = Boolean(
        user?.is_admin
        || user?.app_metadata?.role === 'admin'
        || user?.user_metadata?.role === 'admin'
        || user?.role === 'admin'
    );

    const activeMode = section === 'generator'
        ? 'generator'
        : section === 'formatter'
            ? 'formatter'
            : pathname.startsWith('/generate')
                ? 'generator'
                : 'formatter';

    const mainNavLinks = user ? USER_MAIN_LINKS_BY_MODE[activeMode] : APP_GUEST_LINKS;
    const secondaryNavLinks = user
        ? [
            ...USER_SECONDARY_LINKS,
            ...(isAdminUser ? [{ href: '/admin-dashboard', label: 'Admin Dashboard', icon: 'admin_panel_settings' }] : []),
        ]
        : [];

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
            ? 'edit_square'
            : 'add_circle'
        : 'rocket_launch';

    const handleNavigation = (href) => {
        router.push(href);
        if (onClose) onClose();
    };

    const handleModeChange = (newMode) => {
        if (!user) {
            router.push('/signup');
            return;
        }

        if (newMode === 'generator') {
            router.push('/generate');
        } else {
            router.push('/upload');
        }

        if (onClose) onClose();
    };

    const handleSignOut = async () => {
        await signOut({ redirectToLogin: true });
        if (onClose) onClose();
    };

    return (
        <div className={`flex flex-col h-full py-4 w-full ${isCollapsed ? 'px-2' : 'px-3'}`}>
            {/* Top Close Button for Mobile Overlay */}
            {onClose && (
                <div className="flex justify-end mb-4 pr-1">
                    <button onClick={onClose} className="lg:hidden p-1 text-slate-500 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="Close Sidebar">
                        <span className="material-symbols-outlined" aria-hidden="true">close</span>
                    </button>
                </div>
            )}

            {/* Mode Switcher */}
            <div className={`mb-3 ${isCollapsed ? 'px-0' : 'px-1'}`}>
                <div className={`flex flex-col gap-1 rounded-2xl bg-[#f0f1f3] dark:bg-white/5 border border-slate-200/50 dark:border-white/8 ${isCollapsed ? 'p-1' : 'p-1.5'}`}>
                    <button
                        onClick={() => handleModeChange('formatter')}
                        title={isCollapsed ? 'Formatter' : undefined}
                        className={`active-mode-btn flex items-center gap-3 py-2 rounded-xl text-[15px] transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${isCollapsed ? 'px-0 justify-center w-10 h-10 mx-auto' : 'px-3 w-full'
                            } ${activeMode === 'formatter'
                                ? 'bg-white dark:bg-white/10 shadow-sm text-slate-900 dark:text-white font-bold ring-1 ring-slate-900/5 dark:ring-white/10'
                                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white font-medium hover:bg-slate-200/50 dark:hover:bg-white/5'
                            }`}
                    >
                        <span className="material-symbols-outlined shrink-0 text-[20px]">format_align_left</span>
                        {!isCollapsed && <span className="truncate">Formatter</span>}
                    </button>
                    <button
                        onClick={() => handleModeChange('generator')}
                        title={isCollapsed ? 'Generator' : undefined}
                        className={`active-mode-btn flex items-center gap-3 py-2 rounded-xl text-[15px] transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${isCollapsed ? 'px-0 justify-center w-10 h-10 mx-auto' : 'px-3 w-full'
                            } ${activeMode === 'generator'
                                ? 'bg-white dark:bg-white/10 shadow-sm text-slate-900 dark:text-white font-bold ring-1 ring-slate-900/5 dark:ring-white/10'
                                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white font-medium hover:bg-slate-200/50 dark:hover:bg-white/5'
                            }`}
                    >
                        <span className="material-symbols-outlined shrink-0 text-[20px]">magic_button</span>
                        {!isCollapsed && <span className="truncate">Generator</span>}
                    </button>
                </div>
            </div>

            {/* Navigation Links — flex-1 fills remaining space */}
            <nav className="flex-1 flex flex-col gap-1.5 overflow-y-auto overflow-x-hidden custom-scrollbar">
                {mainNavLinks.map(({ href, label, icon }) => {
                    const active = isLinkActive(pathname, href);

                    return (
                        <button
                            key={href}
                            onClick={() => handleNavigation(href)}
                            title={isCollapsed ? label : undefined}
                            className={`active-nav-link flex items-center gap-3 py-2.5 rounded-xl text-[15px] font-semibold transition-all ${isCollapsed ? 'px-0 justify-center w-11 h-11 mx-auto' : 'px-3 w-full'
                                } ${active
                                    ? 'bg-primary/10 text-primary dark:bg-primary/25 dark:text-blue-400 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]'
                                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white'
                                }`}
                        >
                            <span className={`material-symbols-outlined shrink-0 text-[20px] ${active ? 'fill-current' : ''}`}>
                                {icon}
                            </span>
                            {!isCollapsed && <span className="truncate">{label}</span>}
                        </button>
                    );
                })}

                {secondaryNavLinks.length > 0 && (
                    <>
                        {secondaryNavLinks.map(({ href, label, icon }) => {
                            const active = isLinkActive(pathname, href);

                            return (
                                <button
                                    key={href}
                                    onClick={() => handleNavigation(href)}
                                    title={isCollapsed ? label : undefined}
                                    className={`active-nav-link flex items-center gap-3 py-2.5 rounded-xl text-[15px] font-semibold transition-all ${isCollapsed ? 'px-0 justify-center w-11 h-11 mx-auto' : 'px-3 w-full'
                                        } ${active
                                            ? 'bg-primary/10 text-primary dark:bg-primary/25 dark:text-blue-400 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]'
                                            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white'
                                        }`}
                                >
                                    <span className={`material-symbols-outlined shrink-0 text-[20px] ${active ? 'fill-current' : ''}`}>
                                        {icon}
                                    </span>
                                    {!isCollapsed && <span className="truncate">{label}</span>}
                                </button>
                            );
                        })}
                    </>
                )}
            </nav>

            {/* Action Button — BOTTOM, pushed down by flex-1 nav above */}
            <div className={`pt-4 flex flex-col gap-2 ${isCollapsed ? 'items-center' : ''}`}>
                <button
                    onClick={() => handleNavigation(actionHref)}
                    title={isCollapsed ? actionLabel : undefined}
                    className={`h-11 flex items-center justify-center gap-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-[15px] font-bold active:scale-[0.98] transition-all shadow-lg shadow-primary/20 shrink-0 overflow-hidden ${isCollapsed ? 'w-11 px-0' : 'w-full px-4'
                        }`}
                >
                    <span className="material-symbols-outlined shrink-0 text-[20px]">{actionIcon}</span>
                    {!isCollapsed && <span className="truncate">{actionLabel}</span>}
                </button>
                {user && (
                    <button
                        onClick={handleSignOut}
                        title={isCollapsed ? 'Sign Out' : undefined}
                        className={`h-10 flex items-center justify-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${isCollapsed ? 'w-11 px-0' : 'w-full px-4'}`}
                    >
                        <span className="material-symbols-outlined shrink-0 text-[20px]">logout</span>
                        {!isCollapsed && <span className="truncate font-semibold">Sign Out</span>}
                    </button>
                )}
            </div>
        </div>

    );
}


