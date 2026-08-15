#!/usr/bin/env bash
# One-shot installer: Tailscale, Podman, firewall, image, and pod.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> [1/5] Installing Podman"
"${SCRIPT_DIR}/install-podman.sh"

echo "==> [2/5] Installing Tailscale"
if ! command -v tailscale >/dev/null 2>&1; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi
sudo tailscale up --advertise-tags=tag:home --ssh=false || sudo tailscale up

echo "==> [3/5] Installing firewall"
"${SCRIPT_DIR}/install-firewall.sh"

echo "==> [4/5] Building Luanti image"
podman build -t localhost/luanti-network-lab/luanti:latest "${SCRIPT_DIR}/../server/luanti"

echo "==> [5/5] Initializing data and starting pod"
"${SCRIPT_DIR}/init-data.sh"

# Fill real publish IPs before deploying units
TS_IP="$(tailscale ip -4 2>/dev/null || true)"
LAN_IP="$(hostname -I | awk '{print $1}')"
sed -e "s/100.64.0.0/${TS_IP}/" -e "s/192.168.0.0/${LAN_IP}/" \
  "${SCRIPT_DIR}/../server/luanti/luanti.container" > ~/.config/containers/systemd/luanti.container

mkdir -p ~/.config/containers/systemd
cp "${SCRIPT_DIR}/../server/luanti/luanti.pod" ~/.config/containers/systemd/

systemctl --user daemon-reload
systemctl --user enable --now luanti-pod luanti-container

echo "==> Done. Get the Tailscale IP with: scripts/status.sh"
