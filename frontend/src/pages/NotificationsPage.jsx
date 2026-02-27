import usePageTitle from '../hooks/usePageTitle';
import { useState, useEffect, useCallback } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const STORAGE_KEY = 'scholarform_notifications';

const createNotification = (type, message, meta = {}) => ({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    type,
    message,
    read: false,
    timestamp: new Date().toISOString(),
    ...meta,
});

const loadNotifications = () => {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
};

const saveNotifications = (items) => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {
        /* ignore quota errors */
    }
};

export default function NotificationsPage() {
    usePageTitle('Notifications');
    const [notifications, setNotifications] = useState(loadNotifications);

    useEffect(() => {
        saveNotifications(notifications);
    }, [notifications]);

    const markAsRead = useCallback((id) => {
        setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
    }, []);

    const markAllRead = useCallback(() => {
        setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    }, []);

    const deleteNotification = useCallback((id) => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, []);

    const clearAll = useCallback(() => {
        setNotifications([]);
    }, []);

    const unreadCount = notifications.filter((n) => !n.read).length;

    const typeIcon = (type) => {
        const icons = {
            success: { icon: 'check_circle', color: 'text-green-500' },
            error: { icon: 'error', color: 'text-red-500' },
            info: { icon: 'info', color: 'text-blue-500' },
            warning: { icon: 'warning', color: 'text-amber-500' },
        };
        const cfg = icons[type] || icons.info;
        return <span className={`material-symbols-outlined ${cfg.color}`}>{cfg.icon}</span>;
    };

    const formatTime = (ts) => {
        try {
            const d = new Date(ts);
            const now = new Date();
            const diff = now - d;
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
            return d.toLocaleDateString();
        } catch {
            return '';
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
            <Navbar />
            <main className="max-w-3xl mx-auto px-4 py-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                            <span className="material-symbols-outlined text-primary text-4xl">notifications</span>
                            Notifications
                            {unreadCount > 0 && (
                                <span className="px-2 py-0.5 text-sm bg-red-500 text-white rounded-full font-medium">
                                    {unreadCount}
                                </span>
                            )}
                        </h1>
                    </div>
                    <div className="flex gap-2">
                        {unreadCount > 0 && (
                            <button
                                onClick={markAllRead}
                                className="text-sm px-3 py-2 text-primary hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                            >
                                Mark all read
                            </button>
                        )}
                        {notifications.length > 0 && (
                            <button
                                onClick={clearAll}
                                className="text-sm px-3 py-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                            >
                                Clear all
                            </button>
                        )}
                    </div>
                </div>

                {notifications.length === 0 ? (
                    <div className="text-center py-16">
                        <span className="material-symbols-outlined text-6xl text-slate-300 dark:text-slate-600">notifications_none</span>
                        <p className="text-slate-500 dark:text-slate-400 mt-4 text-lg">No notifications yet</p>
                        <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">
                            You'll see processing updates, feedback responses, and system alerts here.
                        </p>
                    </div>
                ) : (
                    <ul className="space-y-2">
                        {notifications.map((n) => (
                            <li
                                key={n.id}
                                className={`flex items-start gap-3 p-4 rounded-xl border transition-colors cursor-pointer ${n.read
                                    ? 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800'
                                    : 'bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800'
                                    }`}
                                onClick={() => markAsRead(n.id)}
                            >
                                <div className="mt-0.5">{typeIcon(n.type)}</div>
                                <div className="flex-1 min-w-0">
                                    <p className={`text-sm ${n.read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-white font-medium'}`}>
                                        {n.message}
                                    </p>
                                    <p className="text-xs text-slate-400 mt-1">{formatTime(n.timestamp)}</p>
                                </div>
                                <button
                                    onClick={(e) => { e.stopPropagation(); deleteNotification(n.id); }}
                                    className="text-slate-400 hover:text-red-500 transition-colors mt-0.5"
                                >
                                    <span className="material-symbols-outlined text-lg">close</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </main>
            <Footer />
        </div>
    );
}

export { createNotification, loadNotifications, saveNotifications, STORAGE_KEY };
