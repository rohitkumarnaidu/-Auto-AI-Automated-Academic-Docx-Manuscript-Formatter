export const STORAGE_KEY = 'scholarform_notifications';

const createId = () => {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
        return crypto.randomUUID();
    }
    return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
};

export const createNotification = (type, message, meta = {}) => ({
    id: createId(),
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
