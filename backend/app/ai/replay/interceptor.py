from typing import Any, Dict, Optional
from langchain_core.tools import BaseTool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...models.observability import AgentSpan

class MockRequiredError(Exception):
    pass

class ToolInterceptor:
    @staticmethod
    async def intercept(
        db: AsyncSession, 
        trace_id: str, 
        tool_name: str, 
        input_payload: Dict[str, Any], 
        strict_mock: bool = True
    ) -> Any:
        """
        Intercepts a tool call during replay and injects the historical output from the AgentSpan database.
        Raises MockRequiredError if strict_mock is True and no historical span is found.
        """
        result = await db.execute(
            select(AgentSpan)
            .filter(
                AgentSpan.trace_id == trace_id,
                AgentSpan.span_type == "tool",
                AgentSpan.name == tool_name
            )
            .order_by(AgentSpan.started_at.asc())
        )
        historical_span = result.scalars().first()
        
        if historical_span and historical_span.output_payload:
            return historical_span.output_payload.get("output", "")
            
        if strict_mock:
            raise MockRequiredError(f"Strict Mocking Enabled: No historical mock found for tool '{tool_name}' in trace {trace_id}. Real execution blocked to prevent side-effects.")
        else:
            return None 
