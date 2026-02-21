import { Link } from 'react-router-dom';

// eslint-disable-next-line react/prop-types
export default function TemplateSelector({
    category,
    template,
    isProcessing,
    file,
    formatFileSize,
    onCategoryChange,
    onTemplateSelect,
}) {
    return (
        <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-4 w-full sm:w-auto">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white whitespace-nowrap">Select Template</h2>

                    <div className="relative flex-1 sm:w-64 group">
                        <select
                            value={category}
                            onChange={(e) => onCategoryChange(e.target.value)}
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

            <div className="relative group/carousel">
                <div className={`flex overflow-x-auto gap-6 pb-8 pt-4 px-4 snap-x scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-600 scrollbar-track-transparent max-w-[920px] mx-auto ${category !== 'none' ? 'justify-center' : ''}`}>
                    {category === 'none' && (
                        <>
                            <div
                                onClick={() => !isProcessing && onTemplateSelect('none')}
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

                            <div
                                onClick={() => !isProcessing && onTemplateSelect('modern_red')}
                                className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'modern_red' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                            >
                                <div className="aspect-[3/4] bg-white p-6 flex flex-col relative overflow-hidden select-none shadow-inner">
                                    <div className="w-full text-center mb-6">
                                        <div className="text-[10px] font-black text-red-600 uppercase tracking-[0.2em] mb-1">Style Showcase</div>
                                        <div className="w-16 h-[2px] bg-red-600 mx-auto"></div>
                                    </div>
                                    <div className="flex flex-col gap-3">
                                        <div className="w-1/2 h-2.5 bg-slate-800 rounded-sm mb-1"></div>

                                        <div className="w-full flex flex-col gap-1.5 opacity-60">
                                            <div className="w-full h-1 bg-slate-400 rounded-full"></div>
                                            <div className="w-full h-1 bg-slate-400 rounded-full"></div>
                                            <div className="w-5/6 h-1 bg-slate-400 rounded-full"></div>
                                        </div>

                                        <div className="w-full bg-blue-900 rounded-lg mt-3 p-3 shadow-sm">
                                            <div className="w-1/3 h-1.5 bg-white/30 rounded-full mb-2"></div>
                                            <div className="w-full h-1 bg-white/20 rounded-full"></div>
                                        </div>

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

                            <div
                                onClick={() => !isProcessing && onTemplateSelect('modern_gold')}
                                className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'modern_gold' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                            >
                                <div className="aspect-[3/4] bg-white p-6 flex flex-col relative overflow-hidden select-none shadow-inner">
                                    <div className="w-full bg-slate-900 py-2.5 px-4 mb-4 rounded-sm shadow-sm flex items-center justify-between">
                                        <div className="w-20 h-1.5 bg-white/20 rounded-full"></div>
                                        <div className="w-4 h-4 rounded-full border border-amber-500/50"></div>
                                    </div>

                                    <div className="w-full border-l-4 border-amber-500 pl-3 py-1 mb-4 bg-amber-50/50">
                                        <div className="w-1/3 h-2 bg-amber-600/80 rounded-sm"></div>
                                    </div>

                                    <div className="flex flex-col gap-3 px-1">
                                        <div className="w-full flex flex-col gap-1.5 opacity-60">
                                            <div className="w-full h-1 bg-slate-500 rounded-full"></div>
                                            <div className="w-11/12 h-1 bg-slate-500 rounded-full"></div>
                                            <div className="w-full h-1 bg-slate-500 rounded-full"></div>
                                        </div>

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

                            <div
                                onClick={() => !isProcessing && onTemplateSelect('modern_blue')}
                                className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'modern_blue' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                            >
                                <div className="aspect-[3/4] bg-white p-6 flex flex-col relative overflow-hidden select-none shadow-inner">
                                    <div className="w-full bg-blue-600 text-white rounded-md mb-2 p-3 shadow-md">
                                        <div className="w-1/2 h-2 bg-white/90 rounded-sm mx-auto mb-2 opacity-90"></div>
                                        <div className="w-full h-0.5 bg-blue-400/50"></div>
                                    </div>
                                    <div className="w-full h-1.5 bg-blue-100 rounded-full mb-5"></div>

                                    <div className="flex flex-col gap-3">
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

                    {category === 'ieee' && (
                        <div
                            onClick={() => !isProcessing && onTemplateSelect('ieee')}
                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'ieee' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                        >
                            <div className="aspect-[3/4] bg-slate-50 dark:bg-slate-800 p-6 flex flex-col gap-2 relative overflow-hidden select-none">
                                <div className="w-full h-4 bg-slate-200 dark:bg-slate-700 mb-4 mx-auto flex items-center justify-center rounded-sm border border-slate-300 dark:border-slate-600">
                                    <div className="w-2/3 h-2 bg-slate-800 dark:bg-slate-400 rounded-sm"></div>
                                </div>

                                <div className="flex gap-3 flex-1">
                                    <div className="w-1/2 flex flex-col gap-2">
                                        <div className="w-full h-1.5 bg-slate-400 dark:bg-slate-600 rounded-full"></div>
                                        <div className="w-full h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                                        <div className="w-3/4 h-1.5 bg-slate-300 dark:bg-slate-700 rounded-full"></div>

                                        <div className="w-full h-16 bg-white dark:bg-slate-700 rounded border border-slate-200 dark:border-slate-600 mt-2 p-1 flex items-center justify-center">
                                            <span className="material-symbols-outlined text-slate-300 text-lg">image</span>
                                        </div>
                                        <div className="w-full h-1 bg-slate-300 dark:bg-slate-700 rounded-full mt-1"></div>
                                    </div>

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

                    {category === 'springer' && (
                        <div
                            onClick={() => !isProcessing && onTemplateSelect('springer')}
                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'springer' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                        >
                            <div className="aspect-[3/4] bg-slate-50 dark:bg-slate-800 p-8 flex flex-col items-center relative overflow-hidden select-none">
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

                    {category === 'apa' && (
                        <div
                            onClick={() => !isProcessing && onTemplateSelect('apa')}
                            className={`shrink-0 w-[280px] snap-start cursor-pointer group relative rounded-xl border-2 transition-all duration-300 overflow-hidden bg-white dark:bg-slate-900 ${template === 'apa' ? 'border-primary ring-4 ring-primary/10 shadow-xl shadow-primary/10' : 'border-slate-200 dark:border-slate-800 hover:border-primary/50 hover:shadow-lg'}`}
                        >
                            <div className="aspect-[3/4] bg-slate-50 dark:bg-slate-800 p-6 flex flex-col relative overflow-hidden select-none">
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
    );
}
