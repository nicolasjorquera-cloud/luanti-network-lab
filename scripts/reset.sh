#!/usr/bin/env bash
# Stops the pod and reloads the firewall. Does not delete the world.
set -euo pipefail

echo "==> Stopping pod"
systemctl --user stop luanti-container luanti-pod 2>/dev/null || true

echo "==> Reloading firewall"
sudo nft flush ruleset
sudo nft -f /home/beerus/luanti/firewall/nftables.conf

echo "==> Done. Start again with: systemctl --user start luanti-pod luanti-container"
