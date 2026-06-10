# Data Lifecycle & Pruning

AIForge generates a massive amount of telemetry data per second during active Swarm execution. If left unmanaged, the database will exhaust its disk space and memory buffer cache, leading to severe system degradation.

## Data Classification

| Data Type | Tables | Volume | Retention Requirement |
| :--- | :--- | :--- | :--- |
| **System State** | `tenants`, `users` | Low | Indefinite |
| **AI Assets** | `prompts`, `swarms` | Medium | Indefinite (Immutability rule) |
| **Telemetry** | `agent_runs`, `agent_spans` | EXTREMELY HIGH | 90 Days |
| **Audit Logs**| `approval_tickets` | Medium | 7 Years (Compliance) |

## Implementation Gap: Missing Pruning Strategy
**STATUS: CRITICAL RISK**
*Currently, there is no automated pruning strategy implemented in the codebase.*

### Recommended Mitigation (Phase 2 Roadmap)
1.  **Table Partitioning:** The `agent_spans` table MUST be refactored to use PostgreSQL declarative partitioning by `created_at` (e.g., monthly partitions).
2.  **Cron Jobs:** A background worker must execute `DROP TABLE agent_spans_yYYYYmMM` for partitions older than 90 days. Deleting partitions is an `O(1)` operation and does not lock the primary table or generate excessive WAL files, unlike a massive `DELETE FROM` query.

## Backup Strategy
*   **Database:** PostgreSQL WAL (Write-Ahead Logging) archiving must be enabled via `pgBackRest` or a managed cloud equivalent (AWS RDS Automated Backups) to ensure Point-In-Time-Recovery (PITR).
*   **RPO (Recovery Point Objective):** 5 minutes.
*   **RTO (Recovery Time Objective):** 2 hours.
