import AuthGuard from '@/components/AuthGuard';

export default function SharedProtectedLayout({ children }) {
    return <AuthGuard>{children}</AuthGuard>;
}
