/** @type {import('next').NextConfig} */
import { withSentryConfig } from "@sentry/nextjs";
import withPWAInit from "next-pwa";

const withPWA = withPWAInit({
    dest: "public",
    disable: process.env.NODE_ENV === 'development',
    register: true,
    skipWaiting: true,
});

const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ['react-resizable-panels'],
    experimental: {
        // Tree-shake heavy packages so only used exports are compiled
        optimizePackageImports: ['lucide-react', 'framer-motion', '@tanstack/react-query'],
    },
    async rewrites() {
        return [
            {
                source: '/metrics',
                destination: '/api/metrics',
            },
        ];
    },
};

export default withSentryConfig(withPWA(nextConfig), {
    org: process.env.SENTRY_ORG,
    project: process.env.SENTRY_PROJECT,
    silent: !process.env.CI,
    telemetry: false,
    widenClientFileUpload: true,
    hideSourceMaps: true,
    webpack: {
        treeshake: {
            removeDebugLogging: true,
        },
        automaticVercelMonitors: false,
    },
});
