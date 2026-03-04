import AuthGuard from '@/components/AuthGuard';

export default function AdminDashboardLayout({ children }) {
    return <AuthGuard requireAdmin>{children}</AuthGuard>;
}
