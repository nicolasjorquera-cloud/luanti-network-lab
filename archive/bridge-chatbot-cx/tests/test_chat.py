"""Tests for the bridge chat endpoint."""

from __future__ import annotations

from tests.conftest import FakeCx


def _auth() -> dict[str, str]:
    return {"X-Bridge-Token": "test-token"}


def test_chat_returns_cx_reply(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, cx = make_client(bridge_settings)
    resp = client.post(
        "/chat", json={"player": "bob", "message": "hola"}, headers=_auth()
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "respuesta de prueba"
    assert body["intent"] == "test_intent"
    assert cx.last_text == "hola"
    assert cx.last_player == "bob"


def test_chat_strips_bot_name(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, cx = make_client(bridge_settings)
    resp = client.post(
        "/chat",
        json={"player": "bob", "message": "Mino: cómo hago una mesa"},
        headers=_auth(),
    )
    assert resp.status_code == 200
    assert cx.last_text == "cómo hago una mesa"


def test_chat_requires_auth(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings)
    resp = client.post("/chat", json={"player": "bob", "message": "hola"})
    assert resp.status_code == 401


def test_chat_wrong_token_rejected(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings)
    resp = client.post(
        "/chat",
        json={"player": "bob", "message": "hola"},
        headers={"X-Bridge-Token": "wrong"},
    )
    assert resp.status_code == 401


def test_chat_rate_limited(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings, cooldown=60)
    ok = client.post(
        "/chat", json={"player": "bob", "message": "hola"}, headers=_auth()
    )
    limited = client.post(
        "/chat", json={"player": "bob", "message": "hola"}, headers=_auth()
    )
    assert ok.status_code == 200
    assert limited.status_code == 429


def test_chat_falls_back_when_cx_down(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings, cx=FakeCx(fail=True))
    resp = client.post(
        "/chat", json={"player": "bob", "message": "hola"}, headers=_auth()
    )
    assert resp.status_code == 200
    assert bridge_settings.fallback_message in resp.json()["reply"]
