#!/usr/bin/env bash
# Creates the host-side data directory for the Luanti pod.
set -euo pipefail

DATA_DIR="${LUANTI_DATA_DIR:-/home/beerus/luanti-data}"

mkdir -p "${DATA_DIR}/world"
cp /home/beerus/luanti/server/luanti/minetest.conf "${DATA_DIR}/minetest.conf"

echo "==> Data dir ready at ${DATA_DIR}"
ls -la "${DATA_DIR}"
