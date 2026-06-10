from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.prompt import Prompt, PromptVersion, PromptDeployment
from ..schemas.prompt import PromptCreate, PromptVersionCreate
from .base import CRUDBase

class CRUDPrompt(CRUDBase[Prompt, PromptCreate, PromptCreate]):
    async def get_by_name(self, db: AsyncSession, *, tenant_id: str, name: str) -> Optional[Prompt]:
        result = await db.execute(
            select(Prompt)
            .filter(Prompt.tenant_id == tenant_id, Prompt.name == name)
            .options(selectinload(Prompt.versions))
        )
        return result.scalars().first()

    async def create_with_version(self, db: AsyncSession, *, obj_in: PromptCreate, tenant_id: str, author_id: str) -> Prompt:
        db_prompt = Prompt(
            tenant_id=tenant_id,
            name=obj_in.name,
            description=obj_in.description
        )
        db.add(db_prompt)
        await db.flush()
        
        variables_dict = [v.model_dump() for v in obj_in.variables]
        
        db_version = PromptVersion(
            prompt_id=db_prompt.id,
            version_number=1,
            content=obj_in.initial_content,
            variables=variables_dict,
            status="draft",
            author_id=author_id
        )
        db.add(db_version)
        await db.commit()
        await db.refresh(db_prompt)
        return db_prompt

class CRUDPromptVersion(CRUDBase[PromptVersion, PromptVersionCreate, PromptVersionCreate]):
    async def get_latest_version(self, db: AsyncSession, *, prompt_id: str) -> Optional[PromptVersion]:
        result = await db.execute(
            select(PromptVersion)
            .filter(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
        )
        return result.scalars().first()
        
    async def get_by_number(self, db: AsyncSession, *, prompt_id: str, version_number: int) -> Optional[PromptVersion]:
        result = await db.execute(
            select(PromptVersion)
            .filter(PromptVersion.prompt_id == prompt_id, PromptVersion.version_number == version_number)
        )
        return result.scalars().first()

class CRUDPromptDeployment(CRUDBase[PromptDeployment, PromptDeployment, PromptDeployment]):
    async def get_active_deployment(self, db: AsyncSession, *, prompt_id: str, environment: str) -> Optional[PromptDeployment]:
        result = await db.execute(
            select(PromptDeployment)
            .filter(PromptDeployment.prompt_id == prompt_id, PromptDeployment.environment == environment)
            .options(selectinload(PromptDeployment.version))
        )
        return result.scalars().first()
        
    async def deploy_version(self, db: AsyncSession, *, prompt_id: str, version_id: str, environment: str, deployed_by: str) -> PromptDeployment:
        existing = await self.get_active_deployment(db, prompt_id=prompt_id, environment=environment)
        if existing:
            existing.version_id = version_id
            existing.deployed_by = deployed_by
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            new_dep = PromptDeployment(
                prompt_id=prompt_id,
                version_id=version_id,
                environment=environment,
                deployed_by=deployed_by
            )
            db.add(new_dep)
            await db.commit()
            await db.refresh(new_dep)
            return new_dep

prompt = CRUDPrompt(Prompt)
prompt_version = CRUDPromptVersion(PromptVersion)
prompt_deployment = CRUDPromptDeployment(PromptDeployment)
