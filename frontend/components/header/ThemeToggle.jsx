'use client';

import { useTheme } from '@/src/context/ThemeContext';

export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();
    const isDark = theme === 'dark';

    return (
        <button
            onClick={toggleTheme}
            className="flex h-10 w-10 items-center justify-center text-slate-600 dark:text-slate-300 hover:text-primary dark:hover:text-primary-hover transition-colors active:scale-95 focus:outline-none"
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
            <span className="material-symbols-outlined text-[20px]">
                {isDark ? 'light_mode' : 'dark_mode'}
            </span>
        </button>
    );
}
