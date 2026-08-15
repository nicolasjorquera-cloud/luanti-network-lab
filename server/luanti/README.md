# Luanti server container

Base image with Luanti server + the **Mineclonia** subgame.

## Build

```bash
podman build -t localhost/luanti-network-lab/luanti:latest server/luanti
```

## Layout

- `/var/lib/luanti/world` — persistent world (volume)
- `/var/lib/luanti/subgames` — subgames (volume, Mineclonia pre-installed)
- `/etc/luanti/minetest.conf` — server config (mounted read-only)

See `luanti.container` for the quadlet unit that runs it.
