import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@testing-library/react': fileURLToPath(new URL('./node_modules/@testing-library/react', import.meta.url)),
            '@testing-library/user-event': fileURLToPath(new URL('./node_modules/@testing-library/user-event', import.meta.url)),
        },
    },
    server: {
        fs: {
            allow: ['..'],
        },
    },
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/test/setup.js',
        include: [
            'src/**/*.{test,spec}.{js,jsx,ts,tsx}',
            '../tests/frontend/**/*.test.js',
        ],
    },
})
