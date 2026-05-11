// egress.rs — Network egress monitoring (premium)
// Attributes outbound connections to the skill subprocesses that initiated them.
// Uses /proc/net/tcp on Linux and lsof on macOS.

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
use std::path::PathBuf;
use tokio::fs;
use tracing::{debug, info, warn};

#[derive(Debug, Serialize, Deserialize)]
pub struct EgressEvent {
    pub pid: u32,
    pub process_name: String,
    pub skill_name: Option<String>,
    pub remote_addr: String,
    pub remote_port: u16,
    pub declared: bool, // true if skill declared this connection in its manifest
}

#[derive(Debug, Clone)]
struct SocketEntry {
    remote_addr: String,
    remote_port: u16,
    inode: u64,
}

pub async fn snapshot_connections(skill_pids: &[(u32, String)]) -> Result<Vec<EgressEvent>> {
    info!(
        "Snapshotting network connections for {} skill processes",
        skill_pids.len()
    );

    #[cfg(target_os = "linux")]
    return linux_connections(skill_pids).await;

    #[cfg(target_os = "macos")]
    return macos_connections(skill_pids).await;

    #[cfg(not(any(target_os = "linux", target_os = "macos")))]
    anyhow::bail!("Egress monitoring not supported on this platform")
}

#[cfg(target_os = "linux")]
async fn linux_connections(skill_pids: &[(u32, String)]) -> Result<Vec<EgressEvent>> {
    let mut inode_map: HashMap<u64, SocketEntry> = HashMap::new();
    for file in ["/proc/net/tcp", "/proc/net/tcp6"] {
        for socket in parse_proc_net_file(file).await? {
            inode_map.insert(socket.inode, socket);
        }
    }

    let mut events = Vec::new();
    let mut seen = HashSet::new();

    for (pid, skill_name) in skill_pids {
        let declared_destinations = load_declared_destinations(skill_name).await;
        let process_name = read_process_name(*pid)
            .await
            .unwrap_or_else(|| skill_name.clone());

        let fd_dir = format!("/proc/{}/fd", pid);
        let mut dir = match fs::read_dir(&fd_dir).await {
            Ok(dir) => dir,
            Err(e) => {
                debug!("Skipping PID {} fd scan ({}): {}", pid, fd_dir, e);
                continue;
            }
        };

        while let Ok(Some(entry)) = dir.next_entry().await {
            let link_target = match fs::read_link(entry.path()).await {
                Ok(target) => target,
                Err(_) => continue,
            };

            if let Some(inode) = parse_socket_inode(&link_target) {
                if let Some(socket) = inode_map.get(&inode) {
                    let key = (*pid, inode, socket.remote_port);
                    if seen.insert(key) {
                        events.push(EgressEvent {
                            pid: *pid,
                            process_name: process_name.clone(),
                            skill_name: Some(skill_name.clone()),
                            remote_addr: socket.remote_addr.clone(),
                            remote_port: socket.remote_port,
                            declared: destination_declared(
                                &declared_destinations,
                                &socket.remote_addr,
                            ),
                        });
                    }
                }
            }
        }
    }

    Ok(events)
}

#[cfg(target_os = "linux")]
async fn parse_proc_net_file(path: &str) -> Result<Vec<SocketEntry>> {
    let content = fs::read_to_string(path).await?;
    let mut sockets = Vec::new();

    for line in content.lines().skip(1) {
        let cols: Vec<&str> = line.split_whitespace().collect();
        if cols.len() < 10 {
            continue;
        }

        let state = cols[3];
        if state != "01" && state != "02" {
            continue;
        }

        let inode = match cols[9].parse::<u64>() {
            Ok(inode) => inode,
            Err(_) => continue,
        };

        let Some((remote_addr, remote_port)) = decode_proc_address(cols[2]) else {
            continue;
        };

        if remote_port == 0 {
            continue;
        }

        sockets.push(SocketEntry {
            remote_addr,
            remote_port,
            inode,
        });
    }

    Ok(sockets)
}

#[cfg(target_os = "linux")]
fn decode_proc_address(raw: &str) -> Option<(String, u16)> {
    let (hex_addr, hex_port) = raw.split_once(':')?;
    let port = u16::from_str_radix(hex_port, 16).ok()?;

    if hex_addr.len() == 8 {
        let mut octets = [0u8; 4];
        for i in 0..4 {
            let idx = i * 2;
            octets[3 - i] = u8::from_str_radix(&hex_addr[idx..idx + 2], 16).ok()?;
        }
        return Some((Ipv4Addr::from(octets).to_string(), port));
    }

    if hex_addr.len() == 32 {
        let mut bytes = [0u8; 16];
        for i in 0..16 {
            let idx = i * 2;
            bytes[15 - i] = u8::from_str_radix(&hex_addr[idx..idx + 2], 16).ok()?;
        }
        return Some((Ipv6Addr::from(bytes).to_string(), port));
    }

    None
}

fn parse_socket_inode(link_target: &PathBuf) -> Option<u64> {
    let text = link_target.to_string_lossy();
    let inner = text.strip_prefix("socket:[")?.strip_suffix(']')?;
    inner.parse().ok()
}

async fn read_process_name(pid: u32) -> Option<String> {
    let comm_path = format!("/proc/{}/comm", pid);
    fs::read_to_string(comm_path)
        .await
        .ok()
        .map(|s| s.trim().to_string())
}

async fn load_declared_destinations(skill_name: &str) -> Vec<String> {
    if skill_name.is_empty() {
        return Vec::new();
    }

    let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("/tmp"));
    let skill_md = home
        .join(".openclaw/skills")
        .join(skill_name)
        .join("SKILL.md");
    let content = match fs::read_to_string(skill_md).await {
        Ok(content) => content.to_lowercase(),
        Err(_) => return Vec::new(),
    };

    let mut out = Vec::new();
    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("-") {
            out.push(trimmed.trim_start_matches('-').trim().to_string());
        }
        if trimmed.starts_with("network:") || trimmed.starts_with("domains:") {
            if let Some((_, rest)) = trimmed.split_once(':') {
                out.push(rest.trim().to_string());
            }
        }
    }
    out
}

fn destination_declared(declared: &[String], remote_addr: &str) -> bool {
    if declared.is_empty() {
        return false;
    }

    let remote_addr = remote_addr.to_lowercase();
    declared.iter().any(|entry| {
        let entry = entry.trim();
        entry == "any"
            || entry == "*"
            || entry.contains(&remote_addr)
            || entry
                .strip_prefix("*.")
                .map(|suffix| remote_addr.ends_with(suffix))
                .unwrap_or(false)
    })
}

#[cfg(target_os = "macos")]
async fn macos_connections(skill_pids: &[(u32, String)]) -> Result<Vec<EgressEvent>> {
    if skill_pids.is_empty() {
        return Ok(Vec::new());
    }

    let mut skill_name_by_pid = HashMap::new();
    for (pid, skill_name) in skill_pids {
        skill_name_by_pid.insert(*pid, skill_name.clone());
    }

    let pids: Vec<String> = skill_pids.iter().map(|(pid, _)| pid.to_string()).collect();
    let output = tokio::process::Command::new("lsof")
        .args(["-i", "-n", "-P", "-p", &pids.join(",")])
        .output()
        .await?;

    if !output.status.success() {
        warn!("lsof returned non-zero status: {}", output.status);
        return Ok(Vec::new());
    }

    let text = String::from_utf8_lossy(&output.stdout);
    let mut events = Vec::new();
    let mut seen = HashSet::new();

    for line in text.lines().skip(1) {
        let cols: Vec<&str> = line.split_whitespace().collect();
        if cols.len() < 9 {
            continue;
        }

        let Ok(pid) = cols[1].parse::<u32>() else {
            continue;
        };

        if !skill_name_by_pid.contains_key(&pid) {
            continue;
        }

        if !(line.contains("->") || line.contains("TCP")) {
            continue;
        }

        let Some(name_col) = cols.last() else {
            continue;
        };

        let Some((remote_addr, remote_port)) = parse_lsof_destination(name_col) else {
            continue;
        };

        let key = (pid, remote_addr.clone(), remote_port);
        if !seen.insert(key) {
            continue;
        }

        let skill_name = skill_name_by_pid.get(&pid).cloned();
        let declared_destinations = if let Some(skill) = &skill_name {
            load_declared_destinations(skill).await
        } else {
            Vec::new()
        };

        events.push(EgressEvent {
            pid,
            process_name: cols[0].to_string(),
            skill_name,
            remote_addr: remote_addr.clone(),
            remote_port,
            declared: destination_declared(&declared_destinations, &remote_addr),
        });
    }

    Ok(events)
}

#[cfg(target_os = "macos")]
fn parse_lsof_destination(raw: &str) -> Option<(String, u16)> {
    let endpoint = raw.split("->").last()?.trim();
    let (addr, port_str) = endpoint.rsplit_once(':')?;
    let port = port_str.parse::<u16>().ok()?;
    Some((addr.trim_matches(&['[', ']'][..]).to_string(), port))
}

pub fn undeclared_severity(remote_addr: &str, remote_port: u16) -> crate::audit::Severity {
    if remote_port == 4444 || remote_port == 31337 || remote_port == 6667 {
        return crate::audit::Severity::Critical;
    }

    let ip = remote_addr.parse::<IpAddr>().ok();
    if is_internal_destination(ip) {
        crate::audit::Severity::Medium
    } else {
        crate::audit::Severity::High
    }
}

fn is_internal_destination(ip: Option<IpAddr>) -> bool {
    match ip {
        Some(IpAddr::V4(v4)) => {
            v4.is_loopback() || v4.is_private() || v4.is_link_local() || v4.is_multicast()
        }
        Some(IpAddr::V6(v6)) => {
            v6.is_loopback()
                || v6.is_unique_local()
                || v6.is_unicast_link_local()
                || v6.is_multicast()
        }
        None => false,
    }
}
