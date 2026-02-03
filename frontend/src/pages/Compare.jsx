import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDocument } from '../context/DocumentContext';
import Navbar from '../components/Navbar';

export default function Compare() {
    const navigate = useNavigate();
    const { job } = useDocument();
    const [viewMode, setViewMode] = useState('text');
    const [scrollSync, setScrollSync] = useState(true);
    const [highlights, setHighlights] = useState(true);

    // Mock/Fallack text for comparison if not in API response
    // In a real app, this would come from job.originalText and job.processedText
    const originalLines = useMemo(() => {
        if (job?.originalText) return job.originalText.split('\n');
        return [
            "Recent Advancements in Generative Adversarial Networks for Image Synthesis",
            "",
            "Abstract",
            "This paper presents a comprehensive review of GAN architectures. We focus on the evolution from the standard DCGAN to more advanced models like StyleGAN3. Our analysis shows that training stability remains a primary challenge.",
            "",
            "1. Introduction",
            "Generative modeling has witnessed a paradigm shift with the introduction of GANs by Goodfellow et al. (2014). Since then, many variants have been proposed to address issues like mode collapse and training instability.",
            "The core idea behind GANs is a minimax game between two neural networks: a generator and a discriminator. The generator learns to map a latent space to a data distribution of interest, while the discriminator tries to distinguish between real and synthetic samples."
        ];
    }, [job]);

    const processedLines = useMemo(() => {
        if (job?.processedText) return job.processedText.split('\n');
        return [
            "RECENT ADVANCEMENTS IN GENERATIVE ADVERSARIAL NETWORKS FOR IMAGE SYNTHESIS",
            "",
            "Abstract—This paper presents a comprehensive review of Generative Adversarial Network (GAN) architectures. We focus on the evolution from the Deep Convolutional GAN (DCGAN) to more advanced models like StyleGAN3. Our analysis shows that training stability and convergence speed remain primary challenges.",
            "",
            "I. INTRODUCTION",
            "Generative modeling has witnessed a paradigm shift with the introduction of GANs by Goodfellow et al. [1]. Since then, many variants have been proposed to address issues like unstable gradients (mode collapse) and training instability.",
            "The core idea behind GANs is a minimax game between two neural networks: a generator and a discriminator. The generator G learns to map a latent space z to a data distribution p_data, while the discriminator D tries to distinguish between real and synthetic samples."
        ];
    }, [job]);

    if (!job) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-light dark:bg-background-dark">
                <p className="text-slate-500 mb-4">No active document to compare.</p>
                <button onClick={() => navigate('/upload')} className="text-primary font-bold hover:underline">Return to Upload</button>
            </div>
        );
    }

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-[#0d131b] dark:text-slate-50 min-h-screen flex flex-col">
            <Navbar variant="app" />

            <main className="flex-1 flex flex-col max-w-[1600px] mx-auto w-full px-4 lg:px-10 py-6 animate-in fade-in duration-500">
                {/* Section Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between mb-2">
                    <div>
                        <nav className="flex text-xs text-slate-500 mb-1 gap-2 items-center">
                            <Link className="hover:underline" to="/history">Documents</Link>
                            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                            <span className="font-medium">{job.originalFileName}</span>
                        </nav>
                        <h1 className="text-[#0d131b] dark:text-white text-2xl font-bold leading-tight tracking-[-0.015em]">Document Comparison</h1>
                    </div>
                    <div className="flex items-center gap-2 mt-4 md:mt-0">
                        <span className="text-xs font-medium text-slate-500 px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded uppercase">{job.template} Template Applied</span>
                    </div>
                </div>

                {/* Toolbar & Control Bar */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm mb-6 flex flex-col sm:flex-row items-center justify-between p-2">
                    <div className="flex items-center gap-1 w-full sm:w-auto">
                        <div className="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-lg mr-4">
                            <button
                                onClick={() => setViewMode('text')}
                                className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-bold transition-all ${viewMode === 'text' ? 'bg-white dark:bg-slate-700 shadow-sm text-primary' : 'text-slate-500 dark:text-slate-400 hover:text-primary'}`}
                            >
                                <span className="material-symbols-outlined text-[20px]">description</span>
                                Text View
                            </button>
                            <button
                                onClick={() => setViewMode('structured')}
                                className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${viewMode === 'structured' ? 'bg-white dark:bg-slate-700 shadow-sm text-primary' : 'text-slate-500 dark:text-slate-400 hover:text-primary'}`}
                            >
                                <span className="material-symbols-outlined text-[20px]">account_tree</span>
                                Structured
                            </button>
                        </div>
                        <div className="flex h-10 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 p-1">
                            <label onClick={() => setScrollSync(!scrollSync)} className={`cursor-pointer flex h-full items-center justify-center rounded-md px-3 text-xs transition-all ${scrollSync ? 'bg-white dark:bg-slate-700 shadow-sm text-primary font-bold' : 'text-slate-500 dark:text-slate-400 font-medium hover:text-primary'}`}>
                                <span className="material-symbols-outlined text-[18px] mr-1">sync_alt</span>
                                <span className="truncate">Sync: {scrollSync ? 'ON' : 'OFF'}</span>
                            </label>
                            <label onClick={() => setHighlights(!highlights)} className={`cursor-pointer flex h-full items-center justify-center rounded-md px-3 text-xs transition-all ${highlights ? 'bg-white dark:bg-slate-700 shadow-sm text-primary font-bold' : 'text-slate-500 dark:text-slate-400 font-medium hover:text-primary'}`}>
                                <span className="material-symbols-outlined text-[18px] mr-1">auto_fix_high</span>
                                <span className="truncate">Highlights: {highlights ? 'ON' : 'OFF'}</span>
                            </label>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 mt-2 sm:mt-0">
                        <div className="flex gap-1 border-r border-slate-200 dark:border-slate-700 pr-4 mr-2">
                            <button onClick={() => navigate('/download')} className="p-2 text-slate-500 hover:text-primary transition-colors" title="Download">
                                <span className="material-symbols-outlined">file_download</span>
                            </button>
                        </div>
                        <Link to="/edit" className="flex items-center justify-center rounded-lg h-10 bg-primary text-white gap-2 px-6 text-sm font-bold shadow-md hover:bg-blue-600 transition-all">
                            <span className="material-symbols-outlined">edit_note</span>
                            <span className="truncate">Edit Version</span>
                        </Link>
                    </div>
                </div>

                {/* Side-by-Side Split View */}
                <div className="flex-1 flex gap-4 min-h-[600px]">
                    {/* Left Panel: Original */}
                    <div className="flex-1 flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
                        <div className="px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50 flex justify-between items-center">
                            <h3 className="font-bold text-sm text-slate-700 dark:text-slate-200 uppercase tracking-wider flex items-center gap-2">
                                <span className="material-symbols-outlined text-[18px] text-slate-400">history</span>
                                Original
                            </h3>
                            <span className="text-[10px] text-slate-400">Source: {job.originalFileName}</span>
                        </div>
                        <div className={`flex-1 p-8 overflow-y-auto custom-scrollbar leading-relaxed text-slate-800 dark:text-slate-300 font-serif text-[15px] ${scrollSync ? 'scroll-sync-left' : ''}`}>
                            <div className="max-w-2xl mx-auto space-y-4">
                                {originalLines.map((line, i) => (
                                    <p key={i} className={line.trim() === "" ? "h-4" : ""}>{line}</p>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col items-center justify-center px-0 text-slate-300 dark:text-slate-700">
                        <span className="material-symbols-outlined">link</span>
                    </div>

                    {/* Right Panel: Processed */}
                    <div className="flex-1 flex flex-col bg-white dark:bg-slate-900 border-2 border-primary rounded-xl overflow-hidden shadow-lg">
                        <div className="px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-primary/5 flex justify-between items-center">
                            <h3 className="font-bold text-sm text-primary uppercase tracking-wider flex items-center gap-2">
                                <span className="material-symbols-outlined text-[18px]">verified</span>
                                Processed ({job.template})
                            </h3>
                            <div className="flex gap-2">
                                <span className="text-[10px] font-bold text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded">VALIDATED</span>
                            </div>
                        </div>
                        <div className={`flex-1 p-8 overflow-y-auto custom-scrollbar bg-white dark:bg-slate-900 ${scrollSync ? 'scroll-sync-right' : ''}`}>
                            <div className="max-w-2xl mx-auto space-y-4">
                                {processedLines.map((line, i) => {
                                    const isModified = i < originalLines.length && line !== originalLines[i] && line.trim() !== "";
                                    return (
                                        <p key={i} className={`${line.trim() === "" ? "h-4" : ""} ${highlights && isModified ? 'bg-diff-mod/30 border-l-2 border-amber-400 pl-2' : ''}`}>
                                            {line}
                                        </p>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Diff Summary Footer */}
                <div className="mt-4 flex items-center justify-between px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-diff-add border border-green-300"></span>
                            <span className="font-medium">Insertions</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-diff-mod border border-yellow-300"></span>
                            <span className="font-medium">Formatting Changes</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 text-slate-500">
                        <span className="flex items-center gap-1">
                            <span className="material-symbols-outlined text-[16px]">info</span>
                            Real-time synchronization active
                        </span>
                        <span className="border-l border-slate-300 dark:border-slate-600 pl-4">Job ID: {job.id}</span>
                    </div>
                </div>
            </main>
        </div>
    );
}

