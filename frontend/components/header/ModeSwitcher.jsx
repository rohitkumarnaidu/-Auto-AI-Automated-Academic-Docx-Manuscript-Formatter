'use client';

export default function ModeSwitcher({ activeMode, onChange, compact = false }) {
    const baseWrapper = compact
        ? 'flex bg-slate-800/50 rounded-xl p-1 w-full max-w-sm relative shadow-inner'
        : 'relative flex bg-slate-800/50 rounded-xl p-1';

    const baseOption = compact
        ? 'py-2 text-center rounded-lg text-sm font-semibold text-slate-400 peer-checked:text-white peer-checked:bg-primary transition-all duration-300'
        : 'px-6 py-2 rounded-lg text-sm font-semibold text-slate-400 peer-checked:text-white peer-checked:bg-primary peer-checked:shadow-[0_4px_12px_rgba(108,43,238,0.4)] transition-all duration-300 flex items-center gap-2';

    return (
        <div className={baseWrapper}>
            <label className={`cursor-pointer ${compact ? 'flex-1 relative z-10' : 'relative z-10'}`}>
                <input
                    type="radio"
                    name={compact ? 'mode-mobile' : 'mode'}
                    className="peer sr-only"
                    checked={activeMode === 'formatter'}
                    onChange={() => onChange('formatter')}
                    aria-label="Formatter Mode"
                />
                <div className={baseOption}>
                    {!compact && <span className="material-symbols-outlined text-[18px]">format_align_left</span>}
                    Formatter
                </div>
            </label>
            <label className={`cursor-pointer ${compact ? 'flex-1 relative z-10' : 'relative z-10'}`}>
                <input
                    type="radio"
                    name={compact ? 'mode-mobile' : 'mode'}
                    className="peer sr-only"
                    checked={activeMode === 'generator'}
                    onChange={() => onChange('generator')}
                    aria-label="Generator Mode"
                />
                <div className={baseOption}>
                    {!compact && <span className="material-symbols-outlined text-[18px]">auto_awesome</span>}
                    Generator
                </div>
            </label>
        </div>
    );
}
