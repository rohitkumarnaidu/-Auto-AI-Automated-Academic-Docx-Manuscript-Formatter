import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import BatchUploadPanel from '../components/BatchUploadPanel';
import { uploadDocumentWithProgress } from '../services/api';

export default function BatchUpload() {
    const { isLoggedIn } = useAuth();
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [template, setTemplate] = useState('IEEE');
    const [processing, setProcessing] = useState(false);

    const handleFilesSelected = useCallback((selectedFiles) => {
        const newFiles = selectedFiles.map((f) => ({
            file: f,
            id: `${f.name}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
            status: 'pending',
            progress: 0,
            jobId: null,
            error: null,
        }));
        setFiles((prev) => [...prev, ...newFiles]);
    }, []);

    const removeFile = useCallback((id) => {
        setFiles((prev) => prev.filter((f) => f.id !== id));
    }, []);

    const updateFile = useCallback((id, updates) => {
        setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, ...updates } : f)));
    }, []);

    const processAll = async () => {
        const pending = files.filter((f) => f.status === 'pending');
        if (pending.length === 0) return;

        setProcessing(true);

        for (const entry of pending) {
            updateFile(entry.id, { status: 'uploading', progress: 0 });
            try {
                const result = await uploadDocumentWithProgress(
                    entry.file,
                    template,
                    {},
                    {
                        onProgress: (percent) => updateFile(entry.id, { progress: percent }),
                    }
                );
                updateFile(entry.id, {
                    status: 'done',
                    progress: 100,
                    jobId: result?.job_id || null,
                });
            } catch (err) {
                updateFile(entry.id, {
                    status: 'error',
                    error: err.message || 'Upload failed',
                });
            }
        }

        setProcessing(false);
    };

    const completedCount = files.filter((f) => f.status === 'done').length;
    const errorCount = files.filter((f) => f.status === 'error').length;

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
            <Navbar />
            <main className="max-w-4xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-4xl">upload_file</span>
                        Batch Upload
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-2">
                        Upload and process multiple documents at once with the same template settings.
                    </p>
                </div>

                {/* Template Selection */}
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm mb-6">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">style</span>
                        Template
                    </h2>
                    <select
                        value={template}
                        onChange={(e) => setTemplate(e.target.value)}
                        disabled={processing}
                        className="w-full md:w-auto p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary outline-none"
                    >
                        <option value="IEEE">IEEE</option>
                        <option value="Springer">Springer</option>
                        <option value="APA">APA</option>
                        <option value="Nature">Nature</option>
                        <option value="Vancouver">Vancouver</option>
                        <option value="none">None (Auto-detect)</option>
                    </select>
                </div>

                {/* Upload Panel */}
                <BatchUploadPanel
                    files={files}
                    onFilesSelected={handleFilesSelected}
                    onRemove={removeFile}
                    disabled={processing}
                />

                {/* Action Bar */}
                {files.length > 0 && (
                    <div className="mt-6 flex items-center justify-between bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
                        <div className="text-sm text-slate-600 dark:text-slate-400">
                            {files.length} file{files.length !== 1 ? 's' : ''}
                            {completedCount > 0 && (
                                <span className="text-green-600 dark:text-green-400 ml-2">• {completedCount} done</span>
                            )}
                            {errorCount > 0 && (
                                <span className="text-red-600 dark:text-red-400 ml-2">• {errorCount} failed</span>
                            )}
                        </div>
                        <button
                            onClick={processAll}
                            disabled={processing || files.filter((f) => f.status === 'pending').length === 0}
                            className="px-6 py-3 bg-primary hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-primary/25 transition-all disabled:opacity-50 flex items-center gap-2"
                        >
                            {processing ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <span className="material-symbols-outlined">rocket_launch</span>
                                    Process All ({files.filter((f) => f.status === 'pending').length})
                                </>
                            )}
                        </button>
                    </div>
                )}
            </main>
            <Footer />
        </div>
    );
}
