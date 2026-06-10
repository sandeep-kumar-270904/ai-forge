# Authorization & RBAC

AIForge enforces two distinct layers of authorization: **Row-Level Tenancy** and **Role-Based Access Control (RBAC)**.

## 1. Row-Level Tenancy (Multi-Tenant Isolation)

Every database table (except global tables like `users` which act as join tables) contains a `tenant_id` foreign key.
The FastAPI dependency injection system extracts the `tenant_id` from the JWT and passes it to the `CRUDBase` class.

**Constraint:** The `CRUDBase` class hardcodes `WHERE tenant_id = :tenant_id` into *every* SQL query. It is mathematically impossible for a developer to accidentally query another tenant's data using the standard ORM methods.

## 2. Role-Based Access Control (RBAC)

Users are assigned specific roles which govern the API endpoints they can execute.

| Role | Permissions |
| :--- | :--- |
| `Viewer` | Can view Observability traces and read-only Dashboards. |
| `Operator` | Can invoke Swarms and trigger Prompts. Cannot modify Prompts. |
| `Approver` | Can resolve HITL (Human-In-The-Loop) Approval Tickets. |
| `AI Engineer`| Can create, version, and deploy Prompts and Swarm Topologies. |
| `Tenant Admin`| Can manage API Keys, manage Users, and view billing data. |

## FastAPI Implementation Example
Roles are enforced at the Router level using FastAPI `Depends`.
```python
@router.post("/hitl/tickets/{id}/resolve")
async def resolve_ticket(
    ticket_id: str,
    current_user: User = Depends(require_role("Approver"))
):
    # Logic executes
```
