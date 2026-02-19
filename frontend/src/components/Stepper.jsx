/* eslint-disable react/prop-types */

const STEPS = [
    { title: "Uploading Manuscript", desc: "Source file received and secured." },
    { title: "Converting Format", desc: "Extracting semantic layers..." },
    { title: "Parsing Structure", desc: "Identifying headers and sections..." },
    { title: "Analyzing Content (AI)", desc: "Classifying academic intent..." },
    { title: "Journal Validation", desc: "Checking against style guide..." },
    { title: "Final Formatting", desc: "Applying template rules..." },
    { title: "Exporting Result", desc: "Generating output files..." }
];

export default function Stepper({ activeStep = 0 }) {
    return (
        <div className="p-6 space-y-6">
            {STEPS.map((step, index) => {
                const isActive = index === activeStep;
                const isCompleted = index < activeStep;
                const isPending = index > activeStep;

                return (
                    <div key={index} className={`flex items-start gap-4 ${isPending ? 'opacity-50' : ''}`}>
                        <div className="flex flex-col items-center">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 transition-colors 
                                ${isCompleted ? 'bg-green-100 text-green-600 border-transparent' : ''}
                                ${isActive ? 'bg-primary/20 text-primary border-primary' : ''}
                                ${isPending ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 border-transparent' : ''}
                            `}>
                                {isCompleted ? (
                                    <span className="material-symbols-outlined text-sm">check</span>
                                ) : isActive ? (
                                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                                ) : (
                                    <span className="text-xs font-bold">{index + 1}</span>
                                )}
                            </div>
                            {index < STEPS.length - 1 && (
                                <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-800 mt-2"></div>
                            )}
                        </div>
                        <div className="pt-1">
                            <p className={`text-sm font-bold ${isActive ? 'text-primary' : 'text-slate-900 dark:text-white'}`}>
                                {step.title}
                            </p>
                            <p className="text-xs text-slate-500 mt-1">
                                {isActive ? 'Processing...' : isCompleted ? 'Completed' : step.desc}
                            </p>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
