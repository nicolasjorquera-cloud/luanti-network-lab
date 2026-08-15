#!/usr/bin/env bash
# Ensures rootless Podman is installed. Idempotent: skips if podman exists.
# Ubuntu ships podman in its repos; the upstream kubic repo is only a fallback.
set -euo pipefail

if command -v podman >/dev/null 2>&1; then
  echo "==> podman already installed: $(podman --version)"
  podman system migrate
  exit 0
fi

echo "==> Installing podman from the distribution repository"
sudo apt-get update
sudo apt-get install -y podman

if ! command -v podman >/dev/null; then
  echo "podman install failed" >&2
  exit 1
fi
podman system migrate
echo "==> Podman version: $(podman --version)"
echo "Verify with: podman info"
