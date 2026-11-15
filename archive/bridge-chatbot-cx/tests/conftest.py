"""Shared fixtures for the bridge tests."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from bridge.cx_client import CxReply


@dataclass
class FakeCx:
    """Injectable stand-in for CxClient used by the app via ``cx_factory``."""

    reply: CxReply = field(
        default_factory=lambda: CxReply(
            text="respuesta de prueba", session="sessions/test", intent="test_intent"
        )
    )
    fail: bool = False
    last_text: str | None = None
    last_player: str | None = None

    async def detect_intent(self, player: str, text: str, params=None) -> CxReply:  # noqa: ANN001
        if self.fail:
            from bridge.cx_client import CxUnavailable

            raise CxUnavailable("fake CX down")
        self.last_player = player
        self.last_text = text
        return self.reply

    async def aclose(self) -> None:
        return None


@pytest.fixture
def bridge_settings():
    from bridge.config import Settings

    return Settings(
        project_id="test-project",
        agent_id="11111111-2222-3333-4444-555555555555",
        bridge_token="test-token",
        cooldown_seconds=0.001,  # effectively no cooldown for most tests
    )


@pytest.fixture
def make_client():
    """Build a FastAPI TestClient with an injectable fake CX client."""

    def _make(settings, cx: FakeCx | None = None, cooldown: float | None = None):
        from fastapi.testclient import TestClient

        from bridge.app import create_app

        if cx is None:
            cx = FakeCx()
        if cooldown is not None:
            settings.cooldown_seconds = cooldown

        def factory() -> FakeCx:
            return cx

        app = create_app(settings=settings, cx_factory=factory)
        return TestClient(app), cx

    return _make
