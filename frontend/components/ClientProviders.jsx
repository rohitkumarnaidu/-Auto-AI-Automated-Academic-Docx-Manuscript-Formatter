'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/src/context/ThemeContext';
import { AuthProvider } from '@/src/context/AuthContext';
import { ToastProvider } from '@/src/context/ToastContext';
import { DocumentProvider } from '@/src/context/DocumentContext';
import FocusManager from '@/components/FocusManager';
import DynamicMeta from '@/components/DynamicMeta';
import { useState } from 'react';

export default function ClientProviders({ children }) {
    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 10000,
                refetchOnWindowFocus: false,
                retry: 1,
            },
        },
    }));

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <ToastProvider>
                    <AuthProvider>
                        <DocumentProvider>
                            <FocusManager />
                            <DynamicMeta />
                            {children}
                        </DocumentProvider>
                    </AuthProvider>
                </ToastProvider>
            </ThemeProvider>
        </QueryClientProvider>
    );
}
