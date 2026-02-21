export const STATUS = {
    PENDING: 'PENDING',
    PROCESSING: 'PROCESSING',
    COMPLETED: 'COMPLETED',
    COMPLETED_WITH_WARNINGS: 'COMPLETED_WITH_WARNINGS',
    FAILED: 'FAILED',
};

export function isCompleted(status) {
    return status?.toUpperCase() === STATUS.COMPLETED
        || status?.toUpperCase() === STATUS.COMPLETED_WITH_WARNINGS;
}

export function isProcessing(status) {
    return status?.toUpperCase() === STATUS.PROCESSING;
}

export function isFailed(status) {
    return status?.toUpperCase() === STATUS.FAILED;
}
