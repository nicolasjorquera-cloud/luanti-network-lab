#!/usr/bin/env bash
# Health overview for the lab.
set -euo pipefail

echo "── Tailscale ──────────────────────────────"
tailscale status || echo "tailscale: not up"
tailscale ip -4 | sed 's/^/IP: /' || true

echo "── Podman pod ─────────────────────────────"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "── systemd units ──────────────────────────"
systemctl --user status luanti-pod luanti-container --no-pager || true

echo "── Firewall (port 30000) ──────────────────"
sudo nft list ruleset 2>/dev/null | grep "dport 30000" || echo "no 30000 rules"

echo "── Listening (UDP 30000) ──────────────────"
ss -lunp | grep 30000 || echo "not listening"
