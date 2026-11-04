# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository foundation (license, gitignore, editorconfig).
- Phase 0: professional scaffold with CI.
- Phase 1: secure playable Luanti server (Podman rootless, Tailscale as ACL, UFW zero-trust firewall).
- CI: `shellcheck` job for all shell scripts.

### Fixed
- Firewall: `firewall/setup-ufw.sh` now actually enforces deny-by-default (`ufw default deny incoming`, `ufw --force enable`) instead of only adding an allow rule; refuses to run over SSH unless `SSH_VIA_TAILSCALE=1` or `ALLOW_SSH_LOCKOUT=1` is set.
- Container build: fetch Mineclonia from a pinned release tarball (reproducible, resilient to CI runner issues) instead of mutable git HEAD.
