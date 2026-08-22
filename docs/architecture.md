# Architecture

## Overview

```text
                    INTERNET
                       │ (nothing public)
            ┌──────────▼──────────┐
            │   Ubuntu host        │
            │  ┌────────────────┐  │
            │  │ Podman pod      │  │
            │  │  ├─ luanti     │  │  Mineclonia, :30000/udp
            │  │  └─ bridge     │  │  FastAPI → Dialogflow CX (Phase 2)
            │  └────────────────┘  │
            │  Tailscale (ACL) +   │
            │  UFW (zero-trust)    │
            └──────────┬──────────┘
                       │ 100.x.x.x:30000 (Tailscale ONLY)
             ┌─────────┴─────────┐
             │                   │
        Ubuntu (parent)      Windows (child)
```

> **Zero trust:** there is no LAN path. The game binds only to the `tailscale0`
> interface. A device outside the tailnet — whether on the public Internet or on
> the physical LAN — is dropped by UFW.

## Components

- **Tailscale (host)**: private overlay network (WireGuard). The VPN endpoint
  lives on the host; containers publish ports onto the `tailscale0` interface.
- **UFW (host)**: DENY-by-default host firewall. **Only** UDP 30000 from the
  Tailscale network range (`100.64.0.0/10`) is allowed. Nothing binds to the
  physical LAN; those sources fall through to UFW's default drop policy.
- **Podman (rootless)**: the `luanti` container runs unprivileged (container
  root maps to the host user). Managed by an explicit systemd user unit
  (`server/luanti/luanti.service`, deployed by `scripts/deploy-luanti-service.sh`).
  Quadlet units are provided (`luanti.pod` / `luanti.container`) for hosts where
  the podman system generator is available; stale user managers may not re-run
  generators, so the explicit unit is the default.
- **Luanti + Mineclonia**: game server with persistent world volume.
- **Bridge (Phase 2)**: Python FastAPI service that forwards in-game chat to
  Dialogflow CX and returns replies.

See `docs/gcp-architecture.md` (added in Phase 2) for the GCP side.
