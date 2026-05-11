use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use tokio::fs;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessFinding {
    pub pid: u32,
    pub ppid: u32,
    pub skill_name: String,
    pub observed_binary: String,
    pub command: String,
    pub severity: crate::audit::Severity,
    pub declared: bool,
}

pub async fn snapshot_skill_process_findings() -> Result<Vec<ProcessFinding>> {
    #[cfg(target_os = "linux")]
    {
        return linux_snapshot().await;
    }

    #[cfg(not(target_os = "linux"))]
    {
        Ok(Vec::new())
    }
}

pub async fn collect_skill_roots() -> Result<Vec<(u32, String)>> {
    #[cfg(target_os = "linux")]
    {
        return linux_skill_roots().await;
    }

    #[cfg(target_os = "macos")]
    {
        return macos_skill_roots().await;
    }

    #[cfg(not(any(target_os = "linux", target_os = "macos")))]
    {
        Ok(Vec::new())
    }
}

#[cfg(target_os = "linux")]
async fn linux_snapshot() -> Result<Vec<ProcessFinding>> {
    let roots = linux_skill_roots().await?;
    if roots.is_empty() {
        return Ok(Vec::new());
    }

    let all_procs = linux_process_table().await?;
    let mut findings = Vec::new();

    for (root_pid, skill_name) in roots {
        let declared = load_declared_binaries(&skill_name).await;
        let tree = collect_descendants(root_pid, &all_procs);

        for pid in tree {
            let Some(proc_info) = all_procs.get(&pid) else {
                continue;
            };

            let observed = proc_info.binary.clone();
            let is_declared = binary_declared(&observed, &declared);

            if is_declared {
                continue;
            }

            findings.push(ProcessFinding {
                pid,
                ppid: proc_info.ppid,
                skill_name: skill_name.clone(),
                observed_binary: observed.clone(),
                command: proc_info.command.clone(),
                severity: classify_process(&observed, &proc_info.command),
                declared: false,
            });
        }
    }

    Ok(findings)
}

#[cfg(target_os = "linux")]
async fn linux_skill_roots() -> Result<Vec<(u32, String)>> {
    let mut out = Vec::new();
    let mut dir = fs::read_dir("/proc").await?;

    while let Some(entry) = dir.next_entry().await? {
        let Ok(pid) = entry.file_name().to_string_lossy().parse::<u32>() else {
            continue;
        };

        let cmdline_path = format!("/proc/{}/cmdline", pid);
        let cmdline_bytes = match fs::read(&cmdline_path).await {
            Ok(data) => data,
            Err(_) => continue,
        };

        if cmdline_bytes.is_empty() {
            continue;
        }

        let cmdline = String::from_utf8_lossy(&cmdline_bytes).replace('\0', " ");
        if !cmdline.contains("/.openclaw/skills/") {
            continue;
        }

        if let Some(skill_name) = extract_skill_name(&cmdline) {
            out.push((pid, skill_name));
        }
    }

    Ok(out)
}

#[cfg(target_os = "linux")]
#[derive(Debug, Clone)]
struct ProcInfo {
    ppid: u32,
    binary: String,
    command: String,
}

#[cfg(target_os = "linux")]
async fn linux_process_table() -> Result<HashMap<u32, ProcInfo>> {
    let mut map = HashMap::new();
    let mut dir = fs::read_dir("/proc").await?;

    while let Some(entry) = dir.next_entry().await? {
        let Ok(pid) = entry.file_name().to_string_lossy().parse::<u32>() else {
            continue;
        };

        let status_path = format!("/proc/{}/status", pid);
        let status = match fs::read_to_string(&status_path).await {
            Ok(s) => s,
            Err(_) => continue,
        };
        let ppid = parse_ppid(&status).unwrap_or(0);

        let cmdline_bytes = fs::read(format!("/proc/{}/cmdline", pid))
            .await
            .unwrap_or_default();
        let command = if cmdline_bytes.is_empty() {
            fs::read_to_string(format!("/proc/{}/comm", pid))
                .await
                .unwrap_or_else(|_| "<unknown>".to_string())
                .trim()
                .to_string()
        } else {
            String::from_utf8_lossy(&cmdline_bytes)
                .replace('\0', " ")
                .trim()
                .to_string()
        };

        let exe = fs::read_link(format!("/proc/{}/exe", pid)).await.ok();
        let binary = exe
            .as_ref()
            .and_then(|path| path.file_name().map(|n| n.to_string_lossy().to_string()))
            .or_else(|| command.split_whitespace().next().map(binary_name))
            .unwrap_or_else(|| "<unknown>".to_string())
            .to_lowercase();

        map.insert(
            pid,
            ProcInfo {
                ppid,
                binary,
                command,
            },
        );
    }

    Ok(map)
}

#[cfg(target_os = "linux")]
fn parse_ppid(status: &str) -> Option<u32> {
    status.lines().find_map(|line| {
        let (key, value) = line.split_once(':')?;
        if key.trim() == "PPid" {
            return value.trim().parse::<u32>().ok();
        }
        None
    })
}

#[cfg(target_os = "linux")]
fn collect_descendants(root_pid: u32, process_table: &HashMap<u32, ProcInfo>) -> Vec<u32> {
    let mut children: HashMap<u32, Vec<u32>> = HashMap::new();
    for (pid, info) in process_table {
        children.entry(info.ppid).or_default().push(*pid);
    }

    let mut stack = vec![root_pid];
    let mut out = Vec::new();
    let mut seen = HashSet::new();

    while let Some(pid) = stack.pop() {
        if !seen.insert(pid) {
            continue;
        }
        out.push(pid);

        if let Some(next) = children.get(&pid) {
            stack.extend(next.iter().copied());
        }
    }

    out
}

#[cfg(target_os = "macos")]
async fn macos_skill_roots() -> Result<Vec<(u32, String)>> {
    let output = tokio::process::Command::new("ps")
        .args(["-axo", "pid=,command="])
        .output()
        .await?;

    if !output.status.success() {
        anyhow::bail!("ps failed with {}", output.status);
    }

    let mut out = Vec::new();
    let text = String::from_utf8_lossy(&output.stdout);
    for line in text.lines() {
        let mut parts = line.trim().splitn(2, ' ');
        let Some(pid_raw) = parts.next() else {
            continue;
        };
        let Some(cmd) = parts.next() else {
            continue;
        };
        let Ok(pid) = pid_raw.trim().parse::<u32>() else {
            continue;
        };

        if !cmd.contains("/.openclaw/skills/") {
            continue;
        }

        if let Some(skill_name) = extract_skill_name(cmd) {
            out.push((pid, skill_name));
        }
    }
    Ok(out)
}

async fn load_declared_binaries(skill_name: &str) -> Vec<String> {
    if skill_name.is_empty() {
        return Vec::new();
    }

    let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("/tmp"));
    let skill_md = home
        .join(".openclaw/skills")
        .join(skill_name)
        .join("SKILL.md");
    let content = match fs::read_to_string(skill_md).await {
        Ok(content) => content,
        Err(_) => return Vec::new(),
    };

    parse_declared_binaries(&content)
}

fn parse_declared_binaries(content: &str) -> Vec<String> {
    let Some(frontmatter) = frontmatter(content) else {
        return Vec::new();
    };

    let mut out = Vec::new();
    let mut in_binaries = false;

    for line in frontmatter.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("binaries:") {
            in_binaries = true;
            continue;
        }

        if in_binaries {
            if trimmed.starts_with('-') {
                let val = trimmed
                    .trim_start_matches('-')
                    .split('#')
                    .next()
                    .unwrap_or("")
                    .trim();
                if !val.is_empty() {
                    out.push(binary_name(val).to_lowercase());
                }
                continue;
            }

            if !line.starts_with(' ') && !line.starts_with('\t') {
                in_binaries = false;
            }
        }
    }

    out
}

fn frontmatter(content: &str) -> Option<&str> {
    let mut lines = content.lines();
    if lines.next()?.trim() != "---" {
        return None;
    }

    let mut offset = 4;
    for line in lines {
        if line.trim() == "---" {
            return content.get(4..offset);
        }
        offset += line.len() + 1;
    }

    None
}

fn binary_declared(observed: &str, declared: &[String]) -> bool {
    if declared.is_empty() {
        return false;
    }

    declared.iter().any(|entry| {
        entry == "*" || entry == "any" || observed == entry || observed.ends_with(entry)
    })
}

fn classify_process(observed_binary: &str, command: &str) -> crate::audit::Severity {
    let shellish = [
        "sh",
        "bash",
        "zsh",
        "fish",
        "dash",
        "ksh",
        "python",
        "python3",
        "node",
        "perl",
        "ruby",
        "pwsh",
        "powershell",
        "cmd",
        "wget",
        "curl",
    ];

    if shellish.iter().any(|name| observed_binary == *name) {
        return crate::audit::Severity::High;
    }

    let lowered = command.to_lowercase();
    if lowered.contains("/bin/sh") || lowered.contains("-c ") || lowered.contains("eval ") {
        return crate::audit::Severity::Critical;
    }

    crate::audit::Severity::Medium
}

fn binary_name(raw: &str) -> String {
    let trimmed = raw.trim_matches(|c| c == '"' || c == '\'');
    Path::new(trimmed)
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| trimmed.to_string())
}

fn extract_skill_name(cmd: &str) -> Option<String> {
    let marker = "/.openclaw/skills/";
    let start = cmd.find(marker)? + marker.len();
    let rest = &cmd[start..];
    let skill = rest
        .split(['/', ' ', '\'', '"'])
        .find(|token| !token.is_empty())?;
    Some(skill.to_string())
}

#[cfg(test)]
mod tests {
    use super::{binary_name, parse_declared_binaries};

    #[test]
    fn parses_declared_binaries_from_frontmatter() {
        let content = r#"---
name: sample
compatibility:
  binaries:
    - /bin/bash
    - python3 # inline comment
---
# body"#;

        let parsed = parse_declared_binaries(content);
        assert_eq!(parsed, vec!["bash", "python3"]);
    }

    #[test]
    fn normalizes_binary_name() {
        assert_eq!(binary_name("/usr/bin/node"), "node");
        assert_eq!(binary_name("\"python3\""), "python3");
    }
}
