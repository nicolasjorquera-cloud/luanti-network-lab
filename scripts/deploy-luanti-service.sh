#!/usr/bin/env bash
# Deploys the Luanti systemd user unit with the real Tailscale + LAN IPs.
# Uses an explicit Type=simple unit (reliable on user managers) instead of
# quadlet, which needs the podman-system-generator (unavailable on stale
# user managers — see docs/architecture.md).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TS_IP="$(tailscale ip -4 2>/dev/null || true)"
if [[ -z "${TS_IP}" ]]; then
  echo "ERROR: tailscale not up. Run: sudo tailscale up" >&2
  exit 1
fi
LAN_IP="$(hostname -I | awk '{print $1}')"
echo "==> Tailscale IP: ${TS_IP}   LAN IP: ${LAN_IP}"

mkdir -p ~/.config/systemd/user
sed -e "s/%TS_IP%/${TS_IP}/" -e "s/%LAN_IP%/${LAN_IP}/" \
  "${SCRIPT_DIR}/../server/luanti/luanti.service" \
  > ~/.config/systemd/user/luanti.service

systemctl --user daemon-reload
systemctl --user enable --now luanti

echo "==> Status:"
systemctl --user status luanti --no-pager | head -6
