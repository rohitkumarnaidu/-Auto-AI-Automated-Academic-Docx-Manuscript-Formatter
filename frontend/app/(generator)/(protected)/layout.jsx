import AuthGuard from '@/components/AuthGuard';

export default function GeneratorProtectedLayout({ children }) {
    return <AuthGuard>{children}</AuthGuard>;
}
