import { useRef, useCallback } from 'react';

const ACCEPTED_FORMATS = '.docx,.pdf,.tex,.txt,.html,.htm,.md,.markdown,.doc';

export default function BatchUploadPanel({ files, onFilesSelected, onRemove, disabled }) {
    const inputRef = useRef(null);

    const handleDrop = useCallback(
        (e) => {
            e.preventDefault();
            if (disabled) return;
            const dropped = Array.from(e.dataTransfer.files);
            if (dropped.length > 0) onFilesSelected(dropped);
        },
        [disabled, onFilesSelected]
    );

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleInputChange = (e) => {
        const selected = Array.from(e.target.files);
        if (selected.length > 0) onFilesSelected(selected);
        e.target.value = '';
    };

    const statusIcon = (status) => {
        switch (status) {
            case 'done':
                return <span className="material-symbols-outlined text-green-500 text-lg">check_circle</span>;
            case 'error':
                return <span className="material-symbols-outlined text-red-500 text-lg">error</span>;
            case 'uploading':
                return <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />;
            default:
                return <span className="material-symbols-outlined text-slate-400 text-lg">schedule</span>;
        }
    };

    const formatSize = (bytes) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            {/* Drop Zone */}
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => !disabled && inputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl m-4 p-8 text-center cursor-pointer transition-colors ${disabled
                    ? 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 opacity-50 cursor-not-allowed'
                    : 'border-slate-300 dark:border-slate-600 hover:border-primary dark:hover:border-primary bg-slate-50 dark:bg-slate-800/30'
                    }`}
            >
                <span className="material-symbols-outlined text-4xl text-slate-400 dark:text-slate-500 mb-2">cloud_upload</span>
                <p className="text-slate-600 dark:text-slate-400 font-medium">
                    Drag & drop files here, or <span className="text-primary font-semibold">browse</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">
                    Accepts DOCX, PDF, TEX, TXT, HTML, MD files (up to 50MB each)
                </p>
                <input
                    ref={inputRef}
                    type="file"
                    multiple
                    accept={ACCEPTED_FORMATS}
                    onChange={handleInputChange}
                    className="hidden"
                />
            </div>

            {/* File List */}
            {files.length > 0 && (
                <div className="border-t border-slate-200 dark:border-slate-700">
                    <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800/50">
                        <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                            Files ({files.length})
                        </p>
                    </div>
                    <ul className="divide-y divide-slate-100 dark:divide-slate-800 max-h-80 overflow-y-auto">
                        {files.map((entry) => (
                            <li
                                key={entry.id}
                                className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                            >
                                {statusIcon(entry.status)}
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                                        {entry.file.name}
                                    </p>
                                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                                        <span>{formatSize(entry.file.size)}</span>
                                        {entry.error && (
                                            <span className="text-red-500">{entry.error}</span>
                                        )}
                                        {entry.jobId && (
                                            <span className="text-green-600 dark:text-green-400">Job: {entry.jobId.slice(0, 8)}...</span>
                                        )}
                                    </div>
                                    {entry.status === 'uploading' && (
                                        <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full mt-1">
                                            <div
                                                className="h-1 bg-primary rounded-full transition-all duration-300"
                                                style={{ width: `${entry.progress}%` }}
                                            />
                                        </div>
                                    )}
                                </div>
                                {entry.status === 'pending' && (
                                    <button
                                        onClick={(e) => { e.stopPropagation(); onRemove(entry.id); }}
                                        disabled={disabled}
                                        className="text-slate-400 hover:text-red-500 transition-colors disabled:opacity-50"
                                    >
                                        <span className="material-symbols-outlined text-lg">close</span>
                                    </button>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
