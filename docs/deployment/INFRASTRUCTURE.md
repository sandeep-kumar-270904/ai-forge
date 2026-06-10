# Infrastructure Dependencies

## Required Backing Services

| Service | Version | Purpose |
| :--- | :--- | :--- |
| **PostgreSQL** | 15+ | Primary relational datastore and JSONB document store for LangGraph state. |
| **Redis** | 7+ | Fast transient storage for Semantic Caching, Rate Limiting, and (future) Task Queues. |
| **OpenAI API** | N/A | External dependency for GPT-4o model inference. |
| **Anthropic API**| N/A | External dependency for Claude-3 model inference. |

## Network Architecture
*   The FastAPI pods must have outbound internet access to reach external LLM providers.
*   The PostgreSQL database MUST reside in a private subnet with no public ingress.
*   Redis should be isolated similarly within the VPC.
