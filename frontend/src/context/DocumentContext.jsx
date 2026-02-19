import React, { createContext, useState, useContext, useEffect } from 'react';

import { useAuth } from './AuthContext';
import { getDocuments } from '../services/api';

const DocumentContext = createContext();

export const useDocument = () => useContext(DocumentContext);

export const DocumentProvider = ({ children }) => {
    const { user } = useAuth();
    const [job, setJob] = useState(null); // Current active job
    const [history, setHistory] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);

    // Fetch history from backend when user logs in
    useEffect(() => {
        if (user) {
            refreshHistory();
        } else {
            setHistory([]);
        }
    }, [user]);

    const refreshHistory = async () => {
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
    };

    // HYDRATION FIX: Restore active job from session storage
    useEffect(() => {
        const savedJob = sessionStorage.getItem('scholarform_currentJob');
        if (savedJob) {
            try {
                const parsedJob = JSON.parse(savedJob);
                setJob(parsedJob);
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
        // Optimistic update
        const updatedHistory = [newJob, ...history];
        setHistory(updatedHistory);
        // We also trigger a refresh to get the official backend state (id might be temp vs real)
        refreshHistory();
    };

    const startProcessing = () => {
        setProcessing(true);
        setJob(null);
    };

    const finishProcessing = (result, file, template, options) => {
        setProcessing(false);
        const newJob = {
            id: result.job_id || Date.now().toString(),
            timestamp: new Date().toISOString(),
            status: 'completed',
            originalFile: file, // Note: This is an object and won't serialize well to LS
            originalFileName: file.name,
            template: template,
            options: options,
            result: result.validation_result,
            outputPath: result.output_path,
            flags: result.flags
        };
        setJob(newJob);
        // We sanitize for history to avoid storing large file objects in LS
        const historyItem = { ...newJob };
        delete historyItem.originalFile;
        addToHistory(historyItem);
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
