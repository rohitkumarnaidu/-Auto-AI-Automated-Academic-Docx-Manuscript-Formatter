import { getAuthorizedHeaders, fetchWithRetry, parseResponseData } from './api.core';
import { BASE_V1_URL, getV1, postV1, unwrapResponse } from './api.v1';

export async function createSession(files, sessionType, template, config) {
    const url = `${BASE_V1_URL}/generator/sessions`;
    const formData = new FormData();
    formData.append('session_type', sessionType);
    if (template) formData.append('template_id', template);
    if (config) formData.append('config', JSON.stringify(config));
    
    files.forEach(file => {
        formData.append('files', file);
    });

    const headers = await getAuthorizedHeaders({});
    // Do NOT set Content-Type here, let the browser set it to multipart/form-data with boundary
    
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
        } catch(e) {}
        throw new Error(errorData?.error?.message || errorData?.detail || `Failed to create session (${response.status})`);
    }
    
    const payload = await parseResponseData(response);
    return unwrapResponse({ data: payload?.data ?? payload, error: payload?.error });
}

export async function getSession(sessionId) {
    const response = await getV1(`/generator/sessions/${sessionId}`);
    return unwrapResponse(response);
}

export async function sendMessage(sessionId, content) {
    const response = await postV1(`/generator/sessions/${sessionId}/messages`, { content });
    return unwrapResponse(response);
}

export async function approveOutline(sessionId) {
    const response = await postV1(`/generator/sessions/${sessionId}/outline/approve`, {});
    return unwrapResponse(response);
}
