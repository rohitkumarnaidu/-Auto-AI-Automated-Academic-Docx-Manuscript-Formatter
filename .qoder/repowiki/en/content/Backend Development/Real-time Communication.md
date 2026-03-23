# Real-time Communication

<cite>
**Referenced Files in This Document**
- [events.py](file://backend/app/realtime/events.py)
- [pubsub.py](file://backend/app/realtime/pubsub.py)
- [stream.py](file://backend/app/routers/stream.py)
- [preview.py](file://backend/app/routers/preview.py)
- [orchestrator.py](file://backend/app/pipeline/orchestrator.py)
- [prometheus_metrics.py](file://backend/app/middleware/prometheus_metrics.py)
- [redis_cache.py](file://backend/app/cache/redis_cache.py)
- [settings.py](file://backend/app/config/settings.py)
- [serialization.py](file://backend/app/utils/serialization.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document explains the real-time communication systems powering live status updates, progress tracking, and collaborative features. It covers:
- Server-Sent Events (SSE) for long-lived server-to-client updates
- WebSocket support for bidirectional live collaboration
- Redis pub/sub for scalable event distribution across instances
- Event modeling and serialization
- Connection lifecycle, fallbacks, and resilience
- Monitoring and metrics for SSE and WebSocket connections
- Caching strategies for real-time data
- Security and rate-limiting considerations

## Project Structure
The real-time stack spans configuration, event modeling, pub/sub, streaming endpoints, WebSocket routes, orchestration, and metrics.

```mermaid
graph TB
subgraph "Configuration"
S["settings.py"]
end
subgraph "Real-time Core"
E["events.py"]
P["pubsub.py"]
end
subgraph "Streaming"
ST["stream.py"]
ORCH["orchestrator.py"]
end
subgraph "WebSocket"
PV["preview.py"]
end
subgraph "Metrics"
M["prometheus_metrics.py"]
end
subgraph "Caching"
RC["redis_cache.py"]
end
S --> E
S --> P
S --> RC
E --> P
P --> ST
P --> PV
ORCH --> ST
M --> ST
M --> PV
```

**Diagram sources**
- [settings.py:156-174](file://backend/app/config/settings.py#L156-L174)
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)
- [stream.py:24-95](file://backend/app/routers/stream.py#L24-L95)
- [preview.py:25-201](file://backend/app/routers/preview.py#L25-L201)
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [prometheus_metrics.py:98-214](file://backend/app/middleware/prometheus_metrics.py#L98-L214)
- [redis_cache.py:10-102](file://backend/app/cache/redis_cache.py#L10-L102)

**Section sources**
- [settings.py:156-174](file://backend/app/config/settings.py#L156-L174)
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)
- [stream.py:24-95](file://backend/app/routers/stream.py#L24-L95)
- [preview.py:25-201](file://backend/app/routers/preview.py#L25-L201)
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [prometheus_metrics.py:98-214](file://backend/app/middleware/prometheus_metrics.py#L98-L214)
- [redis_cache.py:10-102](file://backend/app/cache/redis_cache.py#L10-L102)

## Core Components
- RealtimeEvent and event factory: define the canonical event shape and serialization for transport.
- RedisPubSub: async pub/sub abstraction with Redis-backed channels and in-memory fallback.
- SSE router: exposes a streaming endpoint per job and emits standardized events.
- WebSocket route: supports live preview collaboration with ping/pong and incremental rendering.
- Orchestrator integration: emits SSE events during pipeline stages.
- Prometheus metrics: tracks active SSE and WebSocket connections.
- Redis cache: provides caching for expensive operations to reduce latency and load.

**Section sources**
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)
- [stream.py:32-95](file://backend/app/routers/stream.py#L32-L95)
- [preview.py:61-128](file://backend/app/routers/preview.py#L61-L128)
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [prometheus_metrics.py:98-214](file://backend/app/middleware/prometheus_metrics.py#L98-L214)
- [redis_cache.py:10-102](file://backend/app/cache/redis_cache.py#L10-L102)

## Architecture Overview
The system uses Redis pub/sub to fan out real-time events to clients subscribed via SSE or WebSocket. The orchestrator publishes status updates, which downstream consumers (UIs) receive through persistent connections. Metrics track connection health and throughput.

```mermaid
sequenceDiagram
participant Client as "Client"
participant SSE as "SSE Router (stream.py)"
participant PS as "RedisPubSub (pubsub.py)"
participant Orchestrator as "Pipeline Orchestrator (orchestrator.py)"
Orchestrator->>SSE : emit_event(job_id, "status_update", data)
SSE->>PS : publish("job : {job_id}", event)
Client->>SSE : GET /api/stream/{job_id}
SSE->>PS : subscribe("job : {job_id}")
PS-->>SSE : event stream
SSE-->>Client : EventSource events
```

**Diagram sources**
- [stream.py:73-95](file://backend/app/routers/stream.py#L73-L95)
- [pubsub.py:55-109](file://backend/app/realtime/pubsub.py#L55-L109)
- [orchestrator.py:159-165](file://backend/app/pipeline/orchestrator.py#L159-L165)

## Detailed Component Analysis

### Event Model and Serialization
- RealtimeEvent captures event_type, correlation identifiers (job_id, session_id), stage, progress, timestamp, and payload.
- make_event constructs canonical events, injects request_id context, and serializes timestamps for transport.

```mermaid
classDiagram
class RealtimeEvent {
+string event_type
+string? job_id
+string? session_id
+string? request_id
+string? stage
+int? progress
+datetime timestamp
+dict payload
}
class EventsModule {
+make_event(event_type, **kwargs) dict
}
EventsModule --> RealtimeEvent : "creates"
```

**Diagram sources**
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)

**Section sources**
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)
- [serialization.py:13-67](file://backend/app/utils/serialization.py#L13-L67)

### Redis Pub/Sub Abstraction
- RedisPubSub manages Redis availability per event loop, with a lock to avoid race conditions.
- publish attempts Redis publish; on failure, falls back to in-memory queues keyed by channel.
- subscribe connects to Redis pubsub or yields from in-memory queues; ensures cleanup on exit.

```mermaid
flowchart TD
Start(["publish(channel, event)"]) --> GetRedis["_get_redis()"]
GetRedis --> HasRedis{"Redis available?"}
HasRedis --> |Yes| TryPublish["client.publish(channel, json)"]
TryPublish --> PublishOK{"Success?"}
PublishOK --> |Yes| Done(["Done"])
PublishOK --> |No| Fallback["Set force_fallback=true"]
HasRedis --> |No| Fallback
Fallback --> InMemory["Enqueue to fallback_channels[channel]"]
subgraph "subscribe(channel)"
SubStart(["subscribe(channel)"]) --> GetSubRedis["_get_redis()"]
GetSubRedis --> SubHasRedis{"Redis available?"}
SubHasRedis --> |Yes| PubSub["pubsub.subscribe(channel)"]
PubSub --> Listen["listen() loop"]
Listen --> Decode["json.loads(data)"]
Decode --> Yield["yield event"]
Yield --> Cleanup["unsubscribe/close"]
SubHasRedis --> |No| MakeQueue["ensure asyncio.Queue"]
MakeQueue --> LoopGet["await queue.get()"]
LoopGet --> Yield
end
```

**Diagram sources**
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)

**Section sources**
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)
- [settings.py:156-174](file://backend/app/config/settings.py#L156-L174)

### Server-Sent Events (SSE)
- The SSE endpoint streams job-specific events to authenticated clients.
- It sends an initial “connected” event, then forwards Redis-published events until the client disconnects.
- Metrics track SSE connection open/close.

```mermaid
sequenceDiagram
participant Client as "Client"
participant Router as "SSE Router (stream.py)"
participant PS as "RedisPubSub (pubsub.py)"
participant Metrics as "MetricsManager"
Client->>Router : GET /api/stream/{job_id}
Router->>Metrics : sse_connection_open()
Router->>PS : subscribe("job : {job_id}")
PS-->>Router : event stream
Router-->>Client : event "connected"
Router-->>Client : event "{event_type}" (json data)
Client-->>Router : disconnect
Router->>Metrics : sse_connection_closed()
```

**Diagram sources**
- [stream.py:32-71](file://backend/app/routers/stream.py#L32-L71)
- [pubsub.py:79-119](file://backend/app/realtime/pubsub.py#L79-L119)
- [prometheus_metrics.py:198-205](file://backend/app/middleware/prometheus_metrics.py#L198-L205)

**Section sources**
- [stream.py:32-95](file://backend/app/routers/stream.py#L32-L95)
- [prometheus_metrics.py:98-214](file://backend/app/middleware/prometheus_metrics.py#L98-L214)

### WebSocket Live Preview
- WebSocket route accepts sessions with validated IDs, maintains a session-to-websocket set, and forwards Redis events to clients.
- Heartbeat pings keep connections alive; client messages trigger live preview rendering and push updates back to the session channel.
- Metrics track WebSocket connection open/close.

```mermaid
sequenceDiagram
participant Client as "Client"
participant WS as "WebSocket Route (preview.py)"
participant PS as "RedisPubSub (pubsub.py)"
participant Metrics as "MetricsManager"
Client->>WS : Connect /api/v1/ws/preview/{sessionId}
WS->>Metrics : ws_connection_open()
WS->>PS : subscribe("preview : {sessionId}")
PS-->>WS : event stream
WS-->>Client : send_json(payload)
Client->>WS : send_json({content, templateId, seq, checksum})
WS->>WS : render_preview()
WS->>PS : publish("preview : {sessionId}", event)
Client-->>WS : disconnect
WS->>Metrics : ws_connection_closed()
```

**Diagram sources**
- [preview.py:78-128](file://backend/app/routers/preview.py#L78-L128)
- [pubsub.py:79-119](file://backend/app/realtime/pubsub.py#L79-L119)
- [prometheus_metrics.py:207-214](file://backend/app/middleware/prometheus_metrics.py#L207-L214)

**Section sources**
- [preview.py:61-128](file://backend/app/routers/preview.py#L61-L128)
- [prometheus_metrics.py:108-116](file://backend/app/middleware/prometheus_metrics.py#L108-L116)

### Pipeline Integration and Event Emission
- The orchestrator updates processing status and emits SSE events for real-time UI feedback.
- It coordinates Supabase updates and SSE publishing to keep clients informed of progress and outcomes.

```mermaid
flowchart TD
A["Orchestrator Stage"] --> B["Upsert ProcessingStatus in DB"]
B --> C["Update Parent Document"]
C --> D["emit_event(job_id, 'status_update', data)"]
D --> E["SSE Router forwards to subscribers"]
```

**Diagram sources**
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [stream.py:73-95](file://backend/app/routers/stream.py#L73-L95)

**Section sources**
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [stream.py:73-95](file://backend/app/routers/stream.py#L73-L95)

### Caching Strategies for Real-time Data
- RedisCache provides optional caching for expensive operations (e.g., LLM results, GROBID results) with TTL.
- When Redis is disabled or unavailable, the cache layer gracefully disables itself and continues without caching.

```mermaid
classDiagram
class RedisCache {
+get_grobid_result(file_content) dict?
+set_grobid_result(file_content, result, ttl)
+get_llm_result(cache_key) str?
+set_llm_result(cache_key, text, ttl)
}
```

**Diagram sources**
- [redis_cache.py:10-102](file://backend/app/cache/redis_cache.py#L10-L102)

**Section sources**
- [redis_cache.py:10-102](file://backend/app/cache/redis_cache.py#L10-L102)
- [settings.py:156-174](file://backend/app/config/settings.py#L156-L174)

## Dependency Analysis
- Configuration: settings controls Redis enablement and URLs, impacting pub/sub availability.
- Eventing: events.py defines the event contract; stream.py and preview.py depend on it.
- Pub/Sub: stream.py and preview.py depend on pubsub.py; orchestrator depends on stream.py’s emit_event.
- Metrics: prometheus_metrics.py is invoked by SSE and WebSocket routes to track connections.
- Serialization: serialization.py ensures payloads are JSON-safe for transport.

```mermaid
graph LR
Settings["settings.py"] --> PubSub["pubsub.py"]
Settings --> RedisCache["redis_cache.py"]
Events["events.py"] --> Stream["stream.py"]
Events --> Preview["preview.py"]
PubSub --> Stream
PubSub --> Preview
Orchestrator["orchestrator.py"] --> Stream
Metrics["prometheus_metrics.py"] --> Stream
Metrics --> Preview
Serialization["serialization.py"] --> Events
```

**Diagram sources**
- [settings.py:156-174](file://backend/app/config/settings.py#L156-L174)
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)
- [stream.py:24-95](file://backend/app/routers/stream.py#L24-L95)
- [preview.py:25-201](file://backend/app/routers/preview.py#L25-L201)
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [prometheus_metrics.py:98-214](file://backend/app/middleware/prometheus_metrics.py#L98-L214)
- [serialization.py:13-67](file://backend/app/utils/serialization.py#L13-L67)

**Section sources**
- [settings.py:156-174](file://backend/app/config/settings.py#L156-L174)
- [events.py:9-34](file://backend/app/realtime/events.py#L9-L34)
- [pubsub.py:18-120](file://backend/app/realtime/pubsub.py#L18-L120)
- [stream.py:24-95](file://backend/app/routers/stream.py#L24-L95)
- [preview.py:25-201](file://backend/app/routers/preview.py#L25-L201)
- [orchestrator.py:115-165](file://backend/app/pipeline/orchestrator.py#L115-L165)
- [prometheus_metrics.py:98-214](file://backend/app/middleware/prometheus_metrics.py#L98-L214)
- [serialization.py:13-67](file://backend/app/utils/serialization.py#L13-L67)

## Performance Considerations
- Redis pub/sub scalability: Redis-backed channels distribute events across workers/processes; fallback to in-memory queues avoids single-point-of-failure but limits cross-instance delivery.
- SSE/WS concurrency: Metrics expose active connections and totals; monitor for spikes and adjust autoscaling accordingly.
- Payload size: Keep event payload minimal; use serialization helpers to ensure safe transport.
- Caching: Use RedisCache for expensive reads to reduce upstream load and latency.
- Timeouts and heartbeats: WebSocket routes implement periodic ping to detect dead peers; SSE checks disconnection to free resources promptly.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Redis connectivity failures:
  - Symptom: Redis warnings and fallback to in-memory queues.
  - Action: Verify REDIS_URL/REDIS_ENABLED; ensure Redis is reachable; confirm ping succeeds.
- SSE disconnects:
  - Symptom: Client stops receiving updates.
  - Action: Confirm client-side EventSource reconnects; check is_disconnected checks in SSE route.
- WebSocket disconnects:
  - Symptom: Session ends unexpectedly.
  - Action: Inspect heartbeat intervals and client ping/pong; verify session ID validation and cleanup paths.
- Metrics anomalies:
  - Symptom: Active connection counters inconsistent.
  - Action: Review metrics middleware invocations for SSE/WS open/close.

**Section sources**
- [pubsub.py:40-53](file://backend/app/realtime/pubsub.py#L40-L53)
- [stream.py:48-57](file://backend/app/routers/stream.py#L48-L57)
- [preview.py:61-76](file://backend/app/routers/preview.py#L61-L76)
- [prometheus_metrics.py:198-214](file://backend/app/middleware/prometheus_metrics.py#L198-L214)

## Conclusion
The system combines Redis pub/sub, SSE, and WebSocket to deliver robust, scalable real-time updates. Events are modeled consistently, published from the orchestrator, and consumed by clients through durable connections. RedisCache reduces latency for expensive operations, while Prometheus metrics provide operational visibility. Proper configuration and monitoring ensure resilience under high concurrency.