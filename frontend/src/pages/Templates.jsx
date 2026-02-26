import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { getBuiltinTemplates } from '../services/api';

// Fallback hardcoded templates when API is unavailable
const FALLBACK_TEMPLATES = [
    { id: 'ieee', name: 'IEEE Transactions', description: 'Official IEEE format for technical, electrical, and engineering research papers.', category: 'Engineering', icon: 'architecture', available: true },
    { id: 'nature', name: 'Nature Portfolio', description: 'Standard formatting template for submission to all Nature Portfolio journals.', category: 'Life Sciences', icon: 'biotech', available: true },
    { id: 'elsevier', name: 'Elsevier Standard', description: "General formatting guidelines compatible with Elsevier's wide range of journals.", category: 'Engineering', icon: 'description', available: true },
    { id: 'springer', name: 'Springer LNCS', description: 'Multi-column layouts and specific LNCS styles for Computer Science.', category: 'Engineering', icon: 'science', available: false },
    { id: 'apa', name: 'APA 7th Edition', description: 'Latest APA formatting standards for social and behavioral sciences research.', category: 'Social Sciences', icon: 'history_edu', available: true },
];

const CATEGORIES = ['All Publishers', 'Engineering', 'Life Sciences', 'Social Sciences'];
const ITEMS_PER_PAGE = 6;

export default function Templates() {
    const navigate = useNavigate();
    const [templates, setTemplates] = useState(FALLBACK_TEMPLATES);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState('All Publishers');
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [previewTemplate, setPreviewTemplate] = useState(null);

    // Fetch templates from API on mount
    useEffect(() => {
        let cancelled = false;
        setIsLoading(true);

        getBuiltinTemplates()
            .then((data) => {
                if (cancelled) return;
                if (Array.isArray(data) && data.length > 0) {
                    setTemplates(data.map(t => ({
                        id: t.id || t.name?.toLowerCase().replace(/\s+/g, '_'),
                        name: t.name || t.id,
                        description: t.description || '',
                        category: t.category || 'Engineering',
                        icon: t.icon || 'description',
                        available: t.available !== false,
                        guidelines: t.guidelines || t.rules || null,
                    })));
                }
            })
            .catch((err) => {
                console.warn('Failed to fetch templates from API, using fallback:', err.message);
            })
            .finally(() => {
                if (!cancelled) setIsLoading(false);
            });

        return () => { cancelled = true; };
    }, []);

    // Filter templates by search and category
    const filteredTemplates = useMemo(() => {
        let list = templates;
        if (activeCategory !== 'All Publishers') {
            list = list.filter(t => t.category === activeCategory);
        }
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            list = list.filter(t =>
                t.name.toLowerCase().includes(q) ||
                t.description.toLowerCase().includes(q) ||
                t.category.toLowerCase().includes(q)
            );
        }
        return list;
    }, [templates, searchQuery, activeCategory]);

    // Pagination
    const totalPages = Math.max(1, Math.ceil(filteredTemplates.length / ITEMS_PER_PAGE));
    const paginatedTemplates = filteredTemplates.slice(
        (currentPage - 1) * ITEMS_PER_PAGE,
        currentPage * ITEMS_PER_PAGE
    );

    // Reset page when filter changes
    useEffect(() => {
        setCurrentPage(1);
    }, [searchQuery, activeCategory]);

    const handleSelectTemplate = (template) => {
        if (!template.available) return;
        navigate('/upload', { state: { preselectedTemplate: template.id } });
    };

    const handlePreviewGuidelines = (template) => {
        setPreviewTemplate(template);
    };

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-[#0d131b] dark:text-slate-200 min-h-screen flex flex-col">
            <Navbar variant="app" />

            <main className="px-4 sm:px-6 lg:px-10 flex flex-1 justify-center py-8 sm:py-10">
                <div className="layout-content-container flex flex-col max-w-[1200px] flex-1">
                    {/* Header Section */}
                    <div className="flex flex-col gap-6 p-4">
                        <div className="flex flex-wrap justify-between items-end gap-3">
                            <div className="flex flex-col gap-3">
                                <p className="text-[#0d131b] dark:text-white text-3xl sm:text-4xl font-black leading-tight tracking-[-0.033em]">Journal Template Library</p>
                                <p className="text-[#4c6c9a] dark:text-slate-400 text-base font-normal leading-normal">Browse and select official academic formatting templates for your manuscript.</p>
                            </div>
                        </div>
                        {/* Search Bar */}
                        <div className="py-3">
                            <label className="flex flex-col min-w-40 h-14 w-full">
                                <div className="flex w-full flex-1 items-stretch rounded-xl h-full shadow-sm">
                                    <div className="text-[#4c6c9a] flex border-none bg-white dark:bg-slate-800 items-center justify-center pl-5 rounded-l-xl border-r-0">
                                        <span className="material-symbols-outlined text-[24px]">search</span>
                                    </div>
                                    <input
                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d131b] dark:text-white focus:outline-0 focus:ring-0 border-none bg-white dark:bg-slate-800 focus:border-none h-full placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 px-4 rounded-l-none border-l-0 pl-3 text-lg font-normal leading-normal"
                                        placeholder="Search for journal (e.g., IEEE, Nature, Elsevier)..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>
                            </label>
                        </div>
                        {/* Filters/Chips */}
                        <div className="flex gap-3 py-2 flex-wrap">
                            {CATEGORIES.map((cat) => (
                                <button
                                    key={cat}
                                    onClick={() => setActiveCategory(cat)}
                                    className={`flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-lg pl-4 pr-3 transition-all ${activeCategory === cat
                                        ? 'bg-primary text-white shadow-md'
                                        : 'bg-white dark:bg-slate-800 border border-[#e7ecf3] dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                                        }`}
                                >
                                    <p className={`text-sm font-${activeCategory === cat ? 'semibold' : 'medium'} leading-normal ${activeCategory !== cat ? 'text-[#0d131b] dark:text-slate-300' : ''}`}>{cat}</p>
                                    <span className="material-symbols-outlined text-[20px]">keyboard_arrow_down</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Skeleton Loading State */}
                    {isLoading && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
                            {Array.from({ length: 6 }).map((_, i) => (
                                <div key={i} className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 animate-pulse">
                                    <div className="flex justify-between items-start">
                                        <div className="size-12 rounded-lg bg-slate-200 dark:bg-slate-700"></div>
                                        <div className="w-16 h-5 rounded-full bg-slate-200 dark:bg-slate-700"></div>
                                    </div>
                                    <div className="flex flex-col gap-2">
                                        <div className="h-5 w-3/4 rounded bg-slate-200 dark:bg-slate-700"></div>
                                        <div className="h-4 w-full rounded bg-slate-100 dark:bg-slate-800"></div>
                                        <div className="h-4 w-2/3 rounded bg-slate-100 dark:bg-slate-800"></div>
                                    </div>
                                    <div className="flex flex-col gap-3 mt-2">
                                        <div className="h-10 rounded-lg bg-slate-200 dark:bg-slate-700"></div>
                                        <div className="h-10 rounded-lg bg-slate-100 dark:bg-slate-800"></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Template Grid */}
                    {!isLoading && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
                            {paginatedTemplates.map((template) => (
                                <div
                                    key={template.id}
                                    className={`flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl transition-all group ${template.available ? 'hover:border-primary/30' : 'opacity-80 grayscale'
                                        }`}
                                >
                                    <div className="flex justify-between items-start">
                                        <div className={`size-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center border border-slate-100 dark:border-slate-700 ${template.available ? 'text-primary' : 'text-slate-400'}`}>
                                            <span className="material-symbols-outlined text-[32px]">{template.icon}</span>
                                        </div>
                                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${template.available
                                            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                            : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                                            }`}>
                                            {template.available ? 'Available' : 'Coming Soon'}
                                        </span>
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <h3 className="text-[#0d131b] dark:text-white text-xl font-bold">{template.name}</h3>
                                        <p className="text-sm text-[#4c6c9a] dark:text-slate-400 leading-relaxed min-h-[40px] line-clamp-2">{template.description}</p>
                                    </div>
                                    <div className="flex flex-col gap-3 mt-2">
                                        <button
                                            onClick={() => handleSelectTemplate(template)}
                                            disabled={!template.available}
                                            className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-colors ${template.available
                                                ? 'bg-primary text-white hover:bg-primary/90'
                                                : 'bg-slate-200 dark:bg-slate-800 text-slate-500 cursor-not-allowed'
                                                }`}
                                        >
                                            Select Template
                                        </button>
                                        <button
                                            onClick={() => handlePreviewGuidelines(template)}
                                            className="w-full bg-slate-100 dark:bg-slate-800 text-[#0d131b] dark:text-slate-300 py-2.5 rounded-lg font-semibold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                                        >
                                            Preview Guidelines
                                        </button>
                                    </div>
                                </div>
                            ))}

                            {/* Request Template Card */}
                            <div
                                className="flex flex-col items-center justify-center gap-4 p-5 rounded-xl bg-slate-50/50 dark:bg-slate-800/20 border-2 border-dashed border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all cursor-pointer group"
                                onClick={() => window.open('mailto:templates@scholarform.ai?subject=Template%20Request', '_self')}
                            >
                                <div className="size-14 rounded-full bg-white dark:bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-primary shadow-sm transition-colors">
                                    <span className="material-symbols-outlined text-[32px]">add_circle</span>
                                </div>
                                <div className="text-center">
                                    <h3 className="text-[#0d131b] dark:text-white text-lg font-bold">Missing a journal?</h3>
                                    <p className="text-sm text-[#4c6c9a] dark:text-slate-400 px-4">Request a new formatting template and our team will add it within 48 hours.</p>
                                </div>
                                <span className="text-primary text-sm font-bold hover:underline">Request Template</span>
                            </div>

                            {/* No results */}
                            {paginatedTemplates.length === 0 && (
                                <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
                                    <span className="material-symbols-outlined text-4xl text-slate-300 mb-3">search_off</span>
                                    <p className="text-slate-500 font-medium">No templates found matching your criteria.</p>
                                    <button
                                        onClick={() => { setSearchQuery(''); setActiveCategory('All Publishers'); }}
                                        className="mt-3 text-primary text-sm font-bold hover:underline"
                                    >
                                        Clear filters
                                    </button>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Pagination */}
                    {!isLoading && totalPages > 1 && (
                        <div className="flex items-center justify-center gap-2 sm:gap-4 mt-12 py-6 border-t border-slate-200 dark:border-slate-800 flex-wrap">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                                className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                                <span className="material-symbols-outlined">chevron_left</span>
                            </button>
                            <div className="flex gap-2">
                                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                                    <button
                                        key={page}
                                        onClick={() => setCurrentPage(page)}
                                        className={`w-10 h-10 rounded-lg font-bold transition-colors ${currentPage === page
                                            ? 'bg-primary text-white'
                                            : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                                            }`}
                                    >
                                        {page}
                                    </button>
                                ))}
                            </div>
                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                                className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                                <span className="material-symbols-outlined">chevron_right</span>
                            </button>
                        </div>
                    )}
                </div>
            </main>

            {/* Preview Guidelines Modal */}
            {previewTemplate && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={() => setPreviewTemplate(null)}>
                    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                    <span className="material-symbols-outlined">{previewTemplate.icon}</span>
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">{previewTemplate.name}</h3>
                                    <p className="text-xs text-slate-500">{previewTemplate.category}</p>
                                </div>
                            </div>
                            <button onClick={() => setPreviewTemplate(null)} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                <span className="material-symbols-outlined text-slate-400">close</span>
                            </button>
                        </div>
                        <div className="p-6">
                            <h4 className="font-bold text-slate-900 dark:text-white mb-3">Formatting Guidelines</h4>
                            {previewTemplate.guidelines ? (
                                <pre className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap font-sans leading-relaxed">{typeof previewTemplate.guidelines === 'string' ? previewTemplate.guidelines : JSON.stringify(previewTemplate.guidelines, null, 2)}</pre>
                            ) : (
                                <div className="space-y-3 text-sm text-slate-600 dark:text-slate-400">
                                    <p>{previewTemplate.description}</p>
                                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 space-y-2">
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Standard Rules:</p>
                                        <ul className="list-disc list-inside space-y-1">
                                            <li>Two-column layout (where applicable)</li>
                                            <li>Times New Roman / Computer Modern fonts</li>
                                            <li>Numbered references in order of citation</li>
                                            <li>Author-date citation style (APA) or numbered</li>
                                            <li>Section numbering with hierarchical headings</li>
                                            <li>Abstract limited to 200-250 words</li>
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </div>
                        <div className="p-6 border-t border-slate-200 dark:border-slate-800 flex gap-3">
                            <button
                                onClick={() => { handleSelectTemplate(previewTemplate); setPreviewTemplate(null); }}
                                disabled={!previewTemplate.available}
                                className={`flex-1 py-2.5 rounded-lg font-bold text-sm transition-colors ${previewTemplate.available ? 'bg-primary text-white hover:bg-blue-600' : 'bg-slate-200 text-slate-500 cursor-not-allowed'}`}
                            >
                                {previewTemplate.available ? 'Use This Template' : 'Coming Soon'}
                            </button>
                            <button
                                onClick={() => setPreviewTemplate(null)}
                                className="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <Footer variant="app" />
        </div>
    );
}
