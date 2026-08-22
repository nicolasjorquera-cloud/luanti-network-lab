# Luanti Network Lab

A secure, observable home lab built around a private **Luanti (Mineclonia)**
server that a parent and child play together — with GCP / AI infrastructure on
the roadmap.

> The game is the interface. The infrastructure is the lesson.

[![CI](https://github.com/nicolasjorquera-cloud/luanti-network-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/nicolasjorquera-cloud/luanti-network-lab/actions/workflows/ci.yml)
[![gitleaks](https://github.com/nicolasjorquera-cloud/luanti-network-lab/actions/workflows/gitleaks.yml/badge.svg)](https://github.com/nicolasjorquera-cloud/luanti-network-lab/actions/workflows/gitleaks.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

## Purpose

This repository is a **portfolio-grade home lab** demonstrating raw Linux,
networking, security, and container skills — reproducible from this repo and
running on existing hardware at **$0 cloud cost** (Google credits only).

## Phase 1 — secure playable server (done)

A secure Luanti (Mineclonia) server for a parent and child:

- **Zero-trust networking**: reachable **only** via a private **Tailscale**
  overlay that acts as the access-control layer (ACL). Never public Internet,
  never LAN — Tailscale is the only path in.
- **DENY-by-default** host firewall (**UFW**): only traffic from the Tailscale
  network range is allowed in; everything else (including LAN) is dropped.
- Server as a **Podman rootless** container managed by systemd.

## Planned (Phase 2) — chatbot on GCP

An in-game chatbot powered by **Dialogflow CX**, managed as GCP infrastructure
as code. Scaffolds only — **not implemented yet**:

- A CX agent managed as **Terraform IaC** (`infra/terraform/`, scaffold)
- A **Python bridge** exposing `Luanti chat ↔ Dialogflow CX`
  (`server/bridge/`, scaffold)
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
server/bridge/   Python bridge: Luanti chat ↔ Dialogflow CX (Phase 2, scaffold)
infra/terraform/ GCP infrastructure as code (Phase 2, scaffold)
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
