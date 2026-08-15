# Tailscale

Tailscale is the private overlay network (WireGuard) that connects the Ubuntu
host and the Windows client without exposing anything to the public Internet.

## Host (Ubuntu)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo tailscale status
```

## Windows client

1. Install Tailscale from https://tailscale.com/download
2. Sign in with the same account as the host.
3. Confirm both devices appear in the admin console.

## Test connectivity

```bash
# from the Windows client
ping <host-tailscale-ip>
```

Then connect Luanti to `<host-tailscale-ip>:30000`.

## Security notes

- The game server is only reachable over `tailscale0` (nftables enforces this).
- Tailscale DNS (`100.100.100.100:53`) is allowed by the firewall.
