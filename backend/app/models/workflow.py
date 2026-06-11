import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="workflows")
    nodes = relationship("WorkflowNode", backref="workflow", cascade="all, delete-orphan")
    edges = relationship("WorkflowEdge", backref="workflow", cascade="all, delete-orphan")


class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"

    id = Column(String, primary_key=True) # Mapped to frontend React Flow node IDs
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), primary_key=True)
    node_type = Column(String, nullable=False) # 'llm', 'tool', 'router', '__start__', '__end__'
    config = Column(JSONB, nullable=True) # LLM model, prompt text, tool bindings


class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"

    id = Column(String, primary_key=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), primary_key=True)
    source_node_id = Column(String, nullable=False)
    target_node_id = Column(String, nullable=False)
    condition_type = Column(String, nullable=True) # 'always', 'conditional'
    condition_config = Column(JSONB, nullable=True) # Rules for conditional edges
