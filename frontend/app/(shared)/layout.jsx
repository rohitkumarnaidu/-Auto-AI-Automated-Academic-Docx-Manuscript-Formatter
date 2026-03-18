import AppShell from '@/src/components/layout/AppShell';

export default function SharedLayout({ children }) {
    return <AppShell section="shared">{children}</AppShell>;
}
