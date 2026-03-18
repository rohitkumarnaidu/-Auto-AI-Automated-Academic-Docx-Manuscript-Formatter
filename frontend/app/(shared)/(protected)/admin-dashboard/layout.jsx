import AuthGuard from '@/src/components/layout/AuthGuard';

export default function AdminDashboardLayout({ children }) {
    return <AuthGuard requireAdmin>{children}</AuthGuard>;
}
