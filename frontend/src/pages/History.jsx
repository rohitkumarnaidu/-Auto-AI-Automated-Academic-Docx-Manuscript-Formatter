import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function History() {
    const navigate = useNavigate();
    const { history, setJob } = useDocument();

    const handleRestore = (item) => {
        // Since we stored a sanitized version in history, we set it as the current active job
        setJob(item);
        navigate('/results');
    };

    const stats = {
        total: history.length,
        valid: history.filter(h => h.status === 'completed' && (!h.result?.errors || h.result.errors.length === 0)).length,
        warnings: history.filter(h => h.result?.warnings?.length > 0).length,
        errors: history.filter(h => h.status === 'failed' || (h.result?.errors?.length > 0)).length
    };

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
            <Navbar variant="app" />

            {/* Page Content */}
            <main className="flex flex-1 justify-center py-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="layout-content-container flex flex-col w-full max-w-[1280px] px-4 md:px-10">
                    {/* PageHeading */}
                    <div className="flex flex-wrap justify-between items-end gap-4 mb-8">
                        <div className="flex flex-col gap-2">
                            <h1 className="text-slate-900 dark:text-white text-3xl font-black tracking-tight">Manuscript Processing History</h1>
                            <p className="text-slate-500 dark:text-slate-400 text-base max-w-2xl">Track and manage your document versions, template compliance, and validation results.</p>
                        </div>
                        <div className="flex gap-3">
                            <Link to="/upload" className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors shadow-lg shadow-primary/20">
                                <span className="material-symbols-outlined">file_upload</span>
                                <span>Process New Manuscript</span>
                            </Link>
                        </div>
                    </div>

                    {/* Stats Summary */}
                    <div className="flex flex-col gap-6">
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
                                <p className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Total Manuscripts</p>
                                <p className="text-2xl font-black text-slate-900 dark:text-white">{stats.total}</p>
                            </div>
                            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
                                <p className="text-green-600 dark:text-green-400 text-xs font-bold uppercase tracking-wider mb-1">Perfect Compliance</p>
                                <p className="text-2xl font-black text-slate-900 dark:text-white">{stats.valid}</p>
                            </div>
                            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
                                <p className="text-amber-600 dark:text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">With Warnings</p>
                                <p className="text-2xl font-black text-slate-900 dark:text-white">{stats.warnings}</p>
                            </div>
                            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
                                <p className="text-red-600 dark:text-red-400 text-xs font-bold uppercase tracking-wider mb-1">Requires Attention</p>
                                <p className="text-2xl font-black text-slate-900 dark:text-white">{stats.errors}</p>
                            </div>
                        </div>

                        {/* History Table */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                            <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex justify-between items-center bg-slate-50/50 dark:bg-slate-900/50">
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">All Versions</h3>
                                <span className="text-xs text-slate-500">{history.length} records found</span>
                            </div>

                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="bg-slate-50/50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 uppercase text-[11px] font-bold tracking-widest">
                                            <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">Date / Time</th>
                                            <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">Manuscript Name</th>
                                            <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">Template</th>
                                            <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">Status</th>
                                            <th className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 text-right">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50">
                                        {history.length === 0 ? (
                                            <tr>
                                                <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                                                    No processing history found. Start by uploading a manuscript.
                                                </td>
                                            </tr>
                                        ) : (
                                            history.map((item) => (
                                                <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors group">
                                                    <td className="px-6 py-5 whitespace-nowrap">
                                                        <span className="text-slate-600 dark:text-slate-400 text-sm">
                                                            {new Date(item.timestamp).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-5">
                                                        <div className="flex items-center gap-2">
                                                            <span className="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">description</span>
                                                            <span className="text-slate-900 dark:text-white font-bold text-sm truncate max-w-[200px]">{item.originalFileName}</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-5">
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 uppercase">
                                                            {item.template}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-5">
                                                        {item.status === 'completed' ? (
                                                            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full w-fit ${item.result?.errors?.length > 0 ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'}`}>
                                                                <span className="material-symbols-outlined !text-sm">{item.result?.errors?.length > 0 ? 'error' : 'check_circle'}</span>
                                                                <span className="text-xs font-bold">{item.result?.errors?.length > 0 ? 'Issue Detect' : 'Passed'}</span>
                                                            </div>
                                                        ) : (
                                                            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 w-fit">
                                                                <span className="material-symbols-outlined !text-sm">cancel</span>
                                                                <span className="text-xs font-bold">Failed</span>
                                                            </div>
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-5">
                                                        <div className="flex justify-end items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <button onClick={() => handleRestore(item)} className="bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-primary hover:text-white transition-all">
                                                                Open Corrected
                                                            </button>
                                                            <button
                                                                onClick={() => {
                                                                    setJob(item);
                                                                    navigate('/download');
                                                                }}
                                                                className="p-1.5 text-slate-400 hover:text-primary transition-colors"
                                                                title="Download"
                                                            >
                                                                <span className="material-symbols-outlined">download</span>
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <Footer variant="app" />
        </div>
    );
}

