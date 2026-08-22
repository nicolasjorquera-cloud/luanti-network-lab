#!/usr/bin/env bash
# Deploys the Luanti systemd user unit bound ONLY to the Tailscale IP.
# Talks only to the tailscale0 interface (zero-trust: no LAN path).
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
CONFIG_DIR="${LUANTI_CONFIG_DIR:-$HOME/luanti-data}"
echo "==> Tailscale IP: ${TS_IP}   Config dir: ${CONFIG_DIR}"

mkdir -p ~/.config/systemd/user
sed -e "s/%TS_IP%/${TS_IP}/" \
    -e "s|%CONFIG_DIR%|${CONFIG_DIR}|g" \
  "${SCRIPT_DIR}/../server/luanti/luanti.service" \
  > ~/.config/systemd/user/luanti.service

systemctl --user daemon-reload
systemctl --user enable --now luanti

echo "==> Status:"
systemctl --user status luanti --no-pager | head -6

