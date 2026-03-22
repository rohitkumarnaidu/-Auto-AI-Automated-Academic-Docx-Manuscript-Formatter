import { useCallback } from 'react';
import { getSynthesisEventsEndpoint } from '../services/api.synthesis';
import { useSessionEventStream } from './useSessionEventStream';

export function useSynthesisSessionStream(sessionId) {
    const getEventsUrl = useCallback(
        (id) => getSynthesisEventsEndpoint(id),
        []
    );
    return useSessionEventStream(sessionId, getEventsUrl, 'useSynthesisSessionStream');
}
