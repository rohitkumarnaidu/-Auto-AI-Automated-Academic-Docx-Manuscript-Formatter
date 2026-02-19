const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const SUPPORTED_EXPORT_FORMATS = ['docx', 'pdf', 'json'];
const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504];
const DEFAULT_MAX_RETRIES = 2;
const BASE_RETRY_DELAY_MS = 500;
const DEFAULT_DEBOUNCE_MS = 250;
const DEBOUNCED_REQUESTS = new Map();
const CSRF_HEADER_NAME = 'X-CSRF-Token';
const CSRF_STORAGE_KEY = 'scholarform_csrf_token';
const CSRF_COOKIE_NAMES = ['csrftoken', 'csrf_token', 'XSRF-TOKEN'];
const SENSITIVE_INPUT_KEYS = /(password|otp|token|secret)/i;

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const normalizeExportFormat = (format = 'docx') => {
    const normalized = String(format || 'docx').toLowerCase();
    return SUPPORTED_EXPORT_FORMATS.includes(normalized) ? normalized : 'docx';
};

const getCookieValue = (name) => {
    if (typeof document === 'undefined') {
        return '';
    }

    const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const match = document.cookie.match(new RegExp(`(?:^|; )${escapedName}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : '';
};

const createRandomToken = () => {
    if (typeof window !== 'undefined' && window.crypto?.getRandomValues) {
        const values = new Uint8Array(16);
        window.crypto.getRandomValues(values);
        return Array.from(values, (value) => value.toString(16).padStart(2, '0')).join('');
    }
    return `${Date.now().toString(16)}${Math.random().toString(16).slice(2)}`;
};

const getCSRFToken = () => {
    for (const cookieName of CSRF_COOKIE_NAMES) {
        const cookieToken = getCookieValue(cookieName);
        if (cookieToken) {
            return cookieToken;
        }
    }

    if (typeof window === 'undefined') {
        return '';
    }

    let token = window.sessionStorage.getItem(CSRF_STORAGE_KEY);
    if (!token) {
        token = createRandomToken();
        window.sessionStorage.setItem(CSRF_STORAGE_KEY, token);
    }
    return token;
};

const sanitizeText = (value) => (
    String(value)
        .replace(/[\u0000-\u001F\u007F]/g, '')
        .replace(/[<>]/g, '')
        .trim()
);

const sanitizeValue = (value, path = '') => {
    if (typeof value === 'string') {
        if (SENSITIVE_INPUT_KEYS.test(path)) {
            return value.trim();
        }
        return sanitizeText(value);
    }

    if (Array.isArray(value)) {
        return value.map((entry, index) => sanitizeValue(entry, `${path}.${index}`));
    }

    if (value && typeof value === 'object') {
        return Object.entries(value).reduce((accumulator, [key, nestedValue]) => {
            const nextPath = path ? `${path}.${key}` : key;
            accumulator[key] = sanitizeValue(nestedValue, nextPath);
            return accumulator;
        }, {});
    }

    return value;
};

const sanitizePayload = (payload) => sanitizeValue(payload);

const isNetworkError = (error) => {
    if (!error) return false;

    const message = String(error.message || error).toLowerCase();
    return (
        error.name === 'TypeError' ||
        message.includes('failed to fetch') ||
        message.includes('networkerror') ||
        message.includes('network request failed') ||
        message.includes('load failed') ||
        message.includes('timeout')
    );
};

const extractServerErrorMessage = (errorData, fallbackMessage = '') => {
    if (!errorData || typeof errorData !== 'object') {
        return fallbackMessage;
    }

    if (typeof errorData.detail === 'string') {
        return errorData.detail;
    }

    if (Array.isArray(errorData.detail)) {
        return errorData.detail
            .map((err) => err.msg || JSON.stringify(err))
            .join('. ');
    }

    if (typeof errorData.detail === 'object') {
        return JSON.stringify(errorData.detail);
    }

    return fallbackMessage;
};

const getFriendlyErrorMessage = ({ status, errorData, fallbackMessage = '', error } = {}) => {
    if (status === 401) {
        return 'Your session has expired. Please log in again.';
    }

    if (status === 403) {
        return 'You do not have permission to perform this action.';
    }

    if (status === 404) {
        return 'The requested resource could not be found.';
    }

    if (status === 429) {
        return 'Too many requests right now. Please wait a moment and try again.';
    }

    if (typeof status === 'number' && status >= 500) {
        return 'The server is temporarily unavailable. Please try again shortly.';
    }

    if (isNetworkError(error)) {
        return 'Unable to reach the server. Please check your internet connection and try again.';
    }

    const serverMessage = extractServerErrorMessage(errorData, '');
    if (serverMessage) {
        return serverMessage;
    }

    if (typeof fallbackMessage === 'string' && fallbackMessage.trim()) {
        return fallbackMessage;
    }

    return 'Something went wrong. Please try again.';
};

const shouldRetryRequest = ({ method = 'GET', status, error, attempt, maxRetries }) => {
    if (attempt >= maxRetries) {
        return false;
    }

    const normalizedMethod = String(method || 'GET').toUpperCase();
    const isSafeMethod = ['GET', 'HEAD', 'OPTIONS'].includes(normalizedMethod);
    if (!isSafeMethod) {
        return false;
    }

    if (isNetworkError(error)) {
        return true;
    }

    if (typeof status === 'number' && RETRYABLE_STATUS_CODES.includes(status)) {
        return true;
    }

    return false;
};

const fetchWithRetry = async (url, options = {}, retryConfig = {}) => {
    const maxRetries = retryConfig.maxRetries ?? DEFAULT_MAX_RETRIES;
    const method = options.method || 'GET';
    let lastError = null;

    for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
        try {
            const response = await fetch(url, options);

            if (response.ok) {
                return response;
            }

            if (!shouldRetryRequest({ method, status: response.status, attempt, maxRetries })) {
                return response;
            }
        } catch (error) {
            lastError = error;

            if (!shouldRetryRequest({ method, error, attempt, maxRetries })) {
                throw error;
            }
        }

        const delayMs = BASE_RETRY_DELAY_MS * (2 ** attempt);
        await wait(delayMs);
    }

    throw lastError || new Error('Request failed after retries.');
};

const getAuthorizedHeaders = async (initialHeaders = {}) => {
    const headers = { ...initialHeaders };
    const csrfToken = getCSRFToken();

    if (csrfToken && !headers[CSRF_HEADER_NAME]) {
        headers[CSRF_HEADER_NAME] = csrfToken;
    }

    try {
        const { supabase } = await import('../lib/supabaseClient');
        const {
            data: { session },
        } = await supabase.auth.getSession();

        if (session?.access_token) {
            headers.Authorization = `Bearer ${session.access_token}`;
        }
    } catch (error) {
        // Keep requests working even if auth bootstrap fails.
        console.warn('Auth header injection skipped:', error);
    }
    return headers;
};

/**
 * Logs frontend errors to the backend for monitoring.
 */
export const logFrontendError = async (errorInfo) => {
    try {
        const headers = await getAuthorizedHeaders({ 'Content-Type': 'application/json' });
        await fetch(`${API_BASE_URL}/api/metrics/log-error`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
                message: errorInfo.message || String(errorInfo),
                stack: errorInfo.stack,
                url: window.location.href,
                timestamp: new Date().toISOString(),
            }),
        });
    } catch (e) {
        // Silently fail to avoid infinite error loops
        console.warn('Failed to log frontend error to backend:', e);
    }
};

/**
 * Generic helper to handle fetch requests and throw detailed errors.
 */
const handleRequest = async (endpoint, options = {}) => {
    try {
        const headers = await getAuthorizedHeaders(options.headers);
        const { retryConfig, ...fetchOptions } = options;

        const finalOptions = {
            ...fetchOptions,
            headers,
            credentials: fetchOptions.credentials || 'include',
        };

        const response = await fetchWithRetry(
            `${API_BASE_URL}${endpoint}`,
            finalOptions,
            retryConfig
        );

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const fallbackMessage = `Request failed (${response.status})`;
            throw new Error(
                getFriendlyErrorMessage({
                    status: response.status,
                    errorData,
                    fallbackMessage,
                })
            );
        }

        return await response.json();
    } catch (error) {
        const finalMessage = getFriendlyErrorMessage({
            error,
            fallbackMessage:
                typeof error.message === 'string' ? error.message : String(error || ''),
        });

        console.error(`API Error [${endpoint}]:`, finalMessage, error);

        // Log to monitoring service
        logFrontendError({
            message: `API Error [${endpoint}]: ${finalMessage}`,
            stack: error.stack,
        });

        throw new Error(finalMessage);
    }
};

const getDebounceKey = (endpoint, options = {}) => {
    const method = String(options.method || 'GET').toUpperCase();
    return `${method}:${endpoint}`;
};

const handleRequestDebounced = (endpoint, options = {}, debounceMs = DEFAULT_DEBOUNCE_MS) => {
    if (!debounceMs || debounceMs <= 0) {
        return handleRequest(endpoint, options);
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
            const result = await handleRequest(existing.endpoint, existing.options);
            existing.waiters.forEach((waiter) => waiter.resolve(result));
        } catch (error) {
            existing.waiters.forEach((waiter) => waiter.reject(error));
        }
    }, debounceMs);

    DEBOUNCED_REQUESTS.set(key, existing);
    return requestPromise;
};

/* =====================
   DOCUMENT APIs
   ===================== */

/**
 * Fetches the list of documents for the current user.
 */
export const getDocuments = async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return handleRequest(`/api/documents?${query}`);
};

/**
 * Uploads a document with template and processing options.
 */
export const uploadDocument = async (file, template, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template', sanitizeText(template));

    // New Formatting Options
    formData.append('add_page_numbers', options.add_page_numbers ?? true);
    formData.append('add_borders', options.add_borders ?? false);
    formData.append('add_cover_page', options.add_cover_page ?? true);
    formData.append('generate_toc', options.generate_toc ?? false);
    formData.append('page_size', sanitizeText(options.page_size || 'Letter'));

    return handleRequest('/api/documents/upload', {
        method: 'POST',
        body: formData,
    });
};

/**
 * Polls the processing status of a job.
 */
export const getJobStatus = async (jobId) => {
    return handleRequest(`/api/documents/${jobId}/status`);
};

/**
 * Fetches the preview data (structured content + validation results).
 */
export const getPreview = async (jobId, options = {}) => {
    return handleRequestDebounced(
        `/api/documents/${jobId}/preview`,
        {},
        options.debounceMs ?? DEFAULT_DEBOUNCE_MS
    );
};

/**
 * Fetches the comparison data (original vs formatted).
 */
export const getComparison = async (jobId, options = {}) => {
    return handleRequestDebounced(
        `/api/documents/${jobId}/compare`,
        {},
        options.debounceMs ?? DEFAULT_DEBOUNCE_MS
    );
};

/**
 * Submits edited content for re-processing.
 */
export const submitEdit = async (jobId, editedData) => {
    return handleRequest(`/api/documents/${jobId}/edit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ edited_structured_data: editedData }),
    });
};

/**
 * Returns the supported export formats for the current frontend flow.
 */
export const getExportFormats = () => [...SUPPORTED_EXPORT_FORMATS];

/**
 * Downloads a processed file.
 */
export const downloadFile = async (jobId, format = 'docx') => {
    const normalizedFormat = normalizeExportFormat(format);

    try {
        const headers = await getAuthorizedHeaders();
        const response = await fetchWithRetry(
            `${API_BASE_URL}/api/documents/${jobId}/download?format=${normalizedFormat}`,
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
        return window.URL.createObjectURL(blob);
    } catch (error) {
        const message = getFriendlyErrorMessage({
            error,
            fallbackMessage: 'Download failed. Please try again.',
        });
        console.error('Download error:', message, error);
        throw new Error(message);
    }
};

const buildJsonFallbackPayload = async (jobId) => {
    const [statusResult, previewResult] = await Promise.allSettled([
        getJobStatus(jobId),
        getPreview(jobId),
    ]);

    const statusData = statusResult.status === 'fulfilled' ? statusResult.value : null;
    const previewData = previewResult.status === 'fulfilled' ? previewResult.value : null;

    if (!statusData && !previewData) {
        return null;
    }

    return {
        job_id: jobId,
        exported_at: new Date().toISOString(),
        status: statusData
            ? {
                status: statusData.status,
                phase: statusData.phase,
                progress_percentage: statusData.progress_percentage,
                message: statusData.message,
            }
            : null,
        metadata: previewData?.metadata || {},
        structured_data: previewData?.structured_data || null,
        validation_results: previewData?.validation_results || null,
    };
};

/**
 * Downloads a selected export format.
 * JSON first attempts backend export and falls back to preview payload.
 */
export const downloadExport = async (jobId, format = 'docx') => {
    const normalizedFormat = normalizeExportFormat(format);

    if (normalizedFormat !== 'json') {
        return downloadFile(jobId, normalizedFormat);
    }

    try {
        return await downloadFile(jobId, 'json');
    } catch (error) {
        const fallbackPayload = await buildJsonFallbackPayload(jobId);
        if (!fallbackPayload) {
            throw error;
        }

        const blob = new Blob([JSON.stringify(fallbackPayload, null, 2)], {
            type: 'application/json',
        });
        return window.URL.createObjectURL(blob);
    }
};

/* =====================
   AUTH APIs (BACKEND PROXY)
   ===================== */

/**
 * Proxies signup to Supabase via backend.
 * Payload: { full_name, email, institution, password, terms_accepted }
 */
export const signup = async (data) => {
    const sanitizedData = sanitizePayload(data);
    return handleRequest('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedData),
    });
};

/**
 * Proxies login to Supabase via backend.
 * Payload: { email, password }
 */
export const login = async (data) => {
    const sanitizedData = sanitizePayload(data);
    return handleRequest('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedData),
    });
};

/**
 * Triggers the Supabase recovery OTP flow.
 * Payload: { email }
 */
export const forgotPassword = async (data) => {
    const sanitizedData = sanitizePayload(data);
    return handleRequest('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedData),
    });
};

/**
 * Verifies the 6-digit OTP.
 * Payload: { email, otp }
 */
export const verifyOtp = async (data) => {
    const sanitizedData = sanitizePayload(data);
    return handleRequest('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedData),
    });
};

/**
 * Finalizes password reset using the verified OTP.
 * Payload: { email, otp, new_password }
 */
export const resetPassword = async (data) => {
    const sanitizedData = sanitizePayload(data);
    return handleRequest('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedData),
    });
};
