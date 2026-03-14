/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ['react-resizable-panels'],
    experimental: {
        // Tree-shake heavy packages so only used exports are compiled
        optimizePackageImports: ['lucide-react', 'framer-motion', '@tanstack/react-query'],
    },
};

export default nextConfig;
