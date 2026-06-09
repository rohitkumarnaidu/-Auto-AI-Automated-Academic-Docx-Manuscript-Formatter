import { fetchWithAuth, sanitizePayload, sanitizeText, unwrapV1Payload } from './api.core';
import { getV1, unwrapResponse } from './api.v1';

export const getCustomTemplates = async () => {
    const response = await fetchWithAuth('/api/v1/templates/custom', {
        suppressConsoleError: true,
        suppressMonitoring: true,
        retryConfig: { maxRetries: 0 },
    });
    return unwrapV1Payload(response);
};

export const saveCustomTemplate = async (template) => {
    const sanitizedTemplate = sanitizePayload(template);
    const response = await fetchWithAuth('/api/v1/templates/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: sanitizedTemplate }),
    });
    return unwrapV1Payload(response);
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
    const response = await fetchWithAuth(`/api/v1/templates/csl/search?q=${encodeURIComponent(sanitized)}`);
    return unwrapV1Payload(response);
};

export const fetchCSLStyle = async (slug) => {
    const sanitized = sanitizeText(slug);
    const response = await fetchWithAuth(`/api/v1/templates/csl/${encodeURIComponent(sanitized)}`);
    return unwrapV1Payload(response);
};
