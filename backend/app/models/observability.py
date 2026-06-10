import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    workflow_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="running") # running, success, failed
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    spans = relationship("AgentSpan", back_populates="run", cascade="all, delete-orphan")


class AgentSpan(Base):
    __tablename__ = "agent_spans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    trace_id = Column(String, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_span_id = Column(String, ForeignKey("agent_spans.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    span_type = Column(String, nullable=False) # node, tool, llm, chain
    input_payload = Column(JSONB, nullable=True)
    output_payload = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    run = relationship("AgentRun", back_populates="spans")
    children = relationship("AgentSpan", back_populates="parent", remote_side=[id])
    parent = relationship("AgentSpan", back_populates="children")
