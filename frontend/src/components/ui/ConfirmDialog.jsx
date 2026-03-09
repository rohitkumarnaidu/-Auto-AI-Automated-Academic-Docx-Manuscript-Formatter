'use client';

import { forwardRef } from 'react';
import Button from './Button';

const cx = (...classes) => classes.filter(Boolean).join(' ');

const ConfirmDialog = forwardRef(function ConfirmDialog(
    {
        className,
        open = false,
        title = 'Are you sure?',
        description,
        confirmLabel = 'Confirm',
        cancelLabel = 'Cancel',
        onConfirm,
        onCancel,
        isLoading = false,
        danger = true,
        ...props
    },
    ref
) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-slate-950/50" onClick={onCancel} />
            <div
                ref={ref}
                role="dialog"
                aria-modal="true"
                className={cx('relative w-full max-w-md rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-2xl', className)}
                {...props}
            >
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
                {description ? (
                    <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{description}</p>
                ) : null}
                <div className="mt-5 flex justify-end gap-2">
                    <Button variant="secondary" onClick={onCancel} disabled={isLoading}>{cancelLabel}</Button>
                    <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm} loading={isLoading}>{confirmLabel}</Button>
                </div>
            </div>
        </div>
    );
});

export default ConfirmDialog;
