# Observability & Alerting

## Application Telemetry
AIForge generates high-fidelity tracing via the `AIForgeTracer` callback handler.
*   **Traces:** Represent an entire `AgentRun` (e.g., a swarm invocation).
*   **Spans:** Represent individual sub-components (e.g., an LLM call, a tool execution) nested inside the trace.

## Alerting Procedures (Proposed)
Because there is no infrastructure-as-code present, the following Datadog/Prometheus alerts are strictly theoretical and must be implemented by the DevOps team.

1.  **Error Rate Alert:** Trigger if `500 Internal Server Error` > 1% of total requests over 5 minutes.
2.  **Latency Alert:** Trigger if `p99` latency on `/api/v1/swarms/*/invoke` > 30 seconds.
3.  **Cost Alert:** Trigger if aggregate `prompt_tokens` across all tenants exceeds `1,000,000` within a 1-hour window.
4.  **Loop Alert:** Trigger if a Swarm hits its `max_loops` threshold > 5 times in an hour (indicates a severely hallucinating agent).
