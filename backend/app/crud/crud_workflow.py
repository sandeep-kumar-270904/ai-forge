from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.workflow import Workflow, WorkflowNode, WorkflowEdge
from app.schemas.workflow import WorkflowCreate

class CRUDWorkflow:
    
    async def create_workflow(self, db: AsyncSession, tenant_id: UUID, obj_in: WorkflowCreate) -> Workflow:
        # 1. Create Workflow Container
        db_workflow = Workflow(
            tenant_id=tenant_id,
            name=obj_in.name,
            description=obj_in.description
        )
        db.add(db_workflow)
        await db.commit()
        await db.refresh(db_workflow)

        # 2. Add Nodes
        db_nodes = []
        for node_data in obj_in.nodes:
            db_nodes.append(
                WorkflowNode(
                    id=node_data.id,
                    workflow_id=db_workflow.id,
                    node_type=node_data.node_type,
                    config=node_data.config
                )
            )
        
        # 3. Add Edges
        db_edges = []
        for edge_data in obj_in.edges:
            db_edges.append(
                WorkflowEdge(
                    id=edge_data.id,
                    workflow_id=db_workflow.id,
                    source_node_id=edge_data.source_node_id,
                    target_node_id=edge_data.target_node_id,
                    condition_type=edge_data.condition_type,
                    condition_config=edge_data.condition_config
                )
            )

        db.add_all(db_nodes)
        db.add_all(db_edges)
        await db.commit()
        
        # 4. Refresh to return full tree
        return await self.get_workflow_with_graph(db, db_workflow.id, tenant_id)

    async def get_workflow_with_graph(self, db: AsyncSession, workflow_id: UUID, tenant_id: UUID) -> Optional[Workflow]:
        stmt = (
            select(Workflow)
            .options(selectinload(Workflow.nodes), selectinload(Workflow.edges))
            .filter(Workflow.id == workflow_id, Workflow.tenant_id == tenant_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()
        
    async def get_all_workflows(self, db: AsyncSession, tenant_id: UUID) -> List[Workflow]:
        stmt = (
            select(Workflow)
            .filter(Workflow.tenant_id == tenant_id)
            .order_by(Workflow.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

crud_workflow = CRUDWorkflow()
