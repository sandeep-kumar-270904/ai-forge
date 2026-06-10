# AIForge Enterprise AI Operating System

[![Status: Production Ready](https://img.shields.io/badge/Status-Production--Ready-success)](#)
[![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-blue)](#)

AIForge is a production-grade, highly-scalable backend platform designed to orchestrate, observe, evaluate, and secure complex Multi-Agent AI workflows. It is built to serve as the foundational infrastructure layer for enterprise AI, moving beyond fragmented scripts into governable, deterministic software.

This README serves as the master entry point to the AIForge Enterprise Documentation Suite. Please refer to the specific architectural sub-documents for deep technical details.

## Executive Summary
Integrating Large Language Models (LLMs) into production systems introduces significant operational risks: prompt drift, hallucination loops, PII leakage, and runaway costs. AIForge solves these challenges by providing a strict, highly-governed, multi-tenant microservices architecture that handles LLM orchestration natively. It enables enterprise engineering teams to securely deploy fleets of specialized autonomous agents with zero-trust execution boundaries.

## Architecture Overview
AIForge relies on an asynchronous, modular design built on top of **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **Redis**. 

The system utilizes a central **Model Gateway** for LLM abstraction, an **Evaluation Framework** for continuous reasoning validation, and **LangGraph** for maintaining state across cyclic multi-agent topologies (Swarms).

> **Deep Dive:** [High Level Design (HLD)](docs/architecture/HLD.md) | [System Design](docs/architecture/SYSTEM_DESIGN.md) | [C4 Model](docs/architecture/C4_MODEL.md)

## Technology Stack
*   **API Framework:** FastAPI (Python 3.11+)
*   **Database:** PostgreSQL 15+ (with Asyncpg)
*   **Caching & Rate Limiting:** Redis 7.0+
*   **Agent Orchestration:** LangGraph / LangChain
*   **ORM:** SQLAlchemy 2.0 (Async)

## Key Features
*   **Model Gateway:** Failover routing and aggressive semantic caching.
*   **Agent Observability:** Recursive LangGraph telemetry and PII masking.
*   **Time-Travel Replay:** Deterministic debugging via historical tool interception.
*   **Human-In-The-Loop (HITL):** Graph suspension and manual approval queues.
*   **Multi-Agent Swarms:** Hierarchical orchestration via LLM Supervisor routers.

> **Deep Dive:** [API Reference](docs/api/API_REFERENCE.md) | [Agent Architecture](docs/ai/AGENT_ARCHITECTURE.md)

## Documentation Index

The AIForge documentation is structured for scale. All engineering, operational, and security decisions are strictly documented.

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

## Quick Start

### 1. Requirements
Ensure Docker, Python 3.11+, and Git are installed.

### 2. Infrastructure Boot
Spin up the backing data stores locally:
```bash
docker-compose up -d db redis
```

### 3. Application Boot
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Deployment Overview
AIForge is container-native. The primary deployment target is Kubernetes, utilizing horizontal pod autoscaling (HPA) for the FastAPI API tier, and managed cloud services (AWS RDS, ElastiCache) for statefulness. See [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md).

## Security Overview
Zero-trust by default. All endpoints enforce row-level `tenant_id` isolation. PII is scrubbed before database persistence via `AIForgeTracer`. All destructive tool calls are gated behind the HITL approval API. See [Security Architecture](docs/security/SECURITY_ARCHITECTURE.md).

## AI Overview
The platform abstracts model variance through the `ModelGateway` and orchestrates multi-agent topologies using LangGraph's cyclic state graphs. LLM hallucination is systematically reduced via automated asynchronous regression testing in the `EvaluationFramework`. See [Agent Architecture](docs/ai/AGENT_ARCHITECTURE.md).

## Support Information
For internal engineering support, please refer to the [Incident Response](docs/operations/INCIDENT_RESPONSE.md) documentation or contact the Platform Engineering on-call alias.
