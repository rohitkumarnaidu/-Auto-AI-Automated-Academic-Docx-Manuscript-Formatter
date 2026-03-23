/** @type {import('next').NextConfig} */
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ['react-resizable-panels'],
    experimental: {
        // Tree-shake heavy packages so only used exports are compiled
        optimizePackageImports: ['lucide-react', 'framer-motion', '@tanstack/react-query'],
    },
};

export default withSentryConfig(nextConfig, {
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
