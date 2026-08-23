"""Minimal Dialogflow CX client.

Talks to the CX REST API (``:detectIntent``) using Application Default
Credentials (ADC) and ``httpx``. We deliberately use the REST API directly
instead of the google-cloud-dialogflow-cx SDK so the HTTP request is explicit
and easy to inspect — and because it lets us set ``x-goog-user-project``, which
fixes the ADC "quota project" error when running with user credentials.

Everything is executable with zero GCP credentials: if auth or the agent
cannot be reached we raise a ``CxUnavailable`` and the app falls back to the
friendly in-game message (fail-closed, never crashes the bridge).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import google.auth  # type: ignore[import-not-found]
import httpx

from .config import Settings

logger = logging.getLogger("bridge.cx")

# Base for the global location. Agent addresses returned by the API already
# include the right regional endpoint; for the common "global" case this is it.
CX_BASE = "https://dialogflow.googleapis.com"


@dataclass
class CxReply:
    """The part of a DetectIntent response the bridge cares about."""

    text: str
    session: str
    intent: str | None = None
    confidence: float = 0.0


class CxUnavailable(Exception):
    """Raised when Dialogflow CX cannot be reached or errors."""


class CxClient:
    """Thin REST client for Dialogflow CX :detectIntent."""

    def __init__(
        self, settings: Settings, http: httpx.AsyncClient | None = None
    ) -> None:
        self.settings = settings
        self._http = http or httpx.AsyncClient(timeout=settings.cx_timeout_seconds)

    def _token(self) -> str:
        """Return an OAuth2 access token from ADC.

        ``google.auth.default`` hands back credentials that may already carry a
        token (service account / user ADC); if not, we refresh them with a
        blocking ``Request``. This runs rarely (on request) and is fine here.
        """
        try:
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            if not credentials.token:
                from google.auth.transport.requests import Request

                credentials.refresh(Request())
            return credentials.token
        except Exception as exc:  # noqa: BLE001 - credentials can fail many ways
            raise CxUnavailable(f"could not get ADC token: {exc}") from exc

    def session_name(self, player: str) -> str:
        """Return the CX session resource for a normalized player name."""
        session_id = _normalize(player)
        return f"{self.settings.cx_session_prefix}/sessions/{session_id}"

    async def detect_intent(
        self,
        player: str,
        text: str,
        params: dict[str, str] | None = None,
    ) -> CxReply:
        """Send ``text`` to the agent and return its textual reply."""
        session = self.session_name(player)
        url = f"{CX_BASE}/v3/{session}:detectIntent"

        payload: dict = {
            "queryInput": {
                "text": {"text": text},
                "languageCode": self.settings.language_code,
            },
        }
        if params:
            payload["queryParams"] = {"parameters": params}

        headers = {"Authorization": f"Bearer {self._token()}"}
        if self.settings.billing_project:
            headers["x-goog-user-project"] = self.settings.billing_project

        try:
            resp = await self._http.post(url, json=payload, headers=headers)
        except (httpx.HTTPError, OSError) as exc:
            raise CxUnavailable(f"network error talking to CX: {exc}") from exc

        if resp.status_code >= 400:
            logger.warning(
                "CX responded HTTP %s: %s", resp.status_code, resp.text[:300]
            )
            raise CxUnavailable(f"CX HTTP {resp.status_code}")

        body = resp.json()
        response_messages = (body.get("queryResult") or {}).get(
            "responseMessages"
        ) or []
        text = "".join(
            m.get("text", {}).get("text", [""])[0]
            for m in response_messages
            if "text" in m
        ).strip()

        intent = (
            (body.get("queryResult") or {})
            .get("match", {})
            .get("intent", {})
            .get("displayName")
        )
        confidence = float(
            (body.get("queryResult") or {}).get("match", {}).get("confidence", 0.0)
            or 0.0
        )
        return CxReply(text=text, session=session, intent=intent, confidence=confidence)

    async def aclose(self) -> None:
        await self._http.aclose()


def _normalize(player: str) -> str:
    """Session IDs must be stable and URL-safe; player names may contain dots."""
    return (
        "".join(c if c.isalnum() else "_" for c in player.lower()).strip("_") or "anon"
    )
