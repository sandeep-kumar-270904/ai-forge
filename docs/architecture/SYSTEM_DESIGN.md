# System Design & Scalability

This document outlines the architectural strategies employed by AIForge to achieve high availability, fault tolerance, and horizontal scalability for enterprise AI workloads.

## Scalability Strategy

### Horizontal Scaling (Stateless API)
The core FastAPI application (`/app`) is entirely stateless. Authentication relies on JWTs, and all workflow state is externalized to PostgreSQL. The application can be scaled horizontally by increasing Kubernetes Pod replicas behind an Ingress controller.

### Asynchronous I/O
AIForge is built on Python's `asyncio` framework. Because LLM API requests are heavily I/O-bound (often taking 5-30 seconds), async execution ensures that worker threads are not blocked waiting for network responses, allowing a single Uvicorn worker to handle thousands of concurrent LLM requests.

### Database Scaling
*   **Connection Pooling:** As FastAPI pods scale horizontally, Postgres connections will exhaust. AIForge assumes deployment alongside `PgBouncer` (transaction pooling mode) to manage connection limits efficiently.
*   **Read Replicas (Future):** The `CRUDBase` class is structured to support routing read queries to a replica and write queries to the primary, though this is not implemented in the MVP.

## Reliability & Availability

### Model Gateway Failover
Relying on a single LLM provider is a critical point of failure. The `ModelGateway` implements automated failover:
1.  Attempt generation via Primary Provider (e.g., OpenAI).
2.  On `5xx` error or timeout, catch exception.
3.  Instantiate Secondary Provider (e.g., Anthropic) with identical payload.
4.  Execute fallback.

### Rate Limiting & Queue Strategy
*   **API Rate Limiting:** Enforced via `fastapi-limiter` backed by Redis to protect the internal database from DoS attacks.
*   **Queueing (Evaluation Framework):** Currently, the evaluation framework uses `BackgroundTasks`. **(CRITICAL DEBT):** This is insufficient for high availability. The design mandates a transition to a distributed task queue (e.g., Celery or ARQ) backed by Redis to ensure evaluation tasks are persisted and retried if an API pod crashes.

## Capacity Planning & Latency Assumptions

### Throughput Assumptions
*   **API Layer:** Expected to handle 5,000 requests per second (RPS) per replica for standard CRUD operations.
*   **LLM Layer:** Throughput is strictly bottlenecked by third-party provider Rate Limits (TPM/RPM). The gateway must buffer or backoff when external limits are reached.

### Latency Assumptions
*   **DB Reads/Writes:** < 10ms.
*   **Redis Caching:** < 2ms.
*   **LLM Inference:** 500ms to 30,000ms (highly variable).

## Cache Strategy
AIForge utilizes Redis for **Semantic Caching**. 
Instead of hashing exact strings, the caching layer hashes the deterministic parameters of the request (model, temperature, prompt). If an exact match is found within the TTL window, the cached response is served, completely bypassing the external LLM API. This drastically reduces latency and API costs for repetitive workflows.

## Cost Considerations
LLM token usage is the primary cost driver. AIForge mitigates this via:
1.  **Aggressive Redis Caching:** (See Cache Strategy).
2.  **Swarm `max_loops`:** Strict integer limits on LangGraph cycles to prevent infinite agent generation loops.
3.  **Token Accounting:** The `AgentSpan` telemetry records exact `prompt_tokens` and `completion_tokens` per request, allowing for granular tenant billing and cost-alerting dashboards.
