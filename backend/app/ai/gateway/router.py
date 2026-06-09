import logging
from typing import AsyncGenerator
from .providers.base import BaseProvider
from .providers.openai import OpenAIProvider
from ....schemas.gateway import ChatCompletionRequest, ChatCompletionResponse

logger = logging.getLogger(__name__)

class ModelRouter:
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
        }
        
    def _resolve_provider(self, model: str) -> BaseProvider:
        if model.startswith("gpt") or model.startswith("o1"):
            return self.providers["openai"]
        return self.providers["openai"]

    async def execute_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        primary_provider = self._resolve_provider(request.model)
        
        try:
            logger.info(f"Routing request to primary provider: {primary_provider.get_provider_name()}")
            return await primary_provider.chat_completion(request)
        except Exception as e:
            logger.error(f"Primary provider {primary_provider.get_provider_name()} failed: {str(e)}")
            
            # Failover logic
            if request.fallback_models:
                for fallback_model in request.fallback_models:
                    fallback_provider = self._resolve_provider(fallback_model)
                    try:
                        logger.warning(f"Attempting failover to {fallback_model} via {fallback_provider.get_provider_name()}")
                        fallback_request = request.model_copy(update={"model": fallback_model})
                        return await fallback_provider.chat_completion(fallback_request)
                    except Exception as fallback_e:
                        logger.error(f"Failover to {fallback_model} failed: {str(fallback_e)}")
            
            raise e

    async def execute_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        provider = self._resolve_provider(request.model)
        async for chunk in provider.chat_completion_stream(request):
            yield chunk
