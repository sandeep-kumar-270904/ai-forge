from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.knowledge import DocumentRead, SearchQuery, SearchResult
from app.crud.crud_knowledge import knowledge
from app.models.knowledge import DocumentChunk
from app.ai.rag.loader import extract_text_from_pdf, chunk_text, generate_embeddings, generate_single_embedding

router = APIRouter()

@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are currently supported")

    # 1. Create Document Record
    doc = await knowledge.create_document(
        db=db, 
        tenant_id=current_user.tenant_id, 
        name=file.filename, 
        file_type=file.content_type
    )

    try:
        # 2. Extract Text
        content_bytes = await file.read()
        raw_text = extract_text_from_pdf(content_bytes)

        # 3. Chunk Text
        text_chunks = chunk_text(raw_text)

        if not text_chunks:
            raise ValueError("No text could be extracted from the document")

        # 4. Generate Embeddings
        embeddings = await generate_embeddings(text_chunks)

        # 5. Save Chunks to Database
        db_chunks = []
        for i, (text_content, embedding) in enumerate(zip(text_chunks, embeddings)):
            chunk = DocumentChunk(
                tenant_id=current_user.tenant_id,
                document_id=doc.id,
                content=text_content,
                embedding=embedding,
                metadata={"chunk_index": i}
            )
            db_chunks.append(chunk)

        await knowledge.insert_chunks(db, db_chunks)

        # 6. Update Status
        await knowledge.update_document_status(db, doc.id, "completed")
        await db.refresh(doc)
        return doc

    except Exception as e:
        await knowledge.update_document_status(db, doc.id, "failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResult])
async def search_knowledge_base(
    payload: SearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Embed the search query
    query_vector = await generate_single_embedding(payload.query)

    # 2. Perform Cosine Similarity Search via pgvector
    results = await knowledge.search_similar_chunks(
        db=db,
        tenant_id=current_user.tenant_id,
        query_embedding=query_vector,
        top_k=payload.top_k
    )

    return results
