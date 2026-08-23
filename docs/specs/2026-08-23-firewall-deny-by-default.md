# Firewall — Make DENY-by-default explicit

**Date:** 2026-08-23
**Status:** Approved
**Author:** nicolasjorquera-cloud
**Scope:** Phase 1 hardening — host firewall

## 1. Problem

The repo claims a **DENY-by-default** host firewall (README, `docs/threat-model.md`,
`docs/decisions/ADR-001-networking-zero-trust.md`): everything not explicitly
allowed is dropped; only the Tailscale overlay is trusted.

However `firewall/setup-ufw.sh` only **adds an allow rule** for the game port and
**assumes** the default-deny policy is already configured on the host:

```bash
sudo ufw allow from "${TS_RANGE}" to any port "${PORT}" proto "${PROTO}"
```

UFW's own default policy is **allow incoming** until told otherwise. So on any
host that runs this script without a pre-existing `default deny incoming`, the
result is: the game is reachable via Tailscale, **but so is every other port**
(SSH, etc.). This contradicts the project's central zero-trust claim.

The goal is to make the DENY-by-default policy **self-contained in the script**,
so the claim travels with the repository and is reproducible on any host that
clones and runs it.

## 2. Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Default policy | `ufw default deny incoming` made **explicit** in the script | Self-contained zero-trust; replicable on any host |
| Enable | `ufw --force enable` (non-interactive) | Applies the policy without a sudo prompt |
| Outgoing | **Not touched** (`default deny outgoing` NOT set) | Avoid breaking outbound traffic / Tailscale handshake |
| Game exception | `allow from 100.64.0.0/10 to port 30000/udp` (kept) | Tailscale CGNAT range only |
| MagicDNS exception | `allow from 100.100.100.100 to port 53/udp` (added) | Tailscale DNS, already referenced in `tailscale/README.md` |
| SSH | **No rule in the script** | Decided explicitly; left to manual host review |
| Firewall backend | UFW, not a standalone nftables table | Avoids clashing with Docker/libvirt/Tailscale (ADR-001) |

## 3. Changes to `firewall/setup-ufw.sh`

Add before the existing game allow rule:

```bash
sudo ufw default deny incoming
sudo ufw --force enable
```

Keep:

```bash
sudo ufw allow from "${TS_RANGE}" to any port "${PORT}" proto "${PROTO}"
```

Add the MagicDNS exception:

```bash
sudo ufw allow from 100.100.100.100 to any port 53 proto udp
```

`set -euo pipefail` already present at the top remains.

## 4. Replicability

Because the default-deny and exceptions live **inside the script**, any host that
runs `install.sh` → `install-firewall.sh` → `setup-ufw.sh` gets the same
zero-trust posture. The only host-specific value is the Tailscale IP, resolved
dynamically in `scripts/deploy-luanti-service.sh`; the Tailscale CGNAT range
`100.64.0.0/10` is identical across the tailnet.

## 5. Consequences / warnings

- **SSH:** with `default deny incoming`, any SSH that previously relied on UFW's
  default-allow will be blocked. SSH via Tailscale is unaffected (Tailscale is
  explicitly allowed). No SSH rule is added here; the operator must confirm their
  SSH path on the host before applying.
- **Outgoing traffic** is untouched, so Tailscale handshake and general egress
  keep working.
- The game remains reachable only from the Tailscale range; everything else
  (including LAN) is dropped by the default policy.

## 6. Verification

- `bash -n firewall/setup-ufw.sh` (syntax)
- Review the full diff.
- Live application is manual (requires sudo on the real host). After applying:
  `sudo ufw status verbose` should show `Default: deny (incoming)`, the game rule
  from `100.64.0.0/10`, and the MagicDNS rule.
