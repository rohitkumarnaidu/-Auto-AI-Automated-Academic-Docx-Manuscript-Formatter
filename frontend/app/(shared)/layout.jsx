import AppShell from '@/components/AppShell';

export default function SharedLayout({ children }) {
    return <AppShell section="shared">{children}</AppShell>;
}
