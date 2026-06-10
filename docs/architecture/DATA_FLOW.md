# Data Flow Diagram

This document traces the flow of data through AIForge, emphasizing trust boundaries, data transformations, and storage interactions.

## Core Data Flow

The AIForge architecture operates on a strict layered model. Data flows sequentially through the API, Service, and Data Access Layers, never bypassing intermediate stages.

```mermaid
graph TD
    subgraph "External Boundary"
        User[Client Application]
        ExternalLLM[External LLM Providers]
    end

    subgraph "Trust Boundary: API Layer"
        Router[FastAPI Router]
        Validator[Pydantic Schemas]
    end

    subgraph "Trust Boundary: Service Layer"
        Executor[AI Service / Swarm Executor]
        Scrubber[PII Masking Filter]
    end

    subgraph "Trust Boundary: Data Layer"
        CRUD[SQLAlchemy Repositories]
        DB[(PostgreSQL)]
        Cache[(Redis)]
    end

    User -- "1. JSON HTTP Request (JWT Auth)" --> Router
    Router -- "2. Schema Parsing" --> Validator
    Validator -- "3. Validated Python Objects" --> Executor
    
    Executor -- "4. Check Cache" --> Cache
    Cache -- "5. Cache Miss" --> Executor
    
    Executor -- "6. API Call (Raw Payload)" --> ExternalLLM
    ExternalLLM -- "7. API Response (JSON)" --> Executor
    
    Executor -- "8. Extract Telemetry" --> Scrubber
    Scrubber -- "9. Sanitized Payload" --> CRUD
    
    CRUD -- "10. Async SQL Transaction" --> DB
    Executor -- "11. Format Output" --> Router
    Router -- "12. JSON HTTP Response" --> User
```

## Data Lifecycle & Security Transformations

1.  **Ingress:** External data enters as raw JSON. FastAPI immediately converts this to strict Python types using Pydantic models. Any invalid data (e.g., missing required fields, type mismatches) is rejected at the perimeter with a `422 Unprocessable Entity`.
2.  **Authentication Filter:** Before reaching the Service Layer, the JWT middleware extracts the `tenant_id` and `user_id`. These parameters are rigidly passed downward to ensure isolation.
3.  **Third-Party Egress:** Before hitting external LLMs, the Model Gateway formats the data into the specific vendor's required payload (e.g., OpenAI vs Anthropic message formats).
4.  **Telemetry Sanitization (Scrubber):** Before saving agent thoughts or prompt inputs to the database, the `AIForgeTracer` applies regex-based masking to remove sensitive data (e.g., replacing credit card numbers with `[REDACTED_CC]`).
5.  **Persistence:** The CRUD layer receives the sanitized, tenant-bound data and uses SQLAlchemy models to generate asynchronous parameterized SQL queries, protecting against SQL injection, before committing to PostgreSQL.
