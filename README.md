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

## Phase 2 — observability & security with Datadog (next)

Instrumenting what already works before adding new features: the zero-trust
stack becomes **evidence** you can show (dashboards, alerts, SIEM). Plan in
[`docs/plans/observability-datadog.md`](docs/plans/observability-datadog.md).

- **Datadog Agent** on the host: logs + system/network metrics
- **Dashboard "Luanti Platform Overview"** across 4 layers: infra · network ·
  app · security
- **Rust exporters** (`rust/luanti-exporter/`): Prometheus metrics scraped by
  the Agent — game player count, uptime, and health signals
- **Alerts + Cloud SIEM**: UFW drops, auth anomalies, container restarts
- **GCP**: budgets, alerts, and Cloud Billing cost reports (FinOps)

> **Deferred:** the in-game chatbot (Dialogflow CX) is **Phase 6**, not now.
> The FastAPI scaffold is kept for the record in
> [`archive/bridge-chatbot-cx/`](archive/bridge-chatbot-cx/) — archived, not
> deleted, and not wired into this phase.

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
rust/            Rust exporters (luanti-exporter: Prometheus metrics)
infra/terraform/ GCP infrastructure as code (Phase 6, scaffold)
firewall/        UFW configuration and setup script
tailscale/       Tailscale setup notes
scripts/         install / status / reset
archive/         deferred work, kept for the record (bridge-chatbot-cx)
```

## Status

- Phase 0 (repo) ✅ · Phase 1 (playable server) ✅
- Phase 2 (observability & security with Datadog) — in progress
- Phase 6 (chatbot on GCP) — deferred

Full status, decisions and roadmap: [docs/ROADMAP.md](docs/ROADMAP.md).

## License

[Apache-2.0](LICENSE)
