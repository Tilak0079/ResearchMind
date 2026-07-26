"""
Phase 2 health check.

Confirms that all four infra services (Postgres, Redis, Qdrant, MinIO) are
running and reachable using the credentials in .env. Run this after
`docker compose up -d` to confirm everything is wired up correctly before
moving on to later phases.
"""

import logging

import psycopg
import redis
from qdrant_client import QdrantClient
import boto3
from botocore.exceptions import ClientError

from src.config import settings
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def check_postgres() -> bool:
    """Tries to open a connection and run a trivial query against Postgres."""
    try:
        conn_string = (
            f"host={settings.postgres_host} "
            f"port={settings.postgres_port} "
            f"dbname={settings.postgres_db} "
            f"user={settings.postgres_user} "
            f"password={settings.postgres_password}"
        )
        with psycopg.connect(conn_string, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        logger.info("Postgres: OK")
        return True
    except psycopg.OperationalError as e:
        logger.error("Postgres: FAILED — %s", e)
        return False


def check_redis() -> bool:
    """Tries to ping the Redis server."""
    try:
        client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            socket_connect_timeout=5,
        )
        client.ping()
        logger.info("Redis: OK")
        return True
    except redis.exceptions.ConnectionError as e:
        logger.error("Redis: FAILED — %s", e)
        return False


def check_qdrant() -> bool:
    """Tries to list collections from Qdrant (works even with zero collections)."""
    try:
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=5)
        client.get_collections()
        logger.info("Qdrant: OK")
        return True
    except Exception as e:  # qdrant-client raises varied exception types on connection failure
        logger.error("Qdrant: FAILED — %s", e)
        return False


def check_minio() -> bool:
    """Tries to list buckets from MinIO using the S3-compatible API."""
    try:
        client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_root_user,
            aws_secret_access_key=settings.minio_root_password,
        )
        client.list_buckets()
        logger.info("MinIO: OK")
        return True
    except ClientError as e:
        logger.error("MinIO: FAILED — %s", e)
        return False


def main() -> None:
    """Runs all four connectivity checks and reports overall pass/fail."""
    logger.info("Phase 2 health check starting...")

    results = {
        "postgres": check_postgres(),
        "redis": check_redis(),
        "qdrant": check_qdrant(),
        "minio": check_minio(),
    }

    if all(results.values()):
        logger.info("Phase 2 health check PASSED — all services reachable.")
    else:
        failed = [name for name, ok in results.items() if not ok]
        logger.error("Phase 2 health check FAILED for: %s", ", ".join(failed))


if __name__ == "__main__":
    main()