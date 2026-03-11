import { useQuery } from '@tanstack/react-query';

import {
    getDocuments,
    getJobStatus,
    mapDocumentRecord,
    normalizeDocumentsParams,
} from './api.documents';

import {
    getMetricsHealth,
    getMetricsDashboard,
} from './api.metrics';

export const useDocuments = (params = {}, queryOptions = {}) => {
    const normalizedParams = normalizeDocumentsParams(params);

    return useQuery({
        queryKey: ['documents', normalizedParams],
        queryFn: () => getDocuments(normalizedParams),
        select: (data) => ({
            ...data,
            documents: Array.isArray(data?.documents)
                ? data.documents.map(mapDocumentRecord)
                : [],
        }),
        ...queryOptions,
    });
};

export const useDocumentStatus = (jobId, queryOptions = {}) => (
    useQuery({
        queryKey: ['document-status', jobId],
        queryFn: ({ signal }) => getJobStatus(jobId, { signal }),
        ...queryOptions,
        enabled: Boolean(jobId) && (queryOptions.enabled ?? true),
    })
);

export const useMetricsHealth = (queryOptions = {}) => (
    useQuery({
        queryKey: ['metrics-health'],
        queryFn: () => getMetricsHealth(),
        retry: false,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
        ...queryOptions,
    })
);

export const useMetricsDashboard = (queryOptions = {}) => (
    useQuery({
        queryKey: ['metrics-dashboard'],
        queryFn: () => getMetricsDashboard(),
        retry: false,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
        ...queryOptions,
    })
);
