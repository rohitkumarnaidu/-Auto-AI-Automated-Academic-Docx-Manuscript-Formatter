const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic helper to handle fetch requests and throw detailed errors.
 */
const handleRequest = async (endpoint, options = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Request failed: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error.message);
        throw error;
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
   AUTH APIs (OTP-BASED)
   ===================== */

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
