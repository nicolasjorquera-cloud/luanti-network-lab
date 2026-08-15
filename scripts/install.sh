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

echo "==> [5/5] Initializing data and deploying systemd service"
"${SCRIPT_DIR}/init-data.sh"
"${SCRIPT_DIR}/deploy-luanti-service.sh"

echo "==> Done. Get the Tailscale IP with: scripts/status.sh"
