"""
Sets up logging for the whole app.

Instead of using print() statements (which are hard to filter, can't show
severity levels, and don't include timestamps by default), we configure
Python's built-in `logging` module once here. Every other file just does:

    import logging
    logger = logging.getLogger(__name__)
    logger.info("something happened")

and it will automatically follow the format/level configured below.
"""

import logging

from src.config import settings


def setup_logging() -> None:
    """
    Configures the root logger. Call this once, at application startup
    (e.g. at the top of main.py or a health-check script).
    """
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )