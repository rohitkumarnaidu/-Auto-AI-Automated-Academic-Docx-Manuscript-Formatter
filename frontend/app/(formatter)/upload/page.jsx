'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { useAuth } from '@/src/context/AuthContext';
import { useDocument } from '@/src/context/DocumentContext';
import Footer from '@/src/components/Footer';
import CategoryTabs from '@/src/components/upload/CategoryTabs';
import TemplateSelector from '@/src/components/upload/TemplateSelector';
import FormattingOptions from '@/src/components/upload/FormattingOptions';
import ProcessingStepper from '@/src/components/upload/ProcessingStepper';
import FastModeToggle from '@/src/components/FastModeToggle';
import { isCompleted, isFailed, isProcessing as isStatusProcessing } from '@/src/constants/status';
import {
    CHUNK_UPLOAD_THRESHOLD_BYTES,
    uploadChunked,
    uploadDocumentWithProgress,
    useDocumentStatus,
} from '@/src/services/api';
import { getRemainingQuota } from '@/src/lib/planTier';
import UpgradeModal from '@/src/components/UpgradeModal';

const ACCEPTED_EXTENSIONS = ['.docx', '.pdf', '.tex', '.txt', '.html', '.htm', '.md', '.markdown', '.doc'];
const ACCEPTED_FORMATS = '.docx,.pdf,.tex,.txt,.html,.htm,.md,.markdown,.doc';
const MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024;

const isAllowedUploadFile = (selectedFile) => {
    if (!selectedFile?.name) {
        return false;
    }

    const fileExtension = selectedFile.name
        .substring(selectedFile.name.lastIndexOf('.'))
        .toLowerCase();

    return (
        ACCEPTED_EXTENSIONS.includes(fileExtension) &&
        selectedFile.size > 0 &&
        selectedFile.size <= MAX_UPLOAD_SIZE_BYTES
    );
};

export default function Upload() {
    usePageTitle('Upload Document');
    const { isLoggedIn } = useAuth();
    const { job, setJob } = useDocument();
    const searchParams = useSearchParams();
    const fileInputRef = useRef(null);
    const terminalStatusHandledRef = useRef(false);
    const completionNotificationSentRef = useRef(false);
    const [file, setFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [activeJobId, setActiveJobId] = useState(null);
    const [progress, setProgress] = useState(0);
    const [currentStep, setCurrentStep] = useState(0);
    const [statusMessage, setStatusMessage] = useState('Initializing...');
    const [template, setTemplate] = useState('none');
    const [category, setCategory] = useState('none'); // New State for Dropdown Filter
    
    // Quota tracking
    const { user } = useAuth();
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);
    const [quotaWarning, setQuotaWarning] = useState(null);
    const { remaining, limit } = getRemainingQuota(user, user?.uploads_count || 0);

    useEffect(() => {
        if (remaining <= 2 && remaining > 0) {
            setQuotaWarning(`${remaining} upload${remaining !== 1 ? 's' : ''} remaining on your current plan.`);
        } else {
            setQuotaWarning(null);
        }
    }, [remaining]);
    // FIX 34: Inline file error instead of navigate('/error')
    const [fileError, setFileError] = useState(null);
    // FEAT 43: Upload cancellation
    const [abortController, setAbortController] = useState(null);
    // New Formatting Options
    const [addPageNumbers, setAddPageNumbers] = useState(true);
    const [addBorders, setAddBorders] = useState(false);
    const [addCoverPage, setAddCoverPage] = useState(true);
    const [generateTOC, setGenerateTOC] = useState(false);
    const [pageSize, setPageSize] = useState('Letter');
    const [fastMode, setFastMode] = useState(false);
    const router = useRouter();
    const navigate = useCallback((href, options = {}) => {
        if (options?.replace) {
            router.replace(href);
            return;
        }
        router.push(href);
    }, [router]);

    // B-FIX-9: Pre-select template from query param when coming from template picker.
    useEffect(() => {
        const preSelectedTemplate = searchParams.get('template');
        if (preSelectedTemplate && typeof preSelectedTemplate === 'string') {
            setTemplate(preSelectedTemplate);
            setCategory(preSelectedTemplate === 'none' ? 'none' : preSelectedTemplate);
        }
    }, [searchParams]);

    const sendCompletionNotification = useCallback(() => {
        if (typeof window === 'undefined' || !('Notification' in window)) {
            return;
        }

        if (Notification.permission === 'granted') {
            new Notification('ScholarForm AI', { body: 'Your document is ready!' });
        }
    }, []);

    // Mapping backend phases to UI Steps
    // Backend phases: UPLOAD, EXTRACTION, NLP_ANALYSIS, VALIDATION, FORMATTING, PERSISTENCE
    const getStepFromPhase = (phase) => {
        switch (phase) {
            case 'UPLOAD': return 1;
            case 'EXTRACTION': return 2; // Covers 'Converting Format' & 'Parsing Structure'
            case 'NLP_ANALYSIS': return 4; // Covers 'Analyzing Content (AI)'
            case 'VALIDATION': return 5;
            case 'FORMATTING': return 6;
            case 'PERSISTENCE': return 7;
            default: return 1;
        }
    };

    const steps = [
        { id: 1, title: 'Uploading Manuscript', desc: 'Sending file to server...' },
        { id: 2, title: 'Converting Format', desc: 'Extracting text and layout...' },
        { id: 3, title: 'Parsing Structure', desc: 'Mapping sections and elements...' },
        { id: 4, title: 'Analyzing Content (AI)', desc: 'Detecting citation errors & gaps...' },
        { id: 5, title: 'Journal Validation', desc: 'Checking against template rules...' },
        { id: 6, title: 'Final Formatting', desc: 'Applying styles and layouts...' },
        { id: 7, title: 'Exporting Result', desc: 'Generating publication-ready file...' },
    ];

    const { data: statusData, error: statusError } = useDocumentStatus(activeJobId, {
        enabled: Boolean(activeJobId) && isProcessing,
        refetchInterval: isProcessing ? 2000 : false,
        staleTime: 0,
    });

    // Sync local upload UI state with the persisted job from context/session storage.
    useEffect(() => {
        if (!job) {
            return;
        }

        const normalizedStatus = job.status?.toUpperCase();
        const currentlyProcessing = isStatusProcessing(normalizedStatus)
            || ['RUNNING', 'IN_PROGRESS'].includes(normalizedStatus);

        if (currentlyProcessing) {
            setIsProcessing(true);
            setActiveJobId(job.id || null);
            if (typeof job.progress === 'number') {
                setProgress(job.progress);
            }
            if (job.phase) {
                setCurrentStep(getStepFromPhase(job.phase));
            } else {
                setCurrentStep((step) => (step > 0 ? step : 1));
            }
            if (statusMessage === 'Initializing...') {
                setStatusMessage('Resuming previous processing job...');
            }
            return;
        }

        if (isCompleted(normalizedStatus)) {
            setIsProcessing(false);
            setActiveJobId(null);
            setProgress(100);
            setCurrentStep(7);
            setStatusMessage('Processing complete!');
            return;
        }

        if (isFailed(normalizedStatus)) {
            setIsProcessing(false);
            setActiveJobId(null);
            if (job.error) {
                setStatusMessage(`Failed: ${job.error}`);
            }
        }
    }, [job, statusMessage]);

    const handleReviewClick = (path) => {
        navigate(path);
    };

    // Real-time status updates via React Query.
    useEffect(() => {
        if (!statusData || !job) {
            return;
        }

        setProgress(statusData.progress_percentage || 0);
        if (statusData.message) {
            setStatusMessage(statusData.message);
        }
        if (statusData.phase) {
            setCurrentStep(getStepFromPhase(statusData.phase));
        }

        const normalizedStatus = statusData.status?.toUpperCase();
        const currentlyProcessing = isStatusProcessing(normalizedStatus)
            || ['RUNNING', 'IN_PROGRESS'].includes(normalizedStatus);

        if (currentlyProcessing) {
            terminalStatusHandledRef.current = false;
            completionNotificationSentRef.current = false;
            setIsProcessing(true);
            return;
        }

        if (isCompleted(normalizedStatus)) {
            if (terminalStatusHandledRef.current) {
                return;
            }
            terminalStatusHandledRef.current = true;
            setIsProcessing(false);
            setActiveJobId(null);
            setProgress(100);
            setCurrentStep(7);
            setStatusMessage(statusData.status === 'COMPLETED_WITH_WARNINGS'
                ? `Completed with warnings: ${statusData.message}`
                : 'Processing complete!');

            const completedJob = {
                ...job,
                status: statusData.status,
                progress: 100,
                outputPath: statusData.output_path,
                phase: statusData.phase,
                warnings: statusData.status === 'COMPLETED_WITH_WARNINGS' ? statusData.message : null,
            };
            setJob(completedJob);
            sessionStorage.setItem('scholarform_currentJob', JSON.stringify(completedJob));

            if (!completionNotificationSentRef.current) {
                sendCompletionNotification();
                completionNotificationSentRef.current = true;
            }

            setTimeout(() => navigate('/download'), 500);
            return;
        }

        if (isFailed(normalizedStatus)) {
            if (terminalStatusHandledRef.current) {
                return;
            }
            terminalStatusHandledRef.current = true;
            setIsProcessing(false);
            setActiveJobId(null);
            console.error('Job failed:', statusData.message);
            setStatusMessage(`Failed: ${statusData.message}`);
            setJob((previousJob) => ({
                ...(previousJob || {}),
                status: statusData.status,
                error: statusData.message,
                progress: statusData.progress_percentage || 0,
                phase: statusData.phase,
            }));
        }
    }, [job, navigate, sendCompletionNotification, setJob, statusData]);

    useEffect(() => {
        if (!statusError || !isProcessing) {
            return;
        }
        console.error('Polling error:', statusError);
    }, [isProcessing, statusError]);

    const handleFileChange = (e) => {
        setFileError(null);
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            if (!isAllowedUploadFile(selectedFile)) {
                // FIX 34: Inline error instead of navigate('/error')
                setFileError('Unsupported file format. Please upload: DOCX, PDF, TEX, TXT, HTML, MD, or DOC.');
                return;
            }
            setFile(selectedFile);
            // Reset progress if new file selected after completion
            if (progress === 100) {
                setProgress(0);
                setCurrentStep(0);
                setStatusMessage('Ready for upload');
            }
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        if (isProcessing) return;
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        if (isProcessing) return;
        setIsDragging(false);
        setFileError(null);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            if (!isAllowedUploadFile(droppedFile)) {
                // FIX 34: Inline error instead of navigate('/error')
                setFileError('Unsupported file format. Please upload: DOCX, PDF, TEX, TXT, HTML, MD, or DOC.');
                return;
            }
            setFile(droppedFile);
            // Reset progress if new file selected after completion
            if (progress === 100) {
                setProgress(0);
                setCurrentStep(0);
                setStatusMessage('Ready for upload');
            }
        }
    };

    // FEAT 43: Cancel processing
    const handleCancel = useCallback(() => {
        if (abortController) abortController.abort();
        setAbortController(null);
        setIsProcessing(false);
        setActiveJobId(null);
        setJob(null);
        setCurrentStep(0);
        setProgress(0);
        setStatusMessage('Processing cancelled.');
        terminalStatusHandledRef.current = false;
        completionNotificationSentRef.current = false;
    }, [abortController, setJob]);

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const handleProcess = useCallback(async () => {
        if (!file || isProcessing) return;

        if (remaining === 0) {
            setShowUpgradeModal(true);
            return;
        }

        if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().catch(() => { });
        }

        const executeUpload = async (attempt = 0) => {
            const controller = new AbortController();
            setAbortController(controller);
            setIsProcessing(true);
            setActiveJobId(null);
            setProgress(0);
            setCurrentStep(1);
            setStatusMessage(attempt > 0 ? `Retrying upload (Attempt ${attempt + 1}/3)...` : 'Initiating upload...');
            terminalStatusHandledRef.current = false;
            completionNotificationSentRef.current = false;

            const uploadOptions = {
                add_page_numbers: addPageNumbers,
                add_borders: addBorders,
                add_cover_page: addCoverPage,
                generate_toc: generateTOC,
                page_size: pageSize,
                fast_mode: fastMode,
            };

            try {
                let result = null;
                const shouldUseChunkedUpload = file.size > CHUNK_UPLOAD_THRESHOLD_BYTES && isLoggedIn;

                if (shouldUseChunkedUpload) {
                    setStatusMessage('Large file detected. Uploading chunks...');
                    const chunkedResult = await uploadChunked(file, {
                        signal: controller.signal,
                        onProgress: ({ chunkIndex, totalChunks, percent }) => {
                            setProgress(percent);
                            setStatusMessage(`Uploading chunk ${chunkIndex + 1}/${totalChunks} (${percent}%)...`);
                        },
                    });

                    if (chunkedResult?.job_id) {
                        result = chunkedResult;
                    }
                }

                if (controller.signal.aborted) return;

                if (!result) {
                    result = await uploadDocumentWithProgress(file, template, uploadOptions, {
                        signal: controller.signal,
                        onProgress: (uploadPercent) => {
                            setProgress(uploadPercent);
                            setStatusMessage(`Uploading manuscript... ${uploadPercent}%`);
                        },
                    });
                }

                if (controller.signal.aborted || !result?.job_id) {
                    if (!result?.job_id) throw new Error('Upload response missing job id.');
                    return;
                }

                const newJob = {
                    id: result.job_id,
                    timestamp: new Date().toISOString(),
                    status: 'processing',
                    phase: 'UPLOAD',
                    originalFileName: file.name,
                    template,
                    flags: {
                        page_numbers: addPageNumbers,
                        borders: addBorders,
                        cover_page: addCoverPage,
                        toc: generateTOC,
                        page_size: pageSize,
                    },
                    progress: 0,
                };
                setStatusMessage('Upload complete. Processing started...');
                setProgress(0);
                setJob(newJob);
                setActiveJobId(newJob.id);
                sessionStorage.setItem('scholarform_currentJob', JSON.stringify(newJob));

            } catch (error) {
                if (controller.signal.aborted) return;
                
                console.error(`Upload attempt ${attempt + 1} failed:`, error);
                
                if (attempt < 2) { // 3 attempts total (0, 1, 2)
                    const backoffTime = Math.pow(2, attempt) * 1000;
                    setStatusMessage(`Upload failed. Retrying in ${backoffTime / 1000}s...`);
                    setTimeout(() => executeUpload(attempt + 1), backoffTime);
                } else {
                    setIsProcessing(false);
                    setStatusMessage(`Upload failed after 3 attempts: ${error.message}`);
                }
            } finally {
                setAbortController((activeController) => (activeController === controller ? null : activeController));
            }
        };

        executeUpload();
    }, [
        addBorders,
        addCoverPage,
        addPageNumbers,
        file,
        generateTOC,
        isLoggedIn,
        isProcessing,
        pageSize,
        setActiveJobId,
        setJob,
        template,
        fastMode,
        remaining,
    ]);

    // FEAT 46: Keyboard shortcuts
    useEffect(() => {
        const handler = (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                handleProcess();
            }
            if (e.key === 'Escape') {
                e.preventDefault();
                handleCancel();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [handleCancel, handleProcess]);

    const handleCategoryChange = useCallback((nextCategory) => {
        if (nextCategory === 'browse_more') {
            navigate('/templates');
            return;
        }
        setCategory(nextCategory);
        setTemplate(nextCategory);
    }, [navigate]);

    const isJobCompleted = isCompleted(job?.status);

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen">

            <main className="max-w-[1280px] mx-auto px-4 sm:px-6 py-6 sm:py-8">
                <div className="mb-8">
                    <h1 className="text-slate-900 dark:text-white text-3xl sm:text-4xl font-black leading-tight tracking-[-0.033em]">
                        Upload Manuscript
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 text-base sm:text-lg mt-2">
                        {isLoggedIn
                            ? 'Transform your research into a publication-ready document in minutes.'
                            : 'Professional academic formatting in seconds. No account required to start.'}
                    </p>
                </div>

                <div className="mb-7 mt-4">
                    {quotaWarning && (
                        <div className="p-4 mb-4 bg-orange-50 border border-orange-200 text-orange-800 dark:bg-orange-900/30 dark:border-orange-800 dark:text-orange-300 rounded-xl flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined">warning</span>
                                <span className="font-medium">{quotaWarning}</span>
                            </div>
                            <button onClick={() => setShowUpgradeModal(true)} className="text-sm font-bold underline hover:text-orange-900 dark:hover:text-orange-200">
                                Upgrade Plan
                            </button>
                        </div>
                    )}
                    <CategoryTabs />
                    <TemplateSelector
                        category={category}
                        template={template}
                        isProcessing={isProcessing}
                        file={file}
                        formatFileSize={formatFileSize}
                        onCategoryChange={handleCategoryChange}
                        onTemplateSelect={setTemplate}
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    <div className="lg:col-span-7 flex flex-col gap-6">
                        {/* 1. Document Source */}
                        <div className="bg-white surface-ladder-06 rounded-xl border border-slate-200 dark:border-slate-700/70 surface-ladder-border-10 p-6 shadow-sm hover:shadow-md dark:hover:shadow-none transition-shadow">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">upload_file</span>
                                1. Document Source
                            </h2>
                            <div
                                id="upload-zone"
                                className={`flex flex-col items-center gap-6 rounded-xl border-2 border-dashed px-6 py-12 transition-all duration-300 relative group/zone ${isDragging 
                                    ? 'border-primary bg-primary/10 scale-[1.02] shadow-xl shadow-primary/10' 
                                    : file 
                                        ? 'border-primary bg-primary/5' 
                                        : 'border-slate-300 dark:border-slate-700 surface-ladder-border-10 bg-slate-50/50 surface-ladder-10'
                                    } hover:border-primary hover:bg-slate-50 dark:hover:bg-white/5 transition-all`}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                            >
                                {isDragging && (
                                    <div className="absolute inset-0 bg-primary/5 animate-pulse rounded-xl pointer-events-none" />
                                )}
                                <div className="flex flex-col items-center gap-4 relative z-10">
                                    <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${isDragging || file ? 'bg-primary text-white scale-110' : 'bg-primary/10 text-primary group-hover/zone:scale-110'}`}>
                                        <span className={`material-symbols-outlined text-4xl ${isProcessing ? 'animate-spin' : ''}`}>
                                            {file ? 'check_circle' : isDragging ? 'download' : 'cloud_upload'}
                                        </span>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-slate-900 dark:text-white text-lg font-bold">
                                            {isDragging ? 'Drop to upload' : file ? 'Manuscript Ready' : 'Drag and drop your manuscript here'}
                                        </p>
                                        <div className="text-slate-500 dark:text-slate-400 text-sm mt-1 flex items-center justify-center gap-2">
                                            {file ? (
                                                <div className="flex items-center gap-2 px-3 py-1 bg-white dark:bg-slate-800 rounded-full border border-slate-200 dark:border-slate-700 shadow-sm">
                                                    <span className="truncate max-w-[200px]">{file.name}</span>
                                                    <span className="text-slate-400 text-xs">({formatFileSize(file.size)})</span>
                                                    <button 
                                                        onClick={(e) => { e.stopPropagation(); setFile(null); setFileError(null); }} 
                                                        className="hover:text-red-500 dark:hover:text-red-400 transition-colors flex items-center p-0.5" 
                                                        title="Remove file"
                                                    >
                                                        <span className="material-symbols-outlined text-sm">close</span>
                                                    </button>
                                                </div>
                                            ) : 'Supported formats: DOCX, PDF, TEX, TXT, HTML, MD, DOC (Max 50MB)'}
                                        </div>
                                        {fileError && <p className="text-red-500 text-xs mt-2 font-bold animate-bounce">{fileError}</p>}
                                    </div>
                                </div>
                                <input
                                    id="file-upload"
                                    type="file"
                                    ref={fileInputRef}
                                    className="sr-only"
                                    onChange={handleFileChange}
                                    accept={ACCEPTED_FORMATS}
                                    disabled={isProcessing}
                                />
                                <label
                                    htmlFor="file-upload"
                                    tabIndex={isProcessing ? -1 : 0}
                                    onKeyDown={(e) => {
                                        if (!isProcessing && (e.key === 'Enter' || e.key === ' ')) {
                                            e.preventDefault();
                                            fileInputRef.current?.click();
                                        }
                                    }}
                                    className={`flex w-full sm:w-auto min-w-[140px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-11 px-6 bg-primary text-white text-sm font-bold tracking-wide shadow-md hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 transition-all relative z-10 ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'}`}
                                >
                                    {isProcessing ? 'Locked' : file ? 'Change File' : 'Browse Files'}
                                </label>
                            </div>
                        </div>

                        {/* 2. Processing Parameters */}
                        <FormattingOptions
                            addPageNumbers={addPageNumbers}
                            setAddPageNumbers={setAddPageNumbers}
                            addBorders={addBorders}
                            setAddBorders={setAddBorders}
                            addCoverPage={addCoverPage}
                            setAddCoverPage={setAddCoverPage}
                            generateTOC={generateTOC}
                            setGenerateTOC={setGenerateTOC}
                            pageSize={pageSize}
                            setPageSize={setPageSize}
                            isProcessing={isProcessing}
                            progress={progress}
                            file={file}
                            onProcess={handleProcess}
                        />

                        {/* Fast Mode Toggle */}
                        <div className="bg-white surface-ladder-06 rounded-xl border border-slate-200 dark:border-slate-700/70 surface-ladder-border-10 p-6 shadow-sm hover:shadow-md dark:hover:shadow-none transition-shadow">
                            <FastModeToggle
                                fastMode={fastMode}
                                setFastMode={setFastMode}
                                disabled={isProcessing || progress === 100}
                            />
                        </div>

                        {isProcessing && (
                            <button
                                onClick={handleCancel}
                                className="w-full mt-3 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 text-red-600 dark:text-red-400 font-bold py-3 rounded-xl border border-red-200 dark:border-red-800 flex items-center justify-center gap-2 transition-all"
                            >
                                <span className="material-symbols-outlined text-lg">cancel</span>
                                Cancel Processing
                            </button>
                        )}

                        {/* Post-Processing Actions */}
                        {isJobCompleted && (
                            <div className="bg-white surface-ladder-06 rounded-xl border border-slate-200 dark:border-slate-700/70 surface-ladder-border-10 p-6 shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500 hover:shadow-md dark:hover:shadow-none transition-shadow">
                                <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                    <span className="material-symbols-outlined text-primary">analytics</span>
                                    Next Steps
                                </h2>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <button
                                        onClick={() => handleReviewClick('/compare')}
                                        disabled={isProcessing}
                                        className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-700/70 surface-ladder-border-10 bg-slate-50 surface-ladder-10 transition-all group ${isProcessing ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 hover:shadow-sm dark:hover:shadow-none text-slate-900 dark:text-white'}`}
                                    >
                                        <span className={`material-symbols-outlined text-2xl ${isProcessing ? 'text-slate-400' : 'text-primary'}`}>difference</span>
                                        <span className="text-sm font-bold">Compare Results</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/preview')}
                                        disabled={isProcessing}
                                        className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-700/70 surface-ladder-border-10 bg-slate-50 surface-ladder-10 transition-all group ${isProcessing ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 hover:shadow-sm dark:hover:shadow-none text-slate-900 dark:text-white'}`}
                                    >
                                        <span className={`material-symbols-outlined text-2xl ${isProcessing ? 'text-slate-400' : 'text-primary'}`}>visibility</span>
                                        <span className="text-sm font-bold">Preview Document</span>
                                    </button>
                                    <button
                                        onClick={() => navigate('/download')}
                                        disabled={isProcessing}
                                        className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-700/70 surface-ladder-border-10 bg-slate-50 surface-ladder-10 transition-all group ${isProcessing ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 hover:shadow-sm dark:hover:shadow-none text-slate-900 dark:text-white'}`}
                                    >
                                        <span className={`material-symbols-outlined text-2xl ${isProcessing ? 'text-slate-400' : 'text-primary'}`}>download</span>
                                        <span className="text-sm font-bold">Download Final</span>
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Progress Sidebar */}
                    <div className="lg:col-span-5">
                        <ProcessingStepper
                            isProcessing={isProcessing}
                            progress={progress}
                            statusMessage={statusMessage}
                            currentStep={currentStep}
                            steps={steps}
                        />
                    </div>
                </div>
            </main>

            <UpgradeModal 
                isOpen={showUpgradeModal} 
                onClose={() => setShowUpgradeModal(false)} 
                title="Upload Limit Reached" 
            />

            <Footer variant="app" />
        </div>
    );
}





