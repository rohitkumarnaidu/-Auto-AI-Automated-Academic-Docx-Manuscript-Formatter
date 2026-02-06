const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic helper to handle fetch requests and throw detailed errors.
 */
const handleRequest = async (endpoint, options = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

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
    formData.append('template_name', template);
    formData.append('enable_ocr', options.enableOCR || false);
    formData.append('enable_ai', options.enableAI || false);

    return handleRequest('/upload', {
        method: 'POST',
        body: formData,
    });
};

/**
 * Downloads a processed file and returns a blob URL.
 */
export const downloadFile = async (filename) => {
    try {
        const response = await fetch(`${API_BASE_URL}/download/${filename}`);

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
    return handleRequest('/auth/signup', {
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
    return handleRequest('/auth/login', {
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
    return handleRequest('/auth/forgot-password', {
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
    return handleRequest('/auth/verify-otp', {
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
    return handleRequest('/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
};
