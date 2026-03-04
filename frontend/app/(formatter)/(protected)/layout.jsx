import AuthGuard from '@/components/AuthGuard';

export default function FormatterProtectedLayout({ children }) {
    return <AuthGuard>{children}</AuthGuard>;
}
