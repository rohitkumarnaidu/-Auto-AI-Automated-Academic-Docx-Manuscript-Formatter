import React from 'react';
import { useNavigate } from 'react-router-dom';
import PreviewView from '../components/Preview';
import { useDocument } from '../context/DocumentContext';

export default function Preview() {
    const navigate = useNavigate();
    const { job } = useDocument();

    if (!job) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-background-light dark:bg-background-dark">
                <div className="text-center p-8 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 max-w-md animate-in fade-in zoom-in duration-300">
                    <span className="material-symbols-outlined text-6xl text-slate-300 dark:text-slate-700 mb-4 block">receipt_long</span>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">No document to preview</h2>
                    <p className="text-slate-500 dark:text-slate-400 mb-6 text-sm leading-relaxed">
                        Please upload and process a manuscript first to see the final formatted preview.
                    </p>
                    <button
                        onClick={() => navigate('/upload')}
                        className="w-full bg-primary text-white font-bold py-3 px-6 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2"
                    >
                        <span className="material-symbols-outlined">upload_file</span>
                        Return to Upload
                    </button>
                </div>
            </div>
        );
    }

    return (
        <PreviewView
            job={job}
            onUpload={() => navigate('/upload')}
            onDownload={() => navigate('/download')}
        />
    );
}
