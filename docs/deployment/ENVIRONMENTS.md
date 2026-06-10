# Environment Promotion

AIForge supports standard multi-environment software development lifecycles.

## Environment Definitions

| Environment | Purpose | Database | LLM Models |
| :--- | :--- | :--- | :--- |
| **Local** | Developer iteration. | Dockerized Postgres | `gpt-4o-mini` (Cost saving) |
| **Staging** | QA and automated evaluation runs. | Managed RDS | `gpt-4o` / `claude-3` |
| **Production** | Live customer traffic. | Multi-AZ RDS | `gpt-4o` / `claude-3-opus` |

## Data Sanitization
Database dumps from Production **MUST NOT** be restored into Staging without running a scrubbing script to completely drop the `agent_spans` and `agent_runs` tables. Even with the `AIForgeTracer` masking PII, raw LLM interactions are considered highly confidential and should never reside in lower environments.
