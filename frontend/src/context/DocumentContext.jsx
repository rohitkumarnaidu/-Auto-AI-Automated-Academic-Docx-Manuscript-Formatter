import React, { createContext, useState, useContext, useEffect } from 'react';

const DocumentContext = createContext();

export const useDocument = () => useContext(DocumentContext);

export const DocumentProvider = ({ children }) => {
    const [job, setJob] = useState(null); // Current active job
    const [history, setHistory] = useState([]);
    const [processing, setProcessing] = useState(false);

    // Load history from local storage on mount
    useEffect(() => {
        const savedHistory = localStorage.getItem('manuscript_history');
        if (savedHistory) {
            setHistory(JSON.parse(savedHistory));
        }

        // HYDRATION FIX: Restore active job from session storage
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

    const addToHistory = (newJob) => {
        const updatedHistory = [newJob, ...history];
        setHistory(updatedHistory);
        localStorage.setItem('manuscript_history', JSON.stringify(updatedHistory));
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
            processing,
            startProcessing,
            finishProcessing,
            failProcessing
        }}>
            {children}
        </DocumentContext.Provider>
    );
};
