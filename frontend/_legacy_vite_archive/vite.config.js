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

                    // Keep the React ecosystem in one chunk to avoid circular cross-chunk imports.
                    if (
                        id.includes('react-router')
                        || id.includes(`${'/'}react${'/'}`)
                        || id.includes('react-dom')
                        || id.includes('scheduler')
                        || id.includes('@tanstack/react-query')
                    ) {
                        return 'vendor-router';
                    }

                    if (id.includes(`${'/'}diff${'/'}`)) {
                        return 'vendor-diff';
                    }
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
