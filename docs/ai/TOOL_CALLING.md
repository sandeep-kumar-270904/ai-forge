# Tool Calling Execution

## Architecture

Tools are Python functions decorated with `@tool` (LangChain). They are bound to specific `SwarmAgentPersona`s via the database.

1.  **Binding:** The Model Gateway dynamically binds the agent's allowed tools to the LLM via the vendor's specific function-calling API (e.g., OpenAI `tools` array).
2.  **Invocation:** The LLM responds with a `tool_calls` message.
3.  **Execution:** The LangGraph `ToolNode` maps the requested function name to the Python callable, executes it, and appends the `ToolMessage` result back to the state.

## Security & Determinism

### 1. The Tool Interceptor (Replay Engine)
During Replay Mode, developers often want to debug a failed graph. However, if a tool executes `ChargeCreditCard(amount=100)`, running the replay would charge the card again.
The `ToolInterceptor` aggressively hooks into the execution graph. If a `run_id` is marked as a replay, the interceptor searches the `agent_spans` table for the historical output of that specific tool call and returns the cached string, bypassing the actual Python function entirely.

### 2. Guardrails (HITL)
Tools marked as `sensitive=True` are placed behind an `interrupt_before` hook in the LangGraph compilation step. Execution yields immediately, emitting an `ApprovalTicket`.
