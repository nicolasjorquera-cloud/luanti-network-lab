#!/usr/bin/env bash
# Installs the host firewall for the lab (DENY-by-default, Tailscale-only).
#
# The host firewall is UFW (see docs/decisions/ADR-001-networking-zero-trust.md
# and firewall/setup-ufw.sh); we deliberately do NOT install a standalone
# nftables table because `flush ruleset` would clash with Docker/libvirt/
# Tailscale. This script just delegates to the UFW setup.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "${SCRIPT_DIR}/../firewall/setup-ufw.sh"
