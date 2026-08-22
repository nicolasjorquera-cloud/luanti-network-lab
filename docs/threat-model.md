# Threat Model

## Trusted

- Parent, child, owned computers
- Private Tailscale network (**the only trusted path**)

## Untrusted

- Public Internet
- **Local LAN / Wi-Fi** — NOT trusted (zero-trust: same as the Internet)
- Unknown network traffic
- Unexpected connection attempts
- Unnecessary exposed services

## Principles

1. **Zero trust** — Tailscale identity is the only ACL. Nothing binds to the
   physical LAN; `tailscale0` is the single ingress path.
2. **Minimize exposure** — nothing public, **nothing on LAN**.
3. **Least privilege** — rootless containers, dedicated users.
4. **Explicit access** — UFW allows only what is required (Tailscale range).
5. **Observable behavior** — blocking UDP 30000 disconnects clients.
6. **Reproducible** — everything rebuildable from this repo.

## Attack surface

- Luanti UDP 30000 — reachable **only** over Tailscale (`tailscale0`). No LAN
  exposure by design.
- SSH on the host — restricted to Tailscale only (recommended: `tailscale0:22`).
- Tailscale DNS — only `100.100.100.100:53` accepted from `tailscale0`.
- GCP APIs — protected by IAM service accounts (Phase 2).

## Tailscale as ACL (the design)

Tailscale is more than a VPN here: it **is** the access-control layer. Device
identity in the tailnet is what grants access to the game. UFW does not trust
any device address; it allows the Tailscale network range and drops everything
else. A device not in the tailnet — whether on the public Internet *or the local
LAN* — is indistinguishable from an attacker and is dropped.
