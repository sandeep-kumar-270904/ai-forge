from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.swarms import SwarmCreate, SwarmResponse, SwarmAgentPersonaCreate, SwarmAgentPersonaResponse, SwarmInvokeRequest
from ..crud.crud_swarms import swarm, swarm_agent
from ..ai.swarms.executor import SwarmExecutor

router = APIRouter()

@router.post("/agents", response_model=SwarmAgentPersonaResponse)
async def create_agent(
    obj_in: SwarmAgentPersonaCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await swarm_agent.create(db, obj_in=obj_in, tenant_id=current_user.tenant_id)

@router.get("/agents", response_model=List[SwarmAgentPersonaResponse])
async def list_agents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await swarm_agent.get_by_tenant(db, tenant_id=current_user.tenant_id)

@router.post("/", response_model=SwarmResponse)
async def create_swarm(
    obj_in: SwarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await swarm.create_with_agents(db, obj_in=obj_in, tenant_id=current_user.tenant_id)

@router.get("/", response_model=List[SwarmResponse])
async def list_swarms(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await swarm.get_by_tenant(db, tenant_id=current_user.tenant_id)

@router.post("/{swarm_id}/invoke")
async def invoke_swarm(
    swarm_id: str,
    request: SwarmInvokeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await SwarmExecutor.invoke_swarm(db, swarm_id=swarm_id, input_message=request.input_message)
