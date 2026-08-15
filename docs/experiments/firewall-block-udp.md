# Experiment: block UDP 30000 and watch the client disconnect

## Goal

Prove that the firewall is the network boundary — blocking the game port
disconnects the client.

## Steps

1. Start the pod (`systemctl --user start luanti-pod`).
2. Connect from Windows over Tailscale.
3. Add a drop rule for UDP 30000 on `tailscale0`.
4. Observe the client loses connection.
5. Delete the rule; observe the client reconnects.

## Result

The game server is reachable **only** because the firewall allows it.
Removing the allowance is immediately observable. The lab is designed to be
broken and understood.
