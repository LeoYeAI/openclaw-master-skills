use anyhow::Result;
use regex::Regex;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tokio::fs;
use tracing::{info, warn};

use crate::injection;
use crate::patterns::CREDENTIAL_PATTERNS;

/// Overall result of an audit run
#[derive(Debug, Serialize, Deserialize)]
pub struct AuditReport {
    pub skills_scanned: usize,
    pub findings: Vec<Finding>,
    pub hash_baseline_updated: bool,
}

/// A single security finding
#[derive(Debug, Serialize, Deserialize)]
pub struct Finding {
    pub skill: String,
    pub severity: Severity,
    pub category: FindingCategory,
    pub detail: String,
    pub file: Option<String>,
    pub line: Option<usize>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord, Clone, Copy)]
#[serde(rename_all = "UPPERCASE")]
pub enum Severity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

impl std::fmt::Display for Severity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Severity::Info => write!(f, "INFO"),
            Severity::Low => write!(f, "LOW"),
            Severity::Medium => write!(f, "MEDIUM"),
            Severity::High => write!(f, "HIGH"),
            Severity::Critical => write!(f, "CRITICAL"),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub enum FindingCategory {
    HashMismatch,
    CredentialExposure,
    InjectionPattern,
    UndeclaredPermission,
    SuspiciousContent,
}

/// Run a full audit of the skills directory
pub async fn run_audit(skills_path: &str, offline: bool) -> Result<AuditReport> {
    let path = resolve_home(skills_path);
    info!("Starting audit of {}", path.display());

    let mut findings = Vec::new();
    let mut skills_scanned = 0;

    if !path.exists() {
        warn!("Skills directory not found: {}", path.display());
        return Ok(AuditReport {
            skills_scanned: 0,
            findings,
            hash_baseline_updated: false,
        });
    }

    let mut dir = fs::read_dir(&path).await?;
    while let Some(entry) = dir.next_entry().await? {
        let skill_path = entry.path();
        if skill_path.is_dir() {
            let skill_name = skill_path
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .to_string();

            let skill_findings = audit_skill_dir(&skill_path, &skill_name, offline).await?;
            findings.extend(skill_findings);
            skills_scanned += 1;
        }
    }

    // Sort findings by severity (highest first)
    findings.sort_by(|a, b| b.severity.cmp(&a.severity));

    let hash_baseline_updated = update_hash_baseline(&path, &findings).await?;

    Ok(AuditReport {
        skills_scanned,
        findings,
        hash_baseline_updated,
    })
}

/// Check a single skill (by path or clawhub ID)
pub async fn check_skill(skill: &str, offline: bool) -> Result<AuditReport> {
    let local_path = resolve_home(skill);
    let path = if local_path.exists() || !is_probably_clawhub_id(skill) {
        local_path
    } else {
        if offline {
            anyhow::bail!(
                "--offline mode: cannot fetch ClawHub skill '{}'; provide a local path instead",
                skill
            );
        }

        // Looks like a ClawHub ID (author/skill-name) — fetch it to a temp dir
        fetch_clawhub_skill(skill).await?
    };

    let skill_name = path
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .to_string();

    let findings = audit_skill_dir(&path, &skill_name, offline).await?;
    let mut sorted = findings;
    sorted.sort_by(|a, b| b.severity.cmp(&a.severity));

    Ok(AuditReport {
        skills_scanned: 1,
        findings: sorted,
        hash_baseline_updated: false,
    })
}

/// Move a skill to the quarantine directory
pub async fn isolate_skill(skill_name: &str) -> Result<()> {
    let skills_dir = resolve_home("~/.openclaw/skills");
    let quarantine_dir = resolve_home("~/.sentinel/quarantine");
    fs::create_dir_all(&quarantine_dir).await?;

    let skill_path = skills_dir.join(skill_name);
    if !skill_path.exists() {
        anyhow::bail!(
            "Skill '{}' not found in {}",
            skill_name,
            skills_dir.display()
        );
    }

    let dest = quarantine_dir.join(skill_name);
    fs::rename(&skill_path, &dest).await?;
    info!(
        "Skill '{}' moved to quarantine: {}",
        skill_name,
        dest.display()
    );
    Ok(())
}

/// Submit a skill report to ClawHub
pub async fn report_skill(skill_name: &str) -> Result<()> {
    let client = reqwest::Client::new();
    let resp = client
        .post("https://clawhub.ai/api/v1/report")
        .json(&serde_json::json!({ "skill": skill_name, "reporter": "runtime-sentinel" }))
        .send()
        .await?;

    if !resp.status().is_success() {
        anyhow::bail!("ClawHub report API returned {}", resp.status());
    }
    Ok(())
}

// ─── Internal helpers ────────────────────────────────────────────────────────

async fn audit_skill_dir(path: &Path, skill_name: &str, offline: bool) -> Result<Vec<Finding>> {
    let mut findings = Vec::new();

    // 1. Hash integrity check
    findings.extend(check_hashes(path, skill_name).await?);

    // 2. Credential exposure scan
    findings.extend(scan_credentials(path, skill_name).await?);

    // 3. Prompt injection patterns in SKILL.md (meta-check: does the skill
    //    itself contain injection patterns targeting the agent loading it?)
    let skill_md = path.join("SKILL.md");
    if skill_md.exists() {
        let content = fs::read_to_string(&skill_md).await?;
        let inj = injection::scan_text(&content, skill_name);
        findings.extend(inj);

        // 4. Permission declaration audit
        findings.extend(audit_permissions(&content, path, skill_name).await?);
    }

    // 5. VirusTotal hash lookup (online only)
    if !offline {
        findings.extend(virustotal_check(path, skill_name).await?);
    }

    Ok(findings)
}

async fn check_hashes(path: &Path, skill_name: &str) -> Result<Vec<Finding>> {
    let baseline_path = resolve_home("~/.sentinel/baselines").join(format!("{}.json", skill_name));
    let mut findings = Vec::new();

    let current_hashes = compute_dir_hashes(path).await?;

    if baseline_path.exists() {
        let stored: HashMap<String, String> =
            serde_json::from_str(&fs::read_to_string(&baseline_path).await?)?;

        for (file, hash) in &current_hashes {
            match stored.get(file) {
                None => {
                    findings.push(Finding {
                        skill: skill_name.to_string(),
                        severity: Severity::Medium,
                        category: FindingCategory::HashMismatch,
                        detail: format!("New file appeared post-install: {}", file),
                        file: Some(file.clone()),
                        line: None,
                    });
                }
                Some(stored_hash) if stored_hash != hash => {
                    let severity = if file.ends_with(".sh")
                        || file.ends_with(".py")
                        || file.ends_with(".js")
                        || file == "SKILL.md"
                    {
                        Severity::High
                    } else {
                        Severity::Medium
                    };
                    findings.push(Finding {
                        skill: skill_name.to_string(),
                        severity,
                        category: FindingCategory::HashMismatch,
                        detail: format!("File modified since install: {}", file),
                        file: Some(file.clone()),
                        line: None,
                    });
                }
                _ => {}
            }
        }
    } else {
        // No baseline yet — write one now
        let baseline_dir = resolve_home("~/.sentinel/baselines");
        fs::create_dir_all(&baseline_dir).await?;
        let json = serde_json::to_string_pretty(&current_hashes)?;
        fs::write(&baseline_path, json).await?;
        info!("Baseline recorded for skill '{}'", skill_name);
    }

    Ok(findings)
}

async fn compute_dir_hashes(path: &Path) -> Result<HashMap<String, String>> {
    let mut hashes = HashMap::new();
    let mut stack = vec![path.to_path_buf()];

    while let Some(dir) = stack.pop() {
        let mut entries = fs::read_dir(&dir).await?;
        while let Some(entry) = entries.next_entry().await? {
            let p = entry.path();
            if p.is_dir() {
                stack.push(p);
            } else {
                let content = fs::read(&p).await?;
                let hash = hex::encode(Sha256::digest(&content));
                let rel = p
                    .strip_prefix(path)
                    .unwrap_or(&p)
                    .to_string_lossy()
                    .to_string();
                hashes.insert(rel, hash);
            }
        }
    }
    Ok(hashes)
}

async fn scan_credentials(path: &Path, skill_name: &str) -> Result<Vec<Finding>> {
    let mut findings = Vec::new();
    let mut stack = vec![path.to_path_buf()];

    while let Some(dir) = stack.pop() {
        let mut entries = fs::read_dir(&dir).await?;
        while let Some(entry) = entries.next_entry().await? {
            let p = entry.path();
            if p.is_dir() {
                stack.push(p);
                continue;
            }
            // Only scan text-like files
            if let Ok(content) = fs::read_to_string(&p).await {
                let rel = p
                    .strip_prefix(path)
                    .unwrap_or(&p)
                    .to_string_lossy()
                    .to_string();

                for (i, line) in content.lines().enumerate() {
                    for (pattern_name, re) in CREDENTIAL_PATTERNS.iter() {
                        if re.is_match(line) {
                            findings.push(Finding {
                                skill: skill_name.to_string(),
                                severity: Severity::High,
                                category: FindingCategory::CredentialExposure,
                                detail: format!("Possible {} exposed in plaintext", pattern_name),
                                file: Some(rel.clone()),
                                line: Some(i + 1),
                            });
                        }
                    }

                    // High-entropy string check (likely a key/secret)
                    for token in line.split_whitespace() {
                        if token.len() >= 32 && looks_like_secret(token) {
                            findings.push(Finding {
                                skill: skill_name.to_string(),
                                severity: Severity::Medium,
                                category: FindingCategory::CredentialExposure,
                                detail: format!("High-entropy token (possible secret) in {}", rel),
                                file: Some(rel.clone()),
                                line: Some(i + 1),
                            });
                        }
                    }
                }
            }
        }
    }
    Ok(findings)
}

/// Rough heuristic: high Shannon entropy + alphanumeric/base64 characters
fn looks_like_secret(s: &str) -> bool {
    let charset_ok = s
        .chars()
        .all(|c| c.is_alphanumeric() || "+/=_-".contains(c));
    if !charset_ok {
        return false;
    }
    let ent = entropy::metric_entropy(s);
    ent > 4.5 // bits per character threshold
}

async fn audit_permissions(
    skill_md_content: &str,
    skill_path: &Path,
    skill_name: &str,
) -> Result<Vec<Finding>> {
    let mut findings = Vec::new();

    // Check if skill has shell scripts but doesn't declare `binaries`
    let has_scripts = {
        let mut found = false;
        let mut stack = vec![skill_path.to_path_buf()];
        'outer: while let Some(dir) = stack.pop() {
            if let Ok(mut entries) = fs::read_dir(&dir).await {
                while let Some(Ok(entry)) = entries.next_entry().await.ok() {
                    let p = entry.path();
                    if p.is_dir() {
                        stack.push(p);
                    } else if matches!(
                        p.extension().and_then(|e| e.to_str()),
                        Some("sh") | Some("py") | Some("js") | Some("rb")
                    ) {
                        found = true;
                        break 'outer;
                    }
                }
            }
        }
        found
    };

    let declares_binaries = skill_md_content.contains("binaries:");

    if has_scripts && !declares_binaries {
        findings.push(Finding {
            skill: skill_name.to_string(),
            severity: Severity::Medium,
            category: FindingCategory::UndeclaredPermission,
            detail: "Skill contains executable scripts but does not declare `binaries` in SKILL.md frontmatter".to_string(),
            file: Some("SKILL.md".to_string()),
            line: None,
        });
    }

    Ok(findings)
}

async fn virustotal_check(path: &Path, skill_name: &str) -> Result<Vec<Finding>> {
    // Hash all files and submit to VirusTotal's public hash lookup
    // (no file upload — hash-only lookup preserves privacy)
    let hashes = compute_dir_hashes(path).await?;
    let client = reqwest::Client::new();
    let mut findings = Vec::new();

    for (file, hash) in &hashes {
        let url = format!("https://www.virustotal.com/api/v3/files/{}", hash);
        if let Ok(resp) = client.get(&url).send().await {
            if resp.status() == 200 {
                if let Ok(body) = resp.json::<serde_json::Value>().await {
                    let malicious = body["data"]["attributes"]["last_analysis_stats"]["malicious"]
                        .as_u64()
                        .unwrap_or(0);
                    if malicious > 0 {
                        findings.push(Finding {
                            skill: skill_name.to_string(),
                            severity: Severity::Critical,
                            category: FindingCategory::SuspiciousContent,
                            detail: format!(
                                "VirusTotal: {} engine(s) flagged {} as malicious",
                                malicious, file
                            ),
                            file: Some(file.clone()),
                            line: None,
                        });
                    }
                }
            }
        }
    }
    Ok(findings)
}

fn is_probably_clawhub_id(skill: &str) -> bool {
    if skill.starts_with('.') || skill.starts_with('/') || skill.starts_with('~') {
        return false;
    }

    let mut parts = skill.split('/');
    let author = parts.next();
    let name = parts.next();

    // Exactly two path segments in the form `author/skill-name`
    author.is_some() && name.is_some() && parts.next().is_none()
}

async fn fetch_clawhub_skill(clawhub_id: &str) -> Result<PathBuf> {
    // Download skill zip to a temp directory for scanning before install
    let client = reqwest::Client::new();
    let url = format!("https://clawhub.ai/api/v1/skills/{}/download", clawhub_id);
    let resp = client.get(&url).send().await?;
    if !resp.status().is_success() {
        anyhow::bail!(
            "Could not fetch skill '{}' from ClawHub: {}",
            clawhub_id,
            resp.status()
        );
    }
    let bytes = resp.bytes().await?;
    let tmp = tempfile::tempdir()?;
    let zip_path = tmp.path().join("skill.zip");
    tokio::fs::write(&zip_path, &bytes).await?;

    // Extract (basic zip extraction — production would use zip crate)
    let output = tokio::process::Command::new("unzip")
        .arg("-q")
        .arg(&zip_path)
        .arg("-d")
        .arg(tmp.path())
        .output()
        .await?;

    if !output.status.success() {
        anyhow::bail!("Failed to extract skill archive");
    }

    // Return path to extracted skill directory
    let skill_name = clawhub_id.split('/').last().unwrap_or(clawhub_id);
    Ok(tmp.into_path().join(skill_name))
}

async fn update_hash_baseline(_skills_path: &Path, findings: &[Finding]) -> Result<bool> {
    // If no hash mismatches, baseline is current
    let has_mismatch = findings
        .iter()
        .any(|f| matches!(f.category, FindingCategory::HashMismatch));
    Ok(!has_mismatch)
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

#[cfg(test)]
mod tests {
    use super::is_probably_clawhub_id;

    #[test]
    fn clawhub_id_detection_accepts_author_skill_name() {
        assert!(is_probably_clawhub_id("author/skill-name"));
    }

    #[test]
    fn clawhub_id_detection_rejects_local_paths() {
        assert!(!is_probably_clawhub_id("./author/skill-name"));
        assert!(!is_probably_clawhub_id("/tmp/skill"));
        assert!(!is_probably_clawhub_id("~/skills/skill-a"));
    }

    #[test]
    fn clawhub_id_detection_rejects_non_canonical_ids() {
        assert!(!is_probably_clawhub_id("author"));
        assert!(!is_probably_clawhub_id("author/skill-name/extra"));
    }
}
