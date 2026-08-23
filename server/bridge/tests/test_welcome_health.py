"""Tests for the welcome and health endpoints."""

from __future__ import annotations


def _auth() -> dict[str, str]:
    return {"X-Bridge-Token": "test-token"}


def test_welcome_returns_greeting(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings)
    resp = client.post("/welcome", json={"player": "bob"}, headers=_auth())
    assert resp.status_code == 200
    assert "Mino" in resp.json()["message"]


def test_welcome_requires_auth(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings)
    assert client.post("/welcome", json={"player": "bob"}).status_code == 401


def test_healthz_open_without_auth(make_client, bridge_settings) -> None:  # noqa: ANN001
    client, _ = make_client(bridge_settings)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
