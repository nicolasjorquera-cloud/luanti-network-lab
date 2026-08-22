# Roadmap & Project Status

Status of each phase and the decisions that shape the project. The design
specification lives in [`docs/specs/`](specs/).

## Status

| Phase | Deliverable | State |
|---|---|---|
| 0 | Professional scaffold (license, CI, gitleaks, docs) | ✅ done |
| 1 | Secure playable Luanti (Mineclonia) server | ✅ done |
| 2 | Chatbot on GCP: Dialogflow CX agent as Terraform, Python bridge, Lua mod, FinOps | next |
| 3 | Moderator/personality; optional App Builder data store; automated FinOps report | planned |
| 4 | Rust bridge port (reference implementation in Python) | planned |
| 5 | Optional: KVM VMs, observability | planned |

## Key decisions

| Decision | Choice | Rationale |
|---|---|---|
| Deployment | Podman rootless + systemd unit | Portfolio value, clean host; explicit unit over quadlet generator (unreliable on a stale user manager) |
| Network | Tailscale overlay = ACL; UFW DENY-by-default, Tailscale range only | Private zero-trust mesh; never exposed to the Internet **or LAN** |
| Game | Mineclonia | Minecraft-like, familiar for a child |
| Chatbot | Dialogflow CX, deterministic intents only | Cheap, fast, predictable; no LLM in the MVP |
| Bridge | Python/FastAPI (MVP) → Rust (Phase 4) | Official SDK + velocity; Rust as a learning target |
| Invocation | Mention the bot by name ("Mino") | Natural control |
| Repository | Public, Apache-2.0, English-only, Conventional Commits, CI + gitleaks | Employability and visibility |
| GCP | Terraform IaC, Secret Manager, Cloud Logging, FinOps budget | Deep, complete GCP story from day one |

## Errors encountered & fixes

Real problems hit while building Phase 1 and how they were resolved:

- Podman install script used `VERSION_CODENAME` (noble) in the kubic URL → 404.
  Fixed with an idempotent script that skips when Podman is already installed.
- `debian:bookworm` ships an old `minetest-server` (no `luanti-server`) → switched
  the base image to `debian:trixie-slim`.
- The server binary is `/usr/games/luantiserver` (no hyphen) → corrected the
  container `ENTRYPOINT`.
- The `luanti` user (uid 30000) could not write host-owned volume data → fixed by
  switching the world to a **Podman named volume** (`luanti-world`), so the
  container runs unprivileged as the `luanti` user (no `--user 0`).
- The server requires `--gameid`; the games directory is `/usr/share/luanti/games`
  (not `subgames`) → Mineclonia is baked into the image and selected via `--gameid`.
- Container ports must be published on the **pod**, not the container.
- Quadlet generator did not re-run on a stale user systemd manager; `podman
  generate systemd --new` also failed ("PID file not owned by root") → used an
  explicit `Type=simple` systemd unit via `scripts/deploy-luanti-service.sh`.
- The subgames volume seed failed silently (permissions) → removed the subgames
  volume; the game is baked into the image.
- `add-apt-repository ppa:minetestdevs/stable` hangs on this host (Launchpad
  timeout) → fallback to Flatpak `org.luanti.luanti`.
- Ubuntu noble `minetest` 5.6.1 is too old for the 5.10 server → the client must
  be >= 5.10 (PPA/Flatpak).

## Next steps

1. **Phase 2** — Dialogflow CX agent (flows/intents/pages) as Terraform; service
   account + Secret Manager + IAM + billing budget; Python bridge exposing
   `/chat` and `/welcome` (sessions, rate limiting, Cloud Logging); Lua mod that
   calls the bridge; unit tests with the CX API mocked; FinOps cost report.
2. **Windows client** — Tailscale + Luanti client on the child's Windows machine.
3. **Phase 3** — moderator/personality, optional App Builder data store,
   automated FinOps report.
4. **Phase 4** — port the bridge to Rust.
