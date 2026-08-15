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
            │  Tailscale + nftables│
            └──────────┬──────────┘
                       │ 100.x.x.x:30000 (Tailscale) + LAN
             ┌─────────┴─────────┐
             │                   │
        Ubuntu (parent)      Windows (child)
```

## Components

- **Tailscale (host)**: private overlay network (WireGuard). The VPN endpoint
  lives on the host; containers publish ports onto the `tailscale0` interface.
- **nftables (host)**: DENY-by-default host firewall. Only UDP 30000 on
  trusted interfaces (tailscale0, LAN) is allowed.
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
