#!/usr/bin/env bash
# Stops the Luanti container and re-asserts the firewall rule. Does not delete the world.
set -euo pipefail

echo "==> Stopping Luanti"
systemctl --user stop luanti 2>/dev/null || true

echo "==> Re-asserting UFW rule for the game port (Tailscale only)"
bash "$(dirname "$0")/../firewall/setup-ufw.sh"

echo "==> Done. Start again with: systemctl --user start luanti"
