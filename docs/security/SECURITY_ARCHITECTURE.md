# Security Architecture

AIForge operates under a **Zero-Trust Architecture**. Agents are treated as untrusted, potentially compromised entities. Every action taken by an LLM is assumed to be an injection attack until proven otherwise.

## Defense in Depth Strategy

### 1. Perimeter Defense (API Gateway Layer)
*   **TLS 1.3:** Enforced universally.
*   **Rate Limiting:** IP-based and Tenant-based rate limits enforced via Redis.
*   **Authentication:** Stateless JWTs.

### 2. Application Defense (FastAPI Layer)
*   **Input Validation:** Pydantic strictly types all incoming JSON. Unexpected fields are stripped.
*   **SQL Injection:** Mitigated via SQLAlchemy ORM parameterized queries.
*   **Cross-Tenant Leakage:** Mitigated via hardcoded row-level security (`tenant_id`) in the `CRUDBase`.

### 3. AI Defense (LangGraph Layer)
*   **Prompt Injection Protection:** The system does not attempt to "filter" prompt injections using heuristics (which are easily bypassed). Instead, the system limits the *blast radius* of an injection.
*   **Blast Radius Limitation:** Agent execution environments have no access to the host file system or root database credentials.
*   **Human-In-The-Loop (HITL):** If a Prompt Injection successfully commands the LLM to execute a destructive tool (e.g., `DropTablesTool` or `SendSpamEmailTool`), the `interrupt_before` hook physically stops the Python thread and demands a JWT-signed API approval from an `Approver` role before executing the API request.

### 4. Privacy & Data Masking (Observability Layer)
*   **PII Scrubbing:** The `AIForgeTracer` runs a regex engine over every string passed to and from the LLM. Emails, Credit Cards, and SSNs are replaced with `[REDACTED]`. This ensures the Postgres database never stores plain-text customer PII in the `inputs` or `outputs` columns.

## Compliance Considerations
*   **SOC2 / HIPAA:** The PII scrubber and immutable HITL audit logs (`approval_tickets`) are designed specifically to ease SOC2 compliance audits regarding autonomous AI actions.
