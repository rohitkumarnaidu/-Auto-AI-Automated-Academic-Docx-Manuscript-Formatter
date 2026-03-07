'use client';

import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/src/context/AuthContext';
import { useState } from 'react';

const AUTH_ROUTES = ['/login', '/signup', '/forgot-password', '/verify-otp', '/reset-password', '/auth/callback'];

export default function AppShell({ children, section = 'shared' }) {
    const pathname = usePathname();
    const { user } = useAuth();

    // Desktop sidebar state (default closed / icon-rail)
    const [isDesktopSidebarOpen, setIsDesktopSidebarOpen] = useState(false);
    // Mobile sidebar state (default closed)
    const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

    // Exactly matches Header's logic to skip sidebar layout for Landing/Auth pages
    const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));
    const isLandingRoute = pathname === '/' || pathname === '/terms' || pathname === '/privacy';

    const showSidebarLayout = user || (!isLandingRoute && !isAuthRoute);

    const toggleSidebar = () => {
        // Different toggle logic based on screen size
        if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
            setIsDesktopSidebarOpen(!isDesktopSidebarOpen);
        } else {
            setIsMobileSidebarOpen(true);
        }
    };

    if (!showSidebarLayout) {
        // Legacy layout for Landing & Auth
        return (
            <div className="relative z-10 flex flex-col min-h-screen">
                <Header section={section} />
                <main className="flex-grow flex flex-col items-center w-full relative z-10">
                    {children}
                </main>
            </div>
        );
    }

    // Sidebar Architecture — fixed header + fixed sidebar + scrolling main
    const sidebarW = isDesktopSidebarOpen ? 240 : 72;

    return (
        <>
            {/* ── BACKGROUND LAYER ── */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute inset-0 bg-[#f6f6f8] dark:bg-gradient-to-br dark:from-slate-900 dark:via-[#0a0f1e] dark:to-indigo-950" />
            </div>

            {/* ── HEADER ── fixed at top */}
            <div className="fixed top-0 left-0 right-0 z-50">
                <Header
                    section={section}
                    isSidebarLayout={true}
                    onOpenMobileSidebar={toggleSidebar}
                />
            </div>

            {/* ── SIDEBAR ── fixed, starts at top: 56px (header height) to bottom */}
            <div
                className={`fixed left-0 hidden lg:flex flex-col justify-start z-40 transition-all duration-300 ease-in-out overflow-y-auto bg-white/60 dark:bg-slate-950/60 backdrop-blur-2xl border-r border-slate-200/50 dark:border-white/[0.06] ${isDesktopSidebarOpen ? 'w-[240px]' : 'w-[72px] items-center'}`}
                style={{ top: '56px', bottom: 0 }}
            >
                <div className="w-full h-full flex flex-col">
                    <Sidebar section={section} isCollapsed={!isDesktopSidebarOpen} />
                </div>
            </div>

            {/* Mobile Sidebar Overlay */}
            {isMobileSidebarOpen && (
                <div className="lg:hidden fixed inset-0 z-50 flex">
                    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm" onClick={() => setIsMobileSidebarOpen(false)} />
                    <div className="sidebar-mobile relative flex flex-col w-[260px] h-full shadow-2xl animate-in slide-in-from-left duration-300">
                        <Sidebar section={section} onClose={() => setIsMobileSidebarOpen(false)} isCollapsed={false} />
                    </div>
                </div>
            )}

            {/* ── MAIN ── scrolls up and BEHIND the fixed glass header */}
            <main
                className="appshell-main relative z-10 min-h-screen custom-scrollbar"
                style={{
                    paddingTop: '56px',
                    paddingLeft: `${sidebarW}px`,
                }}
            >
                {children}
            </main>
        </>
    );
}
