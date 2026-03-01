import forms from '@tailwindcss/forms';
import containerQueries from '@tailwindcss/container-queries';

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
        "./app/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}"
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#6c2bee",
                "primary-hover": "#5b22cd",
                "background-light": "#f6f6f8",
                "background-dark": "#0f172a",
                "surface-dark": "#1e293b",
                "glass-border": "rgba(255, 255, 255, 0.08)",
                "glass-surface": "rgba(30, 41, 59, 0.7)",
                "diff-add": "#dcfce7",
                "diff-remove": "#fee2e2",
                "diff-mod": "#fef9c3",
                "diff-text-add": "#166534",
                "diff-text-remove": "#991b1b",
                "diff-text-mod": "#854d0e",
                "accent": "#8B5CF6",
                "accent-warm": "#F59E0B",
            },
            fontFamily: {
                "display": ['"Manrope"', "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.5rem",
                "lg": "1rem",
                "xl": "1.5rem",
                "2xl": "2rem",
                "full": "9999px"
            },
            backgroundImage: {
                'glow-radial': 'radial-gradient(circle at center, var(--tw-gradient-stops))',
            }
        },
    },
    plugins: [
        forms,
        containerQueries,
    ],
}
