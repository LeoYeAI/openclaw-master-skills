use anyhow::Result;
use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::mpsc;
use tokio::fs;
use tracing::{error, info, warn};

use crate::audit;
use crate::egress;
use crate::payment;
use crate::process;
use chrono::{DateTime, Utc};

const DAEMON_PID_FILE: &str = "~/.sentinel/daemon.pid";
const DAEMON_LOG_FILE: &str = "~/.sentinel/daemon.log";

#[derive(Debug, Serialize, Deserialize)]
struct DaemonState {
    pid: u32,
    started_at: String,
    premium_until: Option<String>,
}

pub async fn start(offline: bool) -> Result<()> {
    let pid_path = resolve_home(DAEMON_PID_FILE);

    if pid_path.exists() {
        let state: DaemonState = serde_json::from_str(&fs::read_to_string(&pid_path).await?)?;
        if process_running(state.pid) {
            println!(
                "Daemon already running (PID {}). Use `sentinel daemon stop` first.",
                state.pid
            );
            return Ok(());
        }

        warn!(
            "Removing stale daemon PID file for non-running PID {}",
            state.pid
        );
        fs::remove_file(&pid_path).await?;
    }

    // Premium gate: acquire x402 session token unless offline
    let mut premium_until = None;
    if !offline {
        println!("Acquiring premium session via x402...");
        match payment::execute_x402_payment(
            "https://api.runtime-sentinel.dev/v1/daemon/start",
            &serde_json::json!({"features": ["egress", "process_anomaly", "file_watch"]}),
        )
        .await
        {
            Ok(resp) => {
                premium_until = extract_premium_expiry(&resp);
                info!("Premium session granted: {:?}", resp);
            }
            Err(e) => {
                warn!(
                    "Premium payment failed ({}). Starting in free-tier mode (file watch only).",
                    e
                );
            }
        }
    }

    let state = DaemonState {
        pid: std::process::id(),
        started_at: chrono::Utc::now().to_rfc3339(),
        premium_until,
    };
    fs::create_dir_all(resolve_home("~/.sentinel")).await?;
    fs::write(&pid_path, serde_json::to_string(&state)?).await?;

    println!("✅ Daemon started (PID {})", state.pid);
    println!("Watching: ~/.openclaw/skills, SOUL.md, MEMORY.md");
    println!("Log: {}", DAEMON_LOG_FILE);

    run_watch_loop().await
}

pub async fn stop() -> Result<()> {
    let pid_path = resolve_home(DAEMON_PID_FILE);
    if !pid_path.exists() {
        println!("Daemon is not running.");
        return Ok(());
    }
    let state: DaemonState = serde_json::from_str(&fs::read_to_string(&pid_path).await?)?;
    if !process_running(state.pid) {
        fs::remove_file(&pid_path).await?;
        println!(
            "Daemon PID file existed, but process {} is not running. Cleaned up stale state.",
            state.pid
        );
        return Ok(());
    }

    // Send SIGTERM to the daemon process
    #[cfg(unix)]
    unsafe {
        libc::kill(state.pid as i32, libc::SIGTERM);
    }

    fs::remove_file(&pid_path).await?;
    println!("Daemon stopped (was PID {}).", state.pid);
    Ok(())
}

pub async fn status() -> Result<()> {
    let pid_path = resolve_home(DAEMON_PID_FILE);
    if !pid_path.exists() {
        println!("Daemon: not running");
        return Ok(());
    }
    let state: DaemonState = serde_json::from_str(&fs::read_to_string(&pid_path).await?)?;
    if !process_running(state.pid) {
        fs::remove_file(&pid_path).await?;
        println!(
            "Daemon: not running (cleaned up stale PID file for {})",
            state.pid
        );
        return Ok(());
    }

    println!("Daemon: running (PID {})", state.pid);
    println!("Started: {}", state.started_at);
    if let Some(premium_until) = active_premium_until(&state) {
        println!("Mode: paid");
        println!("Premium active until: {}", premium_until);
    } else {
        println!("Mode: free tier (file watch only)");
    }
    Ok(())
}

fn extract_premium_expiry(resp: &serde_json::Value) -> Option<String> {
    let metadata = resp.get("metadata").unwrap_or(resp);
    let keys = [
        "premium_until",
        "expires_at",
        "expiresAt",
        "expiry",
        "valid_until",
        "validUntil",
    ];

    keys.into_iter().find_map(|key| {
        metadata.get(key).and_then(|value| {
            value.as_str().and_then(normalize_timestamp).or_else(|| {
                value
                    .as_i64()
                    .and_then(|secs| DateTime::from_timestamp(secs, 0).map(|dt| dt.to_rfc3339()))
            })
        })
    })
}

fn normalize_timestamp(raw: &str) -> Option<String> {
    if let Ok(dt) = DateTime::parse_from_rfc3339(raw) {
        return Some(dt.with_timezone(&Utc).to_rfc3339());
    }

    if let Ok(secs) = raw.parse::<i64>() {
        return DateTime::from_timestamp(secs, 0).map(|dt| dt.to_rfc3339());
    }

    None
}

fn active_premium_until(state: &DaemonState) -> Option<&str> {
    let premium_until = state.premium_until.as_deref()?;
    let parsed = DateTime::parse_from_rfc3339(premium_until).ok()?;
    (parsed.with_timezone(&Utc) > Utc::now()).then_some(premium_until)
}

pub async fn logs(lines: usize) -> Result<()> {
    let log_path = resolve_home(DAEMON_LOG_FILE);
    if !log_path.exists() {
        println!("No log file found at {}", DAEMON_LOG_FILE);
        return Ok(());
    }
    let content = fs::read_to_string(&log_path).await?;
    let all_lines: Vec<&str> = content.lines().collect();
    let start = all_lines.len().saturating_sub(lines);
    for line in &all_lines[start..] {
        println!("{}", line);
    }
    Ok(())
}

async fn run_watch_loop() -> Result<()> {
    let (tx, rx) = mpsc::channel::<notify::Result<Event>>();

    let mut watcher = RecommendedWatcher::new(tx, Config::default())?;

    let skills_dir = resolve_home("~/.openclaw/skills");
    let soul_md = resolve_home("~/.openclaw/SOUL.md");
    let memory_md = resolve_home("~/.openclaw/MEMORY.md");

    if skills_dir.exists() {
        watcher.watch(&skills_dir, RecursiveMode::Recursive)?;
    }
    if soul_md.exists() {
        watcher.watch(&soul_md, RecursiveMode::NonRecursive)?;
    }
    if memory_md.exists() {
        watcher.watch(&memory_md, RecursiveMode::NonRecursive)?;
    }

    info!("File watcher active");

    let egress_interval = std::time::Duration::from_secs(10);
    let mut last_egress_scan = std::time::Instant::now() - egress_interval;

    loop {
        match rx.recv_timeout(std::time::Duration::from_secs(2)) {
            Ok(Ok(event)) => handle_fs_event(event).await,
            Ok(Err(e)) => error!("Watcher error: {:?}", e),
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => break,
        }

        if last_egress_scan.elapsed() >= egress_interval {
            if let Err(e) = scan_egress().await {
                warn!("Egress scan failed: {}", e);
            }
            if let Err(e) = scan_process_anomalies().await {
                warn!("Process anomaly scan failed: {}", e);
            }
            last_egress_scan = std::time::Instant::now();
        }
    }

    Ok(())
}

async fn scan_egress() -> Result<()> {
    let skill_pids = process::collect_skill_roots().await?;
    if skill_pids.is_empty() {
        return Ok(());
    }

    let events = egress::snapshot_connections(&skill_pids).await?;
    for event in events.into_iter().filter(|e| !e.declared) {
        let skill = event
            .skill_name
            .clone()
            .unwrap_or_else(|| event.process_name.clone());
        let severity = egress::undeclared_severity(&event.remote_addr, event.remote_port);
        let msg = format!(
            "[{}] {}: Undeclared outbound connection from pid {} ({}) to {}:{}",
            severity, skill, event.pid, event.process_name, event.remote_addr, event.remote_port
        );

        log_alert(&msg).await;
        if severity >= crate::audit::Severity::High {
            eprintln!("🔴 {}", msg);
        } else {
            eprintln!("🟠 {}", msg);
        }
    }

    Ok(())
}

async fn scan_process_anomalies() -> Result<()> {
    let findings = process::snapshot_skill_process_findings().await?;
    for finding in findings {
        let msg = format!(
            "[{}] {}: Undeclared process execution pid {} (ppid {}) binary={} command={}",
            finding.severity,
            finding.skill_name,
            finding.pid,
            finding.ppid,
            finding.observed_binary,
            finding.command
        );

        log_alert(&msg).await;
        if finding.severity >= crate::audit::Severity::High {
            eprintln!("🔴 {}", msg);
        } else {
            eprintln!("🟠 {}", msg);
        }
    }

    Ok(())
}

async fn handle_fs_event(event: Event) {
    match event.kind {
        EventKind::Modify(_) | EventKind::Create(_) => {
            for path in &event.paths {
                let path_str = path.to_string_lossy();

                // SOUL.md / MEMORY.md writes are always CRITICAL
                if path_str.ends_with("SOUL.md") || path_str.ends_with("MEMORY.md") {
                    let msg = format!(
                        "CRITICAL: Unauthorized write to {} detected. Possible skill poisoning.",
                        path_str
                    );
                    log_alert(&msg).await;
                    eprintln!("🚨 {}", msg);
                    continue;
                }

                // Skill file modifications
                if path_str.contains("/.openclaw/skills/") {
                    // Re-audit the affected skill
                    if let Some(skill_dir) = find_skill_root(path) {
                        let skill_name = skill_dir
                            .file_name()
                            .unwrap_or_default()
                            .to_string_lossy()
                            .to_string();
                        info!("Re-auditing skill '{}' due to file change", skill_name);
                        match audit::run_audit(&skill_dir.to_string_lossy(), false).await {
                            Ok(report) => {
                                for finding in report.findings {
                                    let msg = format!(
                                        "[{}] {}: {}",
                                        finding.severity, finding.skill, finding.detail
                                    );
                                    log_alert(&msg).await;
                                    if finding.severity >= crate::audit::Severity::High {
                                        eprintln!("🔴 {}", msg);
                                    }
                                }
                            }
                            Err(e) => error!("Re-audit failed: {}", e),
                        }
                    }
                }
            }
        }
        _ => {}
    }
}

fn find_skill_root(path: &std::path::Path) -> Option<PathBuf> {
    // Walk up until we find the skills directory's direct child
    let mut current = path.to_path_buf();
    while let Some(parent) = current.parent() {
        if parent.ends_with(".openclaw/skills") {
            return Some(current);
        }
        current = parent.to_path_buf();
    }
    None
}

async fn log_alert(msg: &str) {
    let log_path = resolve_home(DAEMON_LOG_FILE);
    let entry = format!("[{}] {}\n", chrono::Utc::now().to_rfc3339(), msg);
    if let Ok(mut file) = tokio::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
        .await
    {
        use tokio::io::AsyncWriteExt;
        let _ = file.write_all(entry.as_bytes()).await;
    }
}

fn resolve_home(path: &str) -> PathBuf {
    if let Some(stripped) = path.strip_prefix("~/") {
        dirs::home_dir()
            .unwrap_or_else(|| PathBuf::from("/tmp"))
            .join(stripped)
    } else {
        PathBuf::from(path)
    }
}

fn process_running(pid: u32) -> bool {
    #[cfg(unix)]
    unsafe {
        if libc::kill(pid as i32, 0) == 0 {
            return true;
        }

        return std::io::Error::last_os_error().raw_os_error() == Some(libc::EPERM);
    }

    #[cfg(not(unix))]
    {
        let _ = pid;
        true
    }
}
