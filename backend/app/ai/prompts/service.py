import difflib
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ...crud.crud_prompt import prompt, prompt_version, prompt_deployment
from ...schemas.prompt import PromptCreate, PromptVersionCreate

class PromptService:
    @staticmethod
    async def create_prompt(db: AsyncSession, *, tenant_id: str, author_id: str, obj_in: PromptCreate):
        existing = await prompt.get_by_name(db, tenant_id=tenant_id, name=obj_in.name)
        if existing:
            raise HTTPException(status_code=400, detail="Prompt with this name already exists")
        return await prompt.create_with_version(db, obj_in=obj_in, tenant_id=tenant_id, author_id=author_id)

    @staticmethod
    async def create_new_version(db: AsyncSession, *, prompt_id: str, author_id: str, obj_in: PromptVersionCreate):
        latest = await prompt_version.get_latest_version(db, prompt_id=prompt_id)
        if not latest:
            raise HTTPException(status_code=404, detail="Prompt not found")
            
        new_v_num = latest.version_number + 1
        variables_dict = [v.model_dump() for v in obj_in.variables]
        
        from ...models.prompt import PromptVersion
        db_version = PromptVersion(
            prompt_id=prompt_id,
            version_number=new_v_num,
            content=obj_in.content,
            variables=variables_dict,
            status="draft",
            author_id=author_id
        )
        db.add(db_version)
        await db.commit()
        await db.refresh(db_version)
        return db_version

    @staticmethod
    def get_diff(old_content: str, new_content: str) -> str:
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile='Old Version',
            tofile='New Version',
            lineterm=''
        )
        return '\n'.join(list(diff))

    @staticmethod
    async def get_version_diff(db: AsyncSession, *, prompt_id: str, v1: int, v2: int):
        version1 = await prompt_version.get_by_number(db, prompt_id=prompt_id, version_number=v1)
        version2 = await prompt_version.get_by_number(db, prompt_id=prompt_id, version_number=v2)
        if not version1 or not version2:
             raise HTTPException(status_code=404, detail="One or both versions not found")
        return PromptService.get_diff(version1.content, version2.content)

    @staticmethod
    async def submit_for_review(db: AsyncSession, *, version_id: str, user_id: str):
        version = await prompt_version.get(db, id=version_id)
        if not version:
             raise HTTPException(status_code=404, detail="Version not found")
        if version.status != "draft":
             raise HTTPException(status_code=400, detail="Only drafts can be submitted for review")
        
        version.status = "in_review"
        db.add(version)
        await db.commit()
        return version

    @staticmethod
    async def approve_version(db: AsyncSession, *, version_id: str, reviewer_id: str):
        version = await prompt_version.get(db, id=version_id)
        if not version:
             raise HTTPException(status_code=404, detail="Version not found")
        if version.status != "in_review":
             raise HTTPException(status_code=400, detail="Only versions in review can be approved")
        
        # Strict Maker/Checker enforcement
        if version.author_id == reviewer_id:
             raise HTTPException(status_code=403, detail="Maker/Checker Policy Violation: Author cannot approve their own prompt version")
             
        version.status = "approved"
        db.add(version)
        await db.commit()
        return version

    @staticmethod
    async def deploy_version(db: AsyncSession, *, prompt_id: str, version_id: str, environment: str, deployer_id: str):
        version = await prompt_version.get(db, id=version_id)
        if not version:
             raise HTTPException(status_code=404, detail="Version not found")
        if version.status != "approved":
             raise HTTPException(status_code=400, detail="Only approved versions can be deployed")
             
        return await prompt_deployment.deploy_version(
            db, 
            prompt_id=prompt_id, 
            version_id=version_id, 
            environment=environment, 
            deployed_by=deployer_id
        )

    @staticmethod
    def render_prompt(content: str, variables: Dict[str, Any]) -> str:
        rendered = content
        for k, v in variables.items():
            rendered = rendered.replace(f"{{{{{k}}}}}", str(v))
        return rendered
