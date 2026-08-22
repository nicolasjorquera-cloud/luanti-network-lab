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

- **Tailscale IS the access-control layer (ACL)**: the game server is reachable
  **only** over Tailscale. UFW allows the Tailscale range; everything else,
  including the local LAN, is dropped — zero-trust, no LAN path.
- Tailscale DNS (`100.100.100.100:53`) is allowed by the firewall, also only
  from the `tailscale0` interface.
- No device outside the tailnet — no matter its network — can reach the host.
