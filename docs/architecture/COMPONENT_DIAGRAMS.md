# Component Diagrams

This document visually details the internal structure and responsibilities of the core subsystems within AIForge.

## 1. Observability Engine Component

The Observability Engine is responsible for capturing, scrubbing, and persisting telemetry data from active agent runs without blocking the main execution thread.

```mermaid
graph TD
    subgraph "Agent Execution"
        LC[LangChain / LangGraph Executor]
    end

    subgraph "Observability Engine"
        CB[AIForge Callback Handler]
        Scrubber[PII Regex Scrubber]
        SpanBuilder[Span Hierarchy Builder]
    end

    subgraph "Storage"
        DB[(PostgreSQL)]
    end

    LC -- Emits Event (on_llm_start) --> CB
    CB --> Scrubber
    Scrubber -- Masks Data --> SpanBuilder
    SpanBuilder -- Async Insert --> DB
```

## 2. Multi-Agent Swarm Component

The Swarm component orchestrates the routing logic between specialized agents using a shared state object.

```mermaid
graph TD
    Client[Client Request] --> Executor[Swarm Executor]
    
    subgraph "LangGraph Network"
        State[(MessagesState)]
        Supervisor[LLM Supervisor Node]
        
        AgentA[Agent Persona A]
        AgentB[Agent Persona B]
        AgentC[Agent Persona C]
    end

    Executor --> State
    State <--> Supervisor
    
    Supervisor -- Routes (AgentA) --> AgentA
    Supervisor -- Routes (AgentB) --> AgentB
    Supervisor -- Routes (AgentC) --> AgentC
    
    AgentA -- Yields State --> State
    AgentB -- Yields State --> State
    AgentC -- Yields State --> State
    
    Supervisor -- Routes (FINISH) --> Executor
    Executor --> Client
```

## 3. Human-In-The-Loop (HITL) Component

The HITL component safely suspends and resumes execution based on manual human approval.

```mermaid
graph LR
    subgraph "Graph Execution"
        NodeA[Safe Node] --> NodeB[Sensitive Node]
    end
    
    subgraph "HITL Interceptor"
        Checkpointer[PostgresSaver]
        TicketAPI[Approval Ticket API]
    end

    NodeA --> Checkpointer
    Checkpointer -- Suspend (interrupt_before) --> TicketAPI
    TicketAPI -- Wait for Human --> UI[Frontend Approver]
    UI -- POST /resolve --> TicketAPI
    TicketAPI -- Resume Thread --> NodeB
```
