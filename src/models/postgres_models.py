"""
SQLAlchemy models mirroring the PostgreSQL schema in architecture doc
Section 5.1 (paper_registry, chunk_registry, session_history).

These are used two ways:
  1. Alembic reads them to auto-generate migration files (schema-as-code).
  2. Application code (Phase 4 onward) uses them to read/write rows,
     instead of hand-writing raw SQL everywhere.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared base class all our table models inherit from."""
    pass


class PaperRegistry(Base):
    """
    One row per academic paper — whether it came from the local corpus,
    was fetched live from arXiv, or was uploaded by a user.
    Matches architecture doc Section 5.1.
    """
    __tablename__ = "paper_registry"

    paper_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    arxiv_id = Column(String(32), unique=True, nullable=True)
    doi = Column(String(128), nullable=True)
    title = Column(Text, nullable=False)
    authors = Column(JSONB, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    source_type = Column(String(20), nullable=True)
    trust_tier = Column(String(20), default="unverified")
    ingestion_status = Column(String(20), default="pending")
    raw_pdf_s3_path = Column(Text, nullable=True)
    parsed_doc_s3_path = Column(Text, nullable=True)
    citation_count = Column(Integer, default=0)
    parent_citations = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('local_corpus', 'arxiv_fetched', 'user_uploaded')",
            name="valid_source_type",
        ),
    )


class ChunkRegistry(Base):
    """
    One row per chunk produced during ingestion (Section 2.2 chunking).
    `vector_db_id` links this row to the corresponding point in Qdrant.
    Matches architecture doc Section 5.1.
    """
    __tablename__ = "chunk_registry"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(
        UUID(as_uuid=True),
        ForeignKey("paper_registry.paper_id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_type = Column(String(20), nullable=True)  # text|table|equation|figure_caption
    section_name = Column(String(128), nullable=True)
    page_number = Column(Integer, nullable=True)
    part_index = Column(Integer, default=0)
    token_count = Column(Integer, nullable=True)
    vector_db_id = Column(String(64), nullable=True)
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SessionHistory(Base):
    """
    One row per user query/response pair, for audit + analytics.
    `faithfulness_score` is retained per architecture doc Section 4.3 but
    stays NULL — the Output Guardrails layer that used to populate it has
    been intentionally removed.
    """
    __tablename__ = "session_history"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    query = Column(Text, nullable=True)
    route_taken = Column(String(20), nullable=True)
    confidence_score = Column(Float, nullable=True)
    response = Column(Text, nullable=True)
    citations = Column(JSONB, nullable=True)
    faithfulness_score = Column(Float, nullable=True)  # unused in v2, kept for compatibility
    latency_ms = Column(Integer, nullable=True)
    token_cost = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)