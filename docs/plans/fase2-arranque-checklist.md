# Fase 2 — Lista de tareas de arranque (Lab observable Datadog)

> **Qué es esto:** el checklist paso a paso para poner en marcha el lab observable.
> Orden optimizado para no saturarse (regla TDAH): primero la base visible y "que funciona",
> después lo diferenciador (exporters Rust).
> **En tu host real, SIN commits hasta que decidas.** Marca checkboxes a medida que avanzás.
> Nota: los comandos son referencia — adaptá IPs, rutas y nombres a tu entorno real.

---

## FASE 2A — Base: Agent en host + dashboard de infraestructura
> Objetivo: ver el host y (idealmente) los containers en Datadog. ~30-60 min.

### Paso 1 — Cuenta y credenciales Datadog
- [ ] Crear cuenta en https://www.datadoghq.com (trial/free).
- [ ] Anotar la **DD_SITE** que te corresponde (en tu cuenta: Organization Settings →
      verifica el subdominio, ej. `datadoghq.com`, `us3.datadoghq.com`, `eu.datadoghq.com`...).
- [ ] Generar **DD_API_KEY** (Organization Settings → API Keys → New Key).
- [ ] Guardarla en un lugar seguro del host (NO en el repo).

### Paso 2 — Instalar el Datadog Agent en el HOST
- [ ] Instalar: `DD_API_KEY=<KEY> DD_SITE=<SITE> bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent.sh)"`
- [ ] Verificar: `sudo systemctl status datadog-agent` (debe estar active/running).
- [ ] Verificar health: `sudo datadog-agent status`
- [ ] **Comprobar en la UI** (Infrastructure → Host Map): aparece el host con CPU/RAM/disco/red.

### Paso 3 — Auto-descubrimiento de Podman (opcional pero recomendado)
> El Agent ve containers si alcanza el socket de Podman. Podman rootless lo expone por
> `podman system service` en tu `XDG_RUNTIME_DIR`.
- [ ] Levantar/confirmar el socket Podman (`systemctl --user start podman.socket` o
      `podman system service --time=0 unix:///run/user/$(id -u)/podman/podman.sock &`).
- [ ] Configurar el socket en el Agent (`/etc/datadog-agent/conf.d/containerd.d/conf.yaml`
      o `container.d/`) con la ruta correcta del socket.
- [ ] `sudo systemctl restart datadog-agent`
- [ ] En la UI: ver los containers (Luanti) con métricas (`container.*`).
> Si no sale a la primera, no te frenes: continuá con host metrics + logs + exporters
> (dan valor igual) y refiná esto después.

### Paso 4 — Ingestar logs (capa Security baseline)
- [ ] Habilita el log de `/var/log/auth.log` (failed logins, SSH, sudo):
      `sudo tee /etc/datadog-agent/conf.d/system_auth.d/conf.yaml`
- [ ] `sudo systemctl restart datadog-agent`
- [ ] En la UI (Logs): ver `source:auth`.
- [ ] Generá un failed login de prueba y verificá que aparece (SSH con pass incorrecta).

### Paso 5 — Dashboard base "Luanti Platform Overview" (sección Infra)
- [ ] Datadog → Dashboards → New Dashboard.
- [ ] Agregar sección **Infrastructure**: `system.cpu.user`, `system.mem.used`,
      `system.disk.used`, `system.net.bytes_sent/rcvd` (+ `container.*` si hay).
- [ ] Guardar el dashboard con nombre y URL estable.
- [ ] (Opcional) Compartir read-only.

> ✅ **Fin de Fase 2A: ya tenés el host observable en Datadog.** Rellená luego las
> secciones Red/App/Security conforme completes 2B.

---

## FASE 2B — Exporters Rust (tu diferenciador): WireGuard + Luanti
> Objetivo: telemetría propia. El artefacto más valioso del portfolio. 1-2 días.

### Paso 6 — Scaffolding workspace Rust
- [ ] `cargo new` un workspace (`rust/` con `wg-exporter` + `luanti-exporter`).
- [ ] Definir estructura de crates (ver guía `observability-datadog.md` §2).
- [ ] `cargo init`/setup mínimos que compilen.

### Paso 7 — `wg-exporter` (Red + Seguridad)
> **Contexto real confirmado:** interface = `tailscale0`, `wg` NO instalado. Leer stats desde
> `/sys/class/net/tailscale0/statistics/*` + `tailscale status --json`. NO usar `wg show`.
- [ ] Leer `/sys/class/net/tailscale0/statistics/rx_bytes` y `tx_bytes` en Rust.
- [ ] Ejecutar `tailscale status --json` y parsear (peers, online/offline, IPs).
- [ ] Exponer endpoint **OpenMetrics** `/metrics` en HTTP (localhost).
      Métricas: `ts_net_rx_bytes`, `ts_net_tx_bytes`, `ts_peer_online`, `ts_peer_rx_bytes`,
      `ts_peer_tx_bytes`, `ts_peer_count`.
- [ ] Probar: `curl http://127.0.0.1:<PUERTO>/metrics` muestra las métricas.
- [ ] Configurar el check Prometheus/OpenMetrics de Datadog
      (`/etc/datadog-agent/conf.d/wg-exporter.d/conf.yaml` → apuntar a localhost).
- [ ] `sudo systemctl restart datadog-agent`
- [ ] En la UI: ver `ts_*` en Metrics Summary / dashboard.

### Paso 8 — `luanti-exporter` (App)
- [ ] Implementar el status query UDP al Luanti (apuntando al IP Tailscale del container).
- [ ] Parsear respuesta (jugadores, uptime, versión).
- [ ] Empujar métricas via **DogStatsD** (`luanti.players_online`, `luanti.uptime_seconds`,
      etc.) al `8125/udp` del Agent.
- [ ] Verificar que el Agent escucha DogStatsD (confirar en `datadog.yaml`).
- [ ] En la UI: `luanti.*` en Metrics Summary.

### Paso 9 — Dashboard completo (4 secciones)
- [ ] **Infrastructure** (de 2A) + **Network (WireGuard)** (`wg_*`) + **Application**
      (`luanti.*`) + **Security** (`wg_handshake_failures_total`, `ssh_failed_logins_total`).
- [ ] Guardar y compartir read-only para la demo.

### Paso 10 — Alertas (Operate)
- [ ] Monitor: host down / load (`system.load.1`).
- [ ] Monitor seguridad: `wg_handshake_failures_total` sube en 15 min.
- [ ] Monitor app: `luanti.players_online` cae a 0.

---

## Cierre
- [ ] ADR-002 (documentar la decisión de Datadog + exporters Rust) — cuando vayas a commitear.
- [ ] Actualizar README con el dashboard y el stack observable.

---

*Checklist de arranque Fase 2. 2026. Plan, sin commits.*
