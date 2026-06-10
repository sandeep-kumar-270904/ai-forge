from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.knowledge import Document, DocumentChunk
from app.schemas.knowledge import SearchResult

class CRUDKnowledge:
    
    async def create_document(self, db: AsyncSession, tenant_id: UUID, name: str, file_type: str) -> Document:
        doc = Document(tenant_id=tenant_id, name=name, file_type=file_type)
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc
        
    async def update_document_status(self, db: AsyncSession, document_id: UUID, status: str):
        doc = await db.get(Document, document_id)
        if doc:
            doc.status = status
            await db.commit()
            
    async def insert_chunks(self, db: AsyncSession, chunks: List[DocumentChunk]):
        db.add_all(chunks)
        await db.commit()
        
    async def search_similar_chunks(self, db: AsyncSession, tenant_id: UUID, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        # Using pgvector cosine distance (<=>)
        stmt = (
            select(
                DocumentChunk, 
                DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
            )
            .filter(DocumentChunk.tenant_id == tenant_id)
            .order_by("distance")
            .limit(top_k)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        results = []
        for row in rows:
            chunk = row[0]
            distance = row[1]
            similarity_score = 1.0 - float(distance) # Convert distance to similarity
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    metadata=chunk.metadata,
                    similarity_score=similarity_score
                )
            )
        return results

knowledge = CRUDKnowledge()
