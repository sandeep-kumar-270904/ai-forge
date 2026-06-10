import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from ...crud.crud_observability import agent_span
from ...schemas.observability import AgentSpanCreate
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class AIForgeTracer(AsyncCallbackHandler):
    """
    A LangChain/LangGraph callback handler that captures execution spans
    and persists them to the AIForge Observability fallback storage.
    """
    def __init__(self, trace_id: str, db: AsyncSession):
        self.trace_id = trace_id
        self.db = db
        self.run_map: Dict[str, dict] = {} 

    def _mask_pii(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            return {k: ("***MASKED***" if "password" in k.lower() or "secret" in k.lower() else self._mask_pii(v)) for k, v in payload.items()}
        elif isinstance(payload, list):
            return [self._mask_pii(i) for i in payload]
        return payload

    async def _flush_span(self, run_id: str, status: str, end_time: datetime, error: Optional[str] = None, output: Optional[Any] = None):
        span_data = self.run_map.get(run_id)
        if not span_data:
            return
            
        start_time = span_data["started_at"]
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        try:
            await agent_span.create_span(
                self.db,
                obj_in=AgentSpanCreate(
                    id=str(run_id),
                    trace_id=self.trace_id,
                    parent_span_id=str(span_data.get("parent_run_id")) if span_data.get("parent_run_id") else None,
                    name=span_data["name"],
                    span_type=span_data["type"],
                    input_payload=span_data["input"],
                    output_payload=self._mask_pii(output) if output else None,
                    error_message=error,
                    started_at=start_time,
                    completed_at=end_time,
                    duration_ms=duration_ms
                )
            )
        except Exception as e:
            logger.error(f"Failed to flush telemetry span {run_id}: {e}")
        finally:
            if run_id in self.run_map:
                del self.run_map[run_id]

    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        self.run_map[str(run_id)] = {
            "name": serialized.get("name", "Chain") if serialized else "Chain",
            "type": "chain",
            "started_at": datetime.utcnow(),
            "input": self._mask_pii(inputs),
            "parent_run_id": parent_run_id
        }

    async def on_chain_end(self, outputs: Dict[str, Any], *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        await self._flush_span(str(run_id), "success", datetime.utcnow(), output=outputs)

    async def on_chain_error(self, error: BaseException, *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        await self._flush_span(str(run_id), "error", datetime.utcnow(), error=str(error))

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None, inputs: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        self.run_map[str(run_id)] = {
            "name": serialized.get("name", "Tool") if serialized else "Tool",
            "type": "tool",
            "started_at": datetime.utcnow(),
            "input": {"input": self._mask_pii(input_str)},
            "parent_run_id": parent_run_id
        }

    async def on_tool_end(self, output: str, *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        await self._flush_span(str(run_id), "success", datetime.utcnow(), output={"output": output})

    async def on_tool_error(self, error: BaseException, *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        await self._flush_span(str(run_id), "error", datetime.utcnow(), error=str(error))

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
         self.run_map[str(run_id)] = {
            "name": serialized.get("name", "LLM") if serialized else "LLM",
            "type": "llm",
            "started_at": datetime.utcnow(),
            "input": {"prompts": self._mask_pii(prompts)},
            "parent_run_id": parent_run_id
        }

    async def on_llm_end(self, response: LLMResult, *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        out = {"generations": [[g.text for g in gen] for gen in response.generations]}
        await self._flush_span(str(run_id), "success", datetime.utcnow(), output=out)

    async def on_llm_error(self, error: BaseException, *, run_id: uuid.UUID, parent_run_id: Optional[uuid.UUID] = None, tags: Optional[List[str]] = None, **kwargs: Any) -> None:
        await self._flush_span(str(run_id), "error", datetime.utcnow(), error=str(error))
