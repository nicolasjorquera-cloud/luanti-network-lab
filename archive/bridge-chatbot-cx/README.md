# Luanti bridge

FastAPI service that connects the in-game chat to **Dialogflow CX** (Phase 2).

```
"bot, how do I make a crafting table?"
  ▼  (Lua mod → http_fetch → POST /chat)
bridge → per-player session → DetectIntent (CX REST)
  ▼
Dialogflow CX → deterministic intent → reply
  ▼  (chat_send_player)
player sees the bot's answer
```

## Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/chat` | `X-Bridge-Token` | Forward a player message to CX; returns the bot reply |
| `POST` | `/welcome` | `X-Bridge-Token` | Return the join greeting for a player |
| `GET` | `/healthz` | none | Liveness probe for the container |

Requests to `/chat` (`{player, message}`) and `/welcome` (`{player}`) take JSON.
The bridge strips a leading `Mino:` / `Mino,` mention before calling CX.

## Configuration (env)

All variables are optional except those marked ★ (the bridge needs the agent to
reach CX; without them it replies with the friendly fallback).

| Env | Default | Purpose |
|---|---|---|
| `LUANTI_PROJECT_ID` ★ | — | GCP project owning the CX agent |
| `LUANTI_AGENT_ID` ★ | — | Dialogflow CX agent UUID |
| `LUANTI_LOCATION` | `global` | CX agent location |
| `LUANTI_BILLING_PROJECT` | `""` | Set to fix the ADC "quota project" error |
| `LUANTI_BRIDGE_TOKEN` ★ | `""` | Shared secret the Lua mod sends in `X-Bridge-Token` |
| `LUANTI_BOT_NAME` | `Mino` | The mention word stripped before CX |
| `LUANTI_PORT` | `8080` | HTTP port |
| `LUANTI_COOLDOWN_SECONDS` | `3.0` | Per-player anti-spam window |
| `LUANTI_FALLBACK_MESSAGE` | (the owl…) | Reply when CX is down |

## Run locally

```bash
pip install -e ".[dev]"
pytest                       # unit tests (Dialogflow CX mocked)
ruff check src tests

# point at a real agent:
export LUANTI_PROJECT_ID=<project> LUANTI_AGENT_ID=<agent> LUANTI_BRIDGE_TOKEN=<token>
luanti-bridge
```

Authentication to GCP uses Application Default Credentials
(`gcloud auth application-default login`). The client sets `x-goog-user-project`
from `LUANTI_BILLING_PROJECT` so user ADC works.

## Design notes

- Deterministic intents only — no LLM in the MVP (see `docs/specs/…/design.md`).
- **Fail-closed**: if CX is unreachable the bridge returns the friendly
  fallback instead of erroring the game chat.
- Structured JSON logs on stdout, ready for Cloud Logging.
