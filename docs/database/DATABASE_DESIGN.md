# Database Design

AIForge utilizes PostgreSQL as its primary persistent storage, specifically leveraging its JSONB capabilities to handle unstructured AI payload data alongside strict relational constraints.

## Architecture Paradigm
*   **Migrations:** Managed strictly via `alembic`. No manual DDL is permitted.
*   **Driver:** `asyncpg` for non-blocking asynchronous database operations.
*   **ORM:** SQLAlchemy 2.0 (using `DeclarativeBase`).

## Key Tables & Design Decisions

### 1. Observability (`agent_runs` & `agent_spans`)
*   **Pattern:** Hierarchical Tracing.
*   **Design:** `agent_spans` contains a `parent_span_id` creating a recursive tree of LLM operations (e.g., Graph -> Chain -> Tool -> LLM Call).
*   **JSONB Usage:** `inputs`, `outputs`, and `metadata` are stored as `JSONB` to accommodate widely varying provider payload schemas (OpenAI vs Anthropic).

### 2. Prompt Management (`prompts`, `prompt_versions`, `prompt_deployments`)
*   **Pattern:** Append-Only Immutability.
*   **Design:** To prevent "Prompt Drift", a `prompt` can never be edited. Instead, a new `prompt_version` is created. To go live, a version must be attached to a `prompt_deployment`.

### 3. Human-In-The-Loop (`approval_tickets`)
*   **Pattern:** State Suspension.
*   **Design:** `state_snapshot` (JSONB) saves the exact LangGraph memory object at the time of interruption. When approved, this state is re-injected into the checkpointer.

## Concurrency & Locking
*   **Optimistic Locking:** Utilized on `approval_tickets` to prevent two "Approvers" from simultaneously resolving the same ticket. If a ticket status is no longer `pending`, the transaction rolls back.
