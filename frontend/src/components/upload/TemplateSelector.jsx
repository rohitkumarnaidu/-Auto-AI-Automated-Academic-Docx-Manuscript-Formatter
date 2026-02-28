import { Link } from 'react-router-dom';

export default function TemplateSelector({
    category,
    template,
    isProcessing,
    file,
    formatFileSize,
    onCategoryChange,
    onTemplateSelect,
}) {
    const fileMetaText = file ? `${file.name} (${formatFileSize(file.size)})` : 'No file selected';

    return (
        <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 w-full sm:w-auto">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white whitespace-nowrap">Select Template</h2>

                    <div className="relative w-full sm:w-64 group">
                        <select
                            value={category}
                            onChange={(e) => onCategoryChange(e.target.value)}
                            disabled={isProcessing}
                            className="w-full h-10 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 pl-3 pr-8 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none appearance-none disabled:opacity-50 transition-all font-medium cursor-pointer"
                        >
                            <option value="none">None (General Formatting)</option>
                            <option value="ieee">IEEE Standard</option>
                            <option value="springer">Springer Nature (Standard)</option>
                            <option value="apa">APA Style (7th Edition)</option>
                            <option value="modern">Modern Styles (Red, Gold, Blue)</option>
                            <option value="browse_more" className="text-primary font-bold">Browse More Templates...</option>
                        </select>
                        <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center">
                            <span className="material-symbols-outlined text-[18px] text-slate-500 dark:text-slate-400">expand_more</span>
                        </div>
                    </div>
                </div>

                <Link className="text-sm font-medium text-primary hover:underline flex items-center gap-1 shrink-0" to="/templates">
                    Browse Library <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </Link>
            </div>

            {/* Template preview cards intentionally commented out for now.
                Keeping only the dropdown selector and browse action. */}
            <div className="sr-only" aria-hidden="true">
                <span>{fileMetaText}</span>
                <span>{template}</span>
                <span>{typeof onTemplateSelect === 'function' ? 'template-select-enabled' : 'template-select-disabled'}</span>
            </div>
        </div>
    );
}
