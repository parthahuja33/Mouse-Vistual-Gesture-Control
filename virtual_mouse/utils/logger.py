"""Centralised logging configuration for the virtual mouse project."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import ConfigManager

_LOGGER_NAME = "virtual_mouse"
_INITIALISED = False


def configure_logging(
    level: str | None = None,
    log_to_file: Optional[bool] = None,
    filepath: Optional[str] = None,
) -> logging.Logger:
    """Configure and return the root project logger."""

    global _INITIALISED

    config = ConfigManager().get()
    logger = logging.getLogger(_LOGGER_NAME)

    resolved_level = (level or config.logging.level).upper()
    resolved_log_to_file = log_to_file if log_to_file is not None else config.logging.log_to_file
    resolved_path = filepath or config.logging.filepath

    logger.setLevel(resolved_level)

    if not _INITIALISED:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        logger.addHandler(stream_handler)

        if resolved_log_to_file:
            path = Path(resolved_path or "logs/virtual_mouse.log")
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=5)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
            )
            logger.addHandler(file_handler)

        logger.propagate = False
        _INITIALISED = True

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a module specific child logger."""

    return logging.getLogger(f"{_LOGGER_NAME}.{name}")

