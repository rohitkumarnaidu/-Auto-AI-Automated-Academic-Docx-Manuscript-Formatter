import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';

import { useAuth } from './AuthContext';
import { getDocuments } from '../services/api';
import { isCompleted, isFailed, isProcessing } from '../constants/status';

const DocumentContext = createContext();

export const useDocument = () => useContext(DocumentContext);

const toFileMetadata = (file) => ({
    originalFileName: file?.name || '',
    originalFileSize: file?.size || 0,
    originalFileType: file?.type || '',
});

export const DocumentProvider = ({ children }) => {
    const { user } = useAuth();
    const [job, setJob] = useState(null); // Current active job
    const [history, setHistory] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);

    const refreshHistory = useCallback(async () => {
        if (!user) return;
        try {
            setLoadingHistory(true);
            const data = await getDocuments({ limit: 20 });
            // Map backend format to frontend expectation if needed,
            // but the backend format seems compatible mainly: id, filename, status, created_at
            // Backend returns { documents: [...], total: ... }
            if (data && data.documents) {
                // We map to ensure consistent naming if needed, e.g. originalFileName vs filename
                const mappedHistory = data.documents.map(doc => ({
                    ...doc,
                    originalFileName: doc.filename,
                    timestamp: doc.created_at
                }));
                setHistory(mappedHistory);
            }
        } catch (err) {
            console.error("Failed to fetch document history:", err);
        } finally {
            setLoadingHistory(false);
        }
    }, [user]);

    // Fetch history from backend when user logs in
    useEffect(() => {
        if (user) {
            refreshHistory();
        } else {
            setHistory([]);
        }
    }, [refreshHistory, user]);

    // HYDRATION FIX: Restore active job from session storage
    useEffect(() => {
        const savedJob = sessionStorage.getItem('scholarform_currentJob');
        if (savedJob) {
            try {
                const parsedJob = JSON.parse(savedJob);
                const normalizedStatus = parsedJob?.status;
                setJob({
                    ...parsedJob,
                    status: isCompleted(normalizedStatus)
                        ? 'completed'
                        : isFailed(normalizedStatus)
                            ? 'failed'
                            : isProcessing(normalizedStatus)
                                ? 'processing'
                                : normalizedStatus,
                });
            } catch (e) {
                console.error("Failed to hydrate job:", e);
                sessionStorage.removeItem('scholarform_currentJob');
            }
        }
    }, []);

    // Persist active job to session storage
    useEffect(() => {
        if (job) {
            sessionStorage.setItem('scholarform_currentJob', JSON.stringify(job));
        } else {
            sessionStorage.removeItem('scholarform_currentJob');
        }
    }, [job]);

    const addToHistory = (newJob) => {
        // Optimistic update only; network refetch is handled by regular query refresh flow.
        setHistory((prev) => [newJob, ...prev]);
    };

    const startProcessing = () => {
        setProcessing(true);
        setJob(null);
    };

    const finishProcessing = (result, file, template, options) => {
        setProcessing(false);
        const fileMetadata = toFileMetadata(file);
        const newJob = {
            id: result.job_id || Date.now().toString(),
            timestamp: new Date().toISOString(),
            status: 'completed',
            ...fileMetadata,
            template: template,
            options: options,
            result: result.validation_result,
            outputPath: result.output_path,
            flags: result.flags
        };
        setJob(newJob);
        addToHistory(newJob);
    };

    const failProcessing = (error) => {
        setProcessing(false);
        setJob({ status: 'failed', error: error.message });
    };

    return (
        <DocumentContext.Provider value={{
            job,
            setJob,
            history,
            refreshHistory,
            loadingHistory,
            processing,
            startProcessing,
            finishProcessing,
            failProcessing
        }}>
            {children}
        </DocumentContext.Provider>
    );
};
