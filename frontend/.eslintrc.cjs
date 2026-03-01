module.exports = {
    root: true,
    ignorePatterns: [
        'dist/**',
        'node_modules/**',
        '.next/**',
        'playwright-report/**',
        'test-results/**',
        'src/_vite_pages/**',
    ],
    env: { browser: true, es2020: true },
    globals: {
        process: 'readonly',
    },
    extends: [
        'eslint:recommended',
        'plugin:react/recommended',
        'plugin:react-hooks/recommended',
    ],
    parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
    settings: { react: { version: 'detect' } },
    rules: {
        'react/prop-types': 'off',
        'react/react-in-jsx-scope': 'off',
        'no-unused-vars': 'warn',
    },
    overrides: [
        {
            files: ['src/test/**/*.{js,jsx,ts,tsx}', 'src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
            env: {
                node: true,
                jest: true,
            },
            globals: {
                vi: 'readonly',
            },
        },
        {
            files: [
                'playwright.config.js',
                'vitest.config.js',
                'next.config.mjs',
                'tailwind.config.js',
                'postcss.config.js',
                'middleware.js',
                'migrate_*.js',
            ],
            env: {
                node: true,
            },
        },
    ],
};
