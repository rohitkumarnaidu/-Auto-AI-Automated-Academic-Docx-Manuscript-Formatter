import AuthGuard from '@/src/components/layout/AuthGuard';

export default function FormatterProtectedLayout({ children }) {
    return <AuthGuard>{children}</AuthGuard>;
}
