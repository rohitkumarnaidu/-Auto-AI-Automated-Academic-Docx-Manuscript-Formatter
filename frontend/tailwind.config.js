/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#136dec",
                "background-light": "#f6f7f8",
                "background-dark": "#101822",
                "diff-add": "#dcfce7",
                "diff-remove": "#fee2e2",
                "diff-mod": "#fef9c3",
                "diff-text-add": "#166534",
                "diff-text-remove": "#991b1b",
                "diff-text-mod": "#854d0e",
            },
            fontFamily: {
                "display": ["Inter", "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "full": "9999px"
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/container-queries'),
    ],
}
