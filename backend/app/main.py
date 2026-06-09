from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth

app = FastAPI(title="AIForge API", version="1.0.0", root_path="/api")

app.include_router(auth.router, prefix="/auth", tags=["auth"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
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
