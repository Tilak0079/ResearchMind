"""
Creates the Qdrant collection matching the point structure defined in
architecture doc Section 5.2 — a single collection with two NAMED vectors
per point ("dense" and "sparse"), since BGE-m3 produces both from one
model call and we fuse them natively inside Qdrant (Section 2.3).

Run this file directly to create the collection if it doesn't exist yet:
    python -m src.models.qdrant_schema
"""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, SparseVectorParams, VectorParams

from src.config import settings
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

COLLECTION_NAME = "paper_chunks"

# BGE-m3 dense embeddings are 1024-dimensional (see architecture doc Section 5.2 example payload)
DENSE_VECTOR_SIZE = 1024


def create_collection_if_not_exists() -> None:
    """
    Creates the 'paper_chunks' Qdrant collection if it doesn't already exist.
    Safe to run multiple times — does nothing if the collection is already there.
    """
    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    existing_collections = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME in existing_collections:
        logger.info("Qdrant collection '%s' already exists — skipping creation.", COLLECTION_NAME)
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=DENSE_VECTOR_SIZE, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(),
        },
    )
    logger.info("Created Qdrant collection '%s' with dense + sparse named vectors.", COLLECTION_NAME)


if __name__ == "__main__":
    create_collection_if_not_exists()