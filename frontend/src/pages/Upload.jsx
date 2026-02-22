import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import CategoryTabs from '../components/upload/CategoryTabs';
import TemplateSelector from '../components/upload/TemplateSelector';
import FormattingOptions from '../components/upload/FormattingOptions';
import ProcessingStepper from '../components/upload/ProcessingStepper';
import { isCompleted, isFailed, isProcessing as isStatusProcessing } from '../constants/status';
import {
    CHUNK_UPLOAD_THRESHOLD_BYTES,
    uploadChunked,
    uploadDocumentWithProgress,
    useDocumentStatus,
} from '../services/api';

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
    const { isLoggedIn } = useAuth();
    const { job, setJob } = useDocument();
    const fileInputRef = useRef(null);
    const terminalStatusHandledRef = useRef(false);
    const completionNotificationSentRef = useRef(false);
    const [file, setFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currentStep, setCurrentStep] = useState(0);
    const [statusMessage, setStatusMessage] = useState('Initializing...');
    const [template, setTemplate] = useState('none');
    const [category, setCategory] = useState('none'); // New State for Dropdown Filter
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
    const navigate = useNavigate();

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

    const { data: statusData, error: statusError } = useDocumentStatus(job?.id, {
        enabled: Boolean(job?.id) && isProcessing,
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
            setProgress(100);
            setCurrentStep(7);
            setStatusMessage('Processing complete!');
            return;
        }

        if (isFailed(normalizedStatus)) {
            setIsProcessing(false);
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
        setCurrentStep(0);
        setProgress(0);
        setStatusMessage('Processing cancelled.');
        terminalStatusHandledRef.current = false;
        completionNotificationSentRef.current = false;
    }, [abortController]);

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const handleProcess = useCallback(async () => {
        // Allow processing if file exists and NOT currently processing.
        // Even if progress was 100% (previous job), we allow starting a new one.
        if (!file || isProcessing) {
            return;
        }

        if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().catch(() => { });
        }

        const controller = new AbortController();
        setAbortController(controller);
        setIsProcessing(true);
        setProgress(0);
        setCurrentStep(1);
        setStatusMessage('Initiating upload...');
        terminalStatusHandledRef.current = false;
        completionNotificationSentRef.current = false;

        const uploadOptions = {
            add_page_numbers: addPageNumbers,
            add_borders: addBorders,
            add_cover_page: addCoverPage,
            generate_toc: generateTOC,
            page_size: pageSize,
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
                    setStatusMessage('Chunk upload complete. Processing started...');
                } else {
                    setProgress(0);
                    setStatusMessage('Chunk upload complete. Finalizing upload...');
                }
            } else if (file.size > CHUNK_UPLOAD_THRESHOLD_BYTES) {
                setStatusMessage('Large file detected. Uploading in single request mode...');
            }

            if (controller.signal.aborted) {
                return;
            }

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
                if (!result?.job_id) {
                    throw new Error('Upload response missing job id.');
                }
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
            sessionStorage.setItem('scholarform_currentJob', JSON.stringify(newJob));
        } catch (error) {
            if (controller.signal.aborted) {
                return;
            }
            console.error('Upload failed:', error);
            setIsProcessing(false);
            setStatusMessage(`Upload failed: ${error.message}`);
        } finally {
            setAbortController((activeController) => (activeController === controller ? null : activeController));
        }
    }, [
        addBorders,
        addCoverPage,
        addPageNumbers,
        file,
        generateTOC,
        isLoggedIn,
        isProcessing,
        pageSize,
        setJob,
        template,
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
        if (nextCategory === 'none') setTemplate('none');
        else if (nextCategory === 'ieee') setTemplate('ieee');
        else if (nextCategory === 'springer') setTemplate('springer');
        else if (nextCategory === 'apa') setTemplate('apa');
    }, [navigate]);

    const isJobCompleted = isCompleted(job?.status);

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen">
            <Navbar variant="app" activeTab="upload" />

            <main className="max-w-[1280px] mx-auto px-6 py-8">
                {/* NEW HEADER SECTION: Category & Style Selection */}
                <div className="mb-12 space-y-8">
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
                <div className="mb-8">
                    <h1 className="text-slate-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
                        Upload Manuscript
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 text-lg mt-2">
                        {isLoggedIn
                            ? 'Transform your research into a publication-ready document in minutes.'
                            : 'Professional academic formatting in seconds. No account required to start.'}
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    <div className="lg:col-span-7 flex flex-col gap-6">
                        {/* 1. Document Source */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">upload_file</span>
                                1. Document Source
                            </h2>
                            <div
                                className={`flex flex-col items-center gap-6 rounded-xl border-2 border-dashed px-6 py-12 transition-all duration-300 ${isDragging || file ? 'border-primary bg-primary/5' : 'border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50'
                                    } hover:border-primary`}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                            >
                                <div className="flex flex-col items-center gap-4">
                                    <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors duration-300 ${isDragging || file ? 'bg-primary text-white' : 'bg-primary/10 text-primary'}`}>
                                        <span className="material-symbols-outlined text-4xl">{file ? 'check_circle' : 'cloud_upload'}</span>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-slate-900 dark:text-white text-lg font-bold">
                                            {file ? 'File selected' : 'Drag and drop your manuscript here'}
                                        </p>
                                        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
                                            {file ? `File: ${file.name} (${formatFileSize(file.size)})` : 'Supported formats: DOCX, PDF, TEX, TXT, HTML/HTM, MD/MARKDOWN, DOC (Max 50MB)'}
                                        </p>
                                        {fileError && <p className="text-red-500 text-sm mt-2 font-medium">{fileError}</p>}
                                    </div>
                                </div>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    className="hidden"
                                    onChange={handleFileChange}
                                    accept={ACCEPTED_FORMATS}
                                    disabled={isProcessing}
                                />
                                <button
                                    onClick={() => fileInputRef.current.click()}
                                    disabled={isProcessing}
                                    className={`flex min-w-[140px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-11 px-6 bg-primary text-white text-sm font-bold tracking-wide shadow-md hover:bg-blue-700 transition-all ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    Browse Files
                                </button>
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

                        {isProcessing && (
                            <button
                                onClick={handleCancel}
                                className="w-full mt-3 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 text-red-600 dark:text-red-400 font-bold py-3 rounded-xl border border-red-200 dark:border-red-800 flex items-center justify-center gap-2 transition-all"
                            >
                                <span className="material-symbols-outlined text-lg">cancel</span>
                                Cancel Processing
                            </button>
                        )}

                        {/* 3. Post-Processing Actions - ALWAYS SHOW */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">analytics</span>
                                3. Post-Processing Actions
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <button
                                    onClick={() => isJobCompleted && !isProcessing && handleReviewClick('/compare')}
                                    disabled={!isJobCompleted || isProcessing}
                                    className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 transition-all group ${(!isJobCompleted || isProcessing) ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 text-slate-900 dark:text-white'}`}
                                >
                                    <span className={`material-symbols-outlined text-2xl ${(!isJobCompleted || isProcessing) ? 'text-slate-400' : 'text-primary'}`}>difference</span>
                                    <span className="text-sm font-bold">Compare Results</span>
                                </button>
                                <button
                                    onClick={() => isJobCompleted && !isProcessing && navigate('/preview')}
                                    disabled={!isJobCompleted || isProcessing}
                                    className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 transition-all group ${(!isJobCompleted || isProcessing) ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 text-slate-900 dark:text-white'}`}
                                >
                                    <span className={`material-symbols-outlined text-2xl ${(!isJobCompleted || isProcessing) ? 'text-slate-400' : 'text-primary'}`}>visibility</span>
                                    <span className="text-sm font-bold">Preview Document</span>
                                </button>
                                <button
                                    onClick={() => isJobCompleted && !isProcessing && navigate('/download')}
                                    disabled={!isJobCompleted || isProcessing}
                                    className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 transition-all group ${(!isJobCompleted || isProcessing) ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 text-slate-900 dark:text-white'}`}
                                >
                                    <span className={`material-symbols-outlined text-2xl ${(!isJobCompleted || isProcessing) ? 'text-slate-400' : 'text-primary'}`}>download</span>
                                    <span className="text-sm font-bold">Download Final</span>
                                </button>
                            </div>
                            <div className="mt-4 flex items-start gap-2 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                                <span className="material-symbols-outlined text-primary text-[18px]">info</span>
                                <p className="text-xs text-blue-700 dark:text-blue-300 font-medium">These actions will become available once your document processing is complete.</p>
                            </div>
                        </div>
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

            <Footer variant="app" />
        </div>
    );
}



