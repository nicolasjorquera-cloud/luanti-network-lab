#!/usr/bin/env bash
# Installs the DENY-by-default nftables firewall as a systemd service.
set -euo pipefail

echo "==> Checking nftables syntax..."
sudo nft -c -f /home/beerus/luanti/firewall/nftables.conf

echo "==> Installing firewall files..."
sudo cp /home/beerus/luanti/firewall/nftables.conf /etc/luanti-nftables.conf
sudo cp /home/beerus/luanti/firewall/luanti-firewall.service /etc/systemd/system/

echo "==> Enabling firewall..."
sudo systemctl daemon-reload
sudo systemctl enable --now luanti-firewall

echo "==> Active ruleset:"
sudo nft list ruleset
