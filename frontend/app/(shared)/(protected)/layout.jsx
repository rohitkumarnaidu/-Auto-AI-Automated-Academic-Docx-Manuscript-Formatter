import AuthGuard from '@/src/components/layout/AuthGuard';

export default function SharedProtectedLayout({ children }) {
    return <AuthGuard>{children}</AuthGuard>;
}
