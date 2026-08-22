#!/usr/bin/env bash
# Prepares the host-side configuration for the Luanti container.
# The world lives in the Podman named volume `luanti-world`, not on the host.
set -euo pipefail

CONFIG_DIR="${LUANTI_CONFIG_DIR:-$HOME/luanti-data}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${CONFIG_DIR}"
cp "${SCRIPT_DIR}/../server/luanti/minetest.conf" "${CONFIG_DIR}/minetest.conf"

echo "==> Config dir ready at ${CONFIG_DIR}"
ls -la "${CONFIG_DIR}"
