import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import FileUpload from '../components/FileUpload';
import ToggleSwitch from '../components/ToggleSwitch';
import Stepper from '../components/Stepper';
import StatusBadge from '../components/StatusBadge';
import { useNavigate } from 'react-router-dom';
import { useDocument } from '../context/DocumentContext';
import { uploadDocument } from '../services/api';

export default function Upload() {
    const navigate = useNavigate();
    const { startProcessing, finishProcessing, failProcessing, processing } = useDocument();

    const [file, setFile] = useState(null);
    const [template, setTemplate] = useState('none');
    const [enableOCR, setEnableOCR] = useState(false);
    const [enableAI, setEnableAI] = useState(false);
    const [error, setError] = useState(null);

    const handleProcess = async () => {
        if (!file) {
            setError("Please select a document first.");
            return;
        }

        setError(null);
        startProcessing();
        navigate('/processing'); // Navigate to processing immediately to show stages

        try {
            const result = await uploadDocument(file, template, { enableOCR, enableAI });
            finishProcessing(result, file, template, { enableOCR, enableAI });
            // The Processing page will handle the navigation to /results once context updates
        } catch (err) {
            console.error("Upload failed", err);
            failProcessing(err);
            setError(err.message || "An error occurred during upload.");
            navigate('/upload'); // Back to upload if failed
        }
    };

    return (
        <>
            <Navbar variant="app" />

            <main className="max-w-[1280px] mx-auto px-6 py-8">
                {/* Page Heading */}
                <div className="mb-8">
                    <h1 className="text-[#0d131b] dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">Upload Manuscript</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-lg mt-2">Transform your research into a publication-ready document in minutes.</p>
                </div>

                {/* Error Banner */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-xl flex items-center gap-3 text-red-700 dark:text-red-400">
                        <span className="material-symbols-outlined">error</span>
                        <span className="text-sm font-medium">{error}</span>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left Panel: Configuration */}
                    <div className="lg:col-span-7 flex flex-col gap-6">
                        {/* Section 1: Upload Area */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">upload_file</span>
                                1. Document Source
                            </h2>
                            <FileUpload onFileSelect={setFile} />
                        </div>

                        {/* Section 2: Formatting & AI Settings */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">tune</span>
                                2. Processing Parameters
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Journal Template Dropdown */}
                                <div className="flex flex-col gap-2">
                                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Target Journal Template</label>
                                    <div className="relative">
                                        <select
                                            value={template}
                                            onChange={(e) => setTemplate(e.target.value)}
                                            className="w-full h-12 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none appearance-none"
                                        >
                                            <option value="none">None (General Formatting)</option>
                                            <option value="ieee">IEEE Conference/Journal</option>
                                            <option value="springer">Springer Nature (Standard)</option>
                                            <option value="elsevier">Elsevier Article Template</option>
                                            <option value="nature">Nature Communications</option>
                                        </select>
                                        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-slate-400">
                                            <span className="material-symbols-outlined">expand_more</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Toggle Controls */}
                                <div className="flex flex-col gap-4">
                                    {/* OCR Toggle */}
                                    <ToggleSwitch
                                        id="ocr"
                                        label="Enable OCR"
                                        sublabel="Extract text from images/scans"
                                        checked={enableOCR}
                                        onChange={(e) => setEnableOCR(e.target.checked)}
                                    />
                                    {/* AI Analysis Toggle */}
                                    <ToggleSwitch
                                        id="nlp"
                                        label="AI/NLP Analysis"
                                        sublabel="Detect citation errors & gaps"
                                        checked={enableAI}
                                        onChange={(e) => setEnableAI(e.target.checked)}
                                    />
                                </div>
                            </div>

                            <button
                                onClick={handleProcess}
                                disabled={processing || !file}
                                className={`w-full mt-8 bg-primary hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/25 flex items-center justify-center gap-3 transition-all transform hover:-translate-y-0.5 ${processing || !file ? 'opacity-50 cursor-not-allowed grayscale' : ''}`}
                            >
                                <span className="material-symbols-outlined">{processing ? 'sync' : 'rocket_launch'}</span>
                                {processing ? 'Processing...' : 'Process Document'}
                            </button>
                        </div>
                    </div>

                    {/* Right Panel: Stepper/Status */}
                    <div className="lg:col-span-5">
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm sticky top-24">
                            <div className="p-6 border-b border-slate-100 dark:border-slate-800">
                                <div className="flex items-center justify-between mb-4">
                                    <h2 className="text-lg font-bold text-slate-900 dark:text-white">Processing Status</h2>
                                    <StatusBadge status={processing ? 'processing' : 'idle'} />
                                </div>
                                {/* Overall Progress Bar */}
                                <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                                    <div
                                        className="bg-primary h-full transition-all duration-500"
                                        style={{ width: processing ? '45%' : '0%' }}
                                    ></div>
                                </div>
                                <div className="flex justify-between mt-2">
                                    <span className="text-xs text-slate-500">{processing ? 'Uploading and analyzing...' : 'Awaiting document...'}</span>
                                    <span className="text-xs font-bold text-primary">{processing ? '45%' : '0%'}</span>
                                </div>
                            </div>

                            <Stepper activeStep={processing ? 1 : 0} />

                            <div className="p-6 bg-slate-50 dark:bg-slate-800/30 rounded-b-xl flex justify-center">
                                <p className="text-xs text-slate-400 flex items-center gap-1 italic">
                                    <span className="material-symbols-outlined text-[14px]">info</span>
                                    {processing ? 'Processing started...' : 'Est. time remaining: 45 seconds'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <Footer variant="app" />
        </>
    );
}

