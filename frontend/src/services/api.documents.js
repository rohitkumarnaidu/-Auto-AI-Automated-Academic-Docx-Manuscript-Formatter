import {
    API_BASE_URL,
    CHUNK_SIZE_BYTES,
    CHUNK_UPLOAD_THRESHOLD_BYTES,
    fetchWithAuth,
    fetchWithRetry,
    getAuthorizedHeaders,
    getFriendlyErrorMessage,
    normalizeExportFormat,
    sanitizeText,
} from './api.core';

const SUPPORTED_EXPORT_FORMATS = ['docx', 'pdf'];
const DEFAULT_DEBOUNCE_MS = 250;
const DEBOUNCED_REQUESTS = new Map();

const getDebounceKey = (endpoint, options = {}) => {
    const method = String(options.method || 'GET').toUpperCase();
    return `${method}:${endpoint}`;
};

const fetchWithAuthDebounced = (endpoint, options = {}, debounceMs = DEFAULT_DEBOUNCE_MS) => {
    if (!debounceMs || debounceMs <= 0) {
        return fetchWithAuth(endpoint, options);
    }

    const key = getDebounceKey(endpoint, options);
    const existing = DEBOUNCED_REQUESTS.get(key) || {
        endpoint,
        options,
        waiters: [],
        timer: null,
    };

    existing.endpoint = endpoint;
    existing.options = options;

    const requestPromise = new Promise((resolve, reject) => {
        existing.waiters.push({ resolve, reject });
    });

    if (existing.timer) {
        clearTimeout(existing.timer);
    }

    existing.timer = setTimeout(async () => {
        DEBOUNCED_REQUESTS.delete(key);

        try {
            const result = await fetchWithAuth(existing.endpoint, existing.options);
            existing.waiters.forEach((waiter) => waiter.resolve(result));
        } catch (error) {
            existing.waiters.forEach((waiter) => waiter.reject(error));
        }
    }, debounceMs);

    DEBOUNCED_REQUESTS.set(key, existing);
    return requestPromise;
};

const normalizeQueryParams = (params = {}) => (
    Object.fromEntries(
        Object.entries(params || {})
            .filter(([, value]) => value !== undefined && value !== null && value !== '')
            .sort(([left], [right]) => left.localeCompare(right))
    )
);

const DOCUMENTS_LIMIT_MIN = 1;
const DOCUMENTS_LIMIT_MAX = 100;

export const normalizeDocumentsParams = (params = {}) => {
    const normalizedParams = normalizeQueryParams(params);

    if ('limit' in normalizedParams) {
        const parsedLimit = Number.parseInt(String(normalizedParams.limit), 10);
        if (Number.isFinite(parsedLimit)) {
            const clampedLimit = Math.min(DOCUMENTS_LIMIT_MAX, Math.max(DOCUMENTS_LIMIT_MIN, parsedLimit));
            normalizedParams.limit = String(clampedLimit);
        } else {
            delete normalizedParams.limit;
        }
    }

    if ('offset' in normalizedParams) {
        const parsedOffset = Number.parseInt(String(normalizedParams.offset), 10);
        if (Number.isFinite(parsedOffset)) {
            normalizedParams.offset = String(Math.max(0, parsedOffset));
        } else {
            delete normalizedParams.offset;
        }
    }

    return normalizedParams;
};

export const mapDocumentRecord = (doc) => ({
    ...doc,
    originalFileName: doc?.filename,
    timestamp: doc?.created_at,
});

const parseResponseJson = (responseText) => {
    if (!responseText) return {};
    try {
        return JSON.parse(responseText);
    } catch {
        return {};
    }
};

const createAbortError = (message) => {
    if (typeof DOMException === 'function') {
        return new DOMException(message, 'AbortError');
    }
    const error = new Error(message);
    error.name = 'AbortError';
    return error;
};

export const getDocuments = async (params = {}) => {
    const normalizedParams = normalizeDocumentsParams(params);
    const query = new URLSearchParams(normalizedParams).toString();
    const endpoint = query ? `/api/documents?${query}` : '/api/documents';
    return fetchWithAuth(endpoint);
};

export const uploadDocument = async (file, template, options = {}, signal = null) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template', sanitizeText(template));

    formData.append('add_page_numbers', options.add_page_numbers ?? true);
    formData.append('add_borders', options.add_borders ?? false);
    formData.append('add_cover_page', options.add_cover_page ?? true);
    formData.append('generate_toc', options.generate_toc ?? false);
    formData.append('page_size', sanitizeText(options.page_size || 'Letter'));

    const fetchOptions = {
        method: 'POST',
        body: formData,
    };
    if (signal) fetchOptions.signal = signal;

    return fetchWithAuth('/api/documents/upload', fetchOptions);
};

export const uploadDocumentWithProgress = async (
    file,
    template,
    options = {},
    { signal = null, onProgress = null } = {}
) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template', sanitizeText(template));

    formData.append('add_page_numbers', options.add_page_numbers ?? true);
    formData.append('add_borders', options.add_borders ?? false);
    formData.append('add_cover_page', options.add_cover_page ?? true);
    formData.append('generate_toc', options.generate_toc ?? false);
    formData.append('page_size', sanitizeText(options.page_size || 'Letter'));
    formData.append('fast_mode', options.fast_mode ?? false);

    const headers = await getAuthorizedHeaders();

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', `${API_BASE_URL}/api/documents/upload`);
        xhr.withCredentials = true;

        Object.entries(headers).forEach(([header, value]) => {
            if (value !== undefined && value !== null) {
                xhr.setRequestHeader(header, value);
            }
        });

        xhr.upload.onprogress = (event) => {
            if (!event.lengthComputable || typeof onProgress !== 'function') {
                return;
            }
            const percent = Math.round((event.loaded / event.total) * 100);
            onProgress(percent, event);
        };

        xhr.onerror = () => {
            reject(new Error('Upload failed due to a network error.'));
        };

        xhr.onabort = () => {
            reject(createAbortError('Upload was cancelled.'));
        };

        xhr.onload = () => {
            const responsePayload = parseResponseJson(xhr.responseText);
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(responsePayload);
                return;
            }

            reject(
                new Error(
                    getFriendlyErrorMessage({
                        status: xhr.status,
                        errorData: responsePayload,
                        fallbackMessage: `Upload failed (${xhr.status})`,
                    })
                )
            );
        };

        if (signal) {
            if (signal.aborted) {
                xhr.abort();
                return;
            }
            const abortHandler = () => xhr.abort();
            signal.addEventListener('abort', abortHandler, { once: true });
            xhr.onloadend = () => signal.removeEventListener('abort', abortHandler);
        }

        xhr.send(formData);
    });
};

export const uploadChunked = async (file, options = {}) => {
    if (typeof File !== 'undefined' && !(file instanceof File)) {
        throw new Error('Invalid file supplied for chunked upload.');
    }

    const chunkSize = options.chunkSize || CHUNK_SIZE_BYTES;
    const onProgress = typeof options.onProgress === 'function' ? options.onProgress : null;
    const signal = options.signal || null;
    const totalChunks = Math.max(1, Math.ceil(file.size / chunkSize));
    let finalChunkResponse = null;

    const fileId = (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function')
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex += 1) {
        if (signal?.aborted) {
            throw createAbortError('Chunked upload cancelled.');
        }

        const start = chunkIndex * chunkSize;
        const end = Math.min(file.size, start + chunkSize);
        const chunkBlob = file.slice(start, end);
        const formData = new FormData();
        formData.append('file_id', fileId);
        formData.append('chunk_index', String(chunkIndex));
        formData.append('total_chunks', String(totalChunks));
        formData.append('file', chunkBlob, `${file.name}.part${chunkIndex}`);

        const headers = await getAuthorizedHeaders();
        const response = await fetchWithRetry(`${API_BASE_URL}/api/documents/upload/chunked`, {
            method: 'POST',
            headers,
            body: formData,
            credentials: 'include',
            signal,
        });

        const responsePayload = await response.json().catch(() => ({}));
        finalChunkResponse = responsePayload;

        if (!response.ok) {
            throw new Error(
                getFriendlyErrorMessage({
                    status: response.status,
                    errorData: responsePayload,
                    fallbackMessage: `Chunk upload failed (${response.status})`,
                })
            );
        }

        if (onProgress) {
            const loaded = Math.min(file.size, end);
            const percent = Math.round((loaded / file.size) * 100);
            onProgress({
                chunkIndex,
                totalChunks,
                loaded,
                total: file.size,
                percent,
                response: responsePayload,
            });
        }
    }

    if (finalChunkResponse && typeof finalChunkResponse === 'object') {
        return {
            ...finalChunkResponse,
            file_id: finalChunkResponse.file_id || fileId,
            total_chunks: finalChunkResponse.total_chunks || totalChunks,
        };
    }

    return { file_id: fileId, total_chunks: totalChunks, status: 'complete' };
};

export const getJobStatus = async (jobId, options = {}) => (
    fetchWithAuth(`/api/documents/${encodeURIComponent(jobId)}/status`, options)
);

export const getPreview = async (jobId, options = {}) => (
    fetchWithAuthDebounced(
        `/api/documents/${encodeURIComponent(jobId)}/preview`,
        {},
        options.debounceMs ?? DEFAULT_DEBOUNCE_MS
    )
);

export const getComparison = async (jobId, options = {}) => (
    fetchWithAuthDebounced(
        `/api/documents/${encodeURIComponent(jobId)}/compare`,
        {},
        options.debounceMs ?? DEFAULT_DEBOUNCE_MS
    )
);

export const submitEdit = async (jobId, editedData) => (
    fetchWithAuth(`/api/documents/${encodeURIComponent(jobId)}/edit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ edited_structured_data: editedData }),
    })
);

export const getExportFormats = () => [...SUPPORTED_EXPORT_FORMATS];

export const downloadFile = async (jobId, format = 'docx') => {
    const normalizedFormat = normalizeExportFormat(format);

    try {
        const headers = await getAuthorizedHeaders();
        const response = await fetchWithRetry(
            `${API_BASE_URL}/api/documents/${encodeURIComponent(jobId)}/download?format=${normalizedFormat}`,
            { headers, method: 'GET', credentials: 'include' }
        );

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                getFriendlyErrorMessage({
                    status: response.status,
                    errorData,
                    fallbackMessage: 'Download failed. Please try again.',
                })
            );
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        return {
            url,
            cleanup: () => window.URL.revokeObjectURL(url),
        };
    } catch (error) {
        const message = getFriendlyErrorMessage({
            error,
            fallbackMessage: 'Download failed. Please try again.',
        });
        console.error('Download error:', message, error);
        throw new Error(message);
    }
};

export const downloadExport = async (jobId, format = 'docx') => (
    downloadFile(jobId, normalizeExportFormat(format))
);

/**
 * Download a LaTeX (.tex) export — bypasses the normalizer since 'tex'
 * is not yet in SUPPORTED_EXPORT_FORMATS (enabled via feature flag).
 * TODO: Remove bypass once 'tex' is added to SUPPORTED_EXPORT_FORMATS (Module 2).
 */
export const downloadLatex = async (jobId) => {
    try {
        const headers = await getAuthorizedHeaders();
        const response = await fetchWithRetry(
            `${API_BASE_URL}/api/documents/${encodeURIComponent(jobId)}/download?format=tex`,
            { headers, method: 'GET', credentials: 'include' }
        );

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                getFriendlyErrorMessage({
                    status: response.status,
                    errorData,
                    fallbackMessage: 'LaTeX download failed. Please try again.',
                })
            );
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        return {
            url,
            cleanup: () => window.URL.revokeObjectURL(url),
        };
    } catch (error) {
        const message = getFriendlyErrorMessage({
            error,
            fallbackMessage: 'LaTeX download failed. Please try again.',
        });
        console.error('LaTeX download error:', message, error);
        throw new Error(message);
    }
};

export const deleteDocument = async (jobId) => (
    fetchWithAuth(`/api/documents/${encodeURIComponent(jobId)}`, {
        method: 'DELETE',
    })
);

export const getJobSummary = async (jobId) => (
    fetchWithAuth(`/api/documents/${encodeURIComponent(jobId)}/summary`)
);

export { CHUNK_UPLOAD_THRESHOLD_BYTES };
