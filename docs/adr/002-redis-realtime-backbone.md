# 002 - Redis Realtime Backbone

Status: Accepted

Context: The platform needs real-time streaming updates and low-latency pub/sub for SSE and WebSocket connections.

Decision: Use Redis as the realtime backbone for pub/sub and queue depth monitoring, with in-memory fallbacks when Redis is unavailable.

Consequences: Production environments must provision Redis for full realtime features, and monitoring includes Redis health and queue depth metrics.
