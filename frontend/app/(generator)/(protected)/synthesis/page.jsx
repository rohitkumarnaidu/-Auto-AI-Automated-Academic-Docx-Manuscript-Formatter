'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { FileText, Download, ArrowLeft, MessageSquare, AlertCircle } from 'lucide-react';
import { getSession } from '../../../src/services/api.generator.v1';

export default function SynthesisResultPage() {
    const searchParams = useSearchParams();
    const sessionId = searchParams.get('session');
    const router = useRouter();
    
    const [sessionData, setSessionData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!sessionId) {
            setError('No session ID provided.');
            setLoading(false);
            return;
        }

        getSession(sessionId)
            .then(res => {
                setSessionData(res);
                setLoading(false);
            })
            .catch(err => {
                setError('Failed to load session results.');
                setLoading(false);
            });
    }, [sessionId]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (error || !sessionData) {
        return (
            <div className="max-w-3xl mx-auto my-12 p-6 bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 rounded-xl flex items-center">
                <AlertCircle className="w-6 h-6 mr-3" />
                <h2 className="text-xl font-medium">{error || "Could not fetch session."}</h2>
            </div>
        );
    }

    const { target_template, file_id } = sessionData;
    const documentUrl = file_id ? `/api/v1/generator/sessions/${sessionId}/export/docx` : null;
    const pdfUrl = file_id ? `/api/v1/generator/sessions/${sessionId}/export/pdf` : null;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    return (
        <div className="max-w-6xl mx-auto px-4 py-12">
            <button 
                onClick={() => router.back()}
                className="flex items-center text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium mb-8 transition"
            >
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </button>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Result Card */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-8">
                        <div className="flex items-start justify-between">
                            <div>
                                <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
                                    Synthesized Manuscript
                                </h1>
                                <p className="text-slate-500 dark:text-slate-400">
                                    Template: <strong>{target_template || 'Default'}</strong>
                                </p>
                            </div>
                            <div className="h-16 w-16 bg-indigo-50 dark:bg-indigo-900/30 rounded-2xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-800">
                                <FileText className="w-8 h-8" />
                            </div>
                        </div>

                        <div className="mt-8 flex flex-wrap gap-4">
                            <a 
                                href={`${apiUrl}${documentUrl}`}
                                className="flex-1 sm:flex-none inline-flex justify-center items-center px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl shadow-sm transition"
                                download
                            >
                                <Download className="w-5 h-5 mr-2" />
                                Download DOCX
                            </a>
                            <a 
                                href={`${apiUrl}${pdfUrl}`}
                                className="flex-1 sm:flex-none inline-flex justify-center items-center px-6 py-3 bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/40 border border-red-200 dark:border-red-900 font-medium rounded-xl transition"
                                download
                            >
                                <Download className="w-5 h-5 mr-2" />
                                Download PDF
                            </a>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-8 flex items-center justify-between">
                         <div className="flex items-center">
                            <div className="p-3 bg-indigo-100 text-indigo-600 dark:bg-indigo-900/40 dark:text-indigo-400 rounded-full mr-4">
                                <MessageSquare className="w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-900 dark:text-white text-lg">Follow-up Questions?</h3>
                                <p className="text-slate-500 dark:text-slate-400 text-sm">Review your cross-document Q&A session.</p>
                            </div>
                         </div>
                         <button 
                            onClick={() => router.push('/multi-upload')}
                            className="px-5 py-2 whitespace-nowrap bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg text-sm font-medium transition"
                        >
                            New Synthesis
                        </button>
                    </div>
                </div>

                {/* Right Column: Score & Details */}
                <div className="lg:col-span-1 space-y-6">
                    {/* Quality Score Panel */}
                    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 flex flex-col items-center">
                        <h4 className="font-semibold text-slate-700 dark:text-slate-300 mb-6 self-start">Confidence Score</h4>
                        
                        <div className="relative w-32 h-32 flex items-center justify-center">
                            <svg className="w-full h-full transform -rotate-90">
                                <circle cx="64" cy="64" r="56" fill="none" className="stroke-slate-100 dark:stroke-slate-700" strokeWidth="12" />
                                <circle 
                                    cx="64" cy="64" r="56" fill="none" 
                                    className="stroke-green-500" 
                                    strokeWidth="12" 
                                    strokeDasharray="351.8" 
                                    strokeDashoffset={`${351.8 - (351.8 * 92) / 100}`}
                                    strokeLinecap="round" 
                                />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                <span className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">92</span>
                                <span className="text-[10px] font-bold uppercase text-slate-500 leading-none">/ 100</span>
                            </div>
                        </div>

                        <div className="mt-6 w-full space-y-3 pt-6 border-t border-slate-100 dark:border-slate-700">
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-500 dark:text-slate-400">Citation Alignment</span>
                                <span className="font-medium text-green-600 dark:text-green-400">95%</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-500 dark:text-slate-400">Section Continuity</span>
                                <span className="font-medium text-green-600 dark:text-green-400">88%</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-500 dark:text-slate-400">Formatting Match</span>
                                <span className="font-medium text-green-600 dark:text-green-400">93%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
