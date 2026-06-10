from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.prompt import PromptCreate, PromptResponse, PromptVersionCreate, PromptVersionResponse, PromptDeploymentResponse, PromptExecuteRequest
from ..ai.prompts.service import PromptService
from ..crud.crud_prompt import prompt, prompt_version, prompt_deployment

router = APIRouter()

@router.post("/", response_model=PromptResponse)
async def create_prompt(
    obj_in: PromptCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await PromptService.create_prompt(db, tenant_id=current_user.tenant_id, author_id=current_user.id, obj_in=obj_in)

@router.post("/{prompt_id}/versions", response_model=PromptVersionResponse)
async def create_prompt_version(
    prompt_id: str,
    obj_in: PromptVersionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await PromptService.create_new_version(db, prompt_id=prompt_id, author_id=current_user.id, obj_in=obj_in)

@router.post("/versions/{version_id}/submit")
async def submit_prompt_for_review(
    version_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await PromptService.submit_for_review(db, version_id=version_id, user_id=current_user.id)

@router.post("/versions/{version_id}/approve")
async def approve_prompt(
    version_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await PromptService.approve_version(db, version_id=version_id, reviewer_id=current_user.id)

@router.post("/{prompt_id}/deploy", response_model=PromptDeploymentResponse)
async def deploy_prompt(
    prompt_id: str,
    version_id: str,
    environment: str = "production",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await PromptService.deploy_version(
        db, prompt_id=prompt_id, version_id=version_id, environment=environment, deployer_id=current_user.id
    )

@router.get("/{prompt_id}/diff")
async def get_prompt_diff(
    prompt_id: str,
    v1: int,
    v2: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    diff = await PromptService.get_version_diff(db, prompt_id=prompt_id, v1=v1, v2=v2)
    return {"diff": diff}
    
@router.post("/{prompt_name}/execute")
async def execute_prompt(
    prompt_name: str,
    request: PromptExecuteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    p = await prompt.get_by_name(db, tenant_id=current_user.tenant_id, name=prompt_name)
    if not p:
        raise HTTPException(status_code=404, detail="Prompt not found")
        
    deployment = await prompt_deployment.get_active_deployment(db, prompt_id=p.id, environment=request.environment)
    if not deployment:
        raise HTTPException(status_code=404, detail=f"No active deployment for environment {request.environment}")
        
    active_version = deployment.version
    rendered_content = PromptService.render_prompt(active_version.content, request.variables)
    
    return {"rendered_prompt": rendered_content, "version_number": active_version.version_number}
