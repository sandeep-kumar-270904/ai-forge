# Sequence Diagrams

This document illustrates the step-by-step sequential interactions between actors and system components for key workflows.

## 1. LLM Failover & Routing Workflow

This sequence demonstrates how the Model Gateway ensures high availability by automatically falling back to secondary models during primary outages.

```mermaid
sequenceDiagram
    participant App as Application Service
    participant Gateway as Model Gateway
    participant Redis as Semantic Cache
    participant OpenAI as OpenAI API
    participant Anthropic as Anthropic API

    App->>Gateway: generate(prompt, model="gpt-4o")
    Gateway->>Redis: Check Cache (Hash: prompt+model)
    
    alt Cache Hit
        Redis-->>Gateway: Return Cached Response
        Gateway-->>App: Return Result (< 2ms)
    else Cache Miss
        Gateway->>OpenAI: POST /v1/chat/completions
        
        alt Success
            OpenAI-->>Gateway: 200 OK
            Gateway->>Redis: Set Cache (TTL: 1 hour)
            Gateway-->>App: Return Result
        else 429 Too Many Requests
            OpenAI--xGateway: 429 Error
            Note over Gateway: Initiate Failover Logic
            Gateway->>Anthropic: POST /v1/messages (claude-3-opus)
            Anthropic-->>Gateway: 200 OK
            Gateway-->>App: Return Result (Degraded State)
        end
    end
```

## 2. Evaluation Framework Workflow

This sequence shows how asynchronous workers validate new prompt deployments against historical golden datasets.

```mermaid
sequenceDiagram
    participant Dev as AI Engineer
    participant API as FastAPI Router
    participant DB as PostgreSQL
    participant Worker as Evaluation Worker
    participant LLM as LLM Judge

    Dev->>API: POST /evaluations/run (prompt_id, dataset_id)
    API->>DB: Create Evaluation Job (Status: Pending)
    API-->>Dev: 202 Accepted (Job ID)
    
    API->>Worker: Trigger Background Task
    
    loop For Each Dataset Row
        Worker->>DB: Fetch Row Input
        Worker->>LLM: Generate Output using target Prompt
        LLM-->>Worker: Target Response
        
        Worker->>LLM: Evaluate (Target Response vs Expected Output)
        LLM-->>Worker: Score (0.0 to 1.0)
        Worker->>DB: Save EvaluationResult
    end
    
    Worker->>DB: Update Evaluation Job (Status: Completed)
```
