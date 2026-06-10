import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

swarm_agents_association = Table(
    "swarm_agents",
    Base.metadata,
    Column("swarm_id", String, ForeignKey("swarms.id", ondelete="CASCADE"), primary_key=True),
    Column("agent_id", String, ForeignKey("swarm_agent_personas.id", ondelete="CASCADE"), primary_key=True)
)

class SwarmAgentPersona(Base):
    __tablename__ = "swarm_agent_personas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    role_description = Column(Text, nullable=False)
    system_prompt_id = Column(String, ForeignKey("prompts.id"), nullable=True)
    tools = Column(JSONB, nullable=True) # List of tool names
    created_at = Column(DateTime, default=datetime.utcnow)

    swarms = relationship("Swarm", secondary=swarm_agents_association, back_populates="agents")

class Swarm(Base):
    __tablename__ = "swarms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    supervisor_prompt_id = Column(String, ForeignKey("prompts.id"), nullable=True)
    max_loops = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)

    agents = relationship("SwarmAgentPersona", secondary=swarm_agents_association, back_populates="swarms")
