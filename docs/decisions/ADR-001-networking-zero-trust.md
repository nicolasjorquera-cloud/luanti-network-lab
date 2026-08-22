# ADR-001: Networking & firewall strategy (zero-trust, Tailscale as ACL)

**Status:** Accepted (2026-08-22)
**Decision-makers:** nicolasjorquera-cloud
**Scope:** Luanti Network Lab, Phase 1 (host firewall / access control)

---

## Context

The lab runs a Luanti (Mineclonia) server for a parent and child, with friends
to be added later. The host is Ubuntu with **UFW**, **Docker**, **libvirt**, and
**Tailscale** all managing firewall state. Requirements:

- Game reachable **only** over the private Tailscale overlay (zero-trust).
- No exposure to the public Internet **or** the local LAN.
- Identity-based access control: who is allowed in is decided by Tailscale.
- Future observability (Vector) and an edge proxy (Envoy) for monitoring and
  audit of who connects, and when.

## Decision

1. **Tailscale is the access-control layer (ACL).** Whether a device can reach
   the host is decided by the Tailscale tailnet (which users/devices we add).
   The firewall does not enumerate trusted IPs by hand; it trusts the Tailscale
   network range.

2. **UFW (not a custom nftables table) is the host firewall.** The host already
   uses UFW + Docker + libvirt. A standalone nftables table with `flush ruleset`
   would clash with those managers, so UFW is the single source of truth for
   host input rules.

3. **Allow UDP 30000 from the Tailscale CGNAT range (`100.64.0.0/10`).** UDP
   game traffic arrives over the WireGuard mesh from tailnet addresses in that
   range, regardless of which guest is playing. Using the full CGNAT range means
   new tailnet guests (the child's friends) can play without re-editing the
   firewall; Tailscale governs *which* identities hold a tailnet address.

4. **Future phases (noted, not built in Phase 1):**
   - **Vector** — collect connection/audit logs (who connected, from which
     tailnet address, when). Source of audit trail.
   - **Envoy (standalone)** — edge proxy in front of `:30000` for inspection,
     rate-limiting, and control; design pending (UDP vs L4 proxying to be
     evaluated).

## Consequences

- **Positive:** no conflict with UFW/Docker/libvirt; adding a guest is a
  Tailscale change, not a firewall change; clean basis for audit/monitoring.
- **Negative:** a compromised tailnet identity is a path in (mitigated by the
  Tailscale ACL and, later, Envoy); UDP proxying via Envoy is limited compared
  to L4/L7 HTTP, which the design will weigh.
- **Trade-off accepted:** the CGNAT range is broader than enumerating one IP,
  but the actual "who" is enforced by Tailscale membership, not the firewall.

## Related

- `docs/threat-model.md` (zero-trust principles)
- `docs/specs/2026-08-14-luanti-network-lab-design.md`
- `docs/architecture.md`
