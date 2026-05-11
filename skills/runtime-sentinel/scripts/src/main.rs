use anyhow::Result;
use clap::{Parser, Subcommand};
use tracing_subscriber::{fmt, EnvFilter};

mod audit;
mod daemon;
mod egress;
mod injection;
mod patterns;
mod payment;
mod process;
mod report;

#[derive(Parser)]
#[command(
    name = "sentinel",
    about = "runtime-sentinel: OpenClaw runtime security guardian",
    version
)]
struct Cli {
    /// Output JSON instead of human-readable text
    #[arg(long, global = true)]
    json: bool,

    /// Run without any network calls (free tier only)
    #[arg(long, global = true)]
    offline: bool,

    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// First-time setup: generate wallet, run baseline audit
    Setup,

    /// Audit all installed OpenClaw skills (free)
    Audit {
        /// Path to skills directory
        #[arg(long, default_value = "~/.openclaw/skills")]
        path: String,
    },

    /// Check a single skill before installing (free)
    Check {
        /// Path to skill directory or ClawHub skill ID (e.g. author/skill-name)
        skill: String,
    },

    /// Isolate a suspicious skill (move out of active directory)
    Isolate {
        /// Skill name to isolate
        skill: String,
    },

    /// Report a malicious skill to ClawHub
    Report {
        /// Skill name to report
        skill: String,
    },

    /// Daemon management (premium)
    Daemon {
        #[command(subcommand)]
        action: DaemonAction,
    },

    /// Wallet management
    Wallet {
        #[command(subcommand)]
        action: WalletAction,
    },
}

#[derive(Subcommand)]
enum DaemonAction {
    /// Start the guardian in the foreground (use shell backgrounding if desired)
    Start,
    /// Stop the daemon
    Stop,
    /// Show daemon status
    Status,
    /// Tail the audit log
    Logs {
        /// Number of lines to show
        #[arg(short = 'n', default_value = "50")]
        lines: usize,
    },
}

#[derive(Subcommand)]
enum WalletAction {
    /// Show wallet address and USDC balance
    Show,
    /// Print QR code and address to fund wallet with USDC on Base
    Fund,
    /// Set per-day auto-approval spending limit
    SetLimit {
        /// Max USDC per day to auto-approve (0 = always prompt)
        amount: f64,
    },
    /// Export BIP-39 mnemonic for backup (handle with care)
    Export,
    /// Restore wallet from BIP-39 mnemonic
    Recover,
    /// Diagnose wallet and payment issues
    Diagnose,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialise tracing
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    if cli.json {
        fmt().json().with_env_filter(filter).init();
    } else {
        fmt().with_env_filter(filter).init();
    }

    match cli.command {
        Command::Setup => {
            payment::setup_wallet().await?;
            let results = audit::run_audit("~/.openclaw/skills", cli.offline).await?;
            report::print_audit(&results, cli.json);
        }

        Command::Audit { path } => {
            let results = audit::run_audit(&path, cli.offline).await?;
            report::print_audit(&results, cli.json);
        }

        Command::Check { skill } => {
            let result = audit::check_skill(&skill, cli.offline).await?;
            report::print_check(&result, cli.json);
        }

        Command::Isolate { skill } => {
            audit::isolate_skill(&skill).await?;
            println!(
                "Skill '{}' quarantined. Review ~/.sentinel/quarantine/",
                skill
            );
        }

        Command::Report { skill } => {
            if cli.offline {
                anyhow::bail!("--offline mode: cannot report skills without network access");
            }
            audit::report_skill(&skill).await?;
            println!("Report submitted to ClawHub for '{}'", skill);
        }

        Command::Daemon { action } => match action {
            DaemonAction::Start => daemon::start(cli.offline).await?,
            DaemonAction::Stop => daemon::stop().await?,
            DaemonAction::Status => daemon::status().await?,
            DaemonAction::Logs { lines } => daemon::logs(lines).await?,
        },

        Command::Wallet { action } => match action {
            WalletAction::Show => payment::show_wallet().await?,
            WalletAction::Fund => payment::show_fund_qr().await?,
            WalletAction::SetLimit { amount } => payment::set_limit(amount).await?,
            WalletAction::Export => payment::export_mnemonic().await?,
            WalletAction::Recover => payment::recover_wallet().await?,
            WalletAction::Diagnose => payment::diagnose().await?,
        },
    }

    Ok(())
}
