'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import SplitEditor from '@/src/components/live-preview/SplitEditor';
import useLivePreviewSocket from '@/src/hooks/useLivePreviewSocket';
import { getAiSuggestion } from '@/src/services/api.preview.v1';
import { fetchWithAuth } from '@/src/services/api.core';

// ── 17 built-in templates ───────────────────────────────────────────────────
const BUILTIN_TEMPLATES = [
    { id: 'ieee', label: 'IEEE' },
    { id: 'apa7', label: 'APA 7th Edition' },
    { id: 'mla9', label: 'MLA 9th Edition' },
    { id: 'chicago-author-date', label: 'Chicago Author-Date' },
    { id: 'chicago-notes', label: 'Chicago Notes & Bibliography' },
    { id: 'harvard', label: 'Harvard' },
    { id: 'vancouver', label: 'Vancouver' },
    { id: 'ama', label: 'AMA' },
    { id: 'acs', label: 'ACS' },
    { id: 'acm', label: 'ACM' },
    { id: 'elsevier', label: 'Elsevier' },
    { id: 'springer', label: 'Springer' },
    { id: 'nature', label: 'Nature' },
    { id: 'science', label: 'Science' },
    { id: 'plos', label: 'PLOS ONE' },
    { id: 'oxford', label: 'Oxford' },
    { id: 'turabian', label: 'Turabian' },
];

// Generate a UUID — same utility as api.core.js
function generateUUID() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

// ── Connection Status Dot ──────────────────────────────────────────────────
function ConnectionDot({ isConnected }) {
    return (
        <span
            title={isConnected ? 'WebSocket connected' : 'WebSocket disconnected — using HTTP fallback'}
            className={`inline-block w-2 h-2 rounded-full transition-colors duration-500 ${
                isConnected ? 'bg-emerald-400 shadow-[0_0_6px_#34d399]' : 'bg-slate-400'
            }`}
        />
    );
}

// ── AI Sidebar ─────────────────────────────────────────────────────────────
function AiSidebar({ isOpen, onToggle, sessionId, templateId, editorContentRef }) {
    const [suggestions, setSuggestions] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [streamError, setStreamError] = useState(null);
    const esRef = useRef(null);

    const handleAiSuggest = useCallback(() => {
        // Close any existing stream
        if (esRef.current) {
            esRef.current.close();
            esRef.current = null;
        }

        setSuggestions('');
        setStreamError(null);
        setIsStreaming(true);

        const content = editorContentRef.current || '';
        const es = getAiSuggestion(sessionId, content, templateId);
        esRef.current = es;

        es.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.token) setSuggestions((prev) => prev + data.token);
                if (data.done) {
                    setIsStreaming(false);
                    es.close();
                    esRef.current = null;
                }
            } catch {
                // Plain text token
                setSuggestions((prev) => prev + event.data);
            }
        };

        es.onerror = () => {
            setIsStreaming(false);
            setStreamError('AI suggestions are unavailable right now. Please try again.');
            es.close();
            esRef.current = null;
        };
    }, [sessionId, templateId, editorContentRef]);

    // Clean up EventSource on unmount
    useEffect(() => {
        return () => {
            if (esRef.current) { esRef.current.close(); }
        };
    }, []);

    return (
        <AnimatePresence initial={false}>
            {isOpen && (
                <motion.aside
                    key="ai-sidebar"
                    initial={{ width: 0, opacity: 0 }}
                    animate={{ width: 320, opacity: 1 }}
                    exit={{ width: 0, opacity: 0 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    className="flex flex-col shrink-0 overflow-hidden border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 h-full"
                >
                    <div className="w-80 flex flex-col h-full">
                        {/* Header */}
                        <div className="flex items-center justify-between gap-2 px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary text-[20px]">auto_awesome</span>
                                <h3 className="font-bold text-slate-900 dark:text-white text-sm">AI Assistant</h3>
                            </div>
                            <button
                                onClick={onToggle}
                                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                title="Collapse sidebar"
                            >
                                <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                            </button>
                        </div>

                        {/* AI Suggest Button */}
                        <div className="p-4 border-b border-slate-200 dark:border-slate-800">
                            <button
                                id="ai-suggest-btn"
                                onClick={handleAiSuggest}
                                disabled={isStreaming}
                                className="
                                    w-full flex items-center justify-center gap-2
                                    px-4 py-2.5 rounded-xl
                                    bg-gradient-to-r from-violet-600 to-indigo-600
                                    text-white text-sm font-bold
                                    hover:from-violet-700 hover:to-indigo-700
                                    active:scale-[0.98]
                                    disabled:opacity-60 disabled:cursor-not-allowed
                                    shadow-md shadow-violet-500/20
                                    transition-all duration-150
                                "
                            >
                                {isStreaming ? (
                                    <>
                                        <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Generating…
                                    </>
                                ) : (
                                    <>
                                        <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
                                        AI Suggest
                                    </>
                                )}
                            </button>
                            <p className="text-[11px] text-slate-400 dark:text-slate-600 text-center mt-2 leading-tight">
                                Suggestions are generated only when you click this button.
                            </p>
                        </div>

                        {/* Suggestions output */}
                        <div className="flex-1 overflow-y-auto p-4">
                            {streamError && (
                                <div className="p-3 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/30 mb-3">
                                    <p className="text-xs text-red-700 dark:text-red-400">{streamError}</p>
                                </div>
                            )}

                            {suggestions ? (
                                <div className="prose prose-sm dark:prose-invert max-w-none">
                                    <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Suggestions</p>
                                    <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                                        {suggestions}
                                        {isStreaming && (
                                            <span className="inline-block w-1.5 h-4 bg-primary animate-pulse ml-0.5 align-middle rounded-sm" />
                                        )}
                                    </div>
                                </div>
                            ) : (
                                !streamError && (
                                    <div className="flex flex-col items-center justify-center h-full text-center text-slate-400 dark:text-slate-600 py-8">
                                        <span className="material-symbols-outlined text-[36px] mb-2 opacity-30">lightbulb</span>
                                        <p className="text-xs font-medium">Click &ldquo;AI Suggest&rdquo; to get<br/>formatting suggestions</p>
                                    </div>
                                )
                            )}
                        </div>
                    </div>
                </motion.aside>
            )}
        </AnimatePresence>
    );
}

// ── Main Page ──────────────────────────────────────────────────────────────
export default function LiveFormatterPage() {
    usePageTitle('Live Editor');

    const router = useRouter();

    // Session ID — generated once, never changes
    const [sessionId] = useState(() => generateUUID());

    // Template
    const [templateId, setTemplateId] = useState('ieee');

    // AI sidebar
    const [aiOpen, setAiOpen] = useState(true);

    // Export state
    const [isExporting, setIsExporting] = useState(false);
    const [exportError, setExportError] = useState(null);

    // We keep a ref to the current TipTap HTML for AI requests (avoids stale closure)
    const editorContentRef = useRef('');

    // WebSocket hook
    const { html, latencyMs, warnings, isConnected, isAnalyzing, sendContent } = useLivePreviewSocket(sessionId);

    // Wrap sendContent to also update the content ref
    const handleSendContent = useCallback((content, tplId) => {
        editorContentRef.current = content;
        sendContent(content, tplId);
    }, [sendContent]);

    // ── Export ─────────────────────────────────────────────────────────────
    const handleExport = useCallback(async (format = 'docx') => {
        if (isExporting) return;
        setIsExporting(true);
        setExportError(null);

        try {
            const content = editorContentRef.current || '';

            // Convert HTML to a simple text blob to upload
            const blob = new Blob([content], { type: 'text/html; charset=utf-8' });
            const file = new File([blob], `manuscript-${sessionId.slice(0, 8)}.html`, { type: 'text/html' });

            const formData = new FormData();
            formData.append('file', file);
            formData.append('templateId', templateId);
            formData.append('outputFormat', format);
            formData.append('sessionId', sessionId);

            const result = await fetchWithAuth('/api/v1/upload', {
                method: 'POST',
                body: formData,
                // Don't set Content-Type; browser sets multipart boundary
            });

            const jobId = result?.job_id || result?.jobId || result?.id;
            if (jobId) {
                router.push(`/processing?jobId=${encodeURIComponent(jobId)}`);
            } else {
                router.push('/processing');
            }
        } catch (error) {
            console.error('Export failed:', error);
            setExportError(error?.message || 'Export failed. Please try again.');
        } finally {
            setIsExporting(false);
        }
    }, [isExporting, sessionId, templateId, router]);

    return (
        <div
            suppressHydrationWarning
            className="flex flex-col bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display animate-in fade-in duration-300"
            style={{ height: 'calc(100vh - 72px)' }}
        >
            {/* ── Top Toolbar ─────────────────────────────────────────── */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 px-3 sm:px-5 py-2 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0 z-10">
                {/* Template selector */}
                <div className="flex items-center gap-2 min-w-0">
                    <span className="material-symbols-outlined text-[18px] text-slate-400 shrink-0">description</span>
                    <label htmlFor="template-select" className="text-xs font-semibold text-slate-600 dark:text-slate-400 whitespace-nowrap shrink-0">
                        Template
                    </label>
                    <select
                        id="template-select"
                        value={templateId}
                        onChange={(e) => {
                            setTemplateId(e.target.value);
                            // Re-send current content with new template immediately
                            sendContent(editorContentRef.current, e.target.value);
                        }}
                        className="
                            rounded-lg border border-slate-200 dark:border-slate-700
                            bg-slate-50 dark:bg-slate-800
                            text-slate-900 dark:text-white
                            text-xs font-medium
                            px-2.5 py-1.5 pr-7
                            focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
                            transition-colors cursor-pointer
                            max-w-[180px] sm:max-w-none
                        "
                    >
                        {BUILTIN_TEMPLATES.map((t) => (
                            <option key={t.id} value={t.id}>{t.label}</option>
                        ))}
                    </select>
                </div>

                {/* Connection indicator + latency */}
                <div className="flex items-center gap-1.5 ml-1">
                    <ConnectionDot isConnected={isConnected} />
                    {latencyMs !== null && (
                        <span className="text-[10px] text-slate-400 font-mono">{latencyMs}ms</span>
                    )}
                </div>

                {/* Warnings badge */}
                {warnings.length > 0 && (
                    <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-900/30">
                        <span className="material-symbols-outlined text-[12px] text-amber-500">warning</span>
                        <span className="text-[10px] font-bold text-amber-700 dark:text-amber-400">{warnings.length} warning{warnings.length > 1 ? 's' : ''}</span>
                    </div>
                )}

                {/* Spacer */}
                <div className="flex-1" />

                {/* Export error inline */}
                {exportError && (
                    <span className="text-[11px] text-red-600 dark:text-red-400 font-medium">{exportError}</span>
                )}

                {/* Export DOCX */}
                <button
                    id="export-docx-btn"
                    onClick={() => handleExport('docx')}
                    disabled={isExporting}
                    className="
                        flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                        bg-primary text-white text-xs font-bold
                        hover:bg-primary-hover hover:-translate-y-0.5
                        active:translate-y-0
                        shadow-md shadow-primary/20
                        disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none
                        transition-all duration-150
                    "
                >
                    {isExporting ? (
                        <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                        <span className="material-symbols-outlined text-[14px]">download</span>
                    )}
                    Export DOCX
                </button>

                {/* Export PDF */}
                <button
                    id="export-pdf-btn"
                    onClick={() => handleExport('pdf')}
                    disabled={isExporting}
                    className="
                        flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                        border border-slate-200 dark:border-slate-700
                        bg-white dark:bg-slate-800
                        text-slate-700 dark:text-slate-300
                        text-xs font-bold
                        hover:bg-slate-50 dark:hover:bg-slate-700
                        hover:-translate-y-0.5 active:translate-y-0
                        disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none
                        transition-all duration-150
                    "
                >
                    <span className="material-symbols-outlined text-[14px]">picture_as_pdf</span>
                    Export PDF
                </button>

                {/* AI Toggle */}
                <button
                    id="ai-sidebar-toggle"
                    onClick={() => setAiOpen((o) => !o)}
                    title={aiOpen ? 'Collapse AI sidebar' : 'Open AI sidebar'}
                    className={`
                        flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-bold transition-all duration-150
                        ${aiOpen
                            ? 'bg-violet-100 dark:bg-violet-900/20 text-violet-700 dark:text-violet-400 border border-violet-200 dark:border-violet-900/40'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-violet-300 dark:hover:border-violet-700'
                        }
                    `}
                >
                    <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
                    <span className="hidden sm:inline">AI</span>
                </button>
            </div>

            {/* ── Main body: SplitEditor + AI sidebar ─────────────────── */}
            <div className="flex flex-1 min-h-0 overflow-hidden">
                {/* Split editor takes remaining width */}
                <div className="flex-1 min-w-0 min-h-0 overflow-hidden">
                    <SplitEditor
                        sessionId={sessionId}
                        templateId={templateId}
                        html={html}
                        isAnalyzing={isAnalyzing}
                        sendContent={handleSendContent}
                    />
                </div>

                {/* AI Sidebar (collapsible) */}
                <AiSidebar
                    isOpen={aiOpen}
                    onToggle={() => setAiOpen((o) => !o)}
                    sessionId={sessionId}
                    templateId={templateId}
                    editorContentRef={editorContentRef}
                />
            </div>

            {/* ── Bottom status bar ────────────────────────────────────── */}
            <div className="flex items-center gap-4 px-4 py-1.5 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0 text-[10px] font-medium text-slate-400 dark:text-slate-600">
                <span>Session: <span className="font-mono">{sessionId.slice(0, 8)}…</span></span>
                <span>Template: <span className="text-slate-600 dark:text-slate-400">{BUILTIN_TEMPLATES.find(t => t.id === templateId)?.label}</span></span>
                {latencyMs !== null && <span>Latency: {latencyMs}ms</span>}
                <div className="ml-auto flex items-center gap-1.5">
                    <ConnectionDot isConnected={isConnected} />
                    <span>{isConnected ? 'Live' : 'Reconnecting…'}</span>
                </div>
            </div>
        </div>
    );
}
