# Memory Architecture

AIForge relies entirely on **Externalized Checkpointed Memory**.

## The Checkpointer
We utilize LangGraph's native checkpointer mechanism, backed by our PostgreSQL database (`PostgresSaver`). 

Every time a node in the graph finishes execution, the checkpointer serializes the entire `MessagesState` array and saves it as a unique `thread_ts` (Thread Timestamp) within the `thread_id`.

## Advantages
1.  **Fault Tolerance:** If the FastAPI pod crashes mid-execution, the exact state of the agent's thought process is preserved in Postgres.
2.  **Time-Travel Debugging:** The `AgentReplay` engine can load any historical `thread_ts` and resume execution from that exact moment, branching into a new counter-factual reality.
3.  **Human-In-The-Loop:** Memory check-pointing is what allows us to "pause" execution to await a human's API response, dropping the thread from RAM entirely until resumed.

## Context Window Limitations
*Currently, memory grows unboundedly with each cycle.*
**(GAP):** If an agent executes 50 loops, the context window will easily exceed 128k tokens, resulting in a `400 Bad Request` from the LLM provider.
**Fix (Roadmap):** Implement a `SummarizationNode` that conditionally truncates and summarizes the `MessagesState` if the token count exceeds 80% of the model's limit.
