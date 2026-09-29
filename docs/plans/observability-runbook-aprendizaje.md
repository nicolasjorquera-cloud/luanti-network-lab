# RUNBOOK + APRENDIZAJE — Observabilidad Luanti con Datadog

> **Propósito:** que ENTENDÁS (no solo copies) qué hace cada pieza, y que puedas
> **replicar esto en cualquier servidor** y **explicarlo** en una entrevista o a un cliente.
> Es un documento vivo: se actualiza a medida que avanza la Fase 2 (luanti | datadog).

---

# PARTE A — LOS CONCEPTOS (entiende esto y todo lo demás tiene sentido)

## A1. ¿Qué es "observabilidad"? (en cristiano)
Es la capacidad de **saber qué está pasando dentro de tu sistema desde afuera**, sin adivinar.
Imagina que tu servidor es una casa: la observabilidad son los "sensores" (cámaras, medidores,
alarmas) que te dicen qué pasa adentro sin que tengas que entrar. Tiene 3 pilares (los "3 pillars"):

| Pilar | Qué es | Pregunta que responde |
|---|---|---|
| **Métricas** | Números que cambian en el tiempo (CPU, RAM, tráfico) | "¿Cuánto está usando?" |
| **Logs** | Registros de eventos (errores, logins, acciones) | "¿Qué pasó exactamente?" |
| **Traces** | Recorrido de una petición por todo el sistema | "¿Dónde se demoró/falló?" |

En este lab construimos los 3 a la vez, pero el foco son **métricas + logs** (los traces
vendrán después con APM).

## A2. ¿Qué es el Datadog Agent? (la pieza central)
Es un **programa que corre en tu servidor** (un servicio systemd llamado `datadog-agent`)
y cuyo único trabajo es **recolectar datos y mandarlos a la nube de Datadog**.
- Se instala UNA VEZ por servidor.
- Al instalarse, por defecto ya recolecta **métricas del host**: CPU, RAM, disco, red.
  (Por eso viste el host en "Host Map" sin tocar nada.)
- Para que recolecte MÁS cosas (logs, métricas de apps, de containers...), le **agregas
  configuraciones** (ver A3).
- Es de "agente": tú no lo miras, él mira por ti y reporta.

> **IMPORTANTE:** el Agent va en el **HOST** (el servidor), NO dentro de un container.
> Si lo metes dentro de un container, solo vería ese container con visión limitada. Desde
> el host, ve todo (host + containers desde afuera).

## A3. El PATRÓN de toda configuración (¡LA CLAVE DE TODO!)
Todo lo que le pides al Agent que recolecte sigue **SIEMPRE el mismo patrón de 2 pasos**:

1. **Crear un archivo YAML** en `/etc/datadog-agent/conf.d/<nombre>/conf.yaml`
   que le dice al Agent QUÉ recolectar.
2. **Reiniciar el Agent** (`sudo systemctl restart datadog-agent`) para que lo cargue.

Ese archivo YAML define un "check" (una cosa que revisar). Si lo entiendes, ya puedes
añadir cualquier integración de Datadog: todo es "crear archivo + reiniciar".

## A4. Cómo llegan los datos (el flujo)
```
[tu servidor/Luanti] --(Agent recoge)--> [Datadog Agent] --(internet)--> [Nube Datadog]
        │                                                                  │
        └── métricas de host, logs, y (después) métricas de tus exporters ──┘
```
- El **Agent** corre en tu host.
- Los **exporters** (que vamos a escribir en Rust) generan métricas y se las pasan al Agent.
- El Agent sube todo a la **UI de Datadog** (en el navegador) donde armas dashboards y alertas.

## A5. ¿Qué son los exporters y por qué son "tuyos"?
Un **exporter** es un programita que **genera métricas sobre algo específico** y las expone
para que un recolector (el Agent) las tome. 
- Datadog NO tiene integración nativa para tu game server Luanti ni para leer Tailscale/WireGuard.
- Entonces TÚ escribes un exporter (en Rust) que consulta esos datos y los convierte en métricas.
- **Eso es el diferenciador:** en vez de solo "usar Datadog" (que cualquiera hace), construyes
  las piezas que generan la telemetría. Entiendes el sistema completo.

Las 4 capas que vamos a monitorear (tu diseño):
| Capa | Qué mide | Quién la recolecta | Tu pieza |
|---|---|---|---|
| Infra | CPU/RAM/disco/red del host | Agent (automático) | — |
| Red | Tráfico/estado de la VPN WireGuard (Tailscale) | **tu exporter Rust** | `wg-exporter` |
| App | Jugadores online, uptime, versión del Luanti | **tu exporter Rust** | `luanti-exporter` |
| Seguridad | failed logins SSH, eventos auth | Agent + check de logs | config de log |

---

# PARTE B — EL ESTADO REAL (dónde estamos hoy, verificado)

| Paso | Qué era | Estado | Cómo lo sé |
|---|---|---|---|
| 1-2 | Cuenta + Agent instalado + host visible | ✅ HECHO | `systemctl is-active datadog-agent` = active; lo viste en Host Map |
| 3 | Ver el container Luanti (Podman) | ⏭️ SALTADO (opcional) | la config no quedó / se decide después |
| 4 | Logs `auth.log` (capa Seguridad) | ✅ HECHO | `conf.yaml` existe y `Status: OK`, leyó bytes |
| 5 | Dashboard base sección Infra | ⏳ PENDIENTE | — |
| 6-10 | Exporters Rust + dashboard completo | ⏳ PENDIENTE | — |

**Datos técnicos confirmados de tu servidor (importantes para replicar):**
- Interface VPN (WireGuard via Tailscale) = **`tailscale0`**
- **`wg` NO está instalado** → NO se usa `wg show`; se usa `tailscale status --json` + `/sys/class/net/tailscale0/statistics/*`
- Socket Podman rootless = `/run/user/1000/podman/podman.sock`
- Agent = servicio systemd **active + enabled** (corre y arranca al boot)

---

# PARTE C — EL RUNBOOK PASO A PASO (ejecutar en cualquier servidor)

> Graba el patrón de A3: cada cosa = crear archivo + reiniciar Agent.

## Paso 1-2 · Instalar el Agent en un servidor nuevo
```bash
DD_API_KEY=<TU_KEY> DD_SITE=<TU_SITE> bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent.sh)"
```
- `<TU_KEY>` = API key de Datadog (Organization Settings → API Keys).
- `<TU_SITE>` = tu región (verificarla en tu cuenta, ej. `datadoghq.com`, `us3.datadoghq.com`).
- **Trampa #1:** si pones el sitio equivocado, el Agent no reporta nada y "parece roto".
- Verificar: `sudo datadog-agent status` y la UI (Host Map).

## Paso 3 · (Opcional) Ver containers Podman
> **OJO:** este paso puede ser doloroso en Podman rootless (permisos). NO es crítico.
> Se puede saltar sin que se pierda el proyecto — los exporters dan las métricas del Luanti.
- El Agent ve containers si alcanza el socket del runtime.
- Config correcta (para Podman rootless) con la integración podman:
  ```bash
  sudo mkdir -p /etc/datadog-agent/conf.d/podman.d
  sudo tee /etc/datadog-agent/conf.d/podman.d/conf.yaml > /dev/null <<'EOF'
  init_config:
  instances:
    - host: "unix:///run/user/1000/podman/podman.sock"
      connect_timeout: 5
      read_timeout: 5
  EOF
  sudo systemctl restart datadog-agent
  ```
- Verificar: `sudo datadog-agent status | grep -A 25 -i podman` y UI → Containers.
- Si da error de permisos ("permission denied"), es el problema clásico de Podman
  rootless. **No lo pelees más de ~20 min:** saltalo y vuelve después.

## Paso 4 · Ingestar logs de `auth.log` (capa Seguridad) — ✅ HECHO, este es el modelo
```bash
sudo mkdir -p /etc/datadog-agent/conf.d/system_auth.d
sudo tee /etc/datadog-agent/conf.d/system_auth.d/conf.yaml > /dev/null <<'EOF'
logs:
  - type: file
    path: /var/log/auth.log
    service: luanti-host
    source: auth
    sourcecategory: security
EOF
sudo systemctl restart datadog-agent
```
Verificar: `sudo datadog-agent status | grep -A 15 -i log` → debe decir `Status: OK`,
y en la UI buscar `source:auth`.

**Explicación de cada línea (para explicarlo):**
- `type: file` → el Agent leerá un archivo.
- `path: /var/log/auth.log` → cuál archivo (los eventos de autenticación de Ubuntu).
- `source: auth` → etiqueta que usa Datadog para parsear failed logins.
- `service: luanti-host` → bajo qué nombre de servicio se agrupan.
- `sourcecategory: security` → categoría "seguridad".

## Paso 5 · Dashboard base (sección Infra) — en el navegador
1. UI de Datadog → **Dashboards → New Dashboard** → nombre: `Luanti Platform Overview`.
2. **Add widgets** (Agregar widgets):
   - Timeseries CPU: `avg:system.cpu.user{*}`
   - Timeseries RAM: `avg:system.mem.used{*}`
   - Timeseries disco: `avg:system.disk.used{*}`
   - Timeseries red: `avg:system.net.bytes_sent{*}` y `...rcvd`
   - (Opcional, semilla Seguridad) Log stream con `source:auth`.
3. **Save**.
> Los queries usan "avg:" (promedio) + la métrica + `{*}` (todos los hosts).

## Paso 6-8 · Exporters Rust (tu diferenciador) — después
> Sección que se completa cuando los escribamos. Concepto: workspace Rust con 2 crates:
> - `wg-exporter` → lee `tailscale0` stats + `tailscale status --json`, expone OpenMetrics `/metrics`
> - `luanti-exporter` → consulta status UDP del Luanti, manda DogStatsD

## Paso 9 · Dashboard completo (4 capas) — después
## Paso 10 · Alertas — después

---

# PARTE D — CÓMO VERIFICAR (las 3 comprobaciones que siempre haces)
1. **Estado del Agent:** `systemctl is-active datadog-agent` → `active`.
2. **Estado del check:** `sudo datadog-agent status | grep -A N -i <nombre>` → `OK`.
3. **UI de Datadog:** ver los datos (Host Map, Logs, Metrics Summary, Dashboards).

---

# PARTE E — REPLICAR EN OTRO SERVIDOR (checklist portátil)
Para monitorear un servidor NUEVO con esto:
1. Instalar Agent (Paso 1-2).
2. Confirmar host en Host Map.
3. (Opcional) Podman containers (Paso 3) — solo si usas Podman.
4. Ingestar logs de `auth.log` (Paso 4) — copiar el mismo `conf.yaml`.
5. Reusar el mismo dashboard (se exporta/importa en Datadog).
6. (Si aplica) Correr los mismos exporters Rust.

> El valor de tenerlo en un runbook: **cualquier servidor nuevo es solo repetir estos pasos.**

---

*Documento vivo de aprendizaje + runbook. Fase 2 (observabilidad Datadog). 2026.*
