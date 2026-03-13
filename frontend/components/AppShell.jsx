'use client';

import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

const AUTH_ROUTES = ['/login', '/signup', '/forgot-password', '/verify-otp', '/reset-password', '/auth/callback'];

export default function AppShell({ children, section = 'shared' }) {
    const pathname = usePathname();

    const [isDesktopSidebarOpen, setIsDesktopSidebarOpen] = useState(false);
    const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
    const [isDesktop, setIsDesktop] = useState(false);

    const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));
    const isLandingRoute = pathname === '/' || pathname === '/terms' || pathname === '/privacy';

    // Route-based: app routes (upload, dashboard, templates, etc.) get sidebar layout.
    // Landing + auth pages get simple layout.
    // Sidebar.jsx handles guest vs user links internally (APP_GUEST_LINKS vs USER_LINKS).
    const showSidebarLayout = !isLandingRoute && !isAuthRoute;

    useEffect(() => {
        if (typeof window === 'undefined') {
            return undefined;
        }

        const mediaQuery = window.matchMedia('(min-width: 1024px)');
        const handleChange = (event) => {
            setIsDesktop(event.matches);
            if (!event.matches) {
                setIsDesktopSidebarOpen(false);
            }
        };

        setIsDesktop(mediaQuery.matches);

        if (typeof mediaQuery.addEventListener === 'function') {
            mediaQuery.addEventListener('change', handleChange);
            return () => mediaQuery.removeEventListener('change', handleChange);
        }

        mediaQuery.addListener(handleChange);
        return () => mediaQuery.removeListener(handleChange);
    }, []);

    const toggleSidebar = () => {
        if (isDesktop) {
            setIsDesktopSidebarOpen((prev) => !prev);
        } else {
            setIsMobileSidebarOpen(true);
        }
    };

    // Simple layout for landing + auth pages only
    if (!showSidebarLayout) {
        return (
            <div className="relative z-10 flex flex-col min-h-screen">
                <Header section={section} />
                <main id="main-content" tabIndex="-1" className="flex-grow flex flex-col items-center w-full relative z-10 focus:outline-none">
                    {children}
                </main>
            </div>
        );
    }

    // ── APP ROUTES: sidebar layout for both guests and logged-in users ──
    // Sidebar.jsx shows guest links (Upload, Templates, Template Editor) or user links (Dashboard, etc.)
    const appHeaderHeightPx = 48;
    const sidebarW = isDesktopSidebarOpen ? 240 : 72;

    return (
        <>
            {/* Background */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute inset-0 bg-[#f6f6f8] dark:bg-background-dark" />
            </div>

            {/* Fixed Header */}
            <div className="fixed top-0 left-0 right-0 z-50">
                <Header
                    section={section}
                    isSidebarLayout={true}
                    onOpenMobileSidebar={toggleSidebar}
                />
            </div>

            {/* Sidebar — shows for all users on app routes */}
            {/* Sidebar.jsx handles guest vs user links internally */}
            <div
                className={`fixed left-0 hidden lg:flex flex-col justify-start z-40 transition-all duration-300 ease-in-out overflow-y-auto sidebar-desktop bg-background-light dark:bg-background-dark ${isDesktopSidebarOpen ? 'w-[240px]' : 'w-[72px] items-center'}`}
                style={{ top: `${appHeaderHeightPx}px`, bottom: 0 }}
            >
                <div className="w-full h-full flex flex-col">
                    <Sidebar section={section} isCollapsed={!isDesktopSidebarOpen} />
                </div>
            </div>

            {/* Mobile Sidebar — for all users on app routes */}
            {isMobileSidebarOpen && (
                <div className="lg:hidden fixed inset-0 z-50 flex">
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setIsMobileSidebarOpen(false)} />
                    <div className="sidebar-mobile relative flex flex-col w-[260px] h-full shadow-2xl animate-in slide-in-from-left duration-300 bg-background-light dark:bg-background-dark">
                        <Sidebar section={section} onClose={() => setIsMobileSidebarOpen(false)} isCollapsed={false} />
                    </div>
                </div>
            )}

            {/* Main content — sidebar padding only for logged-in users */}
            <main
                id="main-content"
                tabIndex="-1"
                className="appshell-main relative z-10 min-h-screen custom-scrollbar focus:outline-none"
                style={{
                    paddingTop: `${appHeaderHeightPx}px`,
                    paddingLeft: isDesktop ? `${sidebarW}px` : '0px',
                }}
            >
                {children}
            </main>
        </>
    );
}

