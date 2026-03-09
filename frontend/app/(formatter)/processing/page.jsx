'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useCallback, useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

import Footer from '@/src/components/Footer';
import Stepper from '@/src/components/Stepper';
import StatusBadge from '@/src/components/StatusBadge';
import { useDocument } from '@/src/context/DocumentContext';
import { useDocumentStatus } from '@/src/services/api';
import { isCompleted, isFailed } from '@/src/constants/status';

const PHASE_MAPPING = {
    UPLOADED: 0,
    UPLOAD: 1,
    PARSING: 2,
    EXTRACTION: 2,
    CLASSIFICATION: 3,
    INTELLIGENCE: 4,
    NLP_ANALYSIS: 4,
    VALIDATION: 5,
    FORMATTING: 6,
    EXPORT: 6,
    PERSISTENCE: 7,
    COMPLETED: 7,
    FAILED: 7,
};

const HUMAN_PHASE_LABELS = {
    UPLOADED: 'File Uploaded',
    UPLOAD: 'Uploading Manuscript',
    PARSING: 'Parsing Document',
    EXTRACTION: 'Extracting Content',
    CLASSIFICATION: 'Classifying Sections',
    INTELLIGENCE: 'AI Analysis',
    NLP_ANALYSIS: 'AI Content Analysis',
    VALIDATION: 'Validating Format',
    FORMATTING: 'Applying Styles',
    EXPORT: 'Exporting Output',
    PERSISTENCE: 'Saving Results',
    COMPLETED: 'Processing Complete',
    FAILED: 'Processing Failed',
};

export default function Processing() {
    usePageTitle('Processing');
    const router = useRouter();
    const navigate = useCallback((href, options = {}) => {
        if (options?.replace) {
            router.replace(href);
            return;
        }
        router.push(href);
    }, [router]);
    const { job, setJob } = useDocument();
    const [progress, setProgress] = useState(0);
    const [phase, setPhase] = useState('Initializing...');
    const [activeStep, setActiveStep] = useState(0);
    const [isCancelling, setIsCancelling] = useState(false);
    const startTimeRef = useRef(Date.now());
    const [etaString, setEtaString] = useState('');

    const notifyCompletion = useCallback(() => {
        if (typeof window === 'undefined' || !('Notification' in window)) {
            return;
        }

        if (Notification.permission === 'granted') {
            new Notification('ScholarForm AI', { body: 'Your document is ready!' });
        }
    }, []);

    const { data: statusData, error: statusError } = useDocumentStatus(job?.id, {
        enabled: Boolean(job?.id) && !isCancelling,
        refetchInterval: 1500,
        staleTime: 0,
    });

    useEffect(() => {
        if (!job) {
            navigate('/upload');
        }
    }, [job, navigate]);

    useEffect(() => {
        if (!job) {
            return;
        }
        if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().catch(() => { });
        }
    }, [job]);

    useEffect(() => {
        if (!statusData || !job) {
            return;
        }

        const nextPhase = statusData.phase || statusData.current_phase || 'UPLOADED';
        const normalizedPhase = String(nextPhase).toUpperCase();
        const stepIndex = PHASE_MAPPING[normalizedPhase] !== undefined ? PHASE_MAPPING[normalizedPhase] : 1;

        const currentProgress = statusData.progress_percentage || 0;
        setProgress(currentProgress);
        setPhase(statusData.message || HUMAN_PHASE_LABELS[normalizedPhase] || nextPhase || 'Processing...');
        setActiveStep(stepIndex);

        if (currentProgress > 5 && currentProgress < 100) {
            const elapsed = Date.now() - startTimeRef.current;
            const remainingMs = (elapsed / currentProgress) * (100 - currentProgress);
            const remainingSecs = Math.ceil(remainingMs / 1000);
            if (remainingSecs > 60) {
                setEtaString(`~${Math.ceil(remainingSecs / 60)} min remaining`);
            } else {
                setEtaString(`~${remainingSecs} sec remaining`);
            }
        } else if (currentProgress >= 100) {
            setEtaString('');
        }

        if (isCompleted(statusData.status)) {
            setJob((previousJob) => ({
                ...(previousJob || {}),
                status: statusData.status,
                progress: 100,
                phase: nextPhase,
                outputPath: statusData.output_path,
            }));
            notifyCompletion();
            navigate('/download');
            return;
        }

        if (isFailed(statusData.status)) {
            setJob((previousJob) => ({
                ...(previousJob || {}),
                status: statusData.status,
                error: statusData.message,
                phase: nextPhase,
            }));
            navigate('/error');
        }
    }, [job, navigate, notifyCompletion, setJob, statusData]);

    useEffect(() => {
        if (!statusError || !job) {
            return;
        }
        console.error('Polling error:', statusError);
    }, [job, statusError]);

    const handleCancelProcessing = () => {
        setIsCancelling(true);
        // Clear the current job from context — stops polling and returns user to upload
        setJob(null);
        navigate('/upload');
    };

    return (
        <div className="min-h-screen flex flex-col bg-background-light dark:bg-background-dark">
            
            <main className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6">
                <div className="max-w-2xl w-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden animate-in fade-in zoom-in duration-500">
                    <div className="p-6 sm:p-8 border-b border-slate-100 dark:border-slate-800 text-center">
                        <div className="inline-flex items-center justify-center size-20 rounded-full bg-primary/10 text-primary mb-6 animate-pulse">
                            <span className="material-symbols-outlined text-5xl">sync</span>
                        </div>
                        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">Processing Manuscript</h1>
                        <p className="text-slate-500 dark:text-slate-400">Our AI is analyzing your document structure, verifying references, and applying the target template.</p>
                    </div>

                    <div className="p-6 sm:p-8 space-y-8">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-bold text-slate-700 dark:text-slate-300">Overall Progress</span>
                                <div className="flex items-center gap-3">
                                    {etaString && <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">{etaString}</span>}
                                    <span className="text-sm font-black text-primary">{Math.round(progress)}%</span>
                                </div>
                            </div>
                            <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
                                <div className="bg-primary h-full transition-all duration-500 ease-out" style={{ width: `${progress}%` }}></div>
                            </div>
                        </div>

                        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-6 border border-slate-100 dark:border-slate-700">
                            <Stepper activeStep={activeStep} />
                        </div>
                    </div>

                    <div className="p-4 sm:p-6 bg-slate-50 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                        <div className="flex items-center gap-2 min-w-0">
                            <StatusBadge status="processing" />
                            <span className="text-xs font-medium text-slate-500 dark:text-slate-400 truncate">Executing: {phase}</span>
                        </div>
                        <p className="text-[10px] text-slate-400 font-mono break-all sm:text-right">Job ID: {job?.id || 'Initializing...'}</p>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-6 flex flex-col sm:flex-row items-center gap-3">
                    <button
                        onClick={handleCancelProcessing}
                        disabled={isCancelling}
                        className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-slate-800 border border-red-200 dark:border-red-800/50 text-red-600 rounded-xl font-bold text-sm hover:bg-red-50 dark:hover:bg-red-900/20 transition-all disabled:opacity-50"
                    >
                        <span className="material-symbols-outlined text-lg">cancel</span>
                        {isCancelling ? 'Cancelling...' : 'Cancel Processing'}
                    </button>
                    {!isCancelling && (
                        <button
                            onClick={handleCancelProcessing}
                            className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-bold text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-all"
                        >
                            <span className="material-symbols-outlined text-lg">upload_file</span>
                            Upload Another Document
                        </button>
                    )}
                </div>

                <p className="mt-6 text-slate-400 text-sm flex items-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">verified_user</span>
                    Your data is encrypted and stored securely.
                </p>
            </main>

            <Footer variant="app" />
        </div>
    );
}


