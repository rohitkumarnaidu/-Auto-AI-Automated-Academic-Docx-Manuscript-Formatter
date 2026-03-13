'use client';
import { useState, useEffect, useRef, useCallback } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Simple checksum — avoids importing a full md5 library
function simpleHash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) {
        h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
    }
    return (h >>> 0).toString(16);
}

function getWsUrl(sessionId) {
    // Convert http(s):// → ws(s)://
    const base = API_BASE_URL.replace(/^http/, 'ws');
    return `${base}/api/v1/ws/preview/${sessionId}`;
}

/**
 * useLivePreviewSocket – connects to the backend WebSocket preview endpoint.
 *
 * @param {string} sessionId - UUID for this session
 * @returns {{ html: string, latencyMs: number|null, warnings: string[], isConnected: boolean, isAnalyzing: boolean, sendContent: Function }}
 */
export default function useLivePreviewSocket(sessionId) {
    const [html, setHtml] = useState('');
    const [latencyMs, setLatencyMs] = useState(null);
    const [warnings, setWarnings] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const wsRef = useRef(null);
    const debounceTimerRef = useRef(null);
    const seqRef = useRef(0);
    const backoffRef = useRef(1000);
    const unmountedRef = useRef(false);
    const reconnectTimerRef = useRef(null);
    const sentAtRef = useRef(null);
    const lastContentRef = useRef('');

    // ── Connect ────────────────────────────────────────────────────────────────
    const connect = useCallback(() => {
        if (unmountedRef.current) return;
        if (!sessionId) return;

        const url = getWsUrl(sessionId);
        let ws;
        try {
            ws = new WebSocket(url);
        } catch {
            // Retry on construction failure (e.g. invalid URL in test env)
            reconnectTimerRef.current = setTimeout(connect, backoffRef.current);
            return;
        }
        wsRef.current = ws;

        ws.onopen = () => {
            if (unmountedRef.current) { ws.close(); return; }
            setIsConnected(true);
            backoffRef.current = 1000; // reset backoff on success
        };

        ws.onmessage = (event) => {
            if (unmountedRef.current) return;
            try {
                const msg = JSON.parse(event.data);
                if (msg.html !== undefined) setHtml(msg.html);
                if (msg.warnings !== undefined) setWarnings(msg.warnings || []);
                if (sentAtRef.current) {
                    setLatencyMs(Date.now() - sentAtRef.current);
                    sentAtRef.current = null;
                }
                setIsAnalyzing(false);
            } catch {
                // Ignore malformed frames
            }
        };

        ws.onerror = () => {
            // onclose will handle reconnect
        };

        ws.onclose = () => {
            if (unmountedRef.current) return;
            setIsConnected(false);
            // Exponential backoff: 1s → 2s → 4s → 8s → cap 30s
            const delay = Math.min(backoffRef.current, 30000);
            backoffRef.current = Math.min(delay * 2, 30000);
            reconnectTimerRef.current = setTimeout(connect, delay);
        };
    }, [sessionId]);

    // ── Lifecycle ──────────────────────────────────────────────────────────────
    useEffect(() => {
        unmountedRef.current = false;
        connect();

        return () => {
            unmountedRef.current = true;
            clearTimeout(debounceTimerRef.current);
            clearTimeout(reconnectTimerRef.current);
            if (wsRef.current) {
                wsRef.current.onclose = null; // prevent reconnect on intentional close
                wsRef.current.close();
            }
        };
    }, [connect]);

    // ── sendContent ────────────────────────────────────────────────────────────
    const sendContent = useCallback((content, templateId) => {
        // Detect large paste (>1000 char diff from last known)
        const diff = Math.abs((content?.length || 0) - (lastContentRef.current?.length || 0));
        if (diff > 1000) {
            setIsAnalyzing(true);
            // We'll still debounce normally; the analyzing flag just shows the overlay
        }
        lastContentRef.current = content || '';

        clearTimeout(debounceTimerRef.current);
        debounceTimerRef.current = setTimeout(() => {
            if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
            seqRef.current += 1;
            const payload = {
                content: content || '',
                templateId: templateId || null,
                cursor: null,
                checksum: simpleHash(content || ''),
                seq: seqRef.current,
            };
            sentAtRef.current = Date.now();
            wsRef.current.send(JSON.stringify(payload));
        }, 200);
    }, []);

    return { html, latencyMs, warnings, isConnected, isAnalyzing, sendContent };
}
