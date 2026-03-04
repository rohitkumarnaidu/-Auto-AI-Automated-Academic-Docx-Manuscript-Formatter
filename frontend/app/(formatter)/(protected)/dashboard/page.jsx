'use client';
import { useMemo, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useVirtualizer } from '@tanstack/react-virtual';

import usePageTitle from '@/src/hooks/usePageTitle';
import { useAuth } from '@/src/context/AuthContext';
import Footer from '@/src/components/Footer';
import { isCompleted, isProcessing } from '@/constants/status';
import { useDocuments } from '@/src/services/api';

export default function DashboardPage() {
    usePageTitle('Dashboard');
    const router = useRouter();
    const { user } = useAuth();
    const {
        data: documentsPayload,
        isLoading: loadingHistory,
        isFetching: fetchingHistory,
        refetch: refreshHistory,
    } = useDocuments({ limit: 300 });

    const history = useMemo(() => documentsPayload?.documents || [], [documentsPayload]);
    const activityJobs = useMemo(() => history.slice(0, 300), [history]);
    const completedCount = history.filter(
        (item) => String(item?.status || '').toUpperCase() === 'COMPLETED'
    ).length;
    const latestCompletedJob = [...history]
        .filter((item) => String(item?.status || '').toUpperCase() === 'COMPLETED')
        .sort((left, right) => new Date(right.timestamp || 0).getTime() - new Date(left.timestamp || 0).getTime())[0] || null;

    const displayName = user?.user_metadata?.full_name || 'Researcher';
    const activityParentRef = useRef(null);
    const rowVirtualizer = useVirtualizer({
        count: activityJobs.length,
        getScrollElement: () => activityParentRef.current,
        estimateSize: () => 74,
        overscan: 8,
    });

    const handleDownloadLatest = () => {
        if (!latestCompletedJob?.id) {
            return;
        }
        router.push(`/jobs/${encodeURIComponent(latestCompletedJob.id)}/download`);
    };

    const SkeletonDashboard = () => (
        <div className="space-y-12 animate-pulse">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                        <div className="h-48 w-full bg-slate-100 dark:bg-slate-800"></div>
                        <div className="p-6 space-y-4">
                            <div className="h-5 w-3/4 rounded bg-slate-200 dark:bg-slate-700"></div>
                            <div className="h-4 w-full rounded bg-slate-100 dark:bg-slate-800"></div>
                            <div className="h-4 w-2/3 rounded bg-slate-100 dark:bg-slate-800"></div>
                            <div className="h-10 w-full rounded-lg bg-slate-200 dark:bg-slate-700"></div>
                        </div>
                    </div>
                ))}
            </div>
            <div>
                <div className="flex justify-between items-center mb-4 px-1">
                    <div className="h-6 w-40 rounded bg-slate-200 dark:bg-slate-700"></div>
                    <div className="h-4 w-28 rounded bg-slate-200 dark:bg-slate-700"></div>
                </div>
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                <th className="px-6 py-4"><div className="h-3 w-24 rounded bg-slate-200 dark:bg-slate-700"></div></th>
                                <th className="px-6 py-4"><div className="h-3 w-12 rounded bg-slate-200 dark:bg-slate-700"></div></th>
                                <th className="px-6 py-4"><div className="h-3 w-20 rounded bg-slate-200 dark:bg-slate-700"></div></th>
                                <th className="px-6 py-4"><div className="h-3 w-14 rounded bg-slate-200 dark:bg-slate-700"></div></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {Array.from({ length: 4 }).map((_, i) => (
                                <tr key={i}>
                                    <td className="px-6 py-5"><div className="h-4 w-40 rounded bg-slate-200 dark:bg-slate-700"></div></td>
                                    <td className="px-6 py-5"><div className="h-5 w-20 rounded-full bg-slate-200 dark:bg-slate-700"></div></td>
                                    <td className="px-6 py-5"><div className="h-4 w-28 rounded bg-slate-200 dark:bg-slate-700"></div></td>
                                    <td className="px-6 py-5 text-right"><div className="h-4 w-16 rounded bg-slate-200 dark:bg-slate-700 ml-auto"></div></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col transition-colors duration-300">
            <main className="flex-1 max-w-[1280px] mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="mb-10 fade-in-up">
                    <div className="flex flex-col gap-2">
                        <h1 className="text-slate-900 dark:text-white text-3xl sm:text-4xl font-black leading-tight tracking-tight">Welcome back, {displayName}</h1>
                        <p className="text-slate-500 dark:text-slate-400 text-base sm:text-lg font-normal leading-normal max-w-2xl">Manage your academic manuscripts, track validation status, and ensure formatting compliance for upcoming publications.</p>
                    </div>
                </div>

                {loadingHistory ? <SkeletonDashboard /> : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 stagger-children">
                            <Link href="/upload" className="group flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer">
                                <div className="h-48 w-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                    <span className="material-symbols-outlined text-primary text-5xl">cloud_upload</span>
                                </div>
                                <div className="p-6">
                                    <h3 className="text-slate-900 dark:text-white text-lg font-bold mb-2">Upload New Manuscript</h3>
                                    <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-4">Start a new submission and formatting check. Supports .docx and LaTeX files.</p>
                                    <div className="w-full bg-primary text-white py-2.5 px-4 rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 text-center">
                                        <span className="material-symbols-outlined text-sm">add</span>
                                        New Submission
                                    </div>
                                </div>
                            </Link>

                            <Link href="/history" className="group flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer">
                                <div className="h-48 w-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center group-hover:bg-slate-200 dark:group-hover:bg-slate-700 transition-colors">
                                    <span className="material-symbols-outlined text-slate-400 text-5xl">description</span>
                                </div>
                                <div className="p-6">
                                    <div className="flex justify-between items-start mb-2">
                                        <h3 className="text-slate-900 dark:text-white text-lg font-bold">My Manuscripts</h3>
                                        <span className="bg-primary/20 text-primary text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider">{history?.length || 0} Active</span>
                                    </div>
                                    <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-4">Track progress of ongoing projects.</p>
                                    <div className="w-full bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white py-2.5 px-4 rounded-lg font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-center">
                                        View All Projects
                                    </div>
                                </div>
                            </Link>

                            <div className="group flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer">
                                <div className="h-48 w-full bg-green-50 dark:bg-green-900/10 flex items-center justify-center group-hover:bg-green-100 dark:group-hover:bg-green-900/20 transition-colors">
                                    <span className="material-symbols-outlined text-green-600 text-5xl">fact_check</span>
                                </div>
                                <div className="p-6">
                                    <div className="flex justify-between items-start mb-2">
                                        <h3 className="text-slate-900 dark:text-white text-lg font-bold">Validation Results</h3>
                                        <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider">{completedCount} Ready</span>
                                    </div>
                                    <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-4">Detailed formatting compliance reports and export-ready files.</p>
                                    <button
                                        onClick={handleDownloadLatest}
                                        disabled={!latestCompletedJob}
                                        className="w-full bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white py-2.5 px-4 rounded-lg font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        Download Results
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 px-1 gap-3">
                            <h2 className="text-slate-900 dark:text-white text-2xl font-bold tracking-tight">Recent Activity</h2>
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => refreshHistory()}
                                    disabled={loadingHistory || fetchingHistory}
                                    className="text-primary text-sm font-semibold hover:underline flex items-center gap-1 disabled:opacity-50"
                                >
                                    <span className={`material-symbols-outlined text-sm ${(loadingHistory || fetchingHistory) ? 'animate-spin' : ''}`}>refresh</span>
                                    Refresh
                                </button>
                                <Link className="text-primary text-sm font-semibold hover:underline flex items-center gap-1" href="/history">
                                    View full history
                                    <span className="material-symbols-outlined text-sm">arrow_forward</span>
                                </Link>
                            </div>
                        </div>

                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
                            {history.length === 0 && !loadingHistory && !fetchingHistory ? (
                                <div className="px-6 py-16 text-center">
                                    <div className="flex flex-col items-center justify-center max-w-md mx-auto">
                                        <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
                                            <span className="material-symbols-outlined text-5xl text-primary">post_add</span>
                                        </div>
                                        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Ready for your first manuscript?</h3>
                                        <p className="text-slate-500 dark:text-slate-400 mb-8 text-sm">Upload a document to run AI analysis, validate formatting, and export to academic standards.</p>
                                        <button onClick={() => router.push('/upload')} className="bg-primary hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-primary/20 transition-all active:scale-95 flex items-center gap-2">
                                            <span className="material-symbols-outlined text-lg">upload_file</span>
                                            Upload your first manuscript
                                        </button>
                                    </div>
                                </div>
                            ) : activityJobs.length === 0 ? (
                                <div className="px-6 py-12 text-center">
                                    <div className="flex flex-col items-center gap-3">
                                        <span className="material-symbols-outlined text-4xl text-slate-300 dark:text-slate-700">inbox</span>
                                        <p className="text-slate-500 dark:text-slate-400 font-medium">No manuscripts yet</p>
                                    </div>
                                </div>
                            ) : (
                                <div role="table" aria-label="Recent manuscript activity" className="w-full">
                                    <div
                                        role="rowgroup"
                                        className="grid grid-cols-[minmax(220px,2fr)_minmax(140px,1fr)_minmax(180px,1fr)_110px] bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
                                    >
                                        <div role="columnheader">Manuscript Title</div>
                                        <div role="columnheader">Status</div>
                                        <div role="columnheader">Last Modified</div>
                                        <div role="columnheader" className="text-right">Actions</div>
                                    </div>

                                    <div
                                        ref={activityParentRef}
                                        className="max-h-[520px] overflow-auto"
                                        role="rowgroup"
                                        aria-label="Virtualized manuscript rows"
                                    >
                                        <div
                                            style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}
                                        >
                                            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                                                const job = activityJobs[virtualRow.index];
                                                const completed = isCompleted(job?.status);
                                                const processing = isProcessing(job?.status);
                                                const timestamp = job?.timestamp || job?.created_at || new Date().toISOString();

                                                return (
                                                    <div
                                                        key={job?.id || virtualRow.key}
                                                        role="row"
                                                        className="grid grid-cols-[minmax(220px,2fr)_minmax(140px,1fr)_minmax(180px,1fr)_110px] items-center px-6 py-5 border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                                                        style={{
                                                            position: 'absolute',
                                                            top: 0,
                                                            left: 0,
                                                            width: '100%',
                                                            transform: `translateY(${virtualRow.start}px)`,
                                                        }}
                                                    >
                                                        <div role="cell" className="flex items-center gap-3 min-w-0 pr-3">
                                                            <span className="material-symbols-outlined text-slate-400">article</span>
                                                            <span className="text-slate-900 dark:text-white font-medium truncate">{job?.originalFileName || job?.filename || 'Untitled'}</span>
                                                        </div>
                                                        <div role="cell" className="pr-3">
                                                            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${completed
                                                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                                                : processing
                                                                    ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary'
                                                                    : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
                                                                }`}>
                                                                <span className={`w-1.5 h-1.5 rounded-full mr-2 ${completed ? 'bg-green-600 dark:bg-green-400' : 'bg-primary animate-pulse'}`}></span>
                                                                {completed ? 'Validated' : processing ? 'In Progress' : 'Pending'}
                                                            </span>
                                                        </div>
                                                        <div role="cell" className="text-slate-500 dark:text-slate-400 text-sm pr-3">
                                                            {new Date(timestamp).toLocaleString('en-US', {
                                                                month: 'short',
                                                                day: 'numeric',
                                                                year: 'numeric',
                                                                hour: '2-digit',
                                                                minute: '2-digit',
                                                            })}
                                                        </div>
                                                        <div role="cell" className="text-right">
                                                            {completed ? (
                                                                <Link
                                                                    href={job?.id ? `/jobs/${encodeURIComponent(job.id)}/download` : '/download'}
                                                                    className="text-primary hover:text-primary/80 font-bold text-sm transition-colors"
                                                                >
                                                                    Download
                                                                </Link>
                                                            ) : (
                                                                <Link href="/upload" className="text-primary hover:text-primary/80 font-bold text-sm transition-colors">Continue</Link>
                                                            )}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </main>
            <Footer variant="app" />
        </div>
    );
}
