from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.swarms import SwarmAgentPersona, Swarm
from ..schemas.swarms import SwarmAgentPersonaCreate, SwarmCreate
from .base import CRUDBase

class CRUDSwarmAgent(CRUDBase[SwarmAgentPersona, SwarmAgentPersonaCreate, SwarmAgentPersonaCreate]):
    async def get_by_tenant(self, db: AsyncSession, *, tenant_id: str) -> List[SwarmAgentPersona]:
        result = await db.execute(
            select(SwarmAgentPersona).filter(SwarmAgentPersona.tenant_id == tenant_id)
        )
        return list(result.scalars().all())

class CRUDSwarm(CRUDBase[Swarm, SwarmCreate, SwarmCreate]):
    async def create_with_agents(self, db: AsyncSession, *, obj_in: SwarmCreate, tenant_id: str) -> Swarm:
        db_obj = Swarm(
            tenant_id=tenant_id,
            name=obj_in.name,
            description=obj_in.description,
            supervisor_prompt_id=obj_in.supervisor_prompt_id,
            max_loops=obj_in.max_loops
        )
        db.add(db_obj)
        await db.flush()
        
        if obj_in.agent_ids:
            agents_result = await db.execute(select(SwarmAgentPersona).filter(SwarmAgentPersona.id.in_(obj_in.agent_ids)))
            agents = agents_result.scalars().all()
            db_obj.agents.extend(agents)
            
        await db.commit()
        await db.refresh(db_obj)
        
        result = await db.execute(
            select(Swarm).filter(Swarm.id == db_obj.id).options(selectinload(Swarm.agents))
        )
        return result.scalars().first()
        
    async def get_with_agents(self, db: AsyncSession, *, id: str) -> Optional[Swarm]:
        result = await db.execute(
            select(Swarm).filter(Swarm.id == id).options(selectinload(Swarm.agents))
        )
        return result.scalars().first()
        
    async def get_by_tenant(self, db: AsyncSession, *, tenant_id: str) -> List[Swarm]:
         result = await db.execute(
            select(Swarm)
            .filter(Swarm.tenant_id == tenant_id)
            .options(selectinload(Swarm.agents))
        )
         return list(result.scalars().all())

swarm_agent = CRUDSwarmAgent(SwarmAgentPersona)
swarm = CRUDSwarm(Swarm)
