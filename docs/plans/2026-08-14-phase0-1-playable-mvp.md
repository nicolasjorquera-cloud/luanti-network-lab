# Phase 0 + 1 Implementation Plan: Professional Repo + Playable Secure Server

**Goal:** Create a professional, English-only, public-ready GitHub repository for `luanti-network-lab`, and a secure playable Luanti (Mineclonia) server on an Ubuntu host using Podman rootless + quadlet, Tailscale, and nftables.

**Architecture:** The repo is a portfolio-quality project (Apache-2.0, CI with gitleaks, conventional commits). The server runs as a Podman rootless pod managed by systemd (quadlet) on the Ubuntu host. Tailscale on the host provides the private overlay network; nftables applies a DENY-by-default host firewall. The Luanti container publishes UDP 30000 only to the Tailscale and LAN interfaces.

**Tech Stack:** Podman, Quadlet (systemd), Tailscale, nftables, Luanti + Mineclonia, GitHub Actions, gitleaks, Terraform (scaffold only in this plan).

## Global Constraints

- **English-only:** all docs, code, comments, and commit messages in English.
- **Apache-2.0** license; LICENSE file is the canonical Apache 2.0 text.
- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `ci:`, `chore:`, `build:`, `infra:`).
- **Zero secrets** in the repo; `.gitignore` must cover `.tfstate`, credential JSON, `.env`.
- No public Internet exposure of the game server.
- Working directory for all file paths: repo root `/home/beerus/luanti`.
- Do not run `git push` until the user explicitly requests it.

---

### Task 1: Repository Foundation Files

**Files:**
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `CHANGELOG.md`

**Interfaces:**
- Produces: canonical Apache-2.0 `LICENSE`; repo-wide `.gitignore` and `.editorconfig`.

- [ ] **Step 1: Download the canonical Apache-2.0 license text**

Run:
```bash
curl -fsSL https://www.apache.org/licenses/LICENSE-2.0.txt -o LICENSE
```
Expected: `LICENSE` exists and starts with `Apache License`.

- [ ] **Step 2: Create `.gitignore`**

Write `.gitignore`:
```gitignore
# Secrets — never commit
*.json.key
*.pem
.env
.env.*
!*.env.example

# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/

# Rust (later phases)
/target/
Cargo.lock

# Terraform state
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
crash.log

# Editors / OS
.vscode/
.idea/
*.swp
.DS_Store

# Local runtime data
/luanti-data/
```

- [ ] **Step 3: Create `.editorconfig`**

Write `.editorconfig`:
```editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{py,sh,tf,lua}]
indent_style = space
indent_size = 4

[*.{yaml,yml,toml,json,md}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
```

- [ ] **Step 4: Create `CHANGELOG.md`**

Write `CHANGELOG.md`:
```markdown
# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository foundation (license, gitignore, editorconfig).
- Phase 0: professional scaffold with CI.
- Phase 1: secure playable Luanti server (Podman, Tailscale, nftables).
```

- [ ] **Step 5: Commit**

```bash
git add LICENSE .gitignore .editorconfig CHANGELOG.md
git commit -m "chore: add repository foundation files"
```

---

### Task 2: Community and Contributing Documents

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `CODE_OF_CONDUCT.md`

**Interfaces:**
- Produces: professional entry-point docs for the portfolio repo.

- [ ] **Step 1: Write `README.md`**

Write `README.md`:
```markdown
# Luanti Network Lab

A secure Luanti (Mineclonia) server for a parent and child to play together,
with a Dialogflow CX chatbot in the in-game chat.

This repository is a **portfolio-grade home lab**: a real, observable
infrastructure that teaches Linux, networking, security, containers, and the
Google Cloud ecosystem (Terraform IaC, Secret Manager, Cloud Logging,
Dialogflow CX, FinOps).

> The game is the interface. The infrastructure is the lesson.

## Features

- 🔒 Not exposed to the public Internet — private overlay via **Tailscale**
- 🧱 **DENY-by-default** host firewall with **nftables**
- 🐳 Server runs as a **Podman rootless pod** managed by systemd (quadlet)
- 🎮 **Mineclonia** game (Minecraft-like), world persisted in a volume
- 🤖 In-game chatbot powered by **Dialogflow CX** (Phase 2)
- 🌍 GCP resources as **Terraform IaC** (Phase 2)
- 💸 **FinOps**: budgets, alerts, and cost reporting (Phase 2)

## Repository layout

```text
docs/            Architecture, threat model, experiments
server/luanti/   Container image, quadlet unit, config, Lua mod
server/bridge/   Python bridge: Luanti chat ↔ Dialogflow CX (Phase 2)
infra/terraform/ GCP infrastructure as code (Phase 2)
finops/          Cloud Billing cost reporting (Phase 2)
firewall/        nftables configuration
scripts/         install / status / reset
tailscale/       VPN setup notes
```

## Getting started

Follow the phase 1 guides:

1. [Tailscale setup](tailscale/README.md)
2. [Server install](scripts/install.sh) (creates the Podman pod)
3. Connect clients (Linux + Windows) to `100.x.x.x:30000`

See `docs/architecture.md` for the full design and `docs/threat-model.md`
for the security model.

## License

[Apache-2.0](LICENSE)
```

- [ ] **Step 2: Write `CONTRIBUTING.md`**

Write `CONTRIBUTING.md`:
```markdown
# Contributing

Thanks for your interest. This is a small learning homelab — keep changes small
and observable.

## Conventions

- **English only** for code, comments, docs, and commit messages.
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `ci:`, `chore:`, `infra:`.
- **Prefer small focused commits** over large ones.

## Checks

CI runs these on every push — run them locally too:

```bash
ruff check server/bridge
pytest server/bridge/tests
cd infra/terraform && terraform fmt -check && terraform validate
```

## Security

Never commit credentials. The service account key lives in Secret Manager.
Run `gitleaks detect` before pushing if you changed secrets-related files.
```

- [ ] **Step 3: Write `SECURITY.md`**

Write `SECURITY.md`:
```markdown
# Security Policy

## Reporting a vulnerability

This is a home lab, but report issues privately by opening a GitHub issue with
the label `security` or by contacting the maintainer. Do not post secrets or
credentials in issues.

## Security model

- **Private network**: the game server is reachable only over Tailscale and the
  local LAN — never exposed to the public Internet.
- **DENY-by-default**: nftables drops all unapproved inbound traffic.
- **Least privilege**: services run as dedicated users/namespaces in a
  rootless Podman pod.
- **Secrets**: Google service account keys live in Secret Manager and are
  never committed.
- **Reproducibility**: everything is described in this repo and rebuildable
  from scratch.

See `docs/threat-model.md`.
```

- [ ] **Step 4: Write `CODE_OF_CONDUCT.md`**

Write `CODE_OF_CONDUCT.md`:
```markdown
# Code of Conduct

Be kind and respectful. This is a learning project; help others understand
rather than showing off. Harassment of any kind is not tolerated.
```

- [ ] **Step 5: Commit**

```bash
git add README.md CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md
git commit -m "docs: add community and contributing documents"
```

---

### Task 3: CI and Secret Scanning Workflows

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/gitleaks.yml`

**Interfaces:**
- Produces: GitHub Actions CI that must stay green (lint, pytest, terraform fmt/validate, container build) and a gitleaks secret scan.

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

Write `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    name: Lint (ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check server/bridge

  test:
    name: Test (pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e "server/bridge[dev]"
      - run: pytest server/bridge/tests -v

  terraform:
    name: Terraform fmt + validate
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra/terraform
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.9.8"
      - run: terraform fmt -check
      - run: terraform init -backend=false
      - run: terraform validate

  build:
    name: Build Luanti image
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: server/luanti
          push: false
          tags: luanti-network-lab/luanti:test
```

- [ ] **Step 2: Write `.github/workflows/gitleaks.yml`**

Write `.github/workflows/gitleaks.yml`:
```yaml
name: gitleaks

on:
  push:
  pull_request:

jobs:
  scan:
    name: Secret scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ""
```

- [ ] **Step 3: Verify YAML syntax**

Run:
```bash
python -c "import yaml,sys;[yaml.safe_load(open(f)) for f in ['.github/workflows/ci.yml','.github/workflows/gitleaks.yml']]"
```
Expected: no exception. (Install `pyyaml` first if missing.)

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml .github/workflows/gitleaks.yml
git commit -m "ci: add lint, test, terraform, build and gitleaks workflows"
```

---

### Task 4: Documentation and Scaffold for Bridge and Terraform

**Files:**
- Create: `docs/architecture.md`
- Create: `docs/threat-model.md`
- Create: `server/bridge/pyproject.toml`
- Create: `server/bridge/src/bridge/__init__.py`
- Create: `server/bridge/tests/test_smoke.py`
- Create: `infra/terraform/main.tf`
- Create: `infra/terraform/variables.tf`

**Interfaces:**
- Produces: working CI targets (lint + pytest + terraform validate pass); bridge package scaffold that Phase 2 extends; architecture docs.

- [ ] **Step 1: Write `docs/architecture.md`**

Write `docs/architecture.md`:
```markdown
# Architecture

## Overview

```text
                    INTERNET
                       │ (nothing public)
            ┌──────────▼──────────┐
            │   Ubuntu host        │
            │  ┌────────────────┐  │
            │  │ Podman pod      │  │
            │  │  ├─ luanti     │  │  Mineclonia, :30000/udp
            │  │  └─ bridge     │  │  FastAPI → Dialogflow CX (Phase 2)
            │  └────────────────┘  │
            │  Tailscale + nftables│
            └──────────┬──────────┘
                       │ 100.x.x.x:30000 (Tailscale) + LAN
             ┌─────────┴─────────┐
             │                   │
        Ubuntu (parent)      Windows (child)
```

## Components

- **Tailscale (host)**: private overlay network (WireGuard). The VPN endpoint
  lives on the host; containers publish ports onto the `tailscale0` interface.
- **nftables (host)**: DENY-by-default host firewall. Only UDP 30000 on
  trusted interfaces (tailscale0, LAN) is allowed.
- **Podman pod (rootless)**: `luanti` and `bridge` containers share a network
  namespace; `bridge` is only reachable from inside the pod.
- **Luanti + Mineclonia**: game server with persistent world volume.
- **Bridge (Phase 2)**: Python FastAPI service that forwards in-game chat to
  Dialogflow CX and returns replies.

See `docs/gcp-architecture.md` (added in Phase 2) for the GCP side.
```

- [ ] **Step 2: Write `docs/threat-model.md`**

Write `docs/threat-model.md`:
```markdown
# Threat Model

## Trusted

- Parent, child, owned computers
- Private Tailscale network

## Untrusted

- Public Internet
- Unknown network traffic
- Unexpected connection attempts
- Unnecessary exposed services

## Principles

1. **Minimize exposure** — nothing public.
2. **Least privilege** — rootless containers, dedicated users.
3. **Explicit access** — nftables allows only what is required.
4. **Observable behavior** — blocking UDP 30000 disconnects clients.
5. **Reproducible** — everything rebuildable from this repo.

## Attack surface

- Luanti UDP 30000 — reachable only over Tailscale and LAN.
- SSH on the host — restrict to trusted sources (recommended: Tailscale only).
- GCP APIs — protected by IAM service accounts (Phase 2).
```

- [ ] **Step 3: Write the bridge scaffold `pyproject.toml`**

Write `server/bridge/pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "luanti-bridge"
version = "0.1.0"
description = "Bridge between Luanti in-game chat and Dialogflow CX"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "ruff>=0.5",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Write `server/bridge/src/bridge/__init__.py`**

Write `server/bridge/src/bridge/__init__.py`:
```python
"""Luanti ↔ Dialogflow CX bridge package."""

__version__ = "0.1.0"
```

- [ ] **Step 5: Write the smoke test**

Write `server/bridge/tests/test_smoke.py`:
```python
from bridge import __version__


def test_package_version():
    assert __version__ == "0.1.0"
```

- [ ] **Step 6: Write the Terraform scaffold**

Write `infra/terraform/main.tf`:
```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  service_name = "luanti-network-lab"
}
```

Write `infra/terraform/variables.tf`:
```hcl
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Default GCP region"
  type        = string
  default     = "us-central1"
}
```

- [ ] **Step 7: Verify CI targets locally**

Run:
```bash
cd /home/beerus/luanti
pip install -e "server/bridge[dev]" && ruff check server/bridge && pytest server/bridge/tests -v
cd infra/terraform && terraform init -backend=false && terraform fmt -check && terraform validate
```
Expected: ruff clean, 1 test passes, `terraform validate` succeeds.

- [ ] **Step 8: Commit**

```bash
git add docs/architecture.md docs/threat-model.md \
  server/bridge/pyproject.toml server/bridge/src server/bridge/tests \
  infra/terraform/main.tf infra/terraform/variables.tf
git commit -m "docs: add architecture and threat model; scaffold bridge and terraform"
```

---

### Task 5: Luanti Container Image with Mineclonia

**Files:**
- Create: `server/luanti/Containerfile`
- Create: `server/luanti/README.md`

**Interfaces:**
- Produces: image `localhost/luanti-network-lab/luanti:latest` with Luanti server + Mineclonia subgame, running as an unprivileged `luanti` user.

- [ ] **Step 1: Write `server/luanti/Containerfile`**

Write `server/luanti/Containerfile`:
```dockerfile
FROM debian:bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      git \
      luanti-server \
      procps \
 && rm -rf /var/lib/apt/lists/*

RUN useradd --system --uid 30000 --create-home --home /var/lib/luanti luanti \
 && mkdir -p /var/lib/luanti/subgames /var/lib/luanti/world \
 && chown -R luanti:luanti /var/lib/luanti

# Mineclonia subgame (Minecraft-like)
RUN git clone --depth 1 https://codeberg.org/mineclonia/mineclonia.git \
      /var/lib/luanti/subgames/mineclonia \
 && chown -R luanti:luanti /var/lib/luanti/subgames

USER luanti

# World and subgames are mounted as volumes; config path passed via exec.
VOLUME ["/var/lib/luanti/world", "/var/lib/luanti/subgames"]

ENTRYPOINT ["luanti-server", "--config", "/etc/luanti/minetest.conf", "--world", "/var/lib/luanti/world"]
```

- [ ] **Step 2: Write `server/luanti/README.md`**

Write `server/luanti/README.md`:
```markdown
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
```

- [ ] **Step 3: Verify the image builds**

Run:
```bash
podman build -t localhost/luanti-network-lab/luanti:latest /home/beerus/luanti/server/luanti
```
Expected: build succeeds. (Install Podman first if missing — see Task 8.)

- [ ] **Step 4: Commit**

```bash
git add server/luanti/Containerfile server/luanti/README.md
git commit -m "build: add luanti server container image with mineclonia"
```

---

### Task 6: Podman Rootless + Quadlet Units

**Files:**
- Create: `server/luanti/luanti.pod`
- Create: `server/luanti/luanti.container`
- Create: `scripts/install-podman.sh`

**Interfaces:**
- Consumes: image `localhost/luanti-network-lab/luanti:latest` (Task 5).
- Produces: systemd user units `luanti.pod` + `luanti.container` deployed to `~/.config/containers/systemd/`; a rootless `luanti` pod reachable at `TAILSCALE_IP:30000/udp` and `LAN_IP:30000/udp`.

- [ ] **Step 1: Write `server/luanti/luanti.pod`**

Write `server/luanti/luanti.pod`:
```ini
[Unit]
Description=Luanti network lab pod

[Pod]
```

- [ ] **Step 2: Write `server/luanti/luanti.container`**

Write `server/luanti/luanti.container` (replace the IPs with real values):
```ini
[Unit]
Description=Luanti game server
After=network-online.target
Wants=network-online.target

[Container]
Pod=luanti.pod
Image=localhost/luanti-network-lab/luanti:latest
ContainerName=luanti

# Persistent data (host paths)
Volume=/home/beerus/luanti-data/world:/var/lib/luanti/world:Z
Volume=/home/beerus/luanti-data/subgames:/var/lib/luanti/subgames:Z
Volume=/home/beerus/luanti-data/minetest.conf:/etc/luanti/minetest.conf:ro,Z

# Publish UDP 30000 only to Tailscale and LAN interfaces
PublishPort=100.64.0.0:30000:30000/udp
PublishPort=192.168.0.0:30000:30000/udp

Exec=luanti-server --config /etc/luanti/minetest.conf --world /var/lib/luanti/world

[Service]
Restart=on-failure
TimeoutStartSec=0

[Install]
WantedBy=default.target
```

Note: `PublishPort` IPs are placeholders — Task 10 fills in the real Tailscale and LAN IPs at install time.

- [ ] **Step 3: Write `scripts/install-podman.sh`**

Write `scripts/install-podman.sh`:
```bash
#!/usr/bin/env bash
# Installs rootless Podman from the official upstream repo (Debian/Ubuntu).
set -euo pipefail

. /etc/os-release

echo "==> Installing Podman (upstream repo) on ${ID} ${VERSION_CODENAME}"

if [[ -f /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list ]]; then
  echo "Podman repo already configured."
else
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/${VERSION_CODENAME}/Release.key" \
    | sudo gpg --dearmor -o /etc/apt/keyrings/libcontainers.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/libcontainers.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/${VERSION_CODENAME}/" \
    | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
fi

sudo apt-get update
sudo apt-get install -y podman

# Rootless setup (idempotent)
if ! command -v podman >/dev/null; then
  echo "podman install failed" >&2
  exit 1
fi
podman system migrate
echo "==> Podman version: $(podman --version)"
echo "Verify with: podman info"
```

- [ ] **Step 4: Run the installer and verify rootless podman**

Run:
```bash
chmod +x /home/beerus/luanti/scripts/install-podman.sh
/home/beerus/luanti/scripts/install-podman.sh
podman info | head -20
```
Expected: `podman` installed; `podman info` shows rootless storage driver (e.g. `overlay`).

- [ ] **Step 5: Deploy quadlet units and start the pod**

Run (after filling real IPs into `luanti.container`):
```bash
mkdir -p ~/.config/containers/systemd
cp /home/beerus/luanti/server/luanti/luanti.pod /home/beerus/luanti/server/luanti/luanti.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start luanti-pod luanti-container
systemctl --user status luanti-container --no-pager
```
Expected: container `luanti` running; `podman ps` shows it.

- [ ] **Step 6: Commit**

```bash
git add server/luanti/luanti.pod server/luanti/luanti.container scripts/install-podman.sh
git commit -m "infra: add quadlet pod and container units for luanti"
```

---

### Task 7: nftables DENY-by-Default Firewall

**Files:**
- Create: `firewall/nftables.conf`
- Create: `scripts/install-firewall.sh`
- Create: `firewall/luanti-firewall.service`

**Interfaces:**
- Produces: host firewall that allows only UDP 30000 on `tailscale0` and LAN, Tailscale DNS, loopback, and established traffic; drops everything else.

- [ ] **Step 1: Write `firewall/nftables.conf`**

Write `firewall/nftables.conf`:
```nft
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;

    # Keep existing sessions + loopback
    ct state established,related accept
    iif "lo" accept

    # Tailscale (VPN) interface
    iif "tailscale0" udp dport 30000 accept   # Luanti game
    iif "tailscale0" udp dport 53 accept      # Tailscale DNS (100.100.100.100)

    # Local LAN (adjust interface name if needed, e.g. enp0s3)
    iifname "en*" udp dport 30000 accept      # Luanti on LAN

    # Optional: SSH over Tailscale only (uncomment to restrict SSH)
    # iif "tailscale0" tcp dport 22 accept

    # ICMP echo (ping) for LAN diagnostics
    ip protocol icmp icmp type echo-request iifname "en*" accept
  }

  chain forward {
    type filter hook forward priority filter; policy drop;
  }

  chain output {
    type filter hook output priority filter; policy accept;
  }
}
```

- [ ] **Step 2: Write `firewall/luanti-firewall.service`**

Write `firewall/luanti-firewall.service`:
```ini
[Unit]
Description=Luanti network lab nftables firewall
Before=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft -f /etc/luanti-nftables.conf
ExecStop=/usr/sbin/nft flush ruleset

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 3: Write `scripts/install-firewall.sh`**

Write `scripts/install-firewall.sh`:
```bash
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
```

- [ ] **Step 4: Verify syntax and deploy**

Run:
```bash
chmod +x /home/beerus/luanti/scripts/install-firewall.sh
sudo nft -c -f /home/beerus/luanti/firewall/nftables.conf
```
Expected: no errors, ruleset prints.

- [ ] **Step 5: Verify observable behavior**

Run:
```bash
sudo nft list ruleset | grep -A2 "udp dport 30000"
```
Expected: two rules accepting UDP 30000 on `tailscale0` and `en*`.

- [ ] **Step 6: Commit**

```bash
git add firewall/nftables.conf firewall/luanti-firewall.service scripts/install-firewall.sh
git commit -m "infra: add deny-by-default nftables firewall"
```

---

### Task 8: Luanti Server Configuration and Data Layout

**Files:**
- Create: `server/luanti/minetest.conf`
- Create: `scripts/init-data.sh`

**Interfaces:**
- Consumes: container (Task 5) mounting `/home/beerus/luanti-data/`.
- Produces: world + config persisted on host; access limited to trusted players.

- [ ] **Step 1: Write `server/luanti/minetest.conf`**

Write `server/luanti/minetest.conf`:
```ini
# Luanti Network Lab server configuration
name = luanti-network-lab
server_name = Luanti Network Lab
server_description = Secure home server (parent + child)
server_announce = false

# Game port and address
port = 30000
bind_address = 0.0.0.0

# Single world, damage on (survival)
world = /var/lib/luanti/world
enable_damage = true

# Auth / access control (network itself is private via Tailscale)
disallow_empty_password = true
enable_rollback_recording = true

# Gameplay-friendly for a child
enable_weather = true
time_speed = 72

# Motd shown on join
motd = Welcome! Ask the bot for help: type "bot, how do I ..."
```

- [ ] **Step 2: Write `scripts/init-data.sh`**

Write `scripts/init-data.sh`:
```bash
#!/usr/bin/env bash
# Creates the host-side data directory for the Luanti pod.
set -euo pipefail

DATA_DIR="${LUANTI_DATA_DIR:-/home/beerus/luanti-data}"

mkdir -p "${DATA_DIR}/world" "${DATA_DIR}/subgames"
cp /home/beerus/luanti/server/luanti/minetest.conf "${DATA_DIR}/minetest.conf"

# Seed the Mineclonia subgame from the container image (so it survives rebuilds)
podman run --rm \
  -v "${DATA_DIR}/subgames:/target" \
  --entrypoint /bin/sh \
  localhost/luanti-network-lab/luanti:latest \
  -c "cp -rn /var/lib/luanti/subgames/mineclonia /target/ 2>/dev/null || true"

echo "==> Data dir ready at ${DATA_DIR}"
ls -la "${DATA_DIR}"
```

- [ ] **Step 3: Run it and verify the world boots**

Run:
```bash
chmod +x /home/beerus/luanti/scripts/init-data.sh
/home/beerus/luanti/scripts/init-data.sh
journalctl --user -u luanti-container --no-pager | tail -30
```
Expected: server starts, world generates under `/home/beerus/luanti-data/world`.

- [ ] **Step 4: Commit**

```bash
git add server/luanti/minetest.conf scripts/init-data.sh
git commit -m "infra: add luanti server config and data bootstrap"
```

---

### Task 9: Operational Scripts

**Files:**
- Create: `scripts/install.sh`
- Create: `scripts/status.sh`
- Create: `scripts/reset.sh`

**Interfaces:**
- Produces: idempotent `install.sh` (Tailscale + Podman + firewall + pod), `status.sh` (health overview), `reset.sh` (stop pod + reinstall firewall).

- [ ] **Step 1: Write `scripts/install.sh`**

Write `scripts/install.sh`:
```bash
#!/usr/bin/env bash
# One-shot installer: Tailscale, Podman, firewall, image, and pod.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> [1/5] Installing Podman"
"${SCRIPT_DIR}/install-podman.sh"

echo "==> [2/5] Installing Tailscale"
if ! command -v tailscale >/dev/null 2>&1; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi
sudo tailscale up --advertise-tags=tag:home --ssh=false || sudo tailscale up

echo "==> [3/5] Installing firewall"
"${SCRIPT_DIR}/install-firewall.sh"

echo "==> [4/5] Building Luanti image"
podman build -t localhost/luanti-network-lab/luanti:latest "${SCRIPT_DIR}/../server/luanti"

echo "==> [5/5] Initializing data and starting pod"
"${SCRIPT_DIR}/init-data.sh"

mkdir -p ~/.config/containers/systemd
cp "${SCRIPT_DIR}/../server/luanti/luanti.pod" "${SCRIPT_DIR}/../server/luanti/luanti.container" ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user enable --now luanti-pod luanti-container

echo "==> Done. Get the Tailscale IP with: scripts/status.sh"
```

- [ ] **Step 2: Write `scripts/status.sh`**

Write `scripts/status.sh`:
```bash
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
```

- [ ] **Step 3: Write `scripts/reset.sh`**

Write `scripts/reset.sh`:
```bash
#!/usr/bin/env bash
# Stops the pod and reloads the firewall. Does not delete the world.
set -euo pipefail

echo "==> Stopping pod"
systemctl --user stop luanti-container luanti-pod 2>/dev/null || true

echo "==> Reloading firewall"
sudo nft flush ruleset
sudo nft -f /home/beerus/luanti/firewall/nftables.conf

echo "==> Done. Start again with: systemctl --user start luanti-pod luanti-container"
```

- [ ] **Step 4: Make executable and sanity-check**

Run:
```bash
chmod +x scripts/install.sh scripts/status.sh scripts/reset.sh
bash -n scripts/install.sh scripts/status.sh scripts/reset.sh
```
Expected: no syntax errors.

- [ ] **Step 5: Commit**

```bash
git add scripts/install.sh scripts/status.sh scripts/reset.sh
git commit -m "infra: add operational scripts"
```

---

### Task 10: Tailscale Setup and Windows Client Guide

**Files:**
- Create: `tailscale/README.md`
- Modify: `server/luanti/luanti.container` (real IPs)

**Interfaces:**
- Produces: working Tailscale overlay between Ubuntu host and Windows; client connect instructions; firewall bound to real Tailscale IP.

- [ ] **Step 1: Write `tailscale/README.md`**

Write `tailscale/README.md`:
```markdown
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
```

- [ ] **Step 2: Fill real IPs into `luanti.container`**

Run and edit `server/luanti/luanti.container`:
```bash
TS_IP="$(tailscale ip -4)"
LAN_IP="$(hostname -I | awk '{print $1}')"
echo "Tailscale: ${TS_IP}  LAN: ${LAN_IP}"
```
Replace the `PublishPort` placeholder IPs with `TS_IP` and `LAN_IP`, then redeploy:
```bash
cp server/luanti/luanti.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user restart luanti-container
```

- [ ] **Step 3: Verify from the Windows client**

Expected: Luanti client on Windows connects to `TS_IP:30000`; parent connects from Linux over LAN `LAN_IP:30000`.

- [ ] **Step 4: Commit**

```bash
git add tailscale/README.md server/luanti/luanti.container
git commit -m "infra: add tailscale setup and wire real publish IPs"
```

---

### Task 11: End-to-End Verification (LAN + Tailscale + Firewall Block)

**Files:**
- Create: `docs/experiments/firewall-block-udp.md`

**Interfaces:**
- Produces: documented, observable proof of the MVP success criteria.

- [ ] **Step 1: Verify connectivity both ways**

Run from Linux (LAN) and Windows (Tailscale):
- Luanti client connects to `LAN_IP:30000` and `TS_IP:30000`.
- Both players can chat and move in the world.

Expected: both connections work.

- [ ] **Step 2: Run `nmap` from LAN (host)**

Run:
```bash
nmap -sU -p 30000 --top-ports 10 127.0.0.1 || true
sudo nmap -sU -p 30000 LAN_IP
```
Expected: UDP 30000 open; no other unexpected open services.

- [ ] **Step 3: Firewall block experiment**

Run:
```bash
sudo nft add rule inet filter input iif "tailscale0" udp dport 30000 drop
# observe: Windows client disconnects
sudo nft delete rule inet filter input handle <handle>
# observe: Windows client reconnects
```
Expected: disconnecting and reconnecting on firewall change — the observable lesson.

- [ ] **Step 4: Write `docs/experiments/firewall-block-udp.md`**

Write `docs/experiments/firewall-block-udp.md`:
```markdown
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
```

- [ ] **Step 5: Commit**

```bash
git add docs/experiments/firewall-block-udp.md
git commit -m "docs: document firewall block experiment"
```

---

## Self-Review

**Spec coverage (Phase 0 + 1):**
- Phase 0: English docs (T1, T2), CI + gitleaks (T3), scaffold bridge + terraform (T4) — ✅
- Phase 1: Tailscale (T10), Podman rootless + quadlet (T6), Luanti + Mineclonia (T5), nftables (T7), minetest.conf (T8), scripts (T9), Windows client (T10), verification (T11) — ✅
- Success criteria 1 (play LAN+Tailscale) → T11. 2 (not public) → T7, T10. 3 (chatbot) → Phase 2 plan. 4 (firewall block observable) → T11. 5 (no secrets) → T1, T3. — ✅

**Placeholder scan:** PublishPort IPs in `luanti.container` are explicit placeholders filled in Task 10, not TODOs. No other placeholders.

**Type consistency:** image name `localhost/luanti-network-lab/luanti:latest` consistent across T5/T6/T8/T9; unit names `luanti.pod`/`luanti.container` (systemd `luanti-pod`/`luanti-container`) consistent.
