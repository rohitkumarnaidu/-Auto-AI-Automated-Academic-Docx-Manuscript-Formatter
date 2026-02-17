import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const ALLOWED_UPLOAD_EXTENSIONS = ['.docx', '.pdf', '.tex'];
const MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024;

const isAllowedUploadFile = (selectedFile) => {
    if (!selectedFile?.name) {
        return false;
    }

    const fileExtension = selectedFile.name
        .substring(selectedFile.name.lastIndexOf('.'))
        .toLowerCase();

    return (
        ALLOWED_UPLOAD_EXTENSIONS.includes(fileExtension) &&
        selectedFile.size > 0 &&
        selectedFile.size <= MAX_UPLOAD_SIZE_BYTES
    );
};

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
    const [category, setCategory] = useState('none'); // New State for Dropdown Filter
    // New Formatting Options
    const [addPageNumbers, setAddPageNumbers] = useState(true);
    const [addBorders, setAddBorders] = useState(false);
    const [addCoverPage, setAddCoverPage] = useState(true);
    const [generateTOC, setGenerateTOC] = useState(false);
    const [pageSize, setPageSize] = useState('Letter');
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
            if (!isAllowedUploadFile(selectedFile)) {
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
            if (!isAllowedUploadFile(droppedFile)) {
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
                    add_page_numbers: addPageNumbers,
                    add_borders: addBorders,
                    add_cover_page: addCoverPage,
                    generate_toc: generateTOC,
                    page_size: pageSize
                });

                const newJob = {
                    id: result.job_id,
                    timestamp: new Date().toISOString(),
                    status: 'processing',
                    originalFileName: file.name,
                    template: template,
                    flags: {
                        page_numbers: addPageNumbers,
                        borders: addBorders,
                        cover_page: addCoverPage,
                        toc: generateTOC,
                        page_size: pageSize
                    },
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
                {/* NEW HEADER SECTION: Category & Style Selection */}
                <div className="mb-12 space-y-8">
                    {/* Category Tabs: Centered */}
                    <div className="flex flex-col items-center gap-4">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Select Category</h2>
                        <div className="flex bg-slate-100 dark:bg-slate-800/50 p-1.5 rounded-xl inline-flex shadow-inner">
                            <button className="px-8 py-2.5 rounded-lg bg-primary text-white text-sm font-bold shadow-sm transition-all">
                                Documents
                            </button>
                            <button className="px-8 py-2.5 rounded-lg text-slate-500 dark:text-slate-400 text-sm font-medium hover:text-slate-700 dark:hover:text-slate-200 transition-all hover:bg-slate-200/50 dark:hover:bg-slate-700/50">
                                Resume
                            </button>
                            <button className="px-8 py-2.5 rounded-lg text-slate-500 dark:text-slate-400 text-sm font-medium hover:text-slate-700 dark:hover:text-slate-200 transition-all hover:bg-slate-200/50 dark:hover:bg-slate-700/50">
                                Portfolio
                            </button>
                        </div>
                    </div>

                    {/* Style Showcase */}
                    <div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                            <div className="flex items-center gap-4 w-full sm:w-auto">
                                <h2 className="text-xl font-bold text-slate-900 dark:text-white whitespace-nowrap">Select Template</h2>

                                {/* Restored Dropdown */}
                                <div className="relative flex-1 sm:w-64 group">
                                    <select
                                        value={category}
                                        onChange={(e) => {
                                            const val = e.target.value;
                                            if (val === 'browse_more') {
                                                navigate('/templates');
                                            } else {
                                                setCategory(val);
                                                // Auto-select the first appropriate template for the category
                                                if (val === 'none') setTemplate('none');
                                                else if (val === 'ieee') setTemplate('ieee');
                                                else if (val === 'springer') setTemplate('springer');
                                                else if (val === 'apa') setTemplate('apa');
                                            }
                                        }}
                                        disabled={isProcessing}
                                        className="w-full h-10 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 pl-3 pr-8 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none appearance-none disabled:opacity-50 transition-all font-medium cursor-pointer"
                                    >
                                        <option value="none">None (General Formatting)</option>
                                        <option value="ieee">IEEE Standard</option>
                                        <option value="springer">Springer Nature(Standard)</option>
                                        <option value="apa">APA Style(7th Edition)</option>
                                        <option value="browse_more" className="text-primary font-bold">Browse More Templates...</option>
                                    </select>
                                    <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center">
                                        <span className="material-symbols-outlined text-[18px] text-slate-500">expand_more</span>
                                    </div>
                                </div>
                            </div>

                            <Link className="text-sm font-medium text-primary hover:underline flex items-center gap-1 shrink-0" to="/templates">
                                Browse Library <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                            </Link>
                        </div>

                        {/* Carousel Container */}
                        <div className="relative group/carousel">
                            {/* Scrollable Area - Width adjusted for 3 items (280px * 3 + gaps) + peek */}
                            <div className={`flex overflow-x-auto gap-6 pb-8 pt-4 px-4 snap-x scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-600 scrollbar-track-transparent max-w-[920px] mx-auto ${category !== 'none' ? 'justify-center' : ''}`}>

                                {/* CATEGORY: NONE -> SHOW ORIGINAL + MODERN STYLES */}
                                {category === 'none' && (
                                    <>
                                        {/* Template 1: Original */}
                                        <div
                                            onClick={() => !isProcessing && setTemplate('none')}
                                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden ${template === 'none' ? 'border-primary bg-primary/5 ring-4 ring-primary/10' : 'border-dashed border-slate-300 dark:border-slate-700 bg-transparent hover:border-primary/50'}`}
                                        >
                                            <div className="aspect-[3/4] flex flex-col items-center justify-center p-8 text-center relative">
                                                {file ? (
                                                    <div className="animate-in fade-in zoom-in duration-300 w-full">
                                                        <div className="w-20 h-20 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 flex items-center justify-center mb-4 mx-auto">
                                                            <span className="material-symbols-outlined text-4xl text-primary">description</span>
                                                        </div>
                                                        <p className="text-sm font-bold text-slate-900 dark:text-white line-clamp-2 break-all">{file.name}</p>
                                                        <p className="text-xs text-slate-500 mt-1">{formatFileSize(file.size)}</p>
                                                    </div>
                                                ) : (
                                                    <div className="opacity-50">
                                                        <span className="material-symbols-outlined text-5xl text-slate-400 mb-3">upload_file</span>
                                                        <p className="text-sm font-medium text-slate-500">Original File</p>
                                                        <p className="text-xs text-slate-400 mt-1">No styling applied</p>
                                                    </div>
                                                )}
                                                {template === 'none' && (
                                                    <div className="absolute top-3 right-3">
                                                        <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center shadow-md">
                                                            <span className="material-symbols-outlined text-[18px]">check</span>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
                                                <p className={`text-base font-bold ${template === 'none' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>Original</p>
                                                <p className="text-xs text-slate-500 mt-0.5">Keep existing formatting</p>
                                            </div>
                                        </div>

                                        {/* Template 2: Modern Red (High-Fidelity CSS) */}
                                        <div
                                            onClick={() => !isProcessing && setTemplate('modern_red')}
                                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'modern_red' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                                        >
                                            <div className="aspect-[3/4] bg-white p-6 flex flex-col relative overflow-hidden select-none shadow-inner">
                                                {/* Red Header Style */}
                                                <div className="w-full text-center mb-6">
                                                    <div className="text-[10px] font-black text-red-600 uppercase tracking-[0.2em] mb-1">Style Showcase</div>
                                                    <div className="w-16 h-[2px] bg-red-600 mx-auto"></div>
                                                </div>
                                                <div className="flex flex-col gap-3">
                                                    {/* Fake Title */}
                                                    <div className="w-1/2 h-2.5 bg-slate-800 rounded-sm mb-1"></div>

                                                    {/* Fake Text Blocks */}
                                                    <div className="w-full flex flex-col gap-1.5 opacity-60">
                                                        <div className="w-full h-1 bg-slate-400 rounded-full"></div>
                                                        <div className="w-full h-1 bg-slate-400 rounded-full"></div>
                                                        <div className="w-5/6 h-1 bg-slate-400 rounded-full"></div>
                                                    </div>

                                                    {/* Highlight Box */}
                                                    <div className="w-full bg-blue-900 rounded-lg mt-3 p-3 shadow-sm">
                                                        <div className="w-1/3 h-1.5 bg-white/30 rounded-full mb-2"></div>
                                                        <div className="w-full h-1 bg-white/20 rounded-full"></div>
                                                    </div>

                                                    {/* More Text */}
                                                    <div className="w-full flex flex-col gap-1.5 opacity-60 mt-2">
                                                        <div className="w-11/12 h-1 bg-slate-400 rounded-full"></div>
                                                        <div className="w-full h-1 bg-slate-400 rounded-full"></div>
                                                    </div>
                                                </div>

                                                {template === 'modern_red' && (
                                                    <div className="absolute inset-0 bg-primary/10 flex items-center justify-center backdrop-blur-[1px]">
                                                        <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center shadow-xl scale-100 transition-transform"><span className="material-symbols-outlined text-2xl">check</span></div>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                                                <p className={`text-base font-bold ${template === 'modern_red' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>Modern Red</p>
                                                <p className="text-xs text-slate-500 mt-0.5">Bold & Professional</p>
                                            </div>
                                        </div>

                                        {/* Template 3: Modern Gold (High-Fidelity CSS) */}
                                        <div
                                            onClick={() => !isProcessing && setTemplate('modern_gold')}
                                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'modern_gold' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                                        >
                                            <div className="aspect-[3/4] bg-white p-6 flex flex-col relative overflow-hidden select-none shadow-inner">
                                                {/* Gold Header Style */}
                                                <div className="w-full bg-slate-900 py-2.5 px-4 mb-4 rounded-sm shadow-sm flex items-center justify-between">
                                                    <div className="w-20 h-1.5 bg-white/20 rounded-full"></div>
                                                    <div className="w-4 h-4 rounded-full border border-amber-500/50"></div>
                                                </div>

                                                {/* Gold Subhead */}
                                                <div className="w-full border-l-4 border-amber-500 pl-3 py-1 mb-4 bg-amber-50/50">
                                                    <div className="w-1/3 h-2 bg-amber-600/80 rounded-sm"></div>
                                                </div>

                                                <div className="flex flex-col gap-3 px-1">
                                                    <div className="w-full flex flex-col gap-1.5 opacity-60">
                                                        <div className="w-full h-1 bg-slate-500 rounded-full"></div>
                                                        <div className="w-11/12 h-1 bg-slate-500 rounded-full"></div>
                                                        <div className="w-full h-1 bg-slate-500 rounded-full"></div>
                                                    </div>

                                                    {/* List Items */}
                                                    <div className="mt-2 flex flex-col gap-2">
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
                                                            <div className="w-3/4 h-1 bg-slate-400 rounded-full"></div>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
                                                            <div className="w-2/3 h-1 bg-slate-400 rounded-full"></div>
                                                        </div>
                                                    </div>
                                                </div>

                                                {template === 'modern_gold' && (
                                                    <div className="absolute inset-0 bg-primary/10 flex items-center justify-center backdrop-blur-[1px]">
                                                        <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center shadow-xl scale-100 transition-transform"><span className="material-symbols-outlined text-2xl">check</span></div>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                                                <p className={`text-base font-bold ${template === 'modern_gold' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>Modern Gold</p>
                                                <p className="text-xs text-slate-500 mt-0.5">Classic & Elegant</p>
                                            </div>
                                        </div>

                                        {/* Template 4: Modern Blue (High-Fidelity CSS) */}
                                        <div
                                            onClick={() => !isProcessing && setTemplate('modern_blue')}
                                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'modern_blue' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                                        >
                                            <div className="aspect-[3/4] bg-white p-6 flex flex-col relative overflow-hidden select-none shadow-inner">
                                                {/* Blue Header Style */}
                                                <div className="w-full bg-blue-600 text-white rounded-md mb-2 p-3 shadow-md">
                                                    <div className="w-1/2 h-2 bg-white/90 rounded-sm mx-auto mb-2 opacity-90"></div>
                                                    <div className="w-full h-0.5 bg-blue-400/50"></div>
                                                </div>
                                                <div className="w-full h-1.5 bg-blue-100 rounded-full mb-5"></div>

                                                <div className="flex flex-col gap-3">
                                                    {/* Section */}
                                                    <div>
                                                        <div className="flex items-center gap-2 mb-1.5">
                                                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                                            <div className="w-1/3 h-1.5 bg-blue-600 rounded-sm"></div>
                                                        </div>
                                                        <div className="w-full h-[1px] bg-blue-200 mb-2"></div>
                                                        <div className="w-full flex flex-col gap-1.5 opacity-60 pl-4">
                                                            <div className="w-full h-1 bg-slate-500 rounded-full"></div>
                                                            <div className="w-5/6 h-1 bg-slate-500 rounded-full"></div>
                                                        </div>
                                                    </div>

                                                    {/* Boxed Section */}
                                                    <div className="bg-slate-50 border border-slate-100 p-2 rounded-lg mt-1">
                                                        <div className="w-1/4 h-1.5 bg-slate-300 rounded-sm mb-2"></div>
                                                        <div className="w-full h-1 bg-slate-300 rounded-full opacity-50"></div>
                                                    </div>
                                                </div>

                                                {template === 'modern_blue' && (
                                                    <div className="absolute inset-0 bg-primary/10 flex items-center justify-center backdrop-blur-[1px]">
                                                        <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center shadow-xl scale-100 transition-transform"><span className="material-symbols-outlined text-2xl">check</span></div>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                                                <p className={`text-base font-bold ${template === 'modern_blue' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>Modern Blue</p>
                                                <p className="text-xs text-slate-500 mt-0.5">Clean & Corporate</p>
                                            </div>
                                        </div>
                                    </>
                                )}

                                {/* CATEGORY: IEEE */}
                                {category === 'ieee' && (
                                    <div
                                        onClick={() => !isProcessing && setTemplate('ieee')}
                                        className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'ieee' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                                    >
                                        <div className="aspect-[3/4] bg-slate-50 dark:bg-slate-800 p-6 flex flex-col gap-2 relative overflow-hidden select-none">
                                            {/* IEEE Visual - Detailed */}
                                            <div className="w-full h-4 bg-slate-200 dark:bg-slate-700 mb-4 mx-auto flex items-center justify-center rounded-sm border border-slate-300 dark:border-slate-600">
                                                <div className="w-2/3 h-2 bg-slate-800 dark:bg-slate-400 rounded-sm"></div>
                                            </div>

                                            <div className="flex gap-3 flex-1">
                                                {/* Col 1 */}
                                                <div className="w-1/2 flex flex-col gap-2">
                                                    <div className="w-full h-1.5 bg-slate-400 dark:bg-slate-600 rounded-full"></div>
                                                    <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                                                    <div className="w-3/4 h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>

                                                    {/* Figure */}
                                                    <div className="w-full h-16 bg-white dark:bg-slate-700 rounded border border-slate-200 dark:border-slate-600 mt-2 p-1 flex items-center justify-center">
                                                        <span className="material-symbols-outlined text-slate-300 text-lg">image</span>
                                                    </div>
                                                    <div className="w-full h-1 bg-slate-300 dark:bg-slate-700 rounded-full mt-1"></div>
                                                </div>

                                                {/* Col 2 */}
                                                <div className="w-1/2 flex flex-col gap-2">
                                                    <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                                                    <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                                                    <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>

                                                    <div className="w-full h-10 bg-blue-500/10 rounded mt-2 border border-blue-500/20 p-1">
                                                        <div className="w-full h-0.5 bg-blue-500/30 mb-1"></div>
                                                        <div className="w-2/3 h-0.5 bg-blue-500/30"></div>
                                                    </div>
                                                </div>
                                            </div>

                                            {template === 'ieee' && (
                                                <div className="absolute inset-0 bg-primary/5 flex items-center justify-center backdrop-blur-[1px]">
                                                    <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center shadow-xl scale-100 transition-transform"><span className="material-symbols-outlined text-2xl">check</span></div>
                                                </div>
                                            )}
                                        </div>
                                        <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                                            <p className={`text-base font-bold ${template === 'ieee' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>IEEE Standard</p>
                                            <p className="text-xs text-slate-500 mt-0.5">Two-column, technical format</p>
                                        </div>
                                    </div>
                                )}

                                {/* CATEGORY: SPRINGER */}
                                {category === 'springer' && (
                                    <div
                                        onClick={() => !isProcessing && setTemplate('springer')}
                                        className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'springer' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                                    >
                                        <div className="aspect-[3/4] bg-slate-50 dark:bg-slate-800 p-8 flex flex-col items-center relative overflow-hidden select-none">
                                            {/* Springer Visual */}
                                            <div className="w-full h-10 bg-slate-800 dark:bg-slate-700 mb-6 flex items-center justify-center rounded-sm shadow-md">
                                                <div className="w-1/2 h-1.5 bg-white/30 rounded-full"></div>
                                            </div>

                                            <div className="w-full flex flex-col gap-3">
                                                <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
                                                <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                                                <div className="w-5/6 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full"></div>

                                                <div className="w-1/3 h-2 bg-amber-500/80 mt-2 rounded-sm"></div>
                                                <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full"></div>

                                                <div className="w-full h-16 bg-white dark:bg-slate-700/50 border-l-4 border-amber-500 mt-2 p-2 shadow-sm">
                                                    <div className="w-2/3 h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full mb-2"></div>
                                                    <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                                                </div>
                                            </div>

                                            {template === 'springer' && (
                                                <div className="absolute inset-0 bg-primary/5 flex items-center justify-center backdrop-blur-[1px]">
                                                    <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center shadow-xl scale-100 transition-transform"><span className="material-symbols-outlined text-2xl">check</span></div>
                                                </div>
                                            )}
                                        </div>
                                        <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                                            <p className={`text-base font-bold ${template === 'springer' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>Springer Nature</p>
                                            <p className="text-xs text-slate-500 mt-0.5">Clean, single-column layout</p>
                                        </div>
                                    </div>
                                )}

                                {/* CATEGORY: APA */}
                                {category === 'apa' && (
                                    <div
                                        onClick={() => !isProcessing && setTemplate('apa')}
                                        className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'apa' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                                    >
                                        <div className="aspect-[3/4] bg-slate-50 dark:bg-slate-800 p-6 flex flex-col relative overflow-hidden select-none">
                                            {/* APA Visual */}
                                            <div className="w-full h-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm p-4 relative">
                                                <div className="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>

                                                <div className="w-full h-6 bg-blue-50 dark:bg-blue-900/20 mb-4 rounded-sm border-l-4 border-blue-500 flex items-center pl-2">
                                                    <div className="w-1/2 h-1.5 bg-blue-300 dark:bg-blue-700 rounded-full"></div>
                                                </div>

                                                <div className="w-full flex flex-col gap-3">
                                                    <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
                                                    <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                                                    <div className="w-11/12 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
                                                </div>

                                                <div className="mt-6 flex flex-col gap-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                                                        <div className="w-2/3 h-1.5 bg-slate-300 rounded-full"></div>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                                                        <div className="w-1/2 h-1.5 bg-slate-300 rounded-full"></div>
                                                    </div>
                                                </div>

                                                <div className="mt-auto w-full h-10 bg-slate-50 dark:bg-slate-700 rounded border border-slate-100 dark:border-slate-600 flex items-center justify-center text-[8px] text-slate-300">
                                                    References
                                                </div>
                                            </div>

                                            {template === 'apa' && (
                                                <div className="absolute inset-0 bg-primary/5 flex items-center justify-center backdrop-blur-[1px]">
                                                    <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center shadow-xl scale-100 transition-transform"><span className="material-symbols-outlined text-2xl">check</span></div>
                                                </div>
                                            )}
                                        </div>
                                        <div className="p-4 border-t border-slate-100 dark:border-slate-800">
                                            <p className={`text-base font-bold ${template === 'apa' ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>APA Style</p>
                                            <p className="text-xs text-slate-500 mt-0.5">7th Edition Standard</p>
                                        </div>
                                    </div>
                                )}

                            </div>
                        </div>
                    </div>
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
                                            {file ? `File: ${file.name} (${formatFileSize(file.size)})` : 'Supported formats: DOCX, PDF, TEX (Max 50MB)'}
                                        </p>
                                    </div>
                                </div>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    className="hidden"
                                    onChange={handleFileChange}
                                    accept=".docx,.pdf,.tex"
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
                                2. Formatting Options
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="flex flex-col gap-4">
                                    {/* Page Numbers */}
                                    <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 transition-colors">
                                        <div className="flex items-center gap-2">
                                            <span className="material-symbols-outlined text-slate-500">format_list_numbered</span>
                                            <span className="text-sm font-bold text-slate-900 dark:text-white">Add Page Numbers</span>
                                        </div>
                                        <div className="relative inline-block w-10 align-middle select-none transition duration-200 ease-in">
                                            <input
                                                checked={addPageNumbers}
                                                onChange={(e) => setAddPageNumbers(e.target.checked)}
                                                disabled={isProcessing || progress === 100}
                                                className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer right-5 checked:right-0 transition-all duration-300 disabled:opacity-50"
                                                id="page_numbers" name="toggle" style={{ top: 0, right: addPageNumbers ? '0px' : '20px' }} type="checkbox"
                                            />
                                            <label className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer transition-colors duration-300 ${addPageNumbers ? 'bg-primary' : 'bg-slate-300'}`} htmlFor="page_numbers"></label>
                                        </div>
                                    </div>

                                    {/* Borders */}
                                    <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 transition-colors">
                                        <div className="flex items-center gap-2">
                                            <span className="material-symbols-outlined text-slate-500">border_style</span>
                                            <span className="text-sm font-bold text-slate-900 dark:text-white">Add Borders</span>
                                        </div>
                                        <div className="relative inline-block w-10 align-middle select-none transition duration-200 ease-in">
                                            <input
                                                checked={addBorders}
                                                onChange={(e) => setAddBorders(e.target.checked)}
                                                disabled={isProcessing || progress === 100}
                                                className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer right-5 checked:right-0 transition-all duration-300 disabled:opacity-50"
                                                id="borders" name="toggle" style={{ top: 0, right: addBorders ? '0px' : '20px' }} type="checkbox"
                                            />
                                            <label className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer transition-colors duration-300 ${addBorders ? 'bg-primary' : 'bg-slate-300'}`} htmlFor="borders"></label>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-4">
                                    {/* Cover Page */}
                                    <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 transition-colors">
                                        <div className="flex items-center gap-2">
                                            <span className="material-symbols-outlined text-slate-500">article</span>
                                            <span className="text-sm font-bold text-slate-900 dark:text-white">Add Cover Page</span>
                                        </div>
                                        <div className="relative inline-block w-10 align-middle select-none transition duration-200 ease-in">
                                            <input
                                                checked={addCoverPage}
                                                onChange={(e) => setAddCoverPage(e.target.checked)}
                                                disabled={isProcessing || progress === 100}
                                                className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer right-5 checked:right-0 transition-all duration-300 disabled:opacity-50"
                                                id="cover_page" name="toggle" style={{ top: 0, right: addCoverPage ? '0px' : '20px' }} type="checkbox"
                                            />
                                            <label className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer transition-colors duration-300 ${addCoverPage ? 'bg-primary' : 'bg-slate-300'}`} htmlFor="cover_page"></label>
                                        </div>
                                    </div>

                                    {/* TOC */}
                                    <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 transition-colors">
                                        <div className="flex flex-col">
                                            <div className="flex items-center gap-2">
                                                <span className="material-symbols-outlined text-slate-500">toc</span>
                                                <span className="text-sm font-bold text-slate-900 dark:text-white">Generate TOC</span>
                                            </div>
                                            <span className="text-[10px] text-slate-400 pl-8">Auto generates from headings</span>
                                        </div>
                                        <div className="relative inline-block w-10 align-middle select-none transition duration-200 ease-in">
                                            <input
                                                checked={generateTOC}
                                                onChange={(e) => setGenerateTOC(e.target.checked)}
                                                disabled={isProcessing || progress === 100}
                                                className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer right-5 checked:right-0 transition-all duration-300 disabled:opacity-50"
                                                id="toc" name="toggle" style={{ top: 0, right: generateTOC ? '0px' : '20px' }} type="checkbox"
                                            />
                                            <label className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer transition-colors duration-300 ${generateTOC ? 'bg-primary' : 'bg-slate-300'}`} htmlFor="toc"></label>
                                        </div>
                                    </div>
                                </div>

                                {/* Page Size Dropdown - Spans full width */}
                                <div className="col-span-1 md:col-span-2">
                                    <div className="flex flex-col gap-2">
                                        <label className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                            <span className="material-symbols-outlined text-slate-500">aspect_ratio</span>
                                            Page Size
                                        </label>
                                        <select
                                            value={pageSize}
                                            onChange={(e) => setPageSize(e.target.value)}
                                            disabled={isProcessing || progress === 100}
                                            className="w-full p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                        >
                                            <option value="Letter">Letter (US Default)</option>
                                            <option value="A4">A4 (International)</option>
                                            <option value="Legal">Legal</option>
                                        </select>
                                        <p className="text-xs text-slate-500">Your selection becomes the default for future documents.</p>
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
