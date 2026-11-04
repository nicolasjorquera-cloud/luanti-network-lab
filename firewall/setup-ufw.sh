#!/usr/bin/env bash
# Configure UFW for the Luanti lab (zero-trust: Tailscale only).
#
# The host runs UFW + Docker + libvirt + Tailscale. UFW is the single source of
# truth for host input rules; we do NOT install a standalone nftables table,
# because `flush ruleset` would tear down Docker/libvirt/Tailscale rules.
#
# Policy: deny all incoming, allow all outgoing, then open UDP 30000 to the
# Tailscale CGNAT range only. Which identities may hold a tailnet address is
# controlled by the Tailscale ACL, not by this rule.
set -euo pipefail

TS_RANGE="100.64.0.0/10"
PORT="30000"
PROTO="udp"

# Deny-by-default also blocks new SSH logins (LAN or Tailscale). Refuse to run
# from an SSH session unless the operator chose how to keep access.
#   SSH_VIA_TAILSCALE=1  also allow TCP 22 on the tailscale0 interface
#   ALLOW_SSH_LOCKOUT=1  proceed anyway (you have console access)
SSH_VIA_TAILSCALE="${SSH_VIA_TAILSCALE:-0}"
if [[ -n "${SSH_CONNECTION:-}" && "${SSH_VIA_TAILSCALE}" != "1" && "${ALLOW_SSH_LOCKOUT:-0}" != "1" ]]; then
  echo "!! Running over SSH: deny-by-default would block new SSH logins." >&2
  echo "!! Re-run with SSH_VIA_TAILSCALE=1 (keep SSH over Tailscale only)" >&2
  echo "!! or ALLOW_SSH_LOCKOUT=1 (you have console access)." >&2
  exit 1
fi

echo "==> Setting default policies (deny incoming, allow outgoing)"
sudo ufw default deny incoming
sudo ufw default allow outgoing

echo "==> Allowing Luanti (${PORT}/${PROTO}) from ${TS_RANGE} only"
sudo ufw allow from "${TS_RANGE}" to any port "${PORT}" proto "${PROTO}" comment "Luanti (Mineclonia) via Tailscale"

if [[ "${SSH_VIA_TAILSCALE}" == "1" ]]; then
  echo "==> Allowing SSH (22/tcp) on tailscale0 only"
  sudo ufw allow in on tailscale0 to any port 22 proto tcp comment "SSH via Tailscale"
fi

# Tailscale DNS is handled by MagicDNS; no extra rule required.

echo "==> Enabling UFW"
sudo ufw --force enable

echo "==> Current UFW status:"
sudo ufw status verbose

echo "==> Done."
