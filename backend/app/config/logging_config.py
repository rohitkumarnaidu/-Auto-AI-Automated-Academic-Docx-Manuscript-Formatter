"""
Logging Configuration for Backend
Provides structured logging with file rotation and console output.
"""

import logging
import logging.config
import os
from pathlib import Path

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",  # Show INFO, WARNING, and ERROR in console
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "errors.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    "loggers": {
        # Root logger
        "": {
            "level": "INFO",
            "handlers": ["console", "file", "error_file"]
        },
        # App-specific loggers
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "app.routers": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "app.pipeline": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "app.services": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
        # Suppress noisy third-party loggers
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",  # Show all HTTP requests (200, 404, etc.)
            "handlers": ["console"],
            "propagate": False
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        # Silence noisy HTTP and AI model loading logs
        "httpx": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        "transformers": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        "sentence_transformers": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        }
    }
}

def setup_logging():
    """Initialize logging configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized successfully")
    logger.info(f"Log files location: {LOGS_DIR.absolute()}")
    return logger
