# Security Policy

## Reporting a vulnerability

This is a home lab, but report issues privately by opening a GitHub issue with
the label `security` or by contacting the maintainer. Do not post secrets or
credentials in issues.

## Security model

- **Zero-trust network**: the game server is reachable **only** over Tailscale
  (the ACL); nothing is exposed to the public Internet **nor to the local LAN**.
- **DENY-by-default**: UFW drops all unapproved inbound traffic (Tailscale range only).
- **Least privilege**: services run as dedicated users/namespaces in a
  rootless Podman pod.
- **Secrets**: Google service account keys live in Secret Manager and are
  never committed.
- **Reproducible**: everything is described in this repo and rebuildable from
  scratch.

See `docs/threat-model.md`.
