import { useEffect, useState } from 'react';
import ProcessingOptions from './ProcessingOptions';

export default function ExportDialog({
    isOpen,
    defaultFormat = 'docx',
    isDownloading = false,
    error = '',
    onClose,
    onDownload,
}) {
    const [selectedFormat, setSelectedFormat] = useState(defaultFormat);

    useEffect(() => {
        if (isOpen) {
            setSelectedFormat(defaultFormat);
        }
    }, [defaultFormat, isOpen]);

    if (!isOpen) {
        return null;
    }

    const handleDownloadClick = () => {
        onDownload?.(selectedFormat);
    };

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
            role="dialog"
            aria-modal="true"
            aria-label="Export options"
            data-testid="export-dialog"
        >
            <div className="w-full max-w-md rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-6 shadow-2xl">
                <div className="mb-4">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Export Document</h3>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        Select a format and download your manuscript.
                    </p>
                </div>

                <ProcessingOptions
                    selectedFormat={selectedFormat}
                    onFormatChange={setSelectedFormat}
                    disabled={isDownloading}
                />

                {Boolean(error) && (
                    <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                        {error}
                    </p>
                )}

                <div className="mt-6 flex gap-3">
                    <button
                        type="button"
                        onClick={onClose}
                        disabled={isDownloading}
                        className="flex-1 rounded-lg border border-slate-300 dark:border-slate-700 px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-60"
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        onClick={handleDownloadClick}
                        disabled={isDownloading}
                        data-testid="export-download-button"
                        className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                    >
                        {isDownloading ? 'Downloading...' : 'Download'}
                    </button>
                </div>
            </div>
        </div>
    );
}
