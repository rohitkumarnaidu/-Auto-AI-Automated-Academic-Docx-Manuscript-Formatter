'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import MetricsCard from '@/src/components/MetricsCard';
import HealthStatusIndicator from '@/src/components/HealthStatusIndicator';
import Footer from '@/src/components/Footer';
import Skeleton from '@/src/components/ui/Skeleton';
import { getMetricsDb, getMetricsHealth, getMetricsDashboard } from '@/src/services/api';
import { useAuth } from '@/src/context/AuthContext';

export default function AdminDashboard() {
    usePageTitle('Admin Dashboard');
    const router = useRouter();
    const { user } = useAuth();
    const [dbMetrics, setDbMetrics] = useState(null);
    const [healthData, setHealthData] = useState(null);
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadAll = async () => {
            setLoading(true);
            setError('');
            try {
                const [db, health, dashboard] = await Promise.allSettled([
                    getMetricsDb(),
                    getMetricsHealth(),
                    getMetricsDashboard(),
                ]);
                if (db.status === 'fulfilled') setDbMetrics(db.value);
                if (health.status === 'fulfilled') setHealthData(health.value);
                if (dashboard.status === 'fulfilled') setDashboardData(dashboard.value);
            } catch (err) {
                setError('Failed to load some metrics. Services may be unavailable.');
            } finally {
                setLoading(false);
            }
        };
        loadAll();
    }, []);

    const refreshMetrics = async () => {
        setLoading(true);
        try {
            const [db, health, dashboard] = await Promise.allSettled([
                getMetricsDb(),
                getMetricsHealth(),
                getMetricsDashboard(),
            ]);
            if (db.status === 'fulfilled') setDbMetrics(db.value);
            if (health.status === 'fulfilled') setHealthData(health.value);
            if (dashboard.status === 'fulfilled') setDashboardData(dashboard.value);
        } finally {
            setLoading(false);
        }
    };

    // Admin role guard.
    const isAdmin = user?.app_metadata?.role === 'admin' || user?.user_metadata?.role === 'admin';

    useEffect(() => {
        if (user && !isAdmin) {
            router.replace('/dashboard');
        }
    }, [isAdmin, router, user]);

    if (user && !isAdmin) {
        return null;
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 animate-in fade-in duration-500">
            <main className="max-w-7xl mx-auto px-4 py-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                            <span className="material-symbols-outlined text-primary text-4xl">monitoring</span>
                            Admin Dashboard
                        </h1>
                        <p className="text-slate-600 dark:text-slate-400 mt-1">System health, metrics, and AI performance monitoring</p>
                    </div>
                    <button onClick={refreshMetrics} disabled={loading}
                        className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors disabled:opacity-50 shadow-md shadow-primary/20 active:scale-95 min-h-[44px]">
                        <span className={`material-symbols-outlined text-sm ${loading ? 'animate-spin' : ''}`}>refresh</span>
                        Refresh
                    </button>
                </div>

                {error && (
                    <div className="p-4 mb-6 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 text-sm">
                        {error}
                    </div>
                )}

                <section className="mb-8">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-green-500">dns</span>
                        Service Health
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <HealthStatusIndicator
                            status={dbMetrics?.status || 'unknown'}
                            label="Database (Supabase)"
                            details={dbMetrics ? `${dbMetrics.document_count ?? 0} documents stored` : 'Loading...'}
                        />
                        <HealthStatusIndicator
                            status={healthData?.status || 'unknown'}
                            label="AI Services"
                            details={healthData?.model_name || 'Checking...'}
                        />
                        <HealthStatusIndicator
                            status={healthData?.redis_status || 'unknown'}
                            label="Redis Cache"
                            details={healthData?.redis_status === 'healthy' ? 'Connected' : 'Fallback mode'}
                        />
                    </div>
                </section>

                <section className="mb-8">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">analytics</span>
                        Key Metrics
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
                        <MetricsCard title="Total Documents" value={dbMetrics?.document_count ?? '—'} icon="description" color="primary" isLoading={loading} />
                        <MetricsCard title="Processing Success" value={dashboardData?.success_rate ? `${dashboardData.success_rate}%` : '—'} icon="check_circle" color="green" subtitle="Completion rate" isLoading={loading} />
                        <MetricsCard title="Avg Confidence" value={dashboardData?.avg_confidence ? `${(dashboardData.avg_confidence * 100).toFixed(1)}%` : '—'} icon="psychology" color="purple" subtitle="AI model confidence" isLoading={loading} />
                        <MetricsCard title="Error Rate" value={dashboardData?.error_rate ? `${dashboardData.error_rate}%` : '—'} icon="error_outline" color={dashboardData?.error_rate > 5 ? 'red' : 'amber'} subtitle="Last 24 hours" isLoading={loading} />
                    </div>
                </section>

                {dashboardData && (
                    <section className="mb-8">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                            <span className="material-symbols-outlined text-purple-500">smart_toy</span>
                            AI Performance
                        </h2>
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Model</p>
                                    <p className="text-lg font-semibold text-slate-900 dark:text-white">{dashboardData.model_name || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Total Processed</p>
                                    <p className="text-lg font-semibold text-slate-900 dark:text-white">{dashboardData.total_processed ?? 0}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Avg Processing Time</p>
                                    <p className="text-lg font-semibold text-slate-900 dark:text-white">{dashboardData.avg_processing_time ? `${dashboardData.avg_processing_time}s` : 'N/A'}</p>
                                </div>
                            </div>
                            {dashboardData.ab_testing && (
                                <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                                    <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">A/B Testing Results</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        {Object.entries(dashboardData.ab_testing).map(([variant, stats]) => (
                                            <div key={variant} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                                                <p className="text-xs font-medium text-slate-500 uppercase">{variant}</p>
                                                <p className="text-lg font-bold text-slate-900 dark:text-white">{typeof stats === 'object' ? JSON.stringify(stats) : stats}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </section>
                )}

                {loading && !dbMetrics && !healthData && (
                    <div className="animate-in fade-in duration-500">
                        <section className="mb-8">
                            <Skeleton className="h-6 w-40 mb-4" />
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {[1, 2, 3].map(i => (
                                    <Skeleton key={i} className="h-24 w-full" rounded="rounded-xl" />
                                ))}
                            </div>
                        </section>
                        <section className="mb-8">
                            <Skeleton className="h-6 w-32 mb-4" />
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                {[1, 2, 3, 4].map(i => (
                                    <Skeleton key={i} className="h-32 w-full" rounded="rounded-xl" />
                                ))}
                            </div>
                        </section>
                    </div>
                )}
            </main>
            <Footer />
        </div>
    );
}
