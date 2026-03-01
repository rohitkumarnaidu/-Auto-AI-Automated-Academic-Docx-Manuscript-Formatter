'use client';
import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/src/context/AuthContext';
import JobStatusCard from '@/components/JobStatusCard';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useDocuments } from '@/src/services/api';

export default function DashboardPage() {
    usePageTitle('Dashboard - ScholarFormat');
    const { user } = useAuth();
    const [searchQuery, setSearchQuery] = useState('');

    // Fetch live documents
    const {
        data: documentsPayload,
        isLoading: loadingHistory,
        isFetching: fetchingHistory,
        refetch: refreshHistory,
    } = useDocuments({ limit: 50 }); // Reasonable limit for grid view

    const history = useMemo(() => documentsPayload?.documents || [], [documentsPayload]);

    // Filter and map jobs for the Status Card
    const activityJobs = useMemo(() => {
        let filtered = history;
        if (searchQuery) {
            const lowerQuery = searchQuery.toLowerCase();
            filtered = history.filter(job =>
                job.filename?.toLowerCase().includes(lowerQuery) ||
                job.originalFileName?.toLowerCase().includes(lowerQuery)
            );
        }

        return filtered.map(job => {
            const timestamp = job?.timestamp || job?.created_at || new Date().toISOString();

            // Map legacy statuses to standard schema
            const isCompleted = String(job?.status || '').toUpperCase() === 'COMPLETED';
            const isFailed = String(job?.status || '').toUpperCase() === 'FAILED' || String(job?.status || '').toUpperCase() === 'ERROR';
            let mappedStatus = 'processing';
            if (isCompleted) mappedStatus = 'completed';
            else if (isFailed) mappedStatus = 'failed';

            return {
                id: job.id,
                filename: job.originalFileName || job.filename || 'Untitled Document',
                status: mappedStatus,
                template: job.template_name || 'Standard Format',
                timeAgo: new Date(timestamp).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
                size: job.file_size ? `${(job.file_size / 1024 / 1024).toFixed(2)} MB` : null,
                description: mappedStatus === 'completed'
                    ? 'Successfully validated and formatted to academic standards.'
                    : mappedStatus === 'failed'
                        ? 'Error encountered during formatting process. Please review logs.'
                        : 'Currently analyzing manuscript structure and applying formatting rules.',
                raw: job // Keep raw data if needed
            };
        });
    }, [history, searchQuery]);

    return (
        <div className="flex-grow flex flex-col items-center w-full px-6 py-12 animate-in fade-in duration-500">
            <div className="w-full max-w-5xl flex flex-col gap-10">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-glass-border pb-6 slide-in-from-top-2">
                    <div>
                        <h2 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight mb-2">
                            Welcome back, {user?.user_metadata?.first_name || 'Researcher'}
                        </h2>
                        <p className="text-slate-500 dark:text-slate-400">Manage and download your formatted academic documents.</p>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => refreshHistory()}
                            disabled={loadingHistory || fetchingHistory}
                            className={`p-2.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-white dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors border border-slate-200 dark:border-transparent focus:ring-2 focus:ring-primary focus:outline-none cursor-pointer active:scale-95 shadow-sm disabled:opacity-50`}
                            aria-label="Refresh Jobs"
                            title="Refresh"
                        >
                            <span className={`material-symbols-outlined ${(loadingHistory || fetchingHistory) ? 'animate-spin' : ''}`}>refresh</span>
                        </button>
                        <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-slate-500 text-[20px]">search</span>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-200 text-sm rounded-lg focus:ring-primary focus:border-primary block w-full pl-10 p-2.5 placeholder-slate-500 transition-colors focus:outline-none"
                                placeholder="Search files..."
                                aria-label="Search files"
                            />
                        </div>
                        <button className="p-2.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-white dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors border border-slate-200 dark:border-transparent focus:ring-2 focus:ring-primary focus:outline-none cursor-pointer active:scale-95 shadow-sm" aria-label="Filter Jobs">
                            <span className="material-symbols-outlined">filter_list</span>
                        </button>
                    </div>
                </div>

                {/* Cards Grid Component */}
                <div className="grid grid-cols-1 gap-6 stagger-children min-h-[400px]">
                    {loadingHistory ? (
                        // Skeleton Loaders
                        Array.from({ length: 3 }).map((_, i) => (
                            <div key={i} className="glass-panel p-6 rounded-2xl animate-pulse flex flex-col md:flex-row gap-6">
                                <div className="w-full md:w-48 aspect-video md:aspect-[4/3] rounded-xl bg-slate-200 dark:bg-slate-800 shrink-0"></div>
                                <div className="flex-1 space-y-4 py-2">
                                    <div className="h-6 w-3/4 rounded bg-slate-200 dark:bg-slate-700"></div>
                                    <div className="h-4 w-1/2 rounded bg-slate-200 dark:bg-slate-700"></div>
                                    <div className="h-10 w-full rounded-lg bg-slate-200 dark:bg-slate-700 mt-auto"></div>
                                </div>
                            </div>
                        ))
                    ) : activityJobs.length > 0 ? (
                        activityJobs.map(job => (
                            <JobStatusCard key={job.id} job={job} />
                        ))
                    ) : (
                        <div className="glass-panel p-12 rounded-2xl flex flex-col items-center justify-center text-center gap-4 border-dashed h-full">
                            <span className="material-symbols-outlined text-6xl text-slate-300 dark:text-slate-600">post_add</span>
                            <div className="max-w-md">
                                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">No documents found</h3>
                                <p className="text-slate-500 dark:text-slate-400 mb-6">
                                    {searchQuery ? "No manuscripts match your search." : "Upload your first manuscript to automatically format it for any journal."}
                                </p>
                                <Link href="/upload" className="inline-block bg-primary hover:bg-primary-hover text-white px-6 py-3 rounded-xl font-semibold transition-all active:scale-95 shadow-lg shadow-primary/20 focus:ring-2 focus:ring-primary focus:ring-offset-2">
                                    Format New Document
                                </Link>
                            </div>
                        </div>
                    )}
                </div>

                {/* Optional History Link */}
                {activityJobs.length > 0 && !loadingHistory && (
                    <div className="flex justify-center mt-6 slide-in-from-bottom-4">
                        <Link href="/history" className="flex items-center gap-2 text-primary font-bold hover:text-primary-hover bg-primary/10 px-6 py-3 rounded-xl hover:bg-primary/20 transition-colors">
                            View Full History
                            <span className="material-symbols-outlined text-sm">arrow_forward</span>
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
}
