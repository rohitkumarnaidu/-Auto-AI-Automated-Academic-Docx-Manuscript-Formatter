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
    build: {
        rollupOptions: {
            output: {
                manualChunks(id) {
                    if (!id.includes('node_modules')) {
                        return;
                    }

                    if (id.includes('@supabase')) {
                        return 'vendor-supabase';
                    }

                    if (id.includes('react-router')) {
                        return 'vendor-router';
                    }

                    if (id.includes('react-dom') || id.includes(`${'/'}react${'/'}`)) {
                        return 'vendor-react';
                    }

                    if (id.includes(`${'/'}diff${'/'}`)) {
                        return 'vendor-diff';
                    }

                    return 'vendor-misc';
                },
            },
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
