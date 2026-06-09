import os
import time
from typing import AsyncGenerator
from openai import AsyncOpenAI
from .base import BaseProvider
from ....schemas.gateway import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionResponseChoice, UsageInfo

class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def get_provider_name(self) -> str:
        return "openai"
        
    def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        rates = {
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006}
        }
        rate = rates.get(model, {"prompt": 0.00015, "completion": 0.0006}) # Default to cheapest
        return (prompt_tokens / 1000 * rate["prompt"]) + (completion_tokens / 1000 * rate["completion"])

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.time()
        
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response = await self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        cost_usd = self.estimate_cost(request.model, response.usage.prompt_tokens, response.usage.completion_tokens)
        
        usage_info = UsageInfo(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            cost_usd=cost_usd
        )
        
        choices = [
            ChatCompletionResponseChoice(
                index=c.index,
                message={"role": c.message.role, "content": c.message.content},
                finish_reason=c.finish_reason or "stop"
            ) for c in response.choices
        ]
        
        return ChatCompletionResponse(
            id=response.id,
            created=response.created,
            model=response.model,
            choices=choices,
            usage=usage_info,
            provider=self.get_provider_name(),
            latency_ms=latency_ms
        )

    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        stream = await self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
