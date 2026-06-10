import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    rows = relationship("DatasetRow", back_populates="dataset", cascade="all, delete-orphan")
    runs = relationship("EvaluationRun", back_populates="dataset", cascade="all, delete-orphan")

class DatasetRow(Base):
    __tablename__ = "dataset_rows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    dataset_id = Column(String, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    input_data = Column(JSONB, nullable=False)
    expected_output = Column(JSONB, nullable=True)

    dataset = relationship("Dataset", back_populates="rows")
    results = relationship("EvaluationResult", back_populates="row", cascade="all, delete-orphan")

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False, index=True)
    target_prompt_id = Column(String, ForeignKey("prompts.id"), nullable=True)
    status = Column(String, default="queued") # queued, running, completed, failed
    overall_score = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="runs")
    prompt = relationship("Prompt")
    results = relationship("EvaluationResult", back_populates="run", cascade="all, delete-orphan")

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    run_id = Column(String, ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    row_id = Column(String, ForeignKey("dataset_rows.id"), nullable=False, index=True)
    actual_output = Column(JSONB, nullable=True)
    score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)

    run = relationship("EvaluationRun", back_populates="results")
    row = relationship("DatasetRow", back_populates="results")
