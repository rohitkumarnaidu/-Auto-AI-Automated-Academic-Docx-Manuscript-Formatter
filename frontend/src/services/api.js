const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic helper to handle fetch requests and throw detailed errors.
 */
const handleRequest = async (endpoint, options = {}) => {
    try {
        // --- AUTH INJECTION ---
        // Dynamically import supabase to avoid circular dependencies if any
        const { supabase } = await import('../lib/supabaseClient');
        const { data: { session } } = await supabase.auth.getSession();

        const headers = { ...options.headers };

        if (session?.access_token) {
            headers['Authorization'] = `Bearer ${session.access_token}`;
        }

        const finalOptions = {
            ...options,
            headers
        };

        const response = await fetch(`${API_BASE_URL}${endpoint}`, finalOptions);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            let errorMessage = `Request failed: ${response.statusText}`;

            if (errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    // Handle FastAPI validation error lists
                    errorMessage = errorData.detail
                        .map(err => err.msg || JSON.stringify(err))
                        .join('. ');
                } else if (typeof errorData.detail === 'object') {
                    errorMessage = JSON.stringify(errorData.detail);
                }
            }

            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        // Ensure error.message is always a string
        const finalMessage = typeof error.message === 'string'
            ? error.message
            : String(error || 'An unknown error occurred');

        console.error(`API Error [${endpoint}]:`, finalMessage);
        throw new Error(finalMessage);
    }
};

/* =====================
   DOCUMENT APIs
   ===================== */

/**
 * Uploads a document with template and processing options.
 */
export const uploadDocument = async (file, template, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template', template);
    formData.append('enable_ocr', options.enableOCR || false);
    formData.append('enable_ai', options.enableAI || false);

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
export const getPreview = async (jobId) => {
    return handleRequest(`/api/documents/${jobId}/preview`);
};

/**
 * Fetches the comparison data (original vs formatted).
 */
export const getComparison = async (jobId) => {
    return handleRequest(`/api/documents/${jobId}/compare`);
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
 * Downloads a processed file.
 */
export const downloadFile = async (jobId, format = 'docx') => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/${jobId}/download?format=${format}`);

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        return window.URL.createObjectURL(blob);
    } catch (error) {
        console.error("Download error:", error);
        throw error;
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
    return handleRequest('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
};

/**
 * Proxies login to Supabase via backend.
 * Payload: { email, password }
 */
export const login = async (data) => {
    return handleRequest('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
};

/**
 * Triggers the Supabase recovery OTP flow.
 * Payload: { email }
 */
export const forgotPassword = async (data) => {
    return handleRequest('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
};

/**
 * Verifies the 6-digit OTP.
 * Payload: { email, otp }
 */
export const verifyOtp = async (data) => {
    return handleRequest('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
};

/**
 * Finalizes password reset using the verified OTP.
 * Payload: { email, otp, new_password }
 */
export const resetPassword = async (data) => {
    return handleRequest('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
};
