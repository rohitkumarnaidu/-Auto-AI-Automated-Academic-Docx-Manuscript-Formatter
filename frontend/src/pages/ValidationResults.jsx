import { useState } from 'react';
import Navbar from '../components/Navbar';
import ValidationCard from '../components/ValidationCard';
import { useNavigate } from 'react-router-dom';
import { useDocument } from '../context/DocumentContext';

export default function ValidationResults() {
    const navigate = useNavigate();
    const { job } = useDocument();
    const [activeTab, setActiveTab] = useState('all');

    if (!job || !job.result) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center">
                <p className="text-slate-500 mb-4">No validation results found.</p>
                <button onClick={() => navigate('/upload')} className="text-primary font-bold hover:underline">Return to Upload</button>
            </div>
        );
    }

    const { errors = [], warnings = [], advisories = [] } = job.result;

    const filteredIssues = () => {
        if (activeTab === 'errors') return errors;
        if (activeTab === 'warnings') return warnings;
        if (activeTab === 'advisories') return advisories;
        return [...errors.map(e => ({ ...e, type: 'error' })),
        ...warnings.map(w => ({ ...w, type: 'warning' })),
        ...advisories.map(a => ({ ...a, type: 'advisory' }))];
    };

    return (
        <>
            <Navbar variant="app" />

            <main className="max-w-5xl mx-auto px-4 py-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Breadcrumbs */}
                <nav className="flex items-center gap-2 text-sm font-medium text-slate-500 dark:text-slate-400">
                    <a href="#" className="hover:text-primary transition-colors">My Files</a>
                    <span className="material-symbols-outlined text-xs">chevron_right</span>
                    <span className="text-slate-900 dark:text-slate-100">Validation Results</span>
                </nav>

                {/* Page Heading */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div className="space-y-2">
                        <h1 className="text-4xl font-black tracking-tight text-slate-900 dark:text-white">Validation Results Analysis</h1>
                        <p className="text-slate-500 dark:text-slate-400 text-lg">Diagnostic report for <span className="font-mono text-slate-700 dark:text-slate-200">{job.originalFileName}</span></p>
                    </div>
                    <div className="flex gap-3">
                        <button onClick={() => navigate('/upload')} className="flex items-center justify-center rounded-lg h-11 px-6 bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm font-bold hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors">
                            <span className="material-symbols-outlined mr-2 text-lg">upload_file</span>
                            Re-upload
                        </button>
                        <button onClick={() => navigate('/download')} className="flex items-center justify-center rounded-lg h-11 px-6 bg-primary text-white text-sm font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all">
                            <span className="material-symbols-outlined mr-2 text-lg">download</span>
                            Verify & Download
                        </button>
                    </div>
                </div>

                {/* Metadata Summary Card */}
                <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col lg:flex-row gap-6 items-start lg:items-center">
                    <div className="flex-1 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="space-y-1">
                                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Filename</p>
                                <p className="text-slate-900 dark:text-slate-100 font-semibold truncate">{job.originalFileName}</p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Formatting Template</p>
                                <p className="text-slate-900 dark:text-slate-100 font-semibold uppercase">{job.template}</p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">AI Enhancement</p>
                                <p className="text-slate-900 dark:text-slate-100 font-semibold">{job.flags?.ai_used ? 'Enabled' : 'Disabled'}</p>
                            </div>
                        </div>
                    </div>
                    <div className="w-full lg:w-48 h-28 bg-slate-100 dark:bg-slate-800 rounded-lg flex flex-col items-center justify-center text-slate-400 border border-dashed border-slate-300 dark:border-slate-700 overflow-hidden relative group">
                        <span className="material-symbols-outlined text-3xl group-hover:scale-110 transition-transform">description</span>
                        <span className="text-[10px] mt-2 font-mono">DOCUMENT PREVIEW</span>
                        <div className="absolute inset-0 bg-primary/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <button onClick={() => navigate('/compare')} className="text-[10px] font-bold bg-white text-primary px-3 py-1 rounded shadow-sm">VIEW DIFF</button>
                        </div>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="bg-red-50 dark:bg-red-950/20 border border-red-100 dark:border-red-900/30 rounded-xl p-6 flex flex-col">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-red-700 dark:text-red-400 font-bold text-sm">Errors</span>
                            <span className="material-symbols-outlined text-red-600 dark:text-red-400">error</span>
                        </div>
                        <p className="text-4xl font-black text-red-700 dark:text-red-400">{errors.length}</p>
                        <p className="text-xs text-red-600/70 dark:text-red-400/50 mt-1 font-medium italic">{errors.length > 0 ? 'Require immediate attention' : 'No critical issues'}</p>
                    </div>
                    <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/30 rounded-xl p-6 flex flex-col">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-amber-700 dark:text-amber-400 font-bold text-sm">Warnings</span>
                            <span className="material-symbols-outlined text-amber-600 dark:text-amber-400">warning</span>
                        </div>
                        <p className="text-4xl font-black text-amber-700 dark:text-amber-400">{warnings.length}</p>
                        <p className="text-xs text-amber-600/70 dark:text-amber-400/50 mt-1 font-medium italic">Formatting improvements</p>
                    </div>
                    <div className="bg-primary/5 dark:bg-primary/10 border border-primary/10 dark:border-primary/20 rounded-xl p-6 flex flex-col">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-primary font-bold text-sm">AI Advisory</span>
                            <span className="material-symbols-outlined text-primary">auto_awesome</span>
                        </div>
                        <p className="text-4xl font-black text-primary">{advisories.length}</p>
                        <p className="text-xs text-primary/70 mt-1 font-medium italic">Insights and optimizations</p>
                    </div>
                </div>

                {/* Feedback Section */}
                <div className="space-y-6">
                    <div className="flex items-center border-b border-slate-200 dark:border-slate-800 overflow-x-auto">
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`px-6 py-3 border-b-2 text-sm font-bold transition-all whitespace-nowrap ${activeTab === 'all' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            All Feedback
                        </button>
                        <button
                            onClick={() => setActiveTab('errors')}
                            className={`px-6 py-3 border-b-2 text-sm font-bold transition-all whitespace-nowrap ${activeTab === 'errors' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            Errors ({errors.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('warnings')}
                            className={`px-6 py-3 border-b-2 text-sm font-bold transition-all whitespace-nowrap ${activeTab === 'warnings' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            Warnings ({warnings.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('advisories')}
                            className={`px-6 py-3 border-b-2 text-sm font-bold transition-all whitespace-nowrap ${activeTab === 'advisories' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            AI Advisory ({advisories.length})
                        </button>
                    </div>

                    <div className="space-y-4 min-h-[200px]">
                        {filteredIssues().length > 0 ? filteredIssues().map((issue, idx) => (
                            <ValidationCard
                                key={idx}
                                type={issue.type || (activeTab === 'errors' ? 'error' : activeTab === 'warnings' ? 'warning' : 'info')}
                                title={issue.title || issue.issue || "Formatting Issue"}
                                description={issue.description || issue.message || issue}
                                badge={issue.severity || (activeTab === 'errors' ? 'Critical' : 'Notice')}
                            />
                        )) : (
                            <div className="py-12 text-center text-slate-400">
                                <span className="material-symbols-outlined text-4xl mb-2 opacity-20">check_circle</span>
                                <p>No issues found in this category.</p>
                            </div>
                        )}
                    </div>

                    {/* Action Footer */}
                    <div className="flex flex-col sm:flex-row gap-4 pt-8">
                        <button onClick={() => navigate('/compare')} className="flex-1 flex items-center justify-center gap-2 py-4 bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-xl font-bold text-slate-700 dark:text-slate-200 hover:border-primary transition-all shadow-sm">
                            <span className="material-symbols-outlined">compare_arrows</span>
                            Compare with Original
                        </button>
                        <button onClick={() => navigate('/edit')} className="flex-1 flex items-center justify-center gap-2 py-4 bg-primary text-white rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-primary/20">
                            <span className="material-symbols-outlined">edit_note</span>
                            Edit Processed Version
                        </button>
                    </div>
                </div>

                <footer className="max-w-5xl mx-auto px-4 py-12 text-center text-slate-400 text-xs border-t border-slate-200 dark:border-slate-800 mt-12">
                    <p>© 2023 ManuscriptFormatter AI Inc. All rights reserved.</p>
                    <p className="mt-2">Validation performed against {job.template.toUpperCase()} academic standards.</p>
                </footer>
            </main>
        </>
    );
}

