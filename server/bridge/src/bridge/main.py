"""CLI entrypoint: runs the FastAPI app with uvicorn."""

from __future__ import annotations

import uvicorn

from .app import create_app
from .config import get_settings
from .logging_config import setup_logging


def run() -> None:  # pragma: no cover - thin CLI wrapper
    setup_logging()
    settings = get_settings()
    uvicorn.run(
        create_app(settings),
        host=settings.host,
        port=settings.port,
        log_level="info",
        access_log=False,  # our structured middleware logs requests
    )


if __name__ == "__main__":
    run()
