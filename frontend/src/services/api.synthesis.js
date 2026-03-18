import { getAuthorizedHeaders, fetchWithRetry, parseResponseData } from './api.core';
import { BASE_V1_URL, getV1, postV1, unwrapResponse } from './api.v1';

export async function createSynthesisSession(files, template, config) {
    const url = `${BASE_V1_URL}/synthesis/sessions`;
    const formData = new FormData();
    formData.append('session_type', 'multi_doc');
    if (template) formData.append('template', template); // Synthesis backend uses 'template', generator uses 'template_id'
    if (config) formData.append('config', JSON.stringify(config));
    
    files.forEach(file => {
        formData.append('files', file);
    });

    const headers = await getAuthorizedHeaders({});
    
    const response = await fetchWithRetry(url, {
        method: 'POST',
        headers,
        body: formData,
        credentials: 'include'
    });
    
    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = null;
        }
        throw new Error(errorData?.error?.message || errorData?.detail || `Failed to create synthesis session (${response.status})`);
    }
    
    const payload = await parseResponseData(response);
    return unwrapResponse({ data: payload?.data ?? payload, error: payload?.error });
}

export async function getSynthesisSession(sessionId) {
    const response = await getV1(`/synthesis/sessions/${sessionId}`);
    return unwrapResponse(response);
}

export async function sendSynthesisMessage(sessionId, content) {
    const response = await postV1(`/synthesis/sessions/${sessionId}/messages`, { content });
    return unwrapResponse(response);
}

export function getSynthesisEventsEndpoint(sessionId) {
    return `${BASE_V1_URL}/synthesis/sessions/${sessionId}/events`;
}
