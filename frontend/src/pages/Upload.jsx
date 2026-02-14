import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Upload() {
    const { isLoggedIn } = useAuth();
    const { job, setJob } = useDocument();
    const fileInputRef = useRef(null);
    const [file, setFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currentStep, setCurrentStep] = useState(0);
    const [statusMessage, setStatusMessage] = useState('Initializing...');
    const [template, setTemplate] = useState('none');
    const [ocrEnabled, setOcrEnabled] = useState(true);
    const [aiEnabled, setAiEnabled] = useState(false);
    const navigate = useNavigate();

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

    // Job Restoration Logic (for page reloads)
    useEffect(() => {
        const checkSavedJob = async () => {
            const savedJob = sessionStorage.getItem('scholarform_currentJob');
            if (savedJob) {
                try {
                    const parsedJob = JSON.parse(savedJob);
                    const { getJobStatus } = await import('../services/api');

                    // Validate against backend - Source of Truth
                    const statusData = await getJobStatus(parsedJob.id);

                    // If we get here, job exists on backend
                    setJob(parsedJob);
                    setProgress(statusData.progress_percentage || 0);
                    if (statusData.message) setStatusMessage(statusData.message);
                    if (statusData.phase) setCurrentStep(getStepFromPhase(statusData.phase));

                    if (statusData.status === 'processing' || statusData.status === 'RUNNING') {
                        setIsProcessing(true);
                    } else if (statusData.status === 'COMPLETED') {
                        // Job is finished. ensure UI reflects this without clearing state.
                        setIsProcessing(false);
                        setProgress(100);
                        setCurrentStep(7);
                    }
                } catch (error) {
                    console.warn("Found stale job in storage, clearing:", error);
                    sessionStorage.removeItem('scholarform_currentJob');
                    setJob(null);
                    setIsProcessing(false);
                    setProgress(0);
                    setCurrentStep(0);
                }
            }
        };

        checkSavedJob();
    }, [setJob]);

    const handleReviewClick = (path) => {
        navigate(path);
    };

    // REAL-TIME POLLING
    useEffect(() => {
        let interval;
        if (isProcessing && job?.id) {
            interval = setInterval(async () => {
                try {
                    const { getJobStatus } = await import('../services/api');
                    const statusData = await getJobStatus(job.id);

                    // 1. Update Progress
                    setProgress(statusData.progress_percentage || 0);

                    // 2. Update Status Message & Step
                    // Use backend message if available, otherwise fallback
                    if (statusData.message) setStatusMessage(statusData.message);

                    if (statusData.phase) {
                        setCurrentStep(getStepFromPhase(statusData.phase));
                    }

                    // 3. Handle Completion
                    if (statusData.status === 'COMPLETED' || statusData.status === 'COMPLETED_WITH_WARNINGS') {
                        setIsProcessing(false);
                        setProgress(100);
                        setCurrentStep(7);
                        setStatusMessage(statusData.status === 'COMPLETED_WITH_WARNINGS'
                            ? `Completed with warnings: ${statusData.message}`
                            : 'Processing complete!');

                        const completedJob = {
                            ...job,
                            status: 'completed',
                            progress: 100,
                            outputPath: statusData.output_path,
                            warnings: statusData.status === 'COMPLETED_WITH_WARNINGS' ? statusData.message : null
                        };
                        setJob(completedJob);
                        sessionStorage.setItem('scholarform_currentJob', JSON.stringify(completedJob));

                        // Navigate to results
                        setTimeout(() => navigate('/download'), 500);
                    }
                    // 4. Handle Failure
                    else if (statusData.status === 'FAILED') {
                        setIsProcessing(false);
                        console.error("Job failed:", statusData.message);
                        setStatusMessage(`Failed: ${statusData.message}`);
                        // Optionally navigate to error page or stay here to retry
                        // navigate('/error'); 
                        // Staying on page helps user see the error and retry easily.
                        // But user request says "If FAILED: Show backend error, Keep user on Upload page, Allow retry"
                        // But the previous code navigated to /error. I will follow "Keep user on Upload page" as per stricter 1495 prompt.
                    }
                } catch (error) {
                    console.error("Polling error:", error);
                    // Continue polling on transient network errors
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [isProcessing, job, navigate, setJob]);

    const handleFileChange = (e) => {

        const selectedFile = e.target.files[0];
        if (selectedFile) {
            const validTypes = ['.docx', '.doc', '.pdf', '.tex', '.txt', '.html', '.htm', '.md', '.markdown'];
            const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();

            if (!validTypes.includes(fileExtension) || selectedFile.size > 50 * 1024 * 1024) {
                // navigate('/error'); // User request: "If FAILED: ... Keep user on Upload page"
                // But this is client-side validation failure. I'll stick to alert or simple return for now, or existing logic.
                // Existing logic was navigate('/error'). I'll keep it for invalid definition, but for polling failure I removed navigate.
                navigate('/error');
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
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            const validTypes = ['.docx', '.doc', '.pdf', '.tex', '.txt', '.html', '.htm', '.md', '.markdown'];
            const fileExtension = droppedFile.name.substring(droppedFile.name.lastIndexOf('.')).toLowerCase();

            if (!validTypes.includes(fileExtension) || droppedFile.size > 50 * 1024 * 1024) {
                navigate('/error');
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

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const handleProcess = async () => {
        // Allow processing if file exists and NOT currently processing.
        // Even if progress was 100% (previous job), we allow starting a new one.
        if (file && !isProcessing) {
            setIsProcessing(true);
            setProgress(0);
            setCurrentStep(1);
            setStatusMessage("Initiating upload...");

            try {
                const { uploadDocument } = await import('../services/api');
                // Pass real options to backend
                const result = await uploadDocument(file, template, {
                    enableOCR: ocrEnabled,
                    enableAI: aiEnabled
                });

                const newJob = {
                    id: result.job_id,
                    timestamp: new Date().toISOString(),
                    status: 'processing',
                    originalFileName: file.name,
                    template: template,
                    flags: { ai_enhanced: aiEnabled, ocr_applied: ocrEnabled },
                    progress: 0
                };
                setJob(newJob);
                sessionStorage.setItem('scholarform_currentJob', JSON.stringify(newJob));

            } catch (error) {
                console.error("Upload failed:", error);
                setIsProcessing(false);
                setStatusMessage(`Upload failed: ${error.message}`);
                // navigate('/error'); // Keep user on page to retry
            }
        }
    };

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen">
            <Navbar variant="app" activeTab="upload" />

            <main className="max-w-[1280px] mx-auto px-6 py-8">
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
                                            {file ? `File: ${file.name} (${formatFileSize(file.size)})` : 'Supported formats: DOCX, PDF, LaTeX, TXT, HTML, MD (Max 50MB)'}
                                        </p>
                                    </div>
                                </div>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    className="hidden"
                                    onChange={handleFileChange}
                                    accept=".docx,.doc,.pdf,.tex,.txt,.html,.htm,.md,.markdown"
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
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">tune</span>
                                2. Processing Parameters
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="flex flex-col gap-2">
                                    <div className="flex items-center justify-between">
                                        <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Target Journal Template</label>
                                        <Link className="text-xs font-medium text-primary hover:underline flex items-center gap-1" to="/templates">
                                            <span className="material-symbols-outlined text-[14px]">grid_view</span>
                                            Browse Library
                                        </Link>
                                    </div>
                                    <div className="relative w-full group">
                                        <select
                                            value={template}
                                            onChange={(e) => {
                                                const val = e.target.value;
                                                if (val === 'browse_more') {
                                                    navigate('/templates');
                                                } else {
                                                    setTemplate(val);
                                                }
                                            }}
                                            disabled={isProcessing || progress === 100}
                                            className="peer w-full h-12 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 pl-4 pr-10 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none appearance-none disabled:opacity-50 transition-all duration-200 ease-in-out font-medium cursor-pointer disabled:cursor-not-allowed"
                                        >
                                            <option value="none">None (General Formatting)</option>
                                            <option value="ieee">IEEE Conference / Journal</option>
                                            <option value="springer">Springer Nature (Standard)</option>
                                            <option value="apa">APA Style (7th Edition)</option>
                                            <option value="browse_more" className="text-primary font-bold">Browse More Templates...</option>
                                        </select>
                                        <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center">
                                            <svg className={`h-4 w-4 text-slate-500 dark:text-slate-400`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-4">
                                    <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Enable OCR</span>
                                            <span className="text-xs text-slate-500">Extract text from images/scans</span>
                                        </div>
                                        <div className="relative inline-block w-12 align-middle select-none transition duration-200 ease-in">
                                            <input
                                                checked={ocrEnabled}
                                                onChange={(e) => setOcrEnabled(e.target.checked)}
                                                disabled={isProcessing || progress === 100}
                                                className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer right-6 checked:right-0 transition-all duration-300 disabled:opacity-50"
                                                id="ocr" name="toggle" style={{ top: 0, right: ocrEnabled ? '0px' : '24px' }} type="checkbox"
                                            />
                                            <label className={`toggle-label block overflow-hidden h-6 rounded-full cursor-pointer transition-colors duration-300 ${ocrEnabled ? 'bg-primary' : 'bg-slate-300'}`} htmlFor="ocr"></label>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">AI/NLP Analysis</span>
                                            <span className="text-xs text-slate-500">Detect citation errors & gaps</span>
                                        </div>
                                        <div className="relative inline-block w-12 align-middle select-none transition duration-200 ease-in">
                                            <input
                                                checked={aiEnabled}
                                                onChange={(e) => setAiEnabled(e.target.checked)}
                                                disabled={isProcessing || progress === 100}
                                                className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer right-6 checked:right-0 transition-all duration-300 disabled:opacity-50"
                                                id="nlp" name="toggle" style={{ top: 0, right: aiEnabled ? '0px' : '24px' }} type="checkbox"
                                            />
                                            <label className={`toggle-label block overflow-hidden h-6 rounded-full cursor-pointer transition-colors duration-300 ${aiEnabled ? 'bg-primary' : 'bg-slate-300'}`} htmlFor="nlp"></label>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleProcess}
                                disabled={!file || isProcessing}
                                className={`w-full mt-8 bg-primary hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/25 flex items-center justify-center gap-3 transition-all transform ${(!file || isProcessing) ? 'opacity-50 cursor-not-allowed' : 'hover:-translate-y-0.5'}`}
                            >
                                <span className="material-symbols-outlined">
                                    {progress === 100 ? 'replay' : isProcessing ? 'sync' : 'rocket_launch'}
                                </span>
                                {isProcessing ? 'Processing Manuscript...' : progress === 100 ? 'Re-process Manuscript' : 'Process Document'}
                            </button>
                        </div>

                        {/* 3. Post-Processing Actions - ALWAYS SHOW */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">analytics</span>
                                3. Post-Processing Actions
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <button
                                    onClick={() => job?.status === 'completed' && !isProcessing && handleReviewClick('/compare')}
                                    disabled={job?.status !== 'completed' || isProcessing}
                                    className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 transition-all group ${(job?.status !== 'completed' || isProcessing) ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 text-slate-900 dark:text-white'}`}
                                >
                                    <span className={`material-symbols-outlined text-2xl ${(job?.status !== 'completed' || isProcessing) ? 'text-slate-400' : 'text-primary'}`}>difference</span>
                                    <span className="text-sm font-bold">Compare Results</span>
                                </button>
                                <button
                                    onClick={() => job?.status === 'completed' && !isProcessing && navigate('/preview')}
                                    disabled={job?.status !== 'completed' || isProcessing}
                                    className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 transition-all group ${(job?.status !== 'completed' || isProcessing) ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 text-slate-900 dark:text-white'}`}
                                >
                                    <span className={`material-symbols-outlined text-2xl ${(job?.status !== 'completed' || isProcessing) ? 'text-slate-400' : 'text-primary'}`}>visibility</span>
                                    <span className="text-sm font-bold">Preview Document</span>
                                </button>
                                <button
                                    onClick={() => job?.status === 'completed' && !isProcessing && navigate('/download')}
                                    disabled={job?.status !== 'completed' || isProcessing}
                                    className={`flex flex-col items-center justify-center gap-2 p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 transition-all group ${(job?.status !== 'completed' || isProcessing) ? 'opacity-50 cursor-not-allowed text-slate-500' : 'hover:border-primary hover:bg-primary/5 text-slate-900 dark:text-white'}`}
                                >
                                    <span className={`material-symbols-outlined text-2xl ${(job?.status !== 'completed' || isProcessing) ? 'text-slate-400' : 'text-primary'}`}>download</span>
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
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm sticky top-24">
                            <div className="p-6 border-b border-slate-100 dark:border-slate-800">
                                <div className="flex items-center justify-between mb-4">
                                    <h2 className="text-lg font-bold text-slate-900 dark:text-white">Processing Status</h2>
                                    <span className={`text-xs font-bold uppercase tracking-widest px-2 py-1 rounded transition-colors ${isProcessing ? 'bg-primary/10 text-primary animate-pulse' : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                                        }`}>
                                        {isProcessing ? 'Processing' : 'Standby'}
                                    </span>
                                </div>
                                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                                    <div
                                        className="bg-primary h-full transition-all duration-500 ease-out"
                                        style={{ width: `${progress}%` }}
                                    ></div>
                                </div>
                                <div className="flex justify-between mt-2">
                                    <span className="text-xs text-slate-500 truncate max-w-[200px]" title={statusMessage}>
                                        {statusMessage}
                                    </span>
                                    <span className="text-xs font-bold text-primary">{Math.round(progress)}%</span>
                                </div>
                            </div>

                            <div className="p-6 space-y-6">
                                {steps.map((step) => {
                                    const isStepCompleted = currentStep > step.id || progress === 100;
                                    const isStepActive = currentStep === step.id && isProcessing;
                                    const isPending = currentStep < step.id;

                                    return (
                                        <div key={step.id} className={`flex items-start gap-4 transition-opacity duration-500 ${isPending ? 'opacity-50' : 'opacity-100'}`}>
                                            <div className="flex flex-col items-center">
                                                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 transition-all ${isStepCompleted ? 'bg-green-100 border-green-100 text-green-600' :
                                                    isStepActive ? 'bg-primary/20 border-primary text-primary' :
                                                        'bg-slate-100 dark:bg-slate-800 border-transparent text-slate-400'
                                                    }`}>
                                                    {isStepCompleted ? (
                                                        <span className="material-symbols-outlined text-sm font-bold">check</span>
                                                    ) : isStepActive ? (
                                                        <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                                                    ) : (
                                                        <span className="text-xs font-bold">{step.id}</span>
                                                    )}
                                                </div>
                                                {step.id < steps.length && (
                                                    <div className={`w-0.5 h-8 mt-2 transition-colors duration-500 ${isStepCompleted ? 'bg-green-200 dark:bg-green-900' : 'bg-slate-200 dark:bg-slate-800'}`}></div>
                                                )}
                                            </div>
                                            <div className="pt-1">
                                                <p className={`text-sm font-bold transition-colors ${isStepActive ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>
                                                    {step.title}
                                                </p>
                                                <p className="text-xs text-slate-500 mt-1">
                                                    {isStepCompleted ? 'Completed' : isStepActive ? step.desc : 'Pending...'}
                                                </p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            <div className="p-6 bg-slate-50 dark:bg-slate-800/30 rounded-b-xl flex justify-center">
                                <p className="text-xs text-slate-400 flex items-center gap-1 italic">
                                    <span className="material-symbols-outlined text-[14px]">
                                        {isProcessing ? 'sync' : 'info'}
                                    </span>
                                    {isProcessing ? 'Live updates from server...' : 'Ready to process'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <Footer variant="app" />
        </div>
    );
}
