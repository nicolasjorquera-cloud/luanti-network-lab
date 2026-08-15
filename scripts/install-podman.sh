#!/usr/bin/env bash
# Installs rootless Podman from the official upstream repo (Debian/Ubuntu).
set -euo pipefail

. /etc/os-release

echo "==> Installing Podman (upstream repo) on ${ID} ${VERSION_CODENAME}"

if [[ -f /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list ]]; then
  echo "Podman repo already configured."
else
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/${VERSION_CODENAME}/Release.key" \
    | sudo gpg --dearmor -o /etc/apt/keyrings/libcontainers.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/libcontainers.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/${VERSION_CODENAME}/" \
    | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
fi

sudo apt-get update
sudo apt-get install -y podman

if ! command -v podman >/dev/null; then
  echo "podman install failed" >&2
  exit 1
fi
podman system migrate
echo "==> Podman version: $(podman --version)"
echo "Verify with: podman info"
