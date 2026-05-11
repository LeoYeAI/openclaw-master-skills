use crate::audit::Severity;
use once_cell::sync::Lazy;
use regex::Regex;

/// Credential detection patterns: (name, regex)
pub static CREDENTIAL_PATTERNS: Lazy<Vec<(&'static str, Regex)>> = Lazy::new(|| {
    vec![
        (
            "AWS Access Key",
            Regex::new(r"AKIA[0-9A-Z]{16}").unwrap(),
        ),
        (
            "AWS Secret Key",
            Regex::new(r#"(?i)aws.{0,20}secret.{0,20}['"][0-9a-zA-Z/+]{40}['"]"#).unwrap(),
        ),
        (
            "GitHub Personal Access Token",
            Regex::new(r"ghp_[0-9a-zA-Z]{36}").unwrap(),
        ),
        (
            "GitHub OAuth Token",
            Regex::new(r"gho_[0-9a-zA-Z]{36}").unwrap(),
        ),
        (
            "Anthropic API Key",
            Regex::new(r"sk-ant-[0-9a-zA-Z\-]{40,}").unwrap(),
        ),
        (
            "OpenAI API Key",
            Regex::new(r"sk-[0-9a-zA-Z]{48}").unwrap(),
        ),
        (
            "Ethereum Private Key",
            Regex::new(r"(?i)(private.?key|eth.?key).{0,20}0x[0-9a-fA-F]{64}").unwrap(),
        ),
        (
            "BIP-39 Mnemonic (partial)",
            Regex::new(
                r"\b(abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse)\b.{0,200}\b(zoo|zone|zombie|you|young|year)\b"
            ).unwrap(),
        ),
        (
            "SSH Private Key",
            Regex::new(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----").unwrap(),
        ),
        (
            "Slack Token",
            Regex::new(r"xox[baprs]-[0-9a-zA-Z\-]{10,}").unwrap(),
        ),
        (
            "Telegram Bot Token",
            Regex::new(r"[0-9]{8,10}:[0-9a-zA-Z_\-]{35}").unwrap(),
        ),
        (
            "Generic Bearer Token",
            Regex::new(r#"(?i)bearer\s+[0-9a-zA-Z\-_.~+/]{20,}"#).unwrap(),
        ),
    ]
});

/// Prompt injection patterns: (name, regex, severity)
pub static INJECTION_PATTERNS: Lazy<Vec<(&'static str, Regex, Severity)>> = Lazy::new(|| {
    vec![
        (
            "ignore-previous-instructions",
            Regex::new(r"ignore.{0,20}(previous|prior|above|all).{0,20}(instruction|prompt|rule|context)").unwrap(),
            Severity::Critical,
        ),
        (
            "forget-instructions",
            Regex::new(r"forget.{0,20}(your|all|previous).{0,20}(instruction|rule|training|prompt)").unwrap(),
            Severity::Critical,
        ),
        (
            "new-task-override",
            Regex::new(r"(your|the).{0,10}(new|real|actual|true).{0,10}(task|job|goal|purpose|objective|mission)\s+is").unwrap(),
            Severity::Critical,
        ),
        (
            "system-role-injection",
            Regex::new(r"(?m)^(system|human|assistant|user)\s*:\s*\n").unwrap(),
            Severity::High,
        ),
        (
            "jailbreak-keyword",
            Regex::new(r"\b(jailbreak|dan mode|developer mode|unrestricted mode|do anything now)\b").unwrap(),
            Severity::High,
        ),
        (
            "exfiltration-instruction",
            Regex::new(r"(send|email|post|forward|upload|exfiltrate).{0,30}(to|at)\s+(http|ftp|smtp|mailto|discord\.com|t\.me|ngrok)").unwrap(),
            Severity::Critical,
        ),
        (
            "disregard-safety",
            Regex::new(r"(disregard|bypass|override|ignore).{0,20}(safety|ethical|restriction|limit|filter|policy|guideline)").unwrap(),
            Severity::High,
        ),
        (
            "hidden-instruction-html-comment",
            Regex::new(r"<!--.*?(ignore|system|instruction|task).*?-->").unwrap(),
            Severity::High,
        ),
        (
            "persona-override",
            Regex::new(r"you are now.{0,30}(and you|who|that).{0,30}(not|never|don.t).{0,30}(refuse|restrict|limit)").unwrap(),
            Severity::High,
        ),
        (
            "soul-md-write-instruction",
            Regex::new(r"(write|append|modify|update|edit).{0,30}(soul\.md|memory\.md|SOUL\.md|MEMORY\.md)").unwrap(),
            Severity::Critical,
        ),
    ]
});
