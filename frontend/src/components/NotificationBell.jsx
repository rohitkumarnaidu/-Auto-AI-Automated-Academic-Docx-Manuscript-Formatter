'use client';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { loadNotifications, saveNotifications, STORAGE_KEY } from '@/src/utils/notifications';
import { supabase } from '@/src/lib/supabaseClient';
import { useAuth } from '@/src/context/AuthContext';

export default function NotificationBell() {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const dropdownRef = useRef(null);
    const router = useRouter();
    const { user } = useAuth();

    useEffect(() => {
        setNotifications(loadNotifications());

        const handleStorage = (e) => {
            if (e.key === STORAGE_KEY) {
                setNotifications(loadNotifications());
            }
        };
        window.addEventListener('storage', handleStorage);

        const checkInterval = setInterval(() => {
            setNotifications(loadNotifications());
        }, 30000);

        return () => {
            window.removeEventListener('storage', handleStorage);
            clearInterval(checkInterval);
        };
    }, []);

    useEffect(() => {
        if (!user?.id || !supabase) return;

        const channel = supabase
            .channel(`public:notifications:${user.id}`)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'notifications',
                    filter: `user_id=eq.${user.id}`,
                },
                (payload) => {
                    const newNotification = {
                        id: payload.new.id || String(Date.now()),
                        type: payload.new.type || 'info',
                        message: payload.new.message,
                        read: payload.new.read || false,
                        timestamp: payload.new.created_at || new Date().toISOString(),
                    };
                    setNotifications((prev) => {
                        const updated = [newNotification, ...prev].slice(0, 50);
                        saveNotifications(updated);
                        return updated;
                    });
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, [user?.id]);

    useEffect(() => {
        const handleClick = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    const unreadCount = notifications.filter((n) => !n.read).length;
    const recentItems = notifications.slice(0, 5);

    const formatTime = (ts) => {
        try {
            const diff = Date.now() - new Date(ts).getTime();
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
            return `${Math.floor(diff / 86400000)}d`;
        } catch {
            return '';
        }
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen((open) => !open)}
                className="relative p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                aria-label="Notifications"
                aria-expanded={isOpen}
                aria-haspopup="menu"
            >
                <span className="material-symbols-outlined">notifications</span>
                {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow-2xl z-50 overflow-hidden" role="menu" aria-label="Notifications menu">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white">Notifications</p>
                        {unreadCount > 0 && (
                            <span className="text-xs px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full">
                                {unreadCount} new
                            </span>
                        )}
                    </div>

                    {recentItems.length === 0 ? (
                        <div className="px-4 py-8 text-center">
                            <span className="material-symbols-outlined text-3xl text-slate-300 dark:text-slate-600">notifications_none</span>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">No notifications</p>
                        </div>
                    ) : (
                        <ul className="max-h-72 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                            {recentItems.map((n) => (
                                <li
                                    key={n.id}
                                    className={`px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors ${!n.read ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''}`}
                                >
                                    <p className={`text-sm ${n.read ? 'text-slate-500' : 'text-slate-900 dark:text-white font-medium'} line-clamp-2`}>
                                        {n.message}
                                    </p>
                                    <p className="text-xs text-slate-400 mt-1">{formatTime(n.timestamp)}</p>
                                </li>
                            ))}
                        </ul>
                    )}

                    <div className="border-t border-slate-200 dark:border-slate-700 px-4 py-2">
                        <button
                            onClick={() => { setIsOpen(false); router.push('/notifications'); }}
                            className="w-full text-center text-sm text-primary font-medium py-1 hover:underline"
                        >
                            View all notifications
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
