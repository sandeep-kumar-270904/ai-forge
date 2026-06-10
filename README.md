# AIForge: Enterprise AI Operating System

*Status: CRITICAL REVIEW REQUIRED*

This document serves as the master engineering reference for the AIForge platform. It is written for Principal Engineers, DevOps Architects, and Security Officers assuming ownership of the system. 


## 1. Executive Summary

### Project Overview
AIForge is an enterprise-grade backend operating system designed to orchestrate, secure, and evaluate complex Multi-Agent AI workflows. Built on an asynchronous microservices architecture, it abstracts the complexities of Large Language Models (LLMs) and provides a deterministic, secure environment for AI business logic.

### Business Problem Being Solved
Integrating LLMs into production results in fragmented codebases, "prompt drift", unpredictable agent behavior, and security vulnerabilities (PII leakage, unauthorized execution). AIForge centralizes these into a unified platform.

### Target Users
*   **Platform Engineers:** Managing infrastructure, rate limits, and API keys.
*   **AI Engineers:** Designing prompt chains, evaluating models, and building swarms.
*   **Security & Compliance:** Auditing telemetry, managing PII, and enforcing HITL authorizations.

### Core Value Proposition
AIForge transforms wrapper scripts into enterprise software, providing out-of-the-box multi-tenant isolation, Maker/Checker deployments, time-travel debugging, and LLM-as-a-Judge evaluations.

### High-Level System Goals
*   **Deterministic Reliability:** Predictable outcomes from stochastic models via checkpointer replays.
*   **Zero-Trust Security:** Row-level tenant isolation and explicit approval for autonomous actions.
*   **Infinite Scalability:** Support thousands of concurrent executions via async task queues.

---

## 2. Product Vision

### Why This Project Exists
The future of enterprise software relies on swarms of specialized, collaborating AI agents. AIForge is the foundational infrastructure layer powering these swarms securely.

### Real-World Use Cases
*   **Autonomous Financial Auditing:** Swarms ingest ledgers, flag anomalies, and route to a human auditor (HITL).
*   **Automated Software Engineering:** Code generation pipelines (Planner -> Coder -> Evaluator).

### Expected Impact
Reduce LLM operational costs by 40% through intelligent routing. Decrease agent-induced security incidents to zero via strict HITL and PII masking.

### Future Direction
Evolution towards a fully autonomous Enterprise Knowledge Graph (RAG) and dynamic swarm topology generation.

---

## 3. Features Overview

### Model Gateway
*   **Purpose:** Centralized router for all LLM API calls.
*   **User Benefit:** Unified token accounting; prevents vendor lock-in.
*   **Technical Implementation:** Implements `BaseProvider` with dynamic fallback (Anthropic -> OpenAI).
*   **Dependencies:** Redis (Caching), External LLM APIs.
*   **Limitations:** Text-generation only; multimodal pending.

### Prompt Management
*   **Purpose:** Immutable storage and versioning.
*   **User Benefit:** Eliminates "prompt drift".
*   **Technical Implementation:** Maker/Checker workflows using `PromptVersion` and `PromptDeployment` schemas.
*   **Limitations:** Lacks A/B testing native routing.

### Agent Observability
*   **Purpose:** Deep telemetry of executions.
*   **User Benefit:** Complete visibility into agent decision-making.
*   **Technical Implementation:** LangGraph asynchronous callback handlers mapping to `AgentRun`/`AgentSpan`.
*   **Dependencies:** LangGraph checkpointing.

### Agent Replay Engine
*   **Purpose:** Time-travel debugging.
*   **User Benefit:** Reproduce failures without real-world side effects.
*   **Technical Implementation:** `ToolInterceptor` aggressively mocks LangGraph tool nodes using historical SQL span data.

### Evaluation Framework
*   **Purpose:** Automated testing against Golden Datasets.
*   **User Benefit:** Proves if prompt changes improve or degrade performance.
*   **Technical Implementation:** `EvaluationWorker` running via FastAPI `BackgroundTasks` executing `LLMJudge`.
*   **Limitations:** BackgroundTasks do not survive pod restarts (Risk: High).

### Human In The Loop (HITL)
*   **Purpose:** Secure authorization gates.
*   **User Benefit:** Requires manual approval for destructive operations.
*   **Technical Implementation:** LangGraph `interrupt_before` hooks combined with `ApprovalTicket` queues.

### Multi-Agent Swarms
*   **Purpose:** Orchestration of specialized hierarchical agents.
*   **User Benefit:** Solves complex, multi-step problems.
*   **Technical Implementation:** `SupervisorRouter` dynamically analyzing `MessagesState` to delegate tasks.

---

## 4. System Architecture

### Component Architecture

```mermaid
graph TD
    Client[Client UI / Consumers] --> API[FastAPI Entrypoint]
    
    subgraph "Application Layer"
        API --> Auth[Auth Middleware]
        Auth --> Routers[Domain Routers]
        Routers --> Services[Service Layer]
    end
    
    subgraph "AI Core Layer"
        Services --> Gateway[Model Gateway]
        Services --> LangGraph[LangGraph Executor]
        LangGraph --> Interceptor[HITL / Replay]
        LangGraph --> Supervisor[Swarm Supervisor]
    end
    
    subgraph "Data Layer"
        Gateway --> Redis[(Redis Cache)]
        Services --> CRUD[SQLAlchemy Async]
        CRUD --> PG[(PostgreSQL 15+)]
    end
```

*   **Frontend:** N/A (Headless Backend).
*   **Backend:** FastAPI, AsyncIO, strict Layered Architecture (Routers -> Services -> CRUD).
*   **Database:** PostgreSQL (Relational integrity + JSONB for unstructured agent state).
*   **Event Flow:** Graph interruptions yield state back to the DB; API calls resume execution via `PostgresSaver`.
*   **Failure Flow:** (Missing Documentation: Must define DLQs for failed async evaluations).

---

## 5. Technology Stack

| Technology | Version | Purpose | Reason for Selection | Alternatives Considered |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | 3.11+ | Core Language | Robust AI ecosystem (LangChain, LangGraph). | Go, Rust (Lacking AI ecosystem maturity) |
| **FastAPI** | 0.104+ | API Framework | Async native, high performance. | Django, Flask (Too heavy or lack async) |
| **PostgreSQL**| 15+ | Primary Datastore | ACID compliance, JSONB support for unstructured AI state. | MongoDB (Lacks relational integrity) |
| **SQLAlchemy**| 2.0+ | ORM | Type-safe, async database interactions. | Prisma, TortoiseORM |
| **Redis** | 7.0+ | Caching/PubSub| Low latency semantic caching and rate-limiting. | Memcached |
| **LangGraph** | 0.0.x | Orchestration | Stateful, cyclical graph execution for autonomous agents. | AutoGen, CrewAI |

---

## 6. Project Structure

```text
/backend
├── /app
│   ├── /ai               # Core AI logic (Gateway, Observability, Swarms, HITL)
│   ├── /api              # FastAPI Routers (v1). Request parsing and validation.
│   ├── /core             # App configuration, DB engine, JWT Security.
│   ├── /crud             # Data Access Layer. Strict SQLAlchemy interfaces.
│   ├── /models           # Database schema definitions.
│   ├── /schemas          # Pydantic validation models.
│   └── main.py           # Application entrypoint.
├── alembic/              # Database migration scripts.
├── tests/                # Pytest suites (CURRENTLY EMPTY - CRITICAL RISK).
├── requirements.txt      # Dependency lockfile.
└── .env.example          # Environment variable templates.
```

---

## 7. Core Workflows

### Agent Swarm Execution Workflow

```mermaid
sequenceDiagram
    participant Client
    participant SwarmExecutor
    participant Supervisor
    participant Agent
    participant DB

    Client->>SwarmExecutor: POST /swarms/{id}/invoke
    SwarmExecutor->>Supervisor: Init MessagesState
    loop Max Loops
        Supervisor->>Supervisor: LLM Routing Decision
        Supervisor->>Agent: Route to Node
        Agent->>DB: Telemetry Span
        Agent-->>Supervisor: Updated State
    end
    SwarmExecutor-->>Client: Return Final State
```

*   **Auth Flow:** Standard OAuth2 Password Bearer generating stateless JWTs.
*   **Error Handling:** Custom HTTPExceptions caught by FastAPI middleware. (Missing: Global exception handler for unhandled DB timeouts).

---

## 8. Database Design

*   **Entities:** Tenants, Users, Prompts, Observability (Runs/Spans), HITL Tickets, Swarms, Agents.
*   **Relationships:** Enforced via Foreign Keys; cascading deletes applied to child entities (e.g., `AgentRun` -> `AgentSpan`).
*   **Indexes:** B-Trees on all FKs. GIN indexes required on `JSONB` state snapshots.
*   **Retention Strategy:** (CRITICAL GAP: No cron job documented to prune `agent_spans` older than 90 days. Risk of disk exhaustion).

```mermaid
erDiagram
    TENANT ||--o{ USER : contains
    TENANT ||--o{ PROMPT : owns
    PROMPT ||--o{ PROMPT_VERSION : has
    TENANT ||--o{ AGENT_RUN : executes
    AGENT_RUN ||--o{ AGENT_SPAN : generates
    AGENT_RUN ||--o{ APPROVAL_TICKET : triggers
    TENANT ||--o{ SWARM : defines
```

---

## 9. Comprehensive Documentation Suite

The AIForge documentation is structured for scale. All engineering, operational, and security decisions are strictly documented within the `/docs` directory.

### 🏛️ Architecture & Design
*   [High Level Design (HLD)](docs/architecture/HLD.md)
*   [Low Level Design (LLD)](docs/architecture/LLD.md)
*   [System Design & Scalability](docs/architecture/SYSTEM_DESIGN.md)
*   [Component Diagrams](docs/architecture/COMPONENT_DIAGRAMS.md)
*   [Sequence Diagrams](docs/architecture/SEQUENCE_DIAGRAMS.md)
*   [Data Flow](docs/architecture/DATA_FLOW.md)
*   [C4 Model Diagrams](docs/architecture/C4_MODEL.md)

### 🔌 API & Integration
*   [API Reference](docs/api/API_REFERENCE.md)
*   [Authentication](docs/api/AUTHENTICATION.md)
*   [Authorization & RBAC](docs/api/AUTHORIZATION.md)

### 💾 Database
*   [Database Design](docs/database/DATABASE_DESIGN.md)
*   [Entity Relationship (ER) Diagram](docs/database/ER_DIAGRAM.md)
*   [Data Lifecycle & Pruning](docs/database/DATA_LIFECYCLE.md)

### 🔒 Security
*   [Security Architecture](docs/security/SECURITY_ARCHITECTURE.md)
*   [Threat Model](docs/security/THREAT_MODEL.md)
*   [Secrets Management](docs/security/SECRETS_MANAGEMENT.md)

### 🧠 AI Systems
*   [Agent Architecture](docs/ai/AGENT_ARCHITECTURE.md)
*   [Prompt Architecture](docs/ai/PROMPT_ARCHITECTURE.md)
*   [Memory Architecture](docs/ai/MEMORY_ARCHITECTURE.md)
*   [Tool Calling Execution](docs/ai/TOOL_CALLING.md)
*   [Evaluation Framework](docs/ai/EVALUATION_FRAMEWORK.md)

### 🚀 Deployment
*   [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)
*   [Infrastructure Specifications](docs/deployment/INFRASTRUCTURE.md)
*   [CI/CD Pipelines](docs/deployment/CI_CD.md)
*   [Environment Promotion](docs/deployment/ENVIRONMENTS.md)

### 🛠️ Operations
*   [SRE Runbooks](docs/operations/RUNBOOKS.md)
*   [Incident Response](docs/operations/INCIDENT_RESPONSE.md)
*   [Disaster Recovery](docs/operations/DISASTER_RECOVERY.md)
*   [Observability & Alerts](docs/operations/OBSERVABILITY.md)

### 📝 Product & Requirements
*   [Business Rules](docs/product/BUSINESS_RULES.md)
*   [System Requirements](docs/product/REQUIREMENTS.md)

### 📐 Architecture Decision Records (ADR)
*   [ADR-001: Async PostgreSQL](docs/adr/ADR-001.md)
*   [ADR-002: LangGraph Orchestration](docs/adr/ADR-002.md)
*   [ADR-003: Redis Caching](docs/adr/ADR-003.md)

---

## 10. AI and Agent Architecture

*   **Models:** Agnostic (OpenAI `gpt-4o`, Anthropic `claude-3`).
*   **Prompt Strategy:** Stored in DB, semantically versioned, diffed via `difflib`.
*   **Context/Memory Management:** Managed strictly via LangGraph `MessagesState` checkpointers (`PostgresSaver`).
*   **Hallucination Prevention:** `EvaluationFramework` runs Golden Dataset regression tests.
*   **Guardrails:** `HITLInterceptor` acts as a hard stop for `interrupt_before` node configurations.

---

## 11. Security Design

*   **Authentication:** JWT with expiration.
*   **Authorization (RBAC):** (HIGH GAP: Schema lacks explicit role mapping; relies on arbitrary middleware logic).
*   **Tenant Isolation:** Row-level `tenant_id` filters hardcoded in all `CRUDBase` operations.
*   **Secrets Management:** (CRITICAL GAP: `.env` is insufficient. Must integrate HashiCorp Vault or AWS KMS).
*   **PII Masking:** Regex-based sanitization in `AIForgeTracer` before saving to DB.
*   **Prompt Injection:** Mitigated via strict HITL approval queues for destructive actions.

---

## 12. Configuration

| Variable | Required | Type | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | String | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | Yes | String | `redis://host:6379/0` |
| `SECRET_KEY` | Yes | String | 256-bit key for JWT signing |
| `OPENAI_API_KEY`| No | String | Requires `sk-...` |

---

## 13. Local Development Setup

1.  **Prerequisites:** Python 3.11, Docker, Postgres 15, Redis.
2.  **Database Setup:** `docker-compose up -d db redis` (Note: `docker-compose.yml` is missing from the repo).
3.  **Installation:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  **Migration:** `alembic upgrade head`
5.  **Run:** `uvicorn app.main:app --reload`

---

## 14. Testing Strategy

**(CRITICAL GAP: Current Test Coverage is 0%)**
*   **Unit Tests:** Required for PII maskers and Token counters.
*   **Integration Tests:** Required for API routes utilizing rolled-back DB transactions.
*   **AI Evaluation:** Automated LLM-as-a-Judge execution against `EvaluationFramework` datasets.

---

## 15. Logging and Monitoring

*   **Observability:** AI specific traces stored natively in `agent_runs` and `agent_spans`.
*   **(HIGH GAP):** No integration with APM (Datadog/NewRelic). No standard `structlog` setup for FastAPI lifecycle events.

---

## 16. CI/CD Pipeline

**(CRITICAL GAP: No CI/CD manifests exist in the repository.)**
*Expected Pipeline:*
```mermaid
graph LR
    Push --> Lint[Flake8/Black]
    Lint --> Unit[Pytest]
    Unit --> Eval[Run LLM Evaluations]
    Eval --> Docker[Build Image]
    Docker --> Helm[Deploy to K8s]
```

---

## 17. Performance Engineering

*   **Database:** `selectinload` prevents N+1 query problems.
*   **Caching:** Redis semantic caching prevents redundant LLM inferences.
*   **Scalability Bottleneck:** `EvaluationWorker` relies on `BackgroundTasks`. Must be migrated to Celery.

---

## 18. Deployment Guide

**(CRITICAL GAP: Missing IaC and Dockerfiles)**
*   **Production Deployment:** Intended for Kubernetes scaling the FastAPI pods, with managed AWS RDS (Postgres) and ElastiCache (Redis).

---

## 19. Production Readiness Checklist

**Current Score: 32/100 (FAIL)**
*   [ ] Security: Implement AWS KMS for API Keys.
*   [ ] Scalability: Migrate BackgroundTasks to Celery.
*   [ ] Reliability: Implement `tenacity` retry loops for LLM API calls.
*   [ ] Monitoring: Install Prometheus metrics exporter.
*   [ ] Backup: Configure Postgres WAL archiving.

---

## 20. Troubleshooting Guide

*   **Symptom:** Swarms hit `max_loops` constantly.
    *   **Fix:** Supervisor prompt is failing to output `FINISH`. Review the LLM trace in `/api/v1/observability/runs`.
*   **Symptom:** Database connection timeout.
    *   **Fix:** Check `asyncpg` pool size limit.

---

## 21. Future Roadmap

*   **Short-Term (Phase 1):** Rectify missing Dockerfiles, CI/CD, and Celery worker infrastructure.
*   **Mid-Term:** Feature 8: Enterprise Knowledge Graph (RAG) using `pgvector`.
*   **Long-Term:** Multi-modal agents and autonomous Swarm Topology generation.

---

## 22. Technical Debt

*   **Risk Area:** Lack of automated test suites means refactoring the LangGraph logic has a high probability of introducing regressions.
*   **Risk Area:** The telemetry database will grow unboundedly until a pruning cron job is implemented.

---

## 23. Contribution Guide

*   **Branching:** GitFlow.
*   **PRs:** Require 1 Senior Engineer approval. Must include Pytest updates.
*   **Coding Standards:** Enforced via `black` and `mypy` strict type checking.

---

## 24. Appendix

*   **RAG:** Retrieval-Augmented Generation.
*   **HITL:** Human-In-The-Loop.
*   **DAG:** Directed Acyclic Graph.
*   **Golden Dataset:** A verified set of `input_data` and `expected_output` used to mathematically score LLM reliability.
