#!/usr/bin/env bash
# Configure UFW for the Luanti lab (zero-trust: Tailscale only).
#
# The host runs UFW + Docker + libvirt + Tailscale. UFW is the single source of
# truth for host input rules; we do NOT install a standalone nftables table,
# because `flush ruleset` would tear down Docker/libvirt/Tailscale rules.
#
# It opens UDP 30000 to the whole Tailscale CGNAT range. Which identities may
# hold a tailnet address is controlled by the Tailscale ACL, not by this rule.
set -euo pipefail

TS_RANGE="100.64.0.0/10"
PORT="30000"
PROTO="udp"

echo "==> Applying UFW rules for Luanti (${PORT}/${PROTO} from ${TS_RANGE})"

# Allow the game only from the Tailscale range.
sudo ufw allow from "${TS_RANGE}" to any port "${PORT}" proto "${PROTO}" comment "Luanti (Mineclonia) via Tailscale"

# Tailscale DNS is handled by MagicDNS; no extra rule required.

echo "==> Current UFW status (game port):"
sudo ufw status verbose | grep -E "${PORT}|Status" || true

echo "==> Done. Review with: sudo ufw status verbose"
