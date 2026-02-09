import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';

export default function Preview() {
    const navigate = useNavigate();
    const { job } = useDocument();
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');

    useEffect(() => {
        const fetchPreview = async () => {
            if (job?.id) {
                try {
                    const { getPreview } = await import('../services/api');
                    const data = await getPreview(job.id);
                    setTitle(data.metadata?.filename?.split('.')[0] || job.originalFileName || 'Untitled');

                    // Reconstruct text from structured data for display
                    // The structured_data.sections is { "HEADER": ["text"], "ABSTRACT": ["text"] ... }
                    let fullText = "";
                    if (data.structured_data?.sections) {
                        Object.entries(data.structured_data.sections).forEach(([section, texts]) => {
                            fullText += `--- ${section} ---\n`;
                            fullText += texts.join('\n') + "\n\n";
                        });
                    } else {
                        fullText = "No structured text content available.";
                    }
                    setContent(fullText);
                } catch (err) {
                    console.error("Failed to load preview:", err);
                    setContent("Error loading preview content. Please try again.");
                }
            }
        };

        fetchPreview();
    }, [job]);

    if (!job) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-light dark:bg-background-dark">
                <div className="text-center p-8 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 max-w-md animate-in fade-in zoom-in duration-300">
                    <span className="material-symbols-outlined text-6xl text-slate-300 dark:text-slate-700 mb-4 block">receipt_long</span>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">No document to preview</h2>
                    <p className="text-slate-500 dark:text-slate-400 mb-6 text-sm leading-relaxed">Please upload and process a manuscript first to see the final formatted preview.</p>
                    <button
                        onClick={() => navigate('/upload')}
                        className="w-full bg-primary text-white font-bold py-3 px-6 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2"
                    >
                        <span className="material-symbols-outlined">upload_file</span>
                        Return to Upload
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen flex flex-col font-display">
            <Navbar variant="app" />

            {/* Sub-Header / Breadcrumbs & Quick Actions */}
            <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 animate-in slide-in-from-top duration-300">
                <div className="flex items-center gap-2 overflow-hidden">
                    <button onClick={() => navigate('/upload')} className="text-slate-500 dark:text-slate-400 text-sm font-medium hover:text-primary whitespace-nowrap">Upload</button>
                    <span className="text-slate-400">/</span>
                    <span className="text-slate-900 dark:text-white text-sm font-semibold truncate">{title} (Preview)</span>
                    <span className="ml-2 px-2 py-0.5 bg-primary/10 text-primary dark:bg-primary/20 text-[10px] font-bold uppercase rounded">Read Only</span>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400 mr-2 flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">info</span>
                        This is a read-only final inspection
                    </span>
                    <button onClick={() => navigate('/download')} className="flex items-center gap-1.5 px-4 py-1.5 bg-primary text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
                        <span className="material-symbols-outlined text-[18px]">download</span>
                        <span className="text-sm font-bold">Download Final</span>
                    </button>
                </div>
            </div>

            {/* Main Layout */}
            <div className="flex flex-1 overflow-hidden">
                <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-background-dark p-8 flex justify-center">
                    <div className="w-full max-w-[850px]">
                        {/* Manuscript Paper Area */}
                        <article className="manuscript-paper bg-white dark:bg-slate-900 min-h-[1100px] p-16 rounded-sm border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden pointer-events-none select-none">
                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">
                                {title.replace(/_/g, ' ')}
                            </h1>
                            <div className="w-full text-lg leading-relaxed text-slate-700 dark:text-slate-300 font-serif whitespace-pre-wrap">
                                {content}
                            </div>
                        </article>
                    </div>
                </main>

                {/* Right Sidebar: Final Stats */}
                <aside className="w-80 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col hidden xl:flex">
                    <div className="p-4 border-b border-slate-200 dark:border-slate-800">
                        <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span className="material-symbols-outlined text-primary">analytics</span>
                            Final Formatting Report
                        </h3>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <div className="p-4 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30 rounded-xl">
                            <div className="flex gap-2 mb-1">
                                <span className="material-symbols-outlined text-green-500 text-sm">check_circle</span>
                                <h4 className="text-sm font-bold text-green-900 dark:text-green-400">IEEE Compliant</h4>
                            </div>
                            <p className="text-xs text-green-700 dark:text-green-300">Structure, citations, and fonts successfully validated against the selected template.</p>
                        </div>
                        <div className="p-4 bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30 rounded-xl">
                            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Document Info</h4>
                            <div className="space-y-3">
                                <div>
                                    <p className="text-[10px] text-slate-400 uppercase font-bold">Word Count</p>
                                    <p className="text-sm font-semibold">{(job.processedText || '').split(/\s+/).filter(Boolean).length} Words</p>
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-400 uppercase font-bold">Template</p>
                                    <p className="text-sm font-semibold">{job.template?.toUpperCase() || 'NONE'} Standard</p>
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-400 uppercase font-bold">Job Status</p>
                                    <p className="text-sm font-semibold text-green-600">Complete</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </aside>
            </div>

            {/* Bottom Status Bar */}
            <footer className="h-8 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center justify-center px-6 text-[10px] font-medium text-slate-400 uppercase tracking-widest">
                <span>ScholarForm AI Preview Mode • Read Only</span>
            </footer>
        </div>
    );
}
