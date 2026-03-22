import { useCallback } from 'react';
import { API_BASE_URL } from '../services/api.v1';
import { useSessionEventStream } from './useSessionEventStream';

export function useGeneratorSessionStream(sessionId) {
    const getEventsUrl = useCallback(
        (id) => `${API_BASE_URL}/api/v1/generator/sessions/${id}/events`,
        []
    );
    return useSessionEventStream(sessionId, getEventsUrl, 'useGeneratorSessionStream');
}
