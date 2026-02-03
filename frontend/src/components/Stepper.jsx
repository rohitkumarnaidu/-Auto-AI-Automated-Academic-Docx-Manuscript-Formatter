/* eslint-disable react/prop-types */

export default function Stepper() {
    return (
        <div className="p-6 space-y-6">
            {/* Step 1 */}
            <div className="flex items-start gap-4">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center shrink-0">
                        <span className="material-symbols-outlined text-sm">check</span>
                    </div>
                    <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Uploading Manuscript</p>
                    <p className="text-xs text-slate-500 mt-1">Source file received and secured.</p>
                </div>
            </div>
            {/* Step 2 (Active) */}
            <div className="flex items-start gap-4">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center shrink-0 border-2 border-primary">
                        <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                    </div>
                    <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-primary">Converting Format</p>
                    <p className="text-xs text-slate-500 mt-1">Extracting semantic layers from PDF...</p>
                </div>
            </div>
            {/* Step 3 */}
            <div className="flex items-start gap-4 opacity-50">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold">3</span>
                    </div>
                    <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Parsing Structure</p>
                    <p className="text-xs text-slate-500 mt-1">Pending...</p>
                </div>
            </div>
            {/* Step 4 */}
            <div className="flex items-start gap-4 opacity-50">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold">4</span>
                    </div>
                    <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Analyzing Content (AI)</p>
                    <p className="text-xs text-slate-500 mt-1">Pending...</p>
                </div>
            </div>
            {/* Step 5 */}
            <div className="flex items-start gap-4 opacity-50">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold">5</span>
                    </div>
                    <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Journal Validation</p>
                    <p className="text-xs text-slate-500 mt-1">Pending...</p>
                </div>
            </div>
            {/* Step 6 */}
            <div className="flex items-start gap-4 opacity-50">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold">6</span>
                    </div>
                    <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Final Formatting</p>
                    <p className="text-xs text-slate-500 mt-1">Pending...</p>
                </div>
            </div>
            {/* Step 7 */}
            <div className="flex items-start gap-4 opacity-50">
                <div className="flex flex-col items-center">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold">7</span>
                    </div>
                </div>
                <div className="pt-1">
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Exporting Result</p>
                    <p className="text-xs text-slate-500 mt-1">Pending...</p>
                </div>
            </div>
        </div>
    );
}
