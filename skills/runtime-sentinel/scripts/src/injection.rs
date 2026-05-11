use crate::audit::{Finding, FindingCategory, Severity};
use crate::patterns::INJECTION_PATTERNS;
use tracing::debug;

/// Scan arbitrary text for prompt injection patterns.
/// Used both for scanning skill SKILL.md files and for scanning
/// external data (emails, web pages, etc.) before they enter the agent context.
pub fn scan_text(content: &str, source_label: &str) -> Vec<Finding> {
    let mut findings = Vec::new();

    for line in content.lines().enumerate().map(|(i, l)| (i + 1, l)) {
        let (line_num, text) = line;
        let text_lower = text.to_lowercase();

        for (pattern_name, re, severity) in INJECTION_PATTERNS.iter() {
            if re.is_match(&text_lower) {
                debug!(
                    "Injection pattern '{}' matched at line {}",
                    pattern_name, line_num
                );
                findings.push(Finding {
                    skill: source_label.to_string(),
                    severity: *severity,
                    category: FindingCategory::InjectionPattern,
                    detail: format!("Prompt injection pattern '{}' detected", pattern_name),
                    file: None,
                    line: Some(line_num),
                });
            }
        }

        // Unicode homoglyph detection — look for non-ASCII characters that
        // visually resemble ASCII instruction keywords
        if contains_homoglyphs(text) {
            findings.push(Finding {
                skill: source_label.to_string(),
                severity: Severity::High,
                category: FindingCategory::InjectionPattern,
                detail: "Unicode homoglyph substitution detected (possible evasion attempt)"
                    .to_string(),
                file: None,
                line: Some(line_num),
            });
        }

        // Base64 payload detection — look for large base64 blobs that could
        // contain encoded instructions
        if let Some(decoded) = find_and_decode_base64(text) {
            if looks_like_instructions(&decoded) {
                findings.push(Finding {
                    skill: source_label.to_string(),
                    severity: Severity::High,
                    category: FindingCategory::InjectionPattern,
                    detail: "Base64-encoded content decodes to instruction-like text".to_string(),
                    file: None,
                    line: Some(line_num),
                });
            }
        }
    }

    findings
}

/// Scan external data (email body, web page content, API response, etc.)
/// before it enters the agent's reasoning context.
/// Returns (safe_to_use, findings)
pub fn scan_external_data(data: &str, source: &str) -> (bool, Vec<Finding>) {
    let findings = scan_text(data, source);

    // Block if any HIGH or CRITICAL findings
    let should_block = findings.iter().any(|f| f.severity >= Severity::High);

    (!should_block, findings)
}

fn contains_homoglyphs(text: &str) -> bool {
    // Check for known homoglyphs of common ASCII letters used in injections
    // Focus on visually similar characters in Unicode ranges
    let suspicious_ranges = [
        '\u{0400}'..='\u{04FF}', // Cyrillic
        '\u{0370}'..='\u{03FF}', // Greek
    ];

    let ascii_lookalikes: &[char] = &[
        'а', 'е', 'о', 'р', 'с', 'х', // Cyrillic lookalikes
        'α', 'ε', 'ο', 'ρ', // Greek lookalikes
    ];

    text.chars().any(|c| ascii_lookalikes.contains(&c))
        || text
            .chars()
            .any(|c| suspicious_ranges.iter().any(|r| r.contains(&c)))
}

fn find_and_decode_base64(text: &str) -> Option<String> {
    use base64::{engine::general_purpose::STANDARD, Engine as _};

    // Look for base64-like tokens of at least 60 chars
    for token in text.split_whitespace() {
        if token.len() < 60 {
            continue;
        }
        let cleaned =
            token.trim_matches(|c: char| !c.is_alphanumeric() && c != '+' && c != '/' && c != '=');
        if cleaned.len() < 60 {
            continue;
        }
        if let Ok(decoded) = STANDARD.decode(cleaned) {
            if let Ok(s) = String::from_utf8(decoded) {
                return Some(s);
            }
        }
    }
    None
}

fn looks_like_instructions(text: &str) -> bool {
    let instruction_keywords = [
        "ignore previous",
        "forget your",
        "your new task",
        "system:",
        "assistant:",
        "human:",
        "new instruction",
        "disregard",
        "override",
        "jailbreak",
        "do not follow",
    ];
    let lower = text.to_lowercase();
    instruction_keywords.iter().any(|kw| lower.contains(kw))
}
