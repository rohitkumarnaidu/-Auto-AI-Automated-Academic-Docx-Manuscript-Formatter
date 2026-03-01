import { Manrope } from 'next/font/google';
import './globals.css';
import ClientProviders from '@/components/ClientProviders';

const manrope = Manrope({
    subsets: ['latin'],
    weight: ['400', '500', '600', '700', '800'],
    variable: '--font-manrope',
    display: 'swap',
});

export const metadata = {
    title: 'ScholarForm AI',
    description: 'AI-powered academic manuscript formatting for IEEE, APA, Springer, Nature, and 1000+ journals. Upload your paper, get publication-ready output in seconds.',
    openGraph: {
        title: 'ScholarForm AI — Automated Academic Manuscript Formatter',
        description: 'Format your research paper for any journal in seconds. Supports IEEE, APA, Springer, Nature, Elsevier, and 1000+ templates.',
        type: 'website',
        url: 'https://scholarform.ai',
    },
    twitter: {
        card: 'summary_large_image',
        title: 'ScholarForm AI',
        description: 'AI-powered academic manuscript formatting for 1000+ journals.',
    },
};

export const viewport = {
    themeColor: '#2563EB',
};

export default function RootLayout({ children }) {
    return (
        <html lang="en" className={`${manrope.variable} light`} suppressHydrationWarning>
            <head>
                <link
                    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen relative overflow-x-hidden selection:bg-primary selection:text-white">
                <style dangerouslySetInnerHTML={{
                    __html: `
                        .material-symbols-outlined {
                            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
                        }
                    `
                }} />

                {/* Background Glow Effects (Premium Feel) */}
                <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] pointer-events-none z-0"></div>
                <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none z-0"></div>
                <ClientProviders>
                    {children}
                </ClientProviders>
            </body>
        </html>
    );
}
