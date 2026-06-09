from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..api.deps import SessionDep, get_current_active_user
from ..models.user import User
from ..ai.rag import process_document, search_knowledge_base

router = APIRouter()

@router.post("/upload")
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: SessionDep = Depends()
):
    try:
        content = await file.read()
        collection_name = f"workspace_{workspace_id}"
        
        chunks = process_document(content, file.filename, collection_name)
        
        return {
            "message": "Document processed and stored successfully",
            "filename": file.filename,
            "chunks_processed": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
def search_documents(
    workspace_id: str,
    query: str,
    current_user: User = Depends(get_current_active_user)
):
    collection_name = f"workspace_{workspace_id}"
    results = search_knowledge_base(query, collection_name)
    return {"results": [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]}
