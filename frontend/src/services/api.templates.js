import { fetchWithAuth, sanitizePayload, sanitizeText } from './api.core';
import { getV1, unwrapResponse } from './api.v1';

export const getCustomTemplates = async () => {
    return fetchWithAuth('/api/templates/custom');
};

export const saveCustomTemplate = async (template) => {
    const sanitizedTemplate = sanitizePayload(template);
    return fetchWithAuth('/api/templates/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: sanitizedTemplate }),
    });
};

export const getBuiltinTemplates = async () => {
    const response = await getV1('/templates', {
        suppressConsoleError: true,
        suppressMonitoring: true,
        retryConfig: { maxRetries: 0 },
    });
    return unwrapResponse(response);
};

export const searchCSLStyles = async (query) => {
    const sanitized = sanitizeText(query);
    return fetchWithAuth(`/api/templates/csl/search?q=${encodeURIComponent(sanitized)}`);
};

export const fetchCSLStyle = async (slug) => {
    const sanitized = sanitizeText(slug);
    return fetchWithAuth(`/api/templates/csl/${encodeURIComponent(sanitized)}`);
};
