import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';
import { isCompleted } from '../constants/status';

export default function Edit() {
    const navigate = useNavigate();
    const { job, setJob } = useDocument();
    const [content, setContent] = useState('');
    const [title, setTitle] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [lastSaved, setLastSaved] = useState('Just now');
    const [validationMessage, setValidationMessage] = useState(null);

    useEffect(() => {
        if (job) {
            setTitle(job.originalFileName?.split('.')[0] || 'Untitled Manuscript');
            // If the job has processed text, use it, otherwise use a default
            setContent(job.processedText || "Recent Advancements in Generative Adversarial Networks for Image Synthesis\n\nAbstract—This paper presents a comprehensive review of Generative Adversarial Network (GAN) architectures. We focus on the evolution from the Deep Convolutional GAN (DCGAN) to more advanced models like StyleGAN3. Our analysis shows that training stability and convergence speed remain primary challenges.");
        }
    }, [job]);

    if (!job) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-light dark:bg-background-dark">
                <p className="text-slate-500 mb-4">No document loaded for editing.</p>
                <button onClick={() => navigate('/upload')} className="text-primary font-bold hover:underline">Return to Upload</button>
            </div>
        );
    }

    const handleSave = useCallback(async () => {
        if (isSaving) return;
        setIsSaving(true);
        try {
            const { submitEdit } = await import('../services/api');
            // Basic parsing: Treat the whole content as one 'BODY' section for now, 
            // since we don't have a structured editor yet.
            // In a real scenario, we'd enable block-based editing.
            const structuredData = {
                sections: {
                    "BODY": content.split('\n').filter(line => line.trim() !== '')
                }
            };

            await submitEdit(job.id, structuredData);

            setLastSaved(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

            // Redirect to processing/upload page to show progress of re-formatting
            // We reuse the upload page state logic but we need to set the job back to 'processing'
            const updatedJob = { ...job, status: 'processing', progress: 0 };
            setJob(updatedJob);
            sessionStorage.setItem('scholarform_currentJob', JSON.stringify(updatedJob));
            navigate('/upload'); // Reuse polling logic

        } catch (error) {
            console.error("Save failed:", error);
            alert("Failed to save edit.");
        } finally {
            setIsSaving(false);
        }
    }, [content, isSaving, job, navigate, setJob]);

    const handleCancel = useCallback(() => {
        navigate('/history');
    }, [navigate]);

    const handleRevalidate = () => {
        // Simple local validation check
        const hasAbstract = content.toLowerCase().includes('abstract');
        if (!hasAbstract) {
            setValidationMessage({ type: 'warning', text: "Missing 'Abstract' section" });
        } else {
            setValidationMessage({ type: 'success', text: 'Basic structure looks good' });
        }
        // Clear message after 5 seconds
        setTimeout(() => setValidationMessage(null), 5000);
    };

    useEffect(() => {
        const handler = (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                handleSave();
            }
            if (e.key === 'Escape') {
                e.preventDefault();
                handleCancel();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [handleCancel, handleSave]);

    return (
        <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen flex flex-col font-display">
            <Navbar variant="app" />

            {/* Sub-Header / Breadcrumbs & Quick Actions */}
            <div className="flex items-center justify-between px-6 py-2 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 animate-in slide-in-from-top duration-300">
                <div className="flex items-center gap-2 overflow-hidden">
                    <button onClick={() => navigate('/history')} className="text-slate-500 dark:text-slate-400 text-sm font-medium hover:text-primary whitespace-nowrap">My Manuscripts</button>
                    <span className="text-slate-400">/</span>
                    <span className="text-slate-900 dark:text-white text-sm font-semibold truncate">{title}</span>
                    <span className={`ml-2 px-2 py-0.5 ${isSaving ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'} dark:bg-green-900/30 dark:text-green-400 text-[10px] font-bold uppercase rounded`}>
                        {isSaving ? 'Saving...' : 'Saved'}
                    </span>
                </div>
                <div className="flex items-center gap-3">
                    <button onClick={handleSave} className="flex items-center gap-1.5 px-3 py-1.5 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
                        <span className="material-symbols-outlined text-[18px]">save</span>
                        <span className="text-sm font-medium">Save</span>
                    </button>
                    <button onClick={handleRevalidate} className="flex items-center gap-1.5 px-3 py-1.5 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
                        <span className="material-symbols-outlined text-[18px]">refresh</span>
                        <span className="text-sm font-medium">Local Validate</span>
                    </button>
                    <button
                        onClick={() => navigate('/download')}
                        disabled={!isCompleted(job?.status)}
                        className="flex items-center gap-1.5 px-4 py-1.5 bg-primary text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-slate-400"
                    >
                        <span className="material-symbols-outlined text-[18px]">description</span>
                        <span className="text-sm font-bold">Export</span>
                    </button>
                </div>
            </div>

            {/* Main Layout */}
            <div className="flex flex-1 overflow-hidden">
                {/* Editor View */}
                <main className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark p-8 flex justify-center">
                    <div className="w-full max-w-[850px]">
                        {/* Validation Message Banner */}
                        {validationMessage && (
                            <div className={`mb-6 p-4 rounded-xl border animate-in fade-in slide-in-from-top duration-300 ${validationMessage.type === 'success'
                                ? 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-900/30'
                                : 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-900/30'
                                }`}>
                                <div className="flex items-center gap-2">
                                    <span className={`material-symbols-outlined text-sm ${validationMessage.type === 'success' ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400'
                                        }`}>
                                        {validationMessage.type === 'success' ? 'check_circle' : 'warning'}
                                    </span>
                                    <p className={`text-sm font-medium ${validationMessage.type === 'success' ? 'text-green-900 dark:text-green-300' : 'text-amber-900 dark:text-amber-300'
                                        }`}>
                                        {validationMessage.text}
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Manuscript Paper Area */}
                        <article className="manuscript-paper bg-white dark:bg-slate-900 min-h-[1100px] p-16 rounded-sm border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden">
                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8 focus:outline-none" contentEditable spellCheck={false}>
                                {title.replace(/_/g, ' ')}
                            </h1>
                            <textarea
                                className="w-full min-h-[800px] bg-transparent resize-none border-none focus:ring-0 p-0 text-lg leading-relaxed text-slate-700 dark:text-slate-300 font-serif"
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="Start typing your manuscript..."
                                spellCheck={false}
                            />
                        </article>
                    </div>
                </main>

                {/* Right Sidebar: Validation Feedback */}
                <aside className="w-80 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
                    <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                        <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span className="material-symbols-outlined text-primary">analytics</span>
                            Live Report
                        </h3>
                        <span className="text-xs font-semibold bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-600 dark:text-slate-400">
                            {(job.result?.errors?.length || 0) + (job.result?.warnings?.length || 0)} Issues
                        </span>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {job.result?.errors?.map((err, i) => (
                            <div key={i} className="p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-xl">
                                <div className="flex gap-2">
                                    <span className="material-symbols-outlined text-red-500 text-sm">error</span>
                                    <h4 className="text-sm font-bold text-red-900 dark:text-red-400">{err.issue || "Formatting Error"}</h4>
                                </div>
                                <p className="text-xs text-red-700 dark:text-red-300 mt-1">{err.message || err}</p>
                            </div>
                        ))}
                        {job.result?.warnings?.map((warn, i) => (
                            <div key={i} className="p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-900/30 rounded-xl">
                                <div className="flex gap-2">
                                    <span className="material-symbols-outlined text-amber-500 text-sm">warning</span>
                                    <h4 className="text-sm font-bold text-amber-900 dark:text-amber-400">Suggestion</h4>
                                </div>
                                <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">{warn.message || warn}</p>
                            </div>
                        ))}
                    </div>
                </aside>
            </div>

            {/* Bottom Status Bar */}
            <footer className="h-8 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 text-[10px] font-medium text-slate-500 dark:text-slate-400">
                <div className="flex items-center gap-4">
                    <span>Words: {content.split(/\s+/).filter(Boolean).length}</span>
                    <span>Status: {isSaving ? 'Syncing...' : 'Up to date'}</span>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[12px]">schedule</span>
                        <span>Last saved: {lastSaved}</span>
                    </div>
                    <span>ID: {job.id}</span>
                </div>
            </footer>
        </div>
    );
}

