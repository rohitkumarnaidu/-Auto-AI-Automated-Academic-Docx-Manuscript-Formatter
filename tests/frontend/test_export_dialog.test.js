import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ExportDialog from '../../frontend/src/components/ExportDialog';

describe('ExportDialog', () => {
    it('renders export format selector with DOCX/PDF/JSON options', () => {
        render(
            React.createElement(ExportDialog, {
                isOpen: true,
                onClose: vi.fn(),
                onDownload: vi.fn(),
            })
        );

        const formatSelect = screen.getByTestId('export-format-select');
        expect(formatSelect).toBeTruthy();
        expect(screen.getByRole('option', { name: 'DOCX (.docx)' })).toBeTruthy();
        expect(screen.getByRole('option', { name: 'PDF (.pdf)' })).toBeTruthy();
        expect(screen.getByRole('option', { name: 'JSON (.json)' })).toBeTruthy();
    });

    it('calls onDownload with the selected format when download button is clicked', () => {
        const onDownload = vi.fn();

        render(
            React.createElement(ExportDialog, {
                isOpen: true,
                onClose: vi.fn(),
                onDownload,
            })
        );

        fireEvent.change(screen.getByTestId('export-format-select'), {
            target: { value: 'json' },
        });
        fireEvent.click(screen.getByTestId('export-download-button'));

        expect(onDownload).toHaveBeenCalledWith('json');
    });
});
