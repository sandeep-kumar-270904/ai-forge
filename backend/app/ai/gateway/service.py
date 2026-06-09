import redis.asyncio as redis
import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from ....schemas.gateway import ChatCompletionRequest, ChatCompletionResponse
from ....models.token_usage import TokenUsageLog
from ....core.config import settings
from .router import ModelRouter

router = ModelRouter()
redis_client = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)

class GatewayService:
    @staticmethod
    def _generate_cache_key(request: ChatCompletionRequest) -> str:
        content_to_hash = json.dumps([m.model_dump() for m in request.messages], sort_keys=True)
        return f"gw:cache:{hashlib.sha256(content_to_hash.encode()).hexdigest()}"

    @staticmethod
    async def process_chat(request: ChatCompletionRequest, db: AsyncSession, tenant_id: str, workspace_id: str) -> ChatCompletionResponse:
        cache_key = GatewayService._generate_cache_key(request)
        
        # 1. Exact-Match Semantic Cache
        if not request.bypass_cache:
            try:
                cached_res = await redis_client.get(cache_key)
                if cached_res:
                    response_data = json.loads(cached_res)
                    response = ChatCompletionResponse(**response_data)
                    response.cached = True
                    response.latency_ms = 0
                    return response
            except Exception:
                pass # Fail open if redis is down

        # 2. Resilient Router Execution
        response = await router.execute_request(request)

        # 3. Populate Cache
        if not request.bypass_cache:
            try:
                await redis_client.setex(cache_key, 3600, response.model_dump_json())
            except Exception:
                pass

        # 4. Synchronous Accounting Write (to be made async via celery/arq in the future)
        usage_log = TokenUsageLog(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            provider=response.provider,
            model_name=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            cost_usd=response.usage.cost_usd,
            latency_ms=response.latency_ms
        )
        db.add(usage_log)
        await db.commit()

        return response
