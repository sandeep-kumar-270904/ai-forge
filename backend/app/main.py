from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from .api import auth, documents, chat, gateway, prompts, observability, replay, evaluation, hitl, swarms
from .core.config import settings
from .core.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conn = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)
    yield
    await redis_conn.close()

app = FastAPI(title="AIForge API", version="1.0.0", root_path="/api", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(gateway.router, prefix="/api/v1/gateway", tags=["gateway"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(observability.router, prefix="/api/v1/observability", tags=["observability"])
app.include_router(replay.router, prefix="/api/v1/replay", tags=["replay"])
app.include_router(evaluation.router, prefix="/api/v1/evaluations", tags=["evaluations"])
app.include_router(hitl.router, prefix="/api/v1/hitl", tags=["hitl"])
app.include_router(swarms.router, prefix="/api/v1/swarms", tags=["swarms"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Restricted to frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AIForge Backend"}

@app.get("/")
async def root():
    return {"message": "Welcome to AIForge API"}
