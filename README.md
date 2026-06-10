# AIForge 🚀

**The Enterprise AI Operating System for Production-Grade Multi-Agent Swarms**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

AIForge is a production-ready, highly-scalable backend platform designed to orchestrate, observe, evaluate, and secure complex Multi-Agent AI workflows. Built for startups and enterprise teams, AIForge takes the chaos out of LLM integration by providing a rigid framework for Agent creation, deterministic replays, LLM-as-a-judge evaluation, and Human-in-the-Loop (HITL) authorization queues.

---

## 🏗 Architecture Overview

At its core, AIForge uses a modular, asynchronous microservices-style architecture powered by **FastAPI** and **SQLAlchemy 2.0 (Async)**. 

### Core Modules

1. **Model Gateway (`/gateway`)**: A unified, high-performance abstraction layer for LLM providers (OpenAI, Anthropic, etc.). Features built-in failover routing, aggressive Redis caching, and strict token accounting.
2. **Prompt Management (`/prompts`)**: Immutable, semantically versioned prompt storage. Prevents "prompt drift" via a Maker/Checker approval pipeline, ensuring untested prompts never hit production.
3. **Agent Observability (`/observability`)**: Deep telemetry using LangGraph asynchronous callback handlers. Recursively captures graphs, chains, and node executions into a durable SQL timeline, complete with automatic PII payload masking.
4. **Agent Replay Engine (`/replay`)**: Time-travel debugging for AI. Allows developers to rewind execution graphs and step forward. Utilizes a `ToolInterceptor` to mock historical real-world API calls, enabling safe, counter-factual exploration without side effects.
5. **Evaluation Framework (`/evaluations`)**: Automated LLM-as-a-Judge execution engine. Run target agents against Golden Datasets asynchronously to detect regressions in reasoning accuracy before deploying.
6. **Human-In-The-Loop (`/hitl`)**: Zero-trust execution for high-stakes agent actions. Suspends LangGraph threads mid-execution, surfaces a manual approval ticket to the UI, and resumes the thread upon authorization with optional state overrides.
7. **Multi-Agent Swarms (`/swarms`)**: Hierarchical orchestration of specialized worker agents driven by an LLM Supervisor router, backed by shared state management and strict infinite-loop prevention (`max_loops`).

---

## 🌊 Data Flow & Working Mechanism

AIForge operates on a strict **Tenant-Isolated Data Model** ensuring absolute B2B SaaS readiness.

1. **Invocation**: A client application triggers `POST /api/v1/swarms/{id}/invoke`.
2. **Orchestration**: The `SwarmExecutor` initializes a `MessagesState` scratchpad and invokes the `SupervisorRouter`. 
3. **Routing**: The Supervisor analyzes the state and routes the task to a specialized `SwarmAgentPersona` (e.g., Researcher, Coder).
4. **Interruption (HITL)**: If the assigned worker attempts a sensitive action (e.g., executing code, sending email), the `HITLInterceptor` suspends the graph via LangGraph checkpointers and queues an `ApprovalTicket`.
5. **Execution & Telemetry**: Once approved, the Model Gateway processes the request, routing through fallback providers if the primary fails. The `AIForgeTracer` concurrently streams hierarchical span data to the `agent_spans` table.
6. **Evaluation**: Post-execution, the output can be piped into the Evaluation Framework where an Async Worker triggers a strong LLM Judge (e.g., GPT-4o) to grade the response against a `DatasetRow` baseline.

---

## 🚀 Getting Started

### Prerequisites
*   **Python 3.11+**
*   **PostgreSQL 15+** (with `pgvector` extension recommended for RAG capabilities)
*   **Redis** (for Model Gateway caching and rate limiting)

### 1. Installation

Clone the repository and set up your virtual environment:

```bash
git clone https://github.com/your-org/ai-forge.git
cd ai-forge/backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aiforge
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

### 3. Database Migration

Initialize your database schema:

```bash
alembic upgrade head
```

*(Note: Ensure your PostgreSQL instance is running. Alembic will automatically build all Core, HITL, Swarms, and Observability tables).*

### 4. Running the Server

Start the FastAPI application via Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

*   **API Documentation**: Navigate to `http://localhost:8000/docs` to view the interactive Swagger UI and test endpoints directly.
*   **Health Check**: `curl http://localhost:8000/health`

---

## 🔐 Security Stance

Built by security engineers, for enterprise.
*   **Row-Level Tenant Isolation**: All endpoints natively filter by `current_user.tenant_id`.
*   **PII Scrubbing**: Built-in Regex-driven masking of secrets/PII before telemetry hits the database.
*   **Deterministic Mocking**: Real-world side effects are programmatically disabled during Replay sessions.
*   **JWT Rotation**: Refresh token rotation implemented by default.

---

## 🤝 Contributing
Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests. Ensure all code passes `pytest` and `black` formatting before opening a PR.
