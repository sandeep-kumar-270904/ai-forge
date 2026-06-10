# API Reference

AIForge exposes a RESTful API built on FastAPI. Full OpenAPI specifications are available interactively at `/docs` or `/redoc` when running the server locally.

## Global Headers
*   `Authorization`: `Bearer <token>` (Required for all endpoints except `/health` and `/api/v1/auth/login`)
*   `Content-Type`: `application/json`

## Rate Limits
*   All `/api/v1/*` endpoints are rate-limited to 100 requests per minute per IP using Redis `fastapi-limiter`.
*   A `429 Too Many Requests` is returned if exceeded.

## Core Endpoints

### 1. Authentication
*   **POST** `/api/v1/auth/login`
    *   **Body:** OAuth2 Password Request Form (`username`, `password`)
    *   **Response:** `{ "access_token": "jwt", "token_type": "bearer" }`

### 2. Multi-Agent Swarms
*   **POST** `/api/v1/swarms/{swarm_id}/invoke`
    *   **Description:** Triggers a LangGraph multi-agent swarm.
    *   **Body:** `{ "input_message": "string" }`
    *   **Response:** `{ "status": "completed", "loops_executed": int, "final_state": dict }`

### 3. Human-In-The-Loop (HITL)
*   **GET** `/api/v1/hitl/tickets/pending`
    *   **Description:** Retrieves all paused execution graphs awaiting human approval for the current tenant.
*   **POST** `/api/v1/hitl/tickets/{ticket_id}/resolve`
    *   **Body:** `{ "decision": "approved|rejected", "state_overrides": dict }`
    *   **Description:** Resumes the LangGraph checkpointer.

### 4. Observability
*   **GET** `/api/v1/observability/runs`
    *   **Description:** Paginated list of all Agent Executions (Run objects).
*   **GET** `/api/v1/observability/runs/{run_id}/spans`
    *   **Description:** Deep telemetry trace of LLM calls, token usage, and latency.

## Error Handling
AIForge implements standard HTTP error codes:
*   `400 Bad Request`: Invalid parameters.
*   `401 Unauthorized`: Missing or expired JWT.
*   `403 Forbidden`: Cross-tenant data access attempt or insufficient RBAC role.
*   `404 Not Found`: Entity does not exist.
*   `422 Unprocessable Entity`: Pydantic validation failure.
*   `500 Internal Server Error`: Unhandled exception (triggers PagerDuty).
