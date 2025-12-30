"""Logging helpers for structured progress reporting."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def configure_logging(
    name: str = "market_simulation",
    log_dir: str | Path = "logs",
    run_id: Optional[int] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure a logger with console and file handlers.

    Parameters
    ----------
    name
        Logger name.
    log_dir
        Directory to store log files.
    run_id
        Optional run identifier to include in the log filename.
    level
        Logging level.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    suffix = f"_run_{run_id}" if run_id is not None else ""
    file_handler = logging.FileHandler(log_path / f"{name}{suffix}.log")
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_kv(logger: logging.Logger, message: str, **fields: object) -> None:
    """Log a structured message with key-value fields."""

    if fields:
        kv = " ".join(f"{key}={value}" for key, value in fields.items())
        logger.info("%s | %s", message, kv)
    else:
        logger.info("%s", message)
