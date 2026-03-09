import { fetchWithAuth, sanitizePayload, sendFrontendErrorLog } from './api.core';

export const logFrontendError = async (errorInfo) => {
    await sendFrontendErrorLog(errorInfo);
};

export const submitFeedback = async (data) => {
    const sanitizedData = sanitizePayload(data);
    return fetchWithAuth('/api/feedback/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedData),
    });
};

export const getFeedbackSummary = async (jobId) => {
    return fetchWithAuth(`/api/feedback/summary?document_id=${encodeURIComponent(jobId)}`);
};

export const getMetricsDb = async () => {
    return fetchWithAuth('/api/metrics/db');
};

export const getMetricsHealth = async () => {
    return fetchWithAuth('/api/metrics/health');
};

export const getMetricsDashboard = async () => {
    return fetchWithAuth('/api/metrics/dashboard');
};

export const getMetricsEnhancements = async () => {
    return fetchWithAuth('/api/metrics/enhancements');
};
