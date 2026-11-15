"""Structured JSON logging to stdout (Cloud Logging friendly).

Every record is emitted as a single-line JSON object. The ``extra`` dict passed
to the root ``bridge`` loggers is merged into the JSON payload so HTTP and app
fields land on the same record when shipped to Cloud Logging.
"""

from __future__ import annotations

import json
import logging
import sys
import time


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)
            ),
        }
        # Merge structured `extra` fields (http attrs, duration, etc.).
        for key, value in record.__dict__.items():
            if key.startswith("http") or key in {
                "duration_ms",
                "player",
                "intent",
                "session",
            }:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the ``bridge`` loggers to emit JSON to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger("bridge")
    root.setLevel(level)
    root.handlers = [handler]
    root.propagate = False
