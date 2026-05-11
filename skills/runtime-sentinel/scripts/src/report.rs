use crate::audit::{AuditReport, Finding, Severity};

pub fn print_audit(report: &AuditReport, json: bool) {
    if json {
        println!(
            "{}",
            serde_json::to_string_pretty(report).unwrap_or_default()
        );
        return;
    }

    println!();
    println!("━━━ runtime-sentinel audit ━━━━━━━━━━━━━━━━━━━━━━");
    println!("Skills scanned: {}", report.skills_scanned);
    println!("Findings: {}", report.findings.len());
    println!();

    if report.findings.is_empty() {
        println!("✅ No findings. All skills appear clean.");
        println!();
        return;
    }

    for finding in &report.findings {
        let icon = severity_icon(finding.severity);
        println!("{} [{}] {}", icon, finding.skill, finding.detail);
        if let Some(file) = &finding.file {
            if let Some(line) = finding.line {
                println!("   └─ {}:{}", file, line);
            } else {
                println!("   └─ {}", file);
            }
        }
        println!();
    }

    let critical = count_severity(report, Severity::Critical);
    let high = count_severity(report, Severity::High);
    let medium = count_severity(report, Severity::Medium);

    println!(
        "Summary: {} critical  {} high  {} medium",
        critical, high, medium
    );

    if critical > 0 || high > 0 {
        println!();
        println!("⚡ Recommended actions:");
        println!("  sentinel isolate <skill-name>   # quarantine suspicious skill");
        println!("  sentinel report <skill-name>    # report to ClawHub");
    }
    println!();
}

pub fn print_check(report: &AuditReport, json: bool) {
    if json {
        println!(
            "{}",
            serde_json::to_string_pretty(report).unwrap_or_default()
        );
        return;
    }

    let risk = overall_risk(report);
    let icon = match risk {
        Severity::Critical => "🔴",
        Severity::High => "🟠",
        Severity::Medium => "🟡",
        Severity::Low => "🟢",
        Severity::Info => "✅",
    };

    println!();
    println!("{} Risk level: {}", icon, risk);
    println!();

    if report.findings.is_empty() {
        println!("No findings. Safe to install.");
    } else {
        for finding in &report.findings {
            println!("  [{}] {}", finding.severity, finding.detail);
            if let Some(file) = &finding.file {
                println!("         {}", file);
            }
        }
    }
    println!();
}

fn severity_icon(s: Severity) -> &'static str {
    match s {
        Severity::Critical => "🔴",
        Severity::High => "🟠",
        Severity::Medium => "🟡",
        Severity::Low => "🟢",
        Severity::Info => "ℹ️ ",
    }
}

fn count_severity(report: &AuditReport, s: Severity) -> usize {
    report.findings.iter().filter(|f| f.severity == s).count()
}

fn overall_risk(report: &AuditReport) -> Severity {
    report
        .findings
        .iter()
        .map(|f| f.severity)
        .max()
        .unwrap_or(Severity::Info)
}
