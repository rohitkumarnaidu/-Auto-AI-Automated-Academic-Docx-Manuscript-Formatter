'use client';
import { useTheme } from '@/src/context/ThemeContext';
import { useEffect } from 'react';

export default function DynamicMeta() {
    const { theme } = useTheme();

    useEffect(() => {
        const meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.content = theme === 'dark' ? '#0a0f1e' : '#f6f6f8';
        }
    }, [theme]);

    return null;
}
