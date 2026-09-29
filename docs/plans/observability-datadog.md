# Observabilidad Luanti: Exporter Rust + Datadog — Guía (Fase 2 adelantada)

> **Contexto:** construir un stack de observabilidad de 4 capas (Infra + Red + App +
> Seguridad) en un solo dashboard Datadog. La pieza central son **exporteres propios en
> Rust** que generan telemetría real de WireGuard y el servidor Luanti. Esto adelanta la
> Fase 2 del roadmap, consolida los learning paths de Datadog Fundamentals y produce el
> artifacts de portfolio más diferenciador de todo el proyecto.
> **Ejecutar en el HOST REAL (Ubuntu + Podman rootless + Tailscale), no en un sandbox.**
> **SIN COMMITS** mientras sea plan.

---

## 0. Arquitectura objetivo (4 capas)

Gráfico de capa fuente de datos → mecanismo → Datadog, y qué pieza es tuya:

| Capa | Fuente | Mecanismo a Datadog | Pieza tuya (Rust) |
|---|---|---|---|
| **Infra (container)** | Datadog Agent (**host**, auto-descubre Podman) | Integración nativa containers | — |
| **Red (WireGuard)** | `wg show` (raw, en HOST) | **Exporter OpenMetrics en Rust** → check Prometheus scrape | ✅ `wg-exporter` |
| **App (Luanti)** | status query UDP (jugadores, uptime, versión) | **Exporter Rust → DogStatsD** | ✅ `luanti-exporter` |
| **Seguridad** | WireGuard handshake fallidos, conexiones rechazadas | métricas custom (mismo daemon Rust) | ✅ (dentro de `wg-exporter`) |

**Dashboard final:** "Luanti Platform Overview" → 4 secciones (Infra / Red / App / Security).

### ⚠️ Correcciones de arquitectura (críticas, te ahorran horas)
1. **El Datadog Agent corre en el HOST, NO dentro del container de Luanti.** Si lo pones
   dentro del container, solo ves ese container con visión limitada, y NO ves host ni
   WireGuard. En host auto-descubre los containers Podman desde afuera. (Práctica de producción real.)
2. **`wg show` / teletría será leída en el HOST.** La interface WireGuard (`tailscale0`/`wg0`)
   vive en el kernel del host. Tu `wg-exporter` debe correr en el **host**, no dentro del container.
3. El `luanti-exporter` (UDP status) puede correr en el host apuntando al IP Tailscale del container,
   o dentro del pod como sidecar. Host es más simple para el MVP.

---

## 1. Infra: Datadog Agent en el host (capa 1, automática)

```bash
DD_API_KEY=<TU_API_KEY> DD_SITE=datadoghq.com bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent.sh)"
sudo systemctl status datadog-agent
sudo datadog-agent status
```

El Agent en el host auto-descubre los containers Podman **si ve el socket**:
- Podman rootless: `podman system service` en tu `XDG_RUNTIME_DIR`
  (`/run/user/<uid>/podman/podman.sock`).
- Configura el socket en el Agent (`/etc/datadog-agent/conf.d/containerd.d/conf.yaml`
  o `container.d/`) según la versión del Agent.

> Si el auto-discovery de Podman no sale a la primera, NO te frenes: host metrics +
> tus exporters ya dan mucho valor. Refina después.

---

## 2. Pieza tuya #1 — `wg-exporter` (Rust) → OpenMetrics para la capa Red + Seguridad

> **Contexto real del host (verificado):** la interface es **`tailscale0`** (Tailscale, no
> `wg0`), y **`wg` NO está instalado**. Tailscale NO expone stats por `wg show` — se leen
> con `tailscale status --json` + stats del kernel de la interface. Ajuste aplicado.

Un daemon Rust que corre en el **host**, lee el estado de la interface `tailscale0`
(WireGuard via Tailscale), y expone un endpoint **OpenMetrics** (`/metrics`) que Datadog
scrapea con el check Prometheus/OpenMetrics.

**Fuentes de datos (sin `wg`, sin permisos raros):**
- **Tráfico bruto (bytes):** `/sys/class/net/tailscale0/statistics/rx_bytes` y `tx_bytes`
  (lectura simple de archivo en Rust, SIN sudo).
- **Peers / online / offline / IPs:** `tailscale status --json` (parsear JSON en Rust).
- **Seguridad (conexiones/peers):** trackear peers que aparecen/desaparecen en
  `tailscale status` (posible acceso). Handshake fallidos como contador directo NO es
  disponible en Tailscale como en `wg` → alternativa: métricas de rechazos vía logs UFW/firewall
  (afinar en implementación).

**Qué expone (métricas):**
- `ts_net_rx_bytes` / `ts_net_tx_bytes` (totales interface `tailscale0`)
- `ts_peer_online` (por peer: 0/1), `ts_peer_rx_bytes`, `ts_peer_tx_bytes`
- `ts_peer_last_handshake_seconds` (último handshake por peer, si `--json` lo da)
- **Seguridad:** `ts_peer_count` (nº de peers activos), cambios de peers → posible acceso.

**Estructura sugerida (workspace Rust):**
```
rust/
├── Cargo.toml (workspace)
├── crates/
│   ├── wg-exporter/      # lee tailscale0 stats + `tailscale status`, expone /metrics OpenMetrics
│   └── luanti-exporter/  # consulta status UDP Luanti, DogStatsD
```

**Cómo obtiene los datos:** leer `/sys/class/net/tailscale0/statistics/*` y ejecutar
`tailscale status --json`. Si `tailscale status` requiere permisos, documentar el run
correcto (usuario con acceso al CLI de tailscale).

**Cómo lo scrapea Datadog:** check `prometheus`/`openmetrics` apuntando a
`http://127.0.0.1:<PUERTO>/metrics` (conf en `/etc/datadog-agent/conf.d/wg-exporter.d/conf.yaml`).

---

## 3. Pieza tuya #2 — `luanti-exporter` (Rust) → DogStatsD para la capa App

Luanti responde a un **status query UDP** (identificador de protocolo, jugadores conectados,
uptime, versión del server). Tu exporter en Rust:
1. Consulta el container Luanti por UDP.
2. Parsea la respuesta.
3. Empuja las métricas vía **DogStatsD** (el protocolo nativo de Datadog que acepta métricas custom).

**Métricas:**
- `luanti.players_online`
- `luanti.uptime_seconds`
- `luanti.server_version`
- `luanti.avg_rtt`
- (errores/restarts si el server los expone)

**DogStatsD:** el Agent del host escucha el puerto DogStatsD (por defecto `8125/udp`).
El exporter envía métricas ahí. DogStatsD es simple: línea de texto
`luanti.players_online:3|g` (gauge). Fácil en Rust sin dependencias pesadas (o con
`dogstatsd`/`metrics` crates).

---

## 4. Capa Seguridad (dentro de `wg-exporter`)

Además de WireGuard, refuerza la capa de seguridad con:
- Intents de conexión rechazados (UFW events / `dmesg` si logueas)
- Failed logins de SSH: consulta `/var/log/auth.log` y expón contador
  (`ssh_failed_logins_total`) — conecta con tu capa "Security Signals".
- (Opcional) metric de `secure.enable_security` del Luanti como booleano.

---

## 5. Dashboard único — "Luanti Platform Overview" (4 secciones)

En Datadog → Dashboards → New Dashboard:

1. **Infrastructure** — `system.cpu.*`, `system.mem.*`, `system.disk.*`, `container.*` (si auto-descubre).
2. **Network (WireGuard)** — `wg_peer_transfer_*`, `wg_receive_bytes`, `wg_transmit_bytes`, `wg_peer_last_handshake_seconds`.
3. **Application** — `luanti.players_online`, `luanti.uptime_seconds`, restarts, errors.
4. **Security** — `wg_handshake_failures_total`, `ssh_failed_logins_total`, conexiones rechazadas.

Comparte el dashboard (solo lectura) para mostrar la demo completa.

---

## 6. Alertas (cierra Operate)

- **Host down / load:** `system.load.1` > umbral.
- **Seguridad — posible acceso no autorizado:** `wg_handshake_failures_total` aumenta en 15 min.
- **App:** `luanti.players_online` cae a 0 inesperadamente (¿server caído?).

---

## 7. Resultado y valor del portfolio

- **Stack real de 4 capas** en un dashboard: infra + red + app + seguridad.
- **Código Rust propio generando telemetría real** (WireGuard + Luanti) — el diferenciador
  más fuerte del proyecto: "no solo usé Datadog, construí exportadores que generan las métricas".
- Demuestra: Linux (Agent, systemd), containers (Podman auto-discovery), networking
  (WireGuard), seguridad (handshake/SSH), Rust, y observabilidad (Datadog + DogStatsD/OpenMetrics).
- Material directo para roles cloud support / observability / platform engineer.

---

## 8. Notas / trampas

- **Agent en HOST, no dentro del container** (ver §0, corrección 1).
- `wg show` requiere acceso host + permisos (sudo/CAP). Documenta el run correcto.
- DogStatsD por defecto en `8125/udp` — confirma que el Agent lo escucha.
- OpenMetrics scrape exige endpoint HTTP alcanzable por el Agent (localhost está bien si el
  daemon corre en host).
- NO expongas `DD_API_KEY` en el repo público (queda en el host; gitleaks ya protege).
- Documenta el diseño con un ADR (ej. `ADR-002-observability-datadog-rust`) cuando commitees.

---

*Diseño Fase 2 (adelantada). 2026. Plan, sin commits.*
