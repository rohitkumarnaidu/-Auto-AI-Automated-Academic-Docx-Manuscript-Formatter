'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense } from 'react';

function ErrorContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const message = searchParams.get('message') || 'An unexpected error occurred.';

    return (
        <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center animate-in stagger-fade">
            <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-6">
                <span className="material-symbols-outlined text-red-600 dark:text-red-400 text-3xl">error</span>
            </div>
            <h1 className="text-3xl font-bold mb-4 text-slate-800 dark:text-slate-100">Error</h1>
            <p className="text-slate-600 dark:text-slate-400 max-w-md mb-8">
                {message}
            </p>
            <button
                onClick={() => router.push('/')}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition"
            >
                Return Home
            </button>
        </div>
    );
}

export default function ErrorPage() {
    return (
        <Suspense fallback={<div className="min-h-[80vh] flex items-center justify-center">Loading...</div>}>
            <ErrorContent />
        </Suspense>
    );
}
