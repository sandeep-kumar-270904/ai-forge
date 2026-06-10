# C4 Architecture Model

This document provides a C4 (Context, Containers, Components) model visualization of the AIForge system to explain the architecture across different levels of abstraction.

## Level 1: System Context Diagram

The System Context diagram shows how AIForge fits into the broader enterprise environment and how users interact with it.

```mermaid
graph TD
    User((Enterprise User))
    System[AIForge Platform]
    LLM[External LLM Providers]
    
    User -- "Triggers autonomous workflows & approves tasks" --> System
    System -- "Sends prompts & retrieves inference" --> LLM
```

## Level 2: Container Diagram

The Container diagram zooms into the AIForge Platform to show the high-level deployable units and data stores.

```mermaid
graph TD
    User((Client Application))
    
    subgraph "AIForge Platform (Kubernetes)"
        API[FastAPI Web Application<br/>Python 3.11]
        Worker[Evaluation Worker<br/>Python Background Tasks]
    end
    
    DB[(Primary Database<br/>PostgreSQL 15)]
    Cache[(Semantic Cache<br/>Redis 7)]
    LLM[LLM APIs<br/>OpenAI/Anthropic]

    User -- "REST / JSON (HTTPS)" --> API
    API -- "Async I/O" --> Worker
    API -- "SQLAlchemy (asyncpg)" --> DB
    API -- "redis-py" --> Cache
    Worker -- "SQLAlchemy (asyncpg)" --> DB
    
    API -- "REST (HTTPS)" --> LLM
    Worker -- "REST (HTTPS)" --> LLM
```

## Level 3: Component Diagram (FastAPI Application)

This diagram zooms into the FastAPI Web Application container to show the structural building blocks of the codebase.

```mermaid
graph TD
    subgraph "FastAPI Web Application"
        Router[API Routers<br/>app.api]
        Auth[Auth Middleware<br/>app.core.security]
        
        subgraph "Service Layer (app.ai)"
            Swarm[Swarm Orchestrator]
            HITL[HITL Interceptor]
            Gateway[Model Gateway]
            Observability[Telemetry Engine]
        end
        
        subgraph "Data Access Layer (app.crud)"
            CRUD_Base[CRUDBase]
        end
    end
    
    Router --> Auth
    Auth --> Swarm
    Auth --> HITL
    
    Swarm --> HITL
    Swarm --> Gateway
    Swarm --> Observability
    
    HITL --> CRUD_Base
    Observability --> CRUD_Base
    Gateway --> Cache[(Redis)]
    
    CRUD_Base --> DB[(PostgreSQL)]
```
