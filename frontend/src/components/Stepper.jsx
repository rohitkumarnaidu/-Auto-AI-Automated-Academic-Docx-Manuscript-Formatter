import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

const STEPS = [
    { id: 'uploading', title: "Uploading Manuscript", desc: "Source file received and secured." },
    { id: 'converting', title: "Converting Format", desc: "Extracting semantic layers..." },
    { id: 'parsing', title: "Parsing Structure", desc: "Identifying headers and sections..." },
    { id: 'analyzing', title: "Analyzing Content (AI)", desc: "Classifying academic intent..." },
    { id: 'validating', title: "Journal Validation", desc: "Checking against style guide..." },
    { id: 'formatting', title: "Final Formatting", desc: "Applying template rules..." },
    { id: 'exporting', title: "Exporting Result", desc: "Generating output files..." }
];

export default function Stepper({ activeStep = 0 }) {
    return (
        <div className="p-4 sm:p-6 space-y-2">
            <AnimatePresence>
                {STEPS.map((step, index) => {
                    const isActive = index === activeStep;
                    const isCompleted = index < activeStep;
                    const isPending = index > activeStep;

                    if (isPending && index > activeStep + 1) return null; // Show only up to next step

                    return (
                        <motion.div
                            key={step.id}
                            initial={{ opacity: 0, y: 10, height: 0 }}
                            animate={{ opacity: isPending ? 0.5 : 1, y: 0, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className={`flex items-start gap-4 overflow-hidden relative ${isActive ? 'pb-2' : ''}`}
                        >
                            <div className="flex flex-col items-center z-10">
                                <motion.div
                                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 transition-colors bg-white dark:bg-slate-900
                                        ${isCompleted ? 'text-green-500 border-green-500 bg-green-50 dark:bg-green-900/20' : ''}
                                        ${isActive ? 'text-primary border-primary shadow-sm shadow-primary/20 bg-blue-50 dark:bg-blue-900/20' : ''}
                                        ${isPending ? 'text-slate-300 dark:text-slate-600 border-slate-200 dark:border-slate-700' : ''}
                                    `}
                                    animate={isActive ? { scale: [1, 1.05, 1] } : {}}
                                    transition={isActive ? { repeat: Infinity, duration: 2 } : {}}
                                >
                                    {isCompleted ? (
                                        <CheckCircle2 className="w-4 h-4" />
                                    ) : isActive ? (
                                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                                    ) : (
                                        <span className="text-xs font-bold">{index + 1}</span>
                                    )}
                                </motion.div>
                                {index < STEPS.length - 1 && (!isPending || index === activeStep + 1) && (
                                    <div className="w-0.5 h-full min-h-[32px] mt-2 mb-2 bg-slate-100 dark:bg-slate-800 relative rounded-full overflow-hidden">
                                        <motion.div
                                            className="absolute top-0 w-full bg-green-500"
                                            initial={{ height: 0 }}
                                            animate={{ height: isCompleted ? '100%' : '0%' }}
                                            transition={{ duration: 0.5 }}
                                        />
                                    </div>
                                )}
                            </div>

                            <div className="pt-1 w-full pb-4 relative">
                                <p className={`text-sm font-bold transition-colors ${isActive ? 'text-primary' : isCompleted ? 'text-slate-700 dark:text-slate-300' : 'text-slate-500 dark:text-slate-400'}`}>
                                    {step.title}
                                </p>
                                <AnimatePresence>
                                    {(isActive || isCompleted) && (
                                        <motion.p
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="text-xs text-slate-500 dark:text-slate-400 mt-1"
                                        >
                                            {isActive ? 'Processing active layer...' : isCompleted ? 'Completed successfully' : step.desc}
                                        </motion.p>
                                    )}
                                </AnimatePresence>

                                <AnimatePresence>
                                    {isActive && (
                                        <motion.div
                                            initial={{ opacity: 0, scale: 0.95, height: 0 }}
                                            animate={{ opacity: 1, scale: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="mt-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400 flex items-center gap-2"
                                        >
                                            <Loader2 className="w-3 h-3 animate-spin text-primary" />
                                            <span className="animate-pulse">Live activity stream starting...</span>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}
