# Threat Model

A lightweight STRIDE threat model specific to AIForge's Multi-Agent architecture.

## 1. Spoofing
*   **Threat:** A malicious user spoofs another tenant's JWT.
*   **Mitigation:** JWTs are signed with a highly secure `SECRET_KEY`. Keys must be rotated every 90 days.

## 2. Tampering
*   **Threat:** An attacker tampers with the LangGraph state object (`MessagesState`) in Postgres to alter an agent's memory.
*   **Mitigation:** Database access is strictly firewall-protected. Application-level state writes are validated by the `PostgresSaver` checkpointer.

## 3. Repudiation
*   **Threat:** An operator approves a destructive HITL action and later denies doing it.
*   **Mitigation:** The `approval_tickets` table captures the `user_id` of the approver and the exact timestamp. These records are immutable.

## 4. Information Disclosure
*   **Threat:** An LLM hallucinates and outputs internal system prompts or another user's PII.
*   **Mitigation:** `AIForgeTracer` scrubs standard PII. **(GAP):** The system does not currently prevent the disclosure of internal System Prompts if the LLM is jailbroken. Recommended fix: Implement `LlamaGuard` output filtering.

## 5. Denial of Service (DoS)
*   **Threat:** A recursive swarm topology loops infinitely, burning CPU, Postgres IOPS, and API credits.
*   **Mitigation:** The `Swarm` schema enforces a strict `max_loops` integer. The `SwarmExecutor` physically breaks the while-loop if `loop_count >= max_loops`, regardless of the LLM's desire to continue.

## 6. Elevation of Privilege
*   **Threat:** An attacker uses a standard `Viewer` JWT to access `/api/v1/swarms/{id}/invoke`.
*   **Mitigation:** RBAC `Depends(require_role("Operator"))` prevents unauthorized execution.
