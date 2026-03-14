import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../services/api.v1';

export function useGeneratorSessionStream(sessionId) {
    const [stages, setStages] = useState([]);
    const [currentStage, setCurrentStage] = useState('');
    const [progress, setProgress] = useState(0);
    const [isComplete, setIsComplete] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!sessionId) return;

        let eventSource = null;
        let reconnectTimeout = null;
        let retryCount = 0;
        const maxRetries = 5;

        const connect = () => {
            const url = `${API_BASE_URL}/api/v1/generator/sessions/${sessionId}/events`;
            eventSource = new EventSource(url, { withCredentials: true });

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.name) {
                        setStages(prev => {
                            const newStages = [...prev];
                            const existingIndex = newStages.findIndex(s => s.name === data.name);
                            if (existingIndex >= 0) {
                                newStages[existingIndex] = { ...newStages[existingIndex], ...data };
                            } else {
                                newStages.push(data);
                            }
                            return newStages;
                        });
                        
                        setCurrentStage(data.name);
                    }
                    
                    if (data.progress !== undefined) {
                        setProgress(data.progress);
                    }
                    
                    // Mark complete if overall progress reaches 100 or a global "done" status is sent
                    if (data.progress >= 100 || (data.status === 'done' && !data.name) || (data.name === 'Template Rendering' && data.status === 'done')) {
                        setIsComplete(true);
                    }
                    
                    if (data.status === 'error') {
                        setError(new Error(data.message || 'Error during synthesis'));
                    }
                    
                } catch (err) {
                    console.error("Error parsing SSE data", err);
                }
            };

            eventSource.onerror = (err) => {
                console.error("SSE Error", err);
                eventSource.close();
                
                if (retryCount < maxRetries) {
                    retryCount++;
                    const backoff = Math.pow(2, retryCount) * 1000;
                    reconnectTimeout = setTimeout(connect, backoff);
                } else {
                    setError(new Error("Lost connection to synthesis stream. Please refresh."));
                }
            };
        };

        connect();

        return () => {
            if (eventSource) eventSource.close();
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
        };
    }, [sessionId]);

    return { stages, currentStage, progress, isComplete, error };
}
