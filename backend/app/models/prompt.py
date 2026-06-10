import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_prompt_tenant_name'),
    )

    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")
    deployments = relationship("PromptDeployment", back_populates="prompt", cascade="all, delete-orphan")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    prompt_id = Column(String, ForeignKey("prompts.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSONB, nullable=False, default=list) # e.g. [{"name": "tone", "type": "string"}]
    status = Column(String, default="draft", index=True) # draft, in_review, approved, rejected
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('prompt_id', 'version_number', name='uq_prompt_version'),
    )

    prompt = relationship("Prompt", back_populates="versions")
    author = relationship("User")


class PromptDeployment(Base):
    __tablename__ = "prompt_deployments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    prompt_id = Column(String, ForeignKey("prompts.id"), nullable=False, index=True)
    version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=False)
    environment = Column(String, nullable=False, index=True) # development, staging, production
    deployed_by = Column(String, ForeignKey("users.id"), nullable=False)
    deployed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('prompt_id', 'environment', name='uq_prompt_environment'),
    )

    prompt = relationship("Prompt", back_populates="deployments")
    version = relationship("PromptVersion")
    deployer = relationship("User")
