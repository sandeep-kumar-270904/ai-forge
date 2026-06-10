# Business Rules

AIForge enforces specific domain logic rules across the platform.

1.  **Prompt Immutability:** A `Prompt` object can have its `description` changed, but its `template_string` cannot be altered. A new `PromptVersion` must be created.
2.  **Tenant Isolation:** A User belonging to `Tenant A` cannot view, edit, or invoke a Swarm belonging to `Tenant B`, even if they know the UUID. The API will return a `404 Not Found` (to mask existence) or `403 Forbidden`.
3.  **HITL Non-Repudiation:** Once an `ApprovalTicket` is resolved (Approved/Rejected), it is permanently locked. A second attempt to resolve it will throw a `400 Bad Request`.
4.  **Loop Protection:** A Swarm cannot run infinitely. The `max_loops` constraint acts as a hard circuit breaker. If breached, the system forces a termination and returns the final state to the user.
