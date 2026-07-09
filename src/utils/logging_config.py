import logging
import os
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger.

    Log level is controlled by the ``LOG_LEVEL`` environment variable
    (default ``INFO``). Logs are emitted to stderr so they do not
    interfere with any data written to stdout.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
        logger.propagate = False
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level_name, logging.INFO))
    return logger
