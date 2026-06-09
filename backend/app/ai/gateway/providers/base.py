from abc import ABC, abstractmethod
from typing import AsyncGenerator
from ....schemas.gateway import ChatCompletionRequest, ChatCompletionResponse

class BaseProvider(ABC):
    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        pass

    @abstractmethod
    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass
        
    @abstractmethod
    def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        pass
