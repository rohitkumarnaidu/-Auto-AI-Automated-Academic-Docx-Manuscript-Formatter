import Header from '@/components/Header';

export default function AppShell({ children, section = 'shared' }) {
    return (
        <div className="relative z-10 flex flex-col min-h-screen">
            <Header section={section} />
            <main className="flex-grow flex flex-col items-center w-full relative z-10">
                {children}
            </main>
        </div>
    );
}
