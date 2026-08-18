# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository foundation (license, gitignore, editorconfig).
- Phase 0: professional scaffold with CI.
- Phase 1: secure playable Luanti server (Podman, Tailscale, nftables).

### Fixed
- Container build: fetch Mineclonia from a pinned release tarball (reproducible, resilient to CI runner issues) instead of mutable git HEAD.
