# Luanti Network Lab — Design Spec

**Date:** 2026-08-14
**Status:** Approved
**Author:** nicolasjorquera-cloud

## 1. Purpose

A secure Luanti (Mineclonia) server for a parent and child (8–11 years old) to play
together, with a Dialogflow CX chatbot integrated into the in-game chat.

Beyond playing, the repository is a **professional portfolio artifact** demonstrating:

- Raw Linux / networking / security skills.
- Demonstrable GCP ecosystem expertise (IaC with Terraform, Secret Manager,
  Cloud Logging, Dialogflow CX, FinOps with Cloud Billing).
- Target role: AI Platform Engineer.

### MVP success criteria

1. Parent (Linux) and child (Windows) can play together over **Tailscale** only
   (zero-trust: no LAN path). Both devices are in the same tailnet.
2. The server is not exposed to the public Internet **nor to the local LAN**.
3. The chatbot answers when mentioned by name; it greets the player on join and
   proposes missions.
4. Blocking UDP 30000 (removing the UFW allow rule) demonstrably disconnects the client.
5. Zero secrets in the repository (gitleaks + strict `.gitignore`).

## 2. Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Deployment | Podman rootless + quadlet (pod) | Portfolio value, clean host, reproducible |
| Network | Tailscale on the host as the ACL; UFW DENY-by-default, Tailscale range only | VPN endpoint = identity layer; zero exposure to LAN or Internet |
| Game | Mineclonia | Familiar for the child (Minecraft-like) |
| Chatbot | Dialogflow CX (existing credits), deterministic intents | Cheap, fast, reliable for predictable questions |
| Bridge | Python (MVP) → Rust (Phase 4) | Official SDK + velocity; Rust as a learning target |
| Invocation | Mention the bot by name | Balance between naturalness and control |
| Bot name | "Mino" (configurable constant) | Short, playful; changeable in one place |
| Repo | Public GitHub, Apache-2.0, English-only, Conventional Commits, CI | Employability and visibility |
| GCP depth | GCP-first complete: Terraform CX agent, SA, Secret Manager, IAM, Cloud Logging, FinOps budget | Portfolio differentiation from day one |
| LLM usage | None in MVP (CX intents only, no data store, no bucket) | Respects "Dialogflow CX credits only" constraint |
| App Builder (data store) | Optional Phase 3 sub-phase (GCS bucket or wiki URL) | Uses App Builder credits, not required for MVP |

## 3. Architecture

```text
                    INTERNET
                       │ (nothing public)
            ┌──────────▼──────────┐
            │   Ubuntu host        │
            │  ┌────────────────┐  │
            │  │ Podman pod      │  │
            │  │  ├─ luanti     │  │  Mineclonia, :30000/udp
            │  │  └─ bridge     │  │  FastAPI → Dialogflow CX
            │  └────────────────┘  │
            │  Tailscale (ACL) +   │
            │  UFW (zero-trust)    │
            └──────────┬──────────┘
                       │ 100.x.x.x:30000 (Tailscale ONLY)
             ┌─────────┴─────────┐
             │                   │
        Ubuntu (parent)      Windows (child)
```

GCP side (existing project):

```text
GCP project
├── Dialogflow CX agent    → managed with Terraform (IA as code)
├── Service Account        → Dialogflow API role
├── Secret Manager         → service account JSON key
├── Cloud Logging          → bridge structured logs
└── Cloud Billing budget   → FinOps alert thresholds (50/90%)
```

No inbound webhook from GCP into the home: all bot responses live inside the CX
agent (deterministic intents). The bridge injects player context via session
params.

## 4. Chatbot data flow

```text
"bot, how do I make a crafting table?"
  ▼
Lua mod → strip bot name, http_fetch (async) → POST /chat
  ▼
Bridge → session per player, DetectIntent with context params
  ▼
Dialogflow CX → intent "crafting_table" → Spanish reply (8–11 tone)
  ▼
chat_send_player(player, reply)
```

- Sessions keyed by normalized player name.
- Welcome: `register_on_joinplayer` → `POST /welcome` with a small delay.
- Error handling: bridge down/timeout → friendly in-game fallback
  ("The owl is asleep, try again in a bit"); per-player cooldown (e.g. 3 s).

### How the bot "knows" things

Dialogflow CX is a deterministic intent classifier + state machine. It does not
use an LLM and knows nothing about Luanti on its own. Knowledge comes from
hand-written intents/flows/pages (recipes, missions, greetings) authored by us in
Terraform. No data store / bucket / LLM in the MVP.

## 5. Phases

| Phase | Deliverable |
|---|---|
| **0** | Professional scaffold: `git init`, English README / CONTRIBUTING / SECURITY / CODE_OF_CONDUCT / CHANGELOG, Apache-2.0 LICENSE, `.gitignore`, `.editorconfig`, GitHub Actions CI (lint, pytest, gitleaks, terraform fmt/validate), badges, repo structure. |
| **1** | Playable MVP: Tailscale (host + Windows), Podman rootless, Luanti + Mineclonia quadlet pod, UFW DENY-by-default Tailscale-only (zero-trust), `minetest.conf` whitelist, Windows client connect via Tailscale, verify disconnect when UDP 30000 is blocked. |
| **2** | Chatbot GCP-first: Terraform (CX agent / flows / intents / pages, Service Account, Secret Manager, IAM, billing budget); Dialogflow CX agent design (welcome, mission, crafting, fallback); Python bridge (FastAPI, `/chat` + `/welcome`, sessions, rate-limit, Cloud Logging structured logs); Lua mod `bot`; shared-token auth between mod and bridge; unit tests (mocked CX) + in-game tests; FinOps cost-report script. |
| **3** | Moderator + personality; optional App Builder data store (GCS bucket or wiki URL) for open-ended fallbacks; automated FinOps cost report via GitHub Actions cron. |
| **4** | Rust bridge port (`reqwest` + `jsonwebtoken` + `serde`, CX REST `:detectIntent`, token cache), Python as reference. |
| **5** | Optional: KVM VM, Vector observability, Rust `netwatch`. |

## 6. Repository structure

```text
luanti-network-lab/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── .gitignore
├── .editorconfig
├── docs/
│   ├── architecture.md
│   ├── threat-model.md
│   ├── gcp-architecture.md
│   └── experiments/
├── server/
│   ├── luanti/
│   │   ├── Containerfile
│   │   ├── luanti.container
│   │   ├── minetest.conf
│   │   └── mods/bot/init.lua
│   └── bridge/
│       ├── Containerfile
│       ├── bridge.container
│       ├── pyproject.toml
│       └── src/
├── infra/terraform/
│   ├── main.tf
│   ├── cx_agent.tf
│   ├── iam.tf
│   ├── secretmanager.tf
│   ├── billing.tf
│   └── variables.tf
├── finops/
│   ├── cost_report.py
│   └── README.md
├── firewall/
│   └── setup-ufw.sh
├── dialogflow/
│   └── agent-design.md
├── .github/workflows/
│   ├── ci.yml
│   └── gitleaks.yml
└── scripts/
    ├── install.sh
    ├── status.sh
    └── reset.sh
```

## 7. Testing

- Phase 1: Tailscale connection only; UFW allow rule add/remove for UDP 30000 →
  disconnect/reconnect observed.
- Phase 2: bridge unit tests (mocked Dialogflow), in-game tests (mention,
  welcome, fallback with bridge off), gitleaks in CI.
- Security: `nmap` from the LAN and from an external network (no Tailscale) shows
  **nothing** on trusted interfaces; only from a Tailscale device is
  30000/udp reachable. Nothing public, nothing on LAN.
- FinOps: billing budget + alert thresholds created by Terraform; cost report
  returns real data.

## 8. Security

- Service account JSON key in Secret Manager (not host volumes); bridge reads it
  via ADC. Never in the repository.
- gitleaks in CI; strict `.gitignore` (`.tfstate`, credential JSON, `.env`).
- UFW DENY-by-default (Tailscale range only); whitelist in `minetest.conf`;
  shared token between mod and bridge; AppArmor active.
