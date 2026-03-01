import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vitest/config';

export default defineConfig({
    resolve: {
        alias: {
            '@testing-library/react': fileURLToPath(new URL('./node_modules/@testing-library/react', import.meta.url)),
            '@testing-library/user-event': fileURLToPath(new URL('./node_modules/@testing-library/user-event', import.meta.url)),
            'next/navigation': fileURLToPath(new URL('./__mocks__/next/navigation.js', import.meta.url)),
        },
    },
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/test/setup.js',
        include: [
            'src/services/**/*.{test,spec}.{js,jsx,ts,tsx}',
            'src/components/**/*.{test,spec}.{js,jsx,ts,tsx}',
        ],
        exclude: [
            'src/test/**',
            '../tests/frontend/**',
            'src/_vite_pages/**',
        ],
    },
    server: {
        fs: {
            allow: ['..'],
        },
    },
});
