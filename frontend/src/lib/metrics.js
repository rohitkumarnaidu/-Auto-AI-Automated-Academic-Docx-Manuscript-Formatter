import { Registry, Histogram, collectDefaultMetrics } from 'prom-client';

const registry = new Registry();

// Add default metrics (CPU, Memory, etc.)
collectDefaultMetrics({ register: registry, prefix: 'scholarform_frontend_' });

// Request Duration Histogram
export const httpRequestDurationMicroseconds = new Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in microseconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10], // seconds
    registers: [registry],
});

// Cache for metrics
export default registry;
