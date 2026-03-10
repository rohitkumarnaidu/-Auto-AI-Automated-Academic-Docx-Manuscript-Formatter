import { fetchWithAuth, sanitizePayload, sendFrontendErrorLog, API_BASE_URL } from './api.core';

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
    const res = await fetch(`${API_BASE_URL}/api/metrics/health`);
    if (!res.ok) return null;
    return res.json();
};

export const getMetricsDashboard = async () => {
    const res = await fetch(`${API_BASE_URL}/api/metrics/dashboard`);
    if (!res.ok) return null;
    return res.json();
};

export const getMetricsEnhancements = async () => {
    return fetchWithAuth('/api/metrics/enhancements');
};
