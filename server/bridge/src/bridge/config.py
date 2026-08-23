"""Configuration for the Luanti bridge.

All values can be overridden with environment variables (prefix ``LUANTI_``)
so the same image runs anywhere: local dev, the Podman pod, or a GCP context.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, read from the environment (prefix ``LUANTI_``)."""

    model_config = SettingsConfigDict(
        env_prefix="LUANTI_", env_file=".env", extra="ignore"
    )

    # --- GCP / Dialogflow CX -------------------------------------------------
    project_id: str = Field(
        default="",
        description="GCP project that owns the Dialogflow CX agent",
    )
    location: str = Field(
        default="global", description="CX agent location (global|region)"
    )
    agent_id: str = Field(
        default="",
        description="Dialogflow CX agent ID (a 36-char UUID)",
    )
    # Automatically forward the OAuth token with x-goog-user-project to fix the
    # ADC "quota project" error when using user ADC credentials.
    billing_project: str = Field(
        default="", description="Billing/quota project for ADC"
    )

    # --- HTTP server -----------------------------------------------------------
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)

    # --- Auth (shared token between the Lua mod and this bridge) ---------------
    bridge_token: str = Field(
        default="", description="Shared token required in X-Bridge-Token"
    )

    # --- Chatbot behaviour ------------------------------------------------------
    bot_name: str = Field(default="Mino", description="How players mention the bot")
    language_code: str = Field(default="es", description="CX language for DetectIntent")
    welcome_message: str = Field(
        default=(
            "¡Hola! Soy Mino. Pregúntame por ejemplo: "
            "bot, ¿cómo se hace una mesa de crafteo?"
        ),
        description="Reply when a player joins (used when CX is unreachable)",
    )
    fallback_message: str = Field(
        default="El búho está dormido, inténtalo de nuevo en un rato.",
        description="Friendly reply when CX is down or errors",
    )
    cooldown_seconds: float = Field(
        default=3.0, description="Per-player cooldown between calls"
    )
    cx_timeout_seconds: float = Field(
        default=3.0, description="Time to wait for Dialogflow CX"
    )

    @property
    def cx_session_prefix(self) -> str:
        """Dialogueflow session parent: projects/*/locations/*/agents/*."""
        if not (self.project_id and self.agent_id):
            raise RuntimeError("LUANTI_PROJECT_ID and LUANTI_AGENT_ID are required")
        return f"projects/{self.project_id}/locations/{self.location}/agents/{self.agent_id}"  # noqa: E501


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()
