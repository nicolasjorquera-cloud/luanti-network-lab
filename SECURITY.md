# Security Policy

## Reporting a vulnerability

This is a home lab, but report issues privately by opening a GitHub issue with
the label `security` or by contacting the maintainer. Do not post secrets or
credentials in issues.

## Security model

- **Private network**: the game server is reachable only over Tailscale and the
  local LAN — never exposed to the public Internet.
- **DENY-by-default**: nftables drops all unapproved inbound traffic.
- **Least privilege**: services run as dedicated users/namespaces in a
  rootless Podman pod.
- **Secrets**: Google service account keys live in Secret Manager and are
  never committed.
- **Reproducible**: everything is described in this repo and rebuildable from
  scratch.

See `docs/threat-model.md`.
