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

    // New Sidebar Architecture for App Routes
    return (
        <div className="appshell-root flex flex-col h-screen bg-slate-50 dark:bg-[#020617] overflow-hidden relative z-10 w-full transition-all duration-300">
            {/* Background Glow Effects (App Shell Specific — Premium Feel) */}
            <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] pointer-events-none z-0 opacity-0 dark:opacity-100 transition-opacity duration-1000"></div>
            <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none z-0 opacity-0 dark:opacity-100 transition-opacity duration-1000"></div>
            <div className="fixed top-[20%] right-[10%] w-[25%] h-[25%] bg-blue-400/5 rounded-full blur-[100px] pointer-events-none z-0 opacity-0 dark:opacity-70 transition-opacity duration-1000"></div>

            {/* Full-Width Header */}
            <Header
                section={section}
                isSidebarLayout={true}
                onOpenMobileSidebar={toggleSidebar}
            />

            <div className="flex flex-1 overflow-hidden relative w-full h-full">
                {/* Desktop Sidebar (Push/Collapse to Icon Rail) */}
                <div
                    className={`sidebar-desktop hidden lg:flex flex-col border-r border-slate-200/50 bg-white/60 backdrop-blur-2xl h-full shadow-[4px_0_24px_rgba(0,0,0,0.02)] z-20 transition-all duration-300 ease-in-out ${isDesktopSidebarOpen ? 'w-[240px]' : 'w-[72px] items-center'
                        }`}
                >
                    <div className="w-full h-full flex flex-col overflow-hidden">
                        <Sidebar section={section} isCollapsed={!isDesktopSidebarOpen} />
                    </div>
                </div>

                {/* Mobile Sidebar Overlay */}
                {isMobileSidebarOpen && (
                    <div className="lg:hidden fixed inset-0 z-50 flex">
                        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm" onClick={() => setIsMobileSidebarOpen(false)} />
                        <div className="sidebar-mobile relative flex flex-col w-[260px] h-full bg-white shadow-2xl animate-in slide-in-from-left duration-300">
                            <Sidebar section={section} onClose={() => setIsMobileSidebarOpen(false)} isCollapsed={false} />
                        </div>
                    </div>
                )}

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto w-full relative z-10 custom-scrollbar">
                    {children}
                </main>
            </div>
        </div>
    );
}
