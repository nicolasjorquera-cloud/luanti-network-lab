//! luanti-exporter — sondea el estado UDP de un servidor Luanti (Minetest)
//! y empuja métricas al Datadog Agent vía DogStatsD (UDP al puerto 8125).
//!
//! Por qué existe: Datadog NO puede recolectar métricas de un servidor Luanti
//! por sí solo (no hay integración oficial). Este exporter es la pieza propia
//! (tu diferenciador) que llena ese hueco.
//!
//! Protocolo de status de Minetest/Luanti:
//!   1. Se envía 1 byte `M` (0x4D) por UDP al puerto del server (30000).
//!   2. El server responde con `M` + una string ASCII:
//!        "[name] | [version] | [uptime_seconds] | [max_players] | [lista de jugadores]"
//!      Ejemplo: "MyServer | luanti-5.8.0 | 3600 | 20 | Alice, Bob"

use std::env;
use std::net::UdpSocket;
use std::time::Duration;

/// Resultado parseado de la respuesta de status del servidor.
struct LuantiStatus {
    name: String,
    version: String,
    uptime_seconds: u64,
    max_players: u32,
    players: Vec<String>,
}

/// Envía el probe `M`, recibe la respuesta y la parsea.
/// Devuelve `None` si el server no responde o la respuesta es inválida.
fn query_status(host: &str, port: u16, timeout: Duration) -> Option<LuantiStatus> {
    // Socket UDP no conectado: podemos enviar y recibir.
    let socket = UdpSocket::bind("0.0.0.0:0").ok()?;
    socket
        .set_read_timeout(Some(timeout))
        .expect("set read timeout");

    // 1) El probe: un solo byte `M`.
    socket.send_to(&[b'M'], format!("{host}:{port}")).ok()?;

    // 2) Recibir la respuesta (búfer de sobra para la string de status).
    let mut buf = [0u8; 65535];
    let (len, _peer) = socket.recv_from(&mut buf).ok()?;

    parse_status(&buf[..len])
}

/// `buf` = `M` + "name | version | uptime | max_players | players..."
fn parse_status(buf: &[u8]) -> Option<LuantiStatus> {
    // El primer byte debe ser `M` (0x4D).
    if buf.first() != Some(&b'M') {
        return None;
    }

    // El resto es ASCII.
    let body = std::str::from_utf8(&buf[1..]).ok()?;
    // Un trailing NUL o '\n' puede llegar con el paquete; lo recortamos.
    let body = body.trim_end_matches(['\0', '\n', '\r']);

    // Separador: " | " (pipe con espacios).
    let parts: Vec<&str> = body.split(" | ").collect();

    let name = parts.first()?.to_string();
    let version = parts.get(1).unwrap_or(&"unknown").to_string();
    let uptime_seconds: u64 = parts.get(2).unwrap_or(&"0").trim().parse().unwrap_or(0);
    let max_players: u32 = parts.get(3).unwrap_or(&"0").trim().parse().unwrap_or(0);

    // El último campo es la lista de jugadores separada por comas (puede venir vacío).
    let players_field = parts.get(4).unwrap_or(&"");
    let players: Vec<String> = players_field
        .split(',')
        .map(|p| p.trim().to_string())
        .filter(|p| !p.is_empty())
        .collect();

    Some(LuantiStatus {
        name,
        version,
        uptime_seconds,
        max_players,
        players,
    })
}

/// Empuja una métrica gauge por DogStatsD.
/// Formato DogStatsD: `luanti.players_online:3|g|#luanti_version:5.8.0`
fn dogstatsd_gauge(
    socket: &UdpSocket,
    agent_host: &str,
    agent_port: u16,
    metric: &str,
    value: f64,
    tags: &[String],
) {
    let mut line = format!("{metric}:{value}|g");
    if !tags.is_empty() {
        line.push_str("|#");
        line.push_str(&tags.join(","));
    }
    // DogStatsD ignora errores de envío (métricas best-effort).
    let _ = socket.send_to(line.as_bytes(), format!("{agent_host}:{agent_port}"));
}

fn main() {
    // ---- Configuración (con defaults sensatos) -------------------------------
    // El container Luanti escucha por UDP en la IP de Tailscale.
    let luanti_host = env::var("LUANTI_HOST").unwrap_or_else(|_| "100.123.166.124".into());
    let luanti_port: u16 = env::var("LUANTI_PORT")
        .unwrap_or_else(|_| "30000".into())
        .parse()
        .expect("LUANTI_PORT debe ser un número");
    // El Agent Datadog escucha DogStatsD por defecto en 127.0.0.1:8125.
    let dogstatsd_host = env::var("DOGSTATSD_HOST").unwrap_or_else(|_| "127.0.0.1".into());
    let dogstatsd_port: u16 = env::var("DOGSTATSD_PORT")
        .unwrap_or_else(|_| "8125".into())
        .parse()
        .expect("DOGSTATSD_PORT debe ser un número");
    // Cada cuántos segundos sondeamos.
    let interval: u64 = env::var("LUANTI_INTERVAL")
        .unwrap_or_else(|_| "10".into())
        .parse()
        .expect("LUANTI_INTERVAL debe ser un número");
    // Timeout para la respuesta UDP.
    let timeout = Duration::from_secs(
        env::var("LUANTI_TIMEOUT")
            .unwrap_or_else(|_| "2".into())
            .parse()
            .expect("LUANTI_TIMEOUT debe ser un número"),
    );

    eprintln!(
        "luanti-exporter: probe {}:{} -> DogStatsD {}:{} cada {}s",
        luanti_host, luanti_port, dogstatsd_host, dogstatsd_port, interval
    );

    // Socket compartido para enviar métricas por DogStatsD.
    let dsd = UdpSocket::bind("0.0.0.0:0").expect("bind DogStatsD socket");

    loop {
        match query_status(&luanti_host, luanti_port, timeout) {
            Some(st) => {
                let tags: Vec<String> = vec![
                    format!("luanti_version:{}", st.version),
                    format!("luanti_server:{}", st.name),
                ];

                dogstatsd_gauge(&dsd, &dogstatsd_host, dogstatsd_port, "luanti.up", 1.0, &tags);
                dogstatsd_gauge(
                    &dsd,
                    &dogstatsd_host,
                    dogstatsd_port,
                    "luanti.players_online",
                    st.players.len() as f64,
                    &tags,
                );
                dogstatsd_gauge(
                    &dsd,
                    &dogstatsd_host,
                    dogstatsd_port,
                    "luanti.max_players",
                    st.max_players as f64,
                    &tags,
                );
                dogstatsd_gauge(
                    &dsd,
                    &dogstatsd_host,
                    dogstatsd_port,
                    "luanti.uptime_seconds",
                    st.uptime_seconds as f64,
                    &tags,
                );

                eprintln!(
                    "[ok] {} | v{} | uptime {}s | jugadores {}/{}: {:?}",
                    st.name,
                    st.version,
                    st.uptime_seconds,
                    st.players.len(),
                    st.max_players,
                    st.players
                );
            }
            None => {
                // El server no respondió (caído o inalcanzable): reportamos down.
                let tags: Vec<String> = vec![format!("luanti_server:{luanti_host}")];
                dogstatsd_gauge(&dsd, &dogstatsd_host, dogstatsd_port, "luanti.up", 0.0, &tags);
                eprintln!("[down] no hay respuesta de {luanti_host}:{luanti_port}");
            }
        }

        std::thread::sleep(Duration::from_secs(interval));
    }
}
