const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const uploadDocument = async (file, template, options) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template_name', template);
    formData.append('enable_ocr', options.enableOCR || false);
    formData.append('enable_ai', options.enableAI || false);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Upload failed');
        }

        return await response.json();
    } catch (error) {
        console.error("Upload error:", error);
        throw error;
    }
};

export const downloadFile = async (filename) => {
    try {
        const response = await fetch(`${API_BASE_URL}/download/${filename}`, {
            method: 'GET',
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        return url;
    } catch (error) {
        console.error("Download error:", error);
        throw error;
    }
};

