'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useState, useEffect, useCallback, useRef } from 'react';

const STORAGE_KEY = 'scholarform_notifications';
const loadNotifications = () => {
    if (typeof window === 'undefined') return [];
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch { return []; }
};

export default function NotificationsPage() {
    usePageTitle('Notifications');
    const [notifications, setNotifications] = useState([]);
    const [undoState, setUndoState] = useState(null);
    const undoTimeoutRef = useRef(null);

    useEffect(() => { setNotifications(loadNotifications()); }, []);
    useEffect(() => {
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(notifications)); } catch { /* ignore */ }
    }, [notifications]);

    const markAsRead = useCallback((id) => setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n)), []);
    const markAllRead = useCallback(() => {
        setNotifications((prev) => {
            if (!prev.some(n => !n.read)) return prev;
            setUndoState(prev);
            if (undoTimeoutRef.current) clearTimeout(undoTimeoutRef.current);
            undoTimeoutRef.current = setTimeout(() => setUndoState(null), 5000);
            return prev.map(n => ({ ...n, read: true }));
        });
    }, []);
    const handleUndo = useCallback(() => {
        if (undoState) { setNotifications(undoState); setUndoState(null); clearTimeout(undoTimeoutRef.current); }
    }, [undoState]);
    const deleteNotification = useCallback((id) => setNotifications((prev) => prev.filter((n) => n.id !== id)), []);
    const clearAll = useCallback(() => setNotifications([]), []);
    const unreadCount = notifications.filter((n) => !n.read).length;

    const typeIcon = (type) => {
        const map = { success: ['check_circle', 'text-green-500'], error: ['error', 'text-red-500'], info: ['info', 'text-blue-500'], warning: ['warning', 'text-amber-500'] };
        const [icon, color] = map[type] || map.info;
        return <span className={`material-symbols-outlined ${color}`}>{icon}</span>;
    };

    const formatTime = (ts) => {
        try {
            const diff = Date.now() - new Date(ts);
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
            return new Date(ts).toLocaleDateString();
        } catch { return ''; }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 animate-in fade-in duration-500">
            <main className="max-w-3xl mx-auto px-4 py-8">
                <div className="flex items-center justify-between mb-8 gap-4">
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-4xl">notifications</span>
                        Notifications
                        {unreadCount > 0 && <span className="px-2 py-0.5 text-sm bg-red-500 text-white rounded-full font-medium">{unreadCount}</span>}
                    </h1>
                    <div className="flex gap-2 shrink-0">
                        {unreadCount > 0 && <button onClick={markAllRead} className="text-sm px-3 py-2 text-primary hover:bg-primary/10 rounded-lg transition-colors min-h-[44px]">Mark all read</button>}
                        {notifications.length > 0 && <button onClick={clearAll} className="text-sm px-3 py-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors min-h-[44px]">Clear all</button>}
                    </div>
                </div>

                {undoState && (
                    <div className="mb-6 flex items-center justify-between p-4 bg-slate-800 text-white rounded-lg shadow-lg animate-in slide-in-from-top-2 duration-300">
                        <span className="text-sm font-medium">All notifications marked as read.</span>
                        <button onClick={handleUndo} className="text-sm font-bold text-blue-400 hover:text-blue-300 transition-colors uppercase tracking-wide">Undo</button>
                    </div>
                )}

                {notifications.length === 0 ? (
                    <div className="text-center py-16">
                        <span className="material-symbols-outlined text-6xl text-slate-300 dark:text-slate-600">notifications_none</span>
                        <p className="text-slate-500 dark:text-slate-400 mt-4 text-lg">No notifications yet</p>
                        <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">You&apos;ll see processing updates and system alerts here.</p>
                    </div>
                ) : (
                    <ul className="space-y-2">
                        {notifications.map((n) => (
                            <li key={n.id}
                                className={`flex items-start gap-3 p-4 rounded-xl border transition-all cursor-pointer hover:shadow-md ${n.read ? 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800' : 'bg-primary/5 border-primary/20'}`}
                                onClick={() => markAsRead(n.id)}>
                                <div className="mt-0.5">{typeIcon(n.type)}</div>
                                <div className="flex-1 min-w-0">
                                    <p className={`text-sm ${n.read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-white font-medium'}`}>{n.message}</p>
                                    <p className="text-xs text-slate-400 mt-1">{formatTime(n.timestamp)}</p>
                                </div>
                                <button onClick={(e) => { e.stopPropagation(); deleteNotification(n.id); }}
                                    className="text-slate-400 hover:text-red-500 transition-colors p-1 rounded min-w-[36px] min-h-[36px] flex items-center justify-center"
                                    aria-label="Delete notification">
                                    <span className="material-symbols-outlined text-lg">close</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </main>
        </div>
    );
}
