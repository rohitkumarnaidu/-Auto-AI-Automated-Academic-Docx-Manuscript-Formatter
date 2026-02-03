import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Stepper from '../components/Stepper';
import StatusBadge from '../components/StatusBadge';
import { useDocument } from '../context/DocumentContext';

export default function Processing() {
    const navigate = useNavigate();
    const { job, processing } = useDocument();

    useEffect(() => {
        // If processing finished and we have a job, move to results
        if (!processing && job && job.status === 'completed') {
            const timer = setTimeout(() => {
                navigate('/results');
            }, 1000);
            return () => clearTimeout(timer);
        }

        // If processing failed, the context should handle it (or show error here)
        if (!processing && job && job.status === 'failed') {
            navigate('/error');
        }

        // If we are not processing and have no job, maybe the user refreshed?
        if (!processing && !job) {
            navigate('/upload');
        }
    }, [processing, job, navigate]);

    return (
        <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark">
            <Navbar variant="app" />

            <main className="flex-1 flex flex-col items-center justify-center p-6">
                <div className="max-w-2xl w-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden animate-in fade-in zoom-in duration-500">
                    <div className="p-8 border-b border-slate-100 dark:border-slate-800 text-center">
                        <div className="inline-flex items-center justify-center size-20 rounded-full bg-primary/10 text-primary mb-6 animate-pulse">
                            <span className="material-symbols-outlined text-5xl">sync</span>
                        </div>
                        <h1 className="text-3xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">Processing Manuscript</h1>
                        <p className="text-slate-500 dark:text-slate-400">Our AI is analyzing your document structure, verifying references, and applying the target template.</p>
                    </div>

                    <div className="p-8 space-y-8">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-bold text-slate-700 dark:text-slate-300">Overall Progress</span>
                                <span className="text-sm font-black text-primary">65%</span>
                            </div>
                            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
                                <div className="bg-primary h-full transition-all duration-1000 ease-out" style={{ width: '65%' }}></div>
                            </div>
                        </div>

                        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-6 border border-slate-100 dark:border-slate-700">
                            <Stepper activeStep={2} />
                        </div>
                    </div>

                    <div className="p-6 bg-slate-50 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
                        <div className="flex items-center gap-2">
                            <StatusBadge status="processing" />
                            <span className="text-xs font-medium text-slate-500">Executing: Structure Detection</span>
                        </div>
                        <p className="text-[10px] text-slate-400 font-mono">Job ID: {job?.id || 'Initializing...'}</p>
                    </div>
                </div>

                <p className="mt-8 text-slate-400 text-sm flex items-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">verified_user</span>
                    Your data is encrypted and will be deleted after processing.
                </p>
            </main>

            <Footer variant="app" />
        </div>
    );
}
