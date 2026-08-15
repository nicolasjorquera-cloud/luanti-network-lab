# Luanti Network Lab

A secure Luanti (Mineclonia) server for a parent and child to play together,
with a Dialogflow CX chatbot in the in-game chat.

This repository is a **portfolio-grade home lab**: a real, observable
infrastructure that teaches Linux, networking, security, containers, and the
Google Cloud ecosystem (Terraform IaC, Secret Manager, Cloud Logging,
Dialogflow CX, FinOps).

> The game is the interface. The infrastructure is the lesson.

## Features

- 🔒 Not exposed to the public Internet — private overlay via **Tailscale**
- 🧱 **DENY-by-default** host firewall with **nftables**
- 🐳 Server runs as a **Podman rootless pod** managed by systemd (quadlet)
- 🎮 **Mineclonia** game (Minecraft-like), world persisted in a volume
- 🤖 In-game chatbot powered by **Dialogflow CX** (Phase 2)
- 🌍 GCP resources as **Terraform IaC** (Phase 2)
- 💸 **FinOps**: budgets, alerts, and cost reporting (Phase 2)

## Repository layout

```text
docs/            Architecture, threat model, experiments
server/luanti/   Container image, quadlet unit, config, Lua mod
server/bridge/   Python bridge: Luanti chat ↔ Dialogflow CX (Phase 2)
infra/terraform/ GCP infrastructure as code (Phase 2)
finops/          Cloud Billing cost reporting (Phase 2)
firewall/        nftables configuration
scripts/         install / status / reset
tailscale/       VPN setup notes
```

## Getting started

Follow the phase 1 guides:

1. [Tailscale setup](tailscale/README.md)
2. [Server install](scripts/install.sh) (creates the Podman pod)
3. Connect clients (Linux + Windows) to `100.x.x.x:30000`

See `docs/architecture.md` for the full design and `docs/threat-model.md`
for the security model.

## License

[Apache-2.0](LICENSE)
