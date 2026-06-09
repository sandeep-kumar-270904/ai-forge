from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..api.deps import get_db, get_current_active_user
from ..models.user import User
from ..models.workspace import Workspace
from ..crud.crud_workspace import workspace as crud_workspace
from ..ai.rag import process_document, search_knowledge_base
from fastapi_limiter.depends import RateLimiter
import tempfile
import shutil
import os

router = APIRouter()

@router.post("/upload", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id, Workspace.tenant_id == current_user.tenant_id))
    workspace = result.scalars().first()
    if not workspace:
         raise HTTPException(status_code=403, detail="Not enough permissions to access this workspace")

    try:
        _, ext = os.path.splitext(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        collection_name = f"workspace_{workspace_id}"
        chunks = await process_document(temp_file_path, file.filename, collection_name)
        
        return {
            "message": "Document processed and stored successfully",
            "filename": file.filename,
            "chunks_processed": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.get("/search", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def search_documents(
    workspace_id: str,
    query: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id, Workspace.tenant_id == current_user.tenant_id))
    workspace = result.scalars().first()
    if not workspace:
         raise HTTPException(status_code=403, detail="Not enough permissions to access this workspace")

    collection_name = f"workspace_{workspace_id}"
    results = await search_knowledge_base(query, collection_name)
    return {"results": [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]}
