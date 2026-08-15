#!/usr/bin/env bash
# Creates the host-side data directory for the Luanti pod.
set -euo pipefail

DATA_DIR="${LUANTI_DATA_DIR:-/home/beerus/luanti-data}"

mkdir -p "${DATA_DIR}/world" "${DATA_DIR}/subgames"
cp /home/beerus/luanti/server/luanti/minetest.conf "${DATA_DIR}/minetest.conf"

# Seed the Mineclonia subgame from the container image (so it survives rebuilds).
# --user 0 maps to the host user in rootless podman, so it can write the copy.
podman run --rm --user 0 \
  -v "${DATA_DIR}/subgames:/target" \
  --entrypoint /bin/sh \
  localhost/luanti-network-lab/luanti:latest \
  -c "cp -rn /var/lib/luanti/subgames/mineclonia /target/ || true"

echo "==> Data dir ready at ${DATA_DIR}"
ls -la "${DATA_DIR}"
