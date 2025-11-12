"""Centralized logging configuration."""
import logging
import os
from typing import Optional

LOG_LEVEL = os.environ.get("RAG_MED_ASSISTANT_LOG_LEVEL", "INFO").upper()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger with a consistent format."""
    logger = logging.getLogger(name or "rag_medical_backend")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False
    return logger

