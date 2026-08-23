"""FastAPI application for the Luanti bridge.

Endpoints
---------
- ``POST /chat``    -- forward a player's in-game message to Dialogflow CX.
- ``POST /welcome`` -- return a greeting for a player who just joined.
- ``GET  /healthz`` -- liveness probe for the container.

Security
--------
- Every request (except ``/healthz``) must present the shared token in the
  ``X-Bridge-Token`` header (the Lua mod holds the same secret).
- Per-player cooldown to stop spam.

Observability
-------------
- Structured JSON logs on stdout (Cloud Logging friendly).
- Fail-closed: if Dialogflow CX cannot be reached the bridge replies with a
  friendly fallback instead of crashing the game chat.
"""

from __future__ import annotations

import logging
import secrets
import time
from collections import defaultdict

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from .config import Settings, get_settings
from .cx_client import CxClient, CxUnavailable

logger = logging.getLogger("bridge.app")


# --------------------------------------------------------------------------- #
# Rate limiter
# --------------------------------------------------------------------------- #
class RateLimiter:
    """Simple per-key sliding window. One request allowed every ``cooldown``s."""

    def __init__(self, cooldown: float) -> None:
        self.cooldown = cooldown
        self._last: dict[str, float] = defaultdict(float)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = now if now is not None else time.monotonic()
        if now - self._last[key] < self.cooldown:
            return False
        self._last[key] = now
        return True


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class ChatIn(BaseModel):
    player: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=500)


class WelcomeIn(BaseModel):
    player: str = Field(min_length=1, max_length=64)


class ChatOut(BaseModel):
    reply: str
    session: str
    intent: str | None = None


class WelcomeOut(BaseModel):
    message: str


class HealthOut(BaseModel):
    status: str = "ok"


# --------------------------------------------------------------------------- #
# App factory
# --------------------------------------------------------------------------- #
def create_app(
    settings: Settings | None = None,
    cx_factory=None,  # noqa: ANN001 - callable() -> CxClient, injectable for tests
) -> FastAPI:
    settings = settings or get_settings()
    limiter = RateLimiter(settings.cooldown_seconds)

    if cx_factory is None:

        def cx_factory() -> CxClient:
            return CxClient(settings)

    app = FastAPI(title="Luanti bridge", version="0.1.0")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):  # noqa: ANN001, ANN202
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "request",
            extra={
                "http": {
                    "request": {
                        "method": request.method,
                        "url": str(request.url.path),
                    },
                    "response": {"statusCode": response.status_code},
                },
                "duration_ms": round(duration_ms, 1),
            },
        )
        return response

    def _auth(token: str = Header(default="", alias="X-Bridge-Token")) -> str:
        if not settings.bridge_token:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "bridge token not configured"
            )
        if not secrets.compare_digest(token, settings.bridge_token):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid bridge token")
        return token

    def _rate_limit(player: str) -> None:
        if not limiter.allow(player):
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "slow down")

    def _strip_bot_name(message: str) -> str:
        """Remove a leading '<botname,' / '<botname:" / '<botname ' mention."""
        lowered = message.lstrip().lower()
        name_len = len(settings.bot_name)
        for sep in (",", ":", " "):
            if lowered.startswith(settings.bot_name.lower() + sep):
                return message.lstrip()[name_len + len(sep) :].lstrip()
        return message

    async def _cx_or_fallback(player: str, text: str) -> tuple[str, str, str | None]:
        """Return (reply, session, intent). Falls back on any CX failure."""
        cx = cx_factory()
        try:
            result = await cx.detect_intent(player, text, params={"player": player})
            reply = result.text or settings.fallback_message
            return reply, result.session, result.intent
        except CxUnavailable as exc:
            logger.warning("CX unavailable for %s: %s", player, exc)
            return settings.fallback_message, "", None
        finally:
            await cx.aclose()

    @app.get("/healthz", response_model=HealthOut, include_in_schema=False)
    async def healthz() -> HealthOut:
        return HealthOut()

    @app.post("/chat", response_model=ChatOut)
    async def chat(body: ChatIn, _: str = Depends(_auth)) -> ChatOut:
        _rate_limit(body.player)
        text = _strip_bot_name(body.message)
        if not text:
            return ChatOut(reply=settings.welcome_message, session="")
        reply, session, intent = await _cx_or_fallback(body.player, text)
        return ChatOut(reply=reply, session=session, intent=intent)

    @app.post("/welcome", response_model=WelcomeOut)
    async def welcome(body: WelcomeIn, _: str = Depends(_auth)) -> WelcomeOut:
        _rate_limit(f"welcome:{body.player}")
        return WelcomeOut(message=settings.welcome_message)

    return app


app = create_app()
