# Luanti Network Lab

A secure, observable home lab built around a private **Luanti (Mineclonia)**
server that a parent and child play together — with an in-game **Dialogflow CX**
chatbot and GCP infrastructure as code.

> The game is the interface. The infrastructure is the lesson.

## Purpose

This repository is a **portfolio-grade home lab** demonstrating raw Linux,
networking, security, container, and GCP skills — all reproducible from this
repo, all running on existing hardware, all at **$0 cloud cost** (Google
credits only).

Two tracks:

1. **Play & learn** — a secure Luanti (Mineclonia) server for a parent and child:
   - **Zero-trust networking**: reachable **only** via a private **Tailscale**
     overlay that acts as the access-control layer (ACL). Never public Internet,
     never LAN — Tailscale is the only path in.
   - **DENY-by-default** host firewall (**UFW**): only traffic from the Tailscale
     network range is allowed in; everything else (including LAN) is dropped.
   - Server as a **Podman rootless** container managed by systemd
2. **GCP / AI platform** — an in-game chatbot powered by **Dialogflow CX**:
   - The CX agent is managed as **Terraform IaC**
   - Secrets in **Secret Manager**, structured logs in **Cloud Logging**
   - **FinOps**: budgets, alerts, and Cloud Billing cost reports

## Principles

- **Zero trust**: no one is trusted by default. Tailscale identity is the only
  key to the network; UFW drops everything else (including LAN).
- **Observable**: every control can be inspected and deliberately broken
  (block UDP 30000 → clients disconnect).
- **Least privilege**: rootless containers, explicit network access.
- **Reproducible**: rebuild everything from this repo.

## Layout

```text
docs/            architecture, threat model, security lab notes
server/luanti/   container image, systemd unit, config
server/bridge/   Python bridge: Luanti chat ↔ Dialogflow CX
infra/terraform/ GCP infrastructure as code (scaffold)
firewall/        UFW configuration and setup script
tailscale/       Tailscale setup notes
scripts/         install / status / reset
```

## Status

- Phase 0 (repo) ✅ · Phase 1 (playable server) ✅
- Phase 2 (chatbot GCP) — planned

Full status, decisions and roadmap: [docs/ROADMAP.md](docs/ROADMAP.md).

## License

[Apache-2.0](LICENSE)
