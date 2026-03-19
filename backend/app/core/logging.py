"""Structured JSON logging for Cloud Run / Cloud Logging."""

import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone

request_id_var: ContextVar[str] = ContextVar("request_id", default="no-request")


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON for Cloud Logging.

    Cloud Logging parses the 'severity' field natively from stdout JSON.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, str] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with JSON formatter.

    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Invalid values fall back to INFO.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    root = logging.getLogger()
    # Remove any existing handlers (e.g. from basicConfig)
    root.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
    root.setLevel(numeric_level)
