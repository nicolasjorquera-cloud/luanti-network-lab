#!/usr/bin/env bash
# Stops the Luanti container and reloads the firewall. Does not delete the world.
set -euo pipefail

echo "==> Stopping Luanti"
systemctl --user stop luanti 2>/dev/null || true

echo "==> Reloading firewall"
sudo nft flush ruleset
sudo nft -f /home/beerus/luanti/firewall/nftables.conf

echo "==> Done. Start again with: systemctl --user start luanti"
