# Luanti Network Lab

A secure, observable home lab built around a private **Luanti (Mineclonia)**
server that a parent and child play together — with an in-game **Dialogflow CX**
chatbot, GCP infrastructure as code, and an isolated **offensive security
practice range**.

> The game is the interface. The infrastructure — and the attacks — are the lesson.

## Purpose

This repository is a **portfolio-grade home lab** demonstrating raw Linux,
networking, security, container, and GCP skills, plus hands-on offensive
security — all reproducible from this repo, all running on existing hardware,
all at **$0 cloud cost** (Google credits only).

Three tracks:

1. **Play & learn** — a secure Luanti (Mineclonia) server for a parent and child:
   - Reachable only via a private **Tailscale** overlay (never public Internet)
   - **DENY-by-default** host firewall (**nftables**)
   - Server as a **Podman rootless** container managed by systemd
2. **GCP / AI platform** — an in-game chatbot powered by **Dialogflow CX**:
   - The CX agent is managed as **Terraform IaC**
   - Secrets in **Secret Manager**, structured logs in **Cloud Logging**
   - **FinOps**: budgets, alerts, and Cloud Billing cost reports
3. **Offensive security range** — practice attacks against **your own isolated
   VMs**: a full **DNS attack lab** (spoofing, poisoning, tunneling,
   exfiltration, rebinding, enumeration) plus a general red-team playground.

## Principles

- **Observable**: every control can be inspected and deliberately broken
  (block UDP 30000 → clients disconnect).
- **Least privilege**: rootless containers, explicit network access.
- **Reproducible**: rebuild everything from this repo.
- **Safe**: offensive practice only against owned, isolated infrastructure.

## Layout

```text
docs/            architecture, threat model, security lab notes
server/luanti/   container image, systemd unit, config
server/bridge/   Python bridge: Luanti chat ↔ Dialogflow CX (Phase 2)
infra/terraform/ GCP infrastructure as code (Phase 2)
finops/          Cloud Billing cost reporting (Phase 2)
firewall/        nftables configuration
security/        offensive lab (DNS attacks, parental visibility)
scripts/         install / status / reset
```

## Status

- Phase 0 (repo) ✅ · Phase 1 (playable server) ✅
- Phase 2 (chatbot GCP) · Phase 3 (offensive DNS lab) — in progress

## License

[Apache-2.0](LICENSE)
