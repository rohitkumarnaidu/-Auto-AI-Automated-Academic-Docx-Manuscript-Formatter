import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
    fetchWithAuthMock,
    fetchWithRetryMock,
    getAuthorizedHeadersMock,
    normalizeExportFormatMock,
    sanitizeTextMock,
} = vi.hoisted(() => ({
    fetchWithAuthMock: vi.fn(),
    fetchWithRetryMock: vi.fn(),
    getAuthorizedHeadersMock: vi.fn(),
    normalizeExportFormatMock: vi.fn((format = 'docx') => {
        const normalized = String(format || 'docx').toLowerCase();
        return ['docx', 'pdf'].includes(normalized) ? normalized : 'docx';
    }),
    sanitizeTextMock: vi.fn((value) => String(value ?? '').replace(/[<>]/g, '')),
}));

vi.mock('./api.core', () => ({
    API_BASE_URL: 'http://localhost:8000',
    CHUNK_SIZE_BYTES: 5 * 1024 * 1024,
    CHUNK_UPLOAD_THRESHOLD_BYTES: 10 * 1024 * 1024,
    fetchWithAuth: fetchWithAuthMock,
    fetchWithRetry: fetchWithRetryMock,
    getAuthorizedHeaders: getAuthorizedHeadersMock,
    getFriendlyErrorMessage: vi.fn(({ fallbackMessage = 'Request failed.' } = {}) => fallbackMessage),
    normalizeExportFormat: normalizeExportFormatMock,
    sanitizeText: sanitizeTextMock,
}));

import {
    downloadExport,
    downloadFile,
    uploadChunked,
    uploadDocument,
} from './api.documents';

describe('api.documents', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        getAuthorizedHeadersMock.mockResolvedValue({ Authorization: 'Bearer test' });

        globalThis.URL.createObjectURL = vi.fn(() => 'blob:test-url');
        globalThis.URL.revokeObjectURL = vi.fn();
    });

    it('uploads a document with sanitized template and options', async () => {
        fetchWithAuthMock.mockResolvedValue({ job_id: 'job-1' });
        const file = new File(['example'], 'paper.docx', {
            type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        });

        await uploadDocument(file, '<b>IEEE</b>', { add_page_numbers: false });

        expect(fetchWithAuthMock).toHaveBeenCalledWith(
            '/api/documents/upload',
            expect.objectContaining({ method: 'POST' })
        );

        const payload = fetchWithAuthMock.mock.calls[0][1].body;
        expect(payload).toBeInstanceOf(FormData);
        expect(payload.get('template')).toBe('bIEEE/b');
        expect(payload.get('add_page_numbers')).toBe('false');
    });

    it('uploads chunked files and reports progress', async () => {
        fetchWithRetryMock.mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'ok' }),
        });

        const onProgress = vi.fn();
        const file = new File([new Uint8Array([1, 2, 3, 4])], 'chunked.docx');
        const result = await uploadChunked(file, {
            chunkSize: 2,
            onProgress,
        });

        expect(fetchWithRetryMock).toHaveBeenCalledTimes(2);
        expect(onProgress).toHaveBeenCalledTimes(2);
        expect(onProgress.mock.calls[1][0].percent).toBe(100);
        expect(result.total_chunks).toBe(2);
    });

    it('returns download URL and cleanup handler', async () => {
        fetchWithRetryMock.mockResolvedValue({
            ok: true,
            blob: async () => new Blob(['document']),
        });

        const download = await downloadFile('job-123', 'pdf');

        expect(download.url).toBe('blob:test-url');
        expect(typeof download.cleanup).toBe('function');

        download.cleanup();
        expect(globalThis.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url');
    });

    it('normalizes export format through downloadExport', async () => {
        fetchWithRetryMock.mockResolvedValue({
            ok: true,
            blob: async () => new Blob(['document']),
        });

        await downloadExport('job-456', 'LATEX');

        expect(normalizeExportFormatMock).toHaveBeenCalledWith('LATEX');
        expect(fetchWithRetryMock.mock.calls[0][0]).toContain('format=docx');
    });
});
