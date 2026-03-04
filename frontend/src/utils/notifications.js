export const STORAGE_KEY = 'scholarform_notifications';

export const createNotification = (type, message, meta = {}) => ({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    type,
    message,
    read: false,
    timestamp: new Date().toISOString(),
    ...meta,
});

export const loadNotifications = () => {
    if (typeof window === 'undefined') return [];
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
};

export const saveNotifications = (items) => {
    if (typeof window === 'undefined') return;
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {
        // ignore quota errors
    }
};
