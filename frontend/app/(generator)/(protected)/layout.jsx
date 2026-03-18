import AuthGuard from '@/src/components/layout/AuthGuard';

export default function GeneratorProtectedLayout({ children }) {
    return <AuthGuard>{children}</AuthGuard>;
}
