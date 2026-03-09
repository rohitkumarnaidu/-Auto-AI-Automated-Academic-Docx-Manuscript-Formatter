import {
    API_BASE_URL,
    fetchWithAuth,
    fetchWithRetry,
    getAuthorizedHeaders,
    getFriendlyErrorMessage,
    normalizeExportFormat,
    sanitizePayload,
} from './api.core';

export const generateDocument = async (payload) => {
    const sanitizedPayload = sanitizePayload(payload);
    return fetchWithAuth('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedPayload),
    });
};

export const getGenerationStatus = async (jobId) => (
    fetchWithAuth(`/api/generate/status/${encodeURIComponent(jobId)}`)
);

export const streamGenerationStatus = async (jobId, onEvent, onError) => {
    const abortController = new AbortController();
    const headers = await getAuthorizedHeaders({ Accept: 'text/event-stream' });

    (async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/stream/${encodeURIComponent(jobId)}`, {
                method: 'GET',
                headers,
                credentials: 'include',
                signal: abortController.signal,
            });

            if (!response.ok || !response.body) {
                throw new Error(`Failed to open generation stream (${response.status})`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (!abortController.signal.aborted) {
                const { value, done } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                let boundaryIndex = buffer.indexOf('\n\n');
                while (boundaryIndex !== -1) {
                    const frame = buffer.slice(0, boundaryIndex);
                    buffer = buffer.slice(boundaryIndex + 2);
                    boundaryIndex = buffer.indexOf('\n\n');

                    let eventType = 'message';
                    const dataLines = [];

                    for (const lineRaw of frame.split(/\r?\n/)) {
                        const line = lineRaw.trimEnd();
                        if (line.startsWith('event:')) {
                            eventType = line.slice(6).trim();
                        } else if (line.startsWith('data:')) {
                            dataLines.push(line.slice(5).trim());
                        }
                    }

                    if (!dataLines.length) continue;

                    const payloadRaw = dataLines.join('\n');
                    let payload = payloadRaw;
                    try {
                        payload = JSON.parse(payloadRaw);
                    } catch {
                        // Keep raw payload if not JSON.
                    }

                    if (typeof onEvent === 'function') {
                        onEvent({ event: eventType, data: payload });
                    }
                }
            }
        } catch (error) {
            if (abortController.signal.aborted) return;
            if (typeof onError === 'function') {
                onError(error instanceof Error ? error : new Error(String(error)));
            }
        }
    })();

    return () => abortController.abort();
};

export const downloadGeneratedDocument = async (jobId, format = 'docx') => {
    const normalizedFormat = normalizeExportFormat(format);
    const headers = await getAuthorizedHeaders();
    const response = await fetchWithRetry(
        `${API_BASE_URL}/api/generate/download/${encodeURIComponent(jobId)}?format=${normalizedFormat}`,
        { headers, method: 'GET', credentials: 'include' }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            getFriendlyErrorMessage({
                status: response.status,
                errorData,
                fallbackMessage: 'Generation download failed.',
            })
        );
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    setTimeout(() => window.URL.revokeObjectURL(url), 300000);
    return url;
};
