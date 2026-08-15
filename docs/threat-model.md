# Threat Model

## Trusted

- Parent, child, owned computers
- Private Tailscale network

## Untrusted

- Public Internet
- Unknown network traffic
- Unexpected connection attempts
- Unnecessary exposed services

## Principles

1. **Minimize exposure** — nothing public.
2. **Least privilege** — rootless containers, dedicated users.
3. **Explicit access** — nftables allows only what is required.
4. **Observable behavior** — blocking UDP 30000 disconnects clients.
5. **Reproducible** — everything rebuildable from this repo.

## Attack surface

- Luanti UDP 30000 — reachable only over Tailscale and LAN.
- SSH on the host — restrict to trusted sources (recommended: Tailscale only).
- GCP APIs — protected by IAM service accounts (Phase 2).
