use alloy::hex;
use alloy::network::EthereumWallet;
use alloy::primitives::{Address, Bytes, U256};
use alloy::signers::local::{coins_bip39::English, MnemonicBuilder, PrivateKeySigner};
use alloy::signers::{Signer, SignerSync};
use alloy::sol_types::{eip712_domain, SolStruct};
use anyhow::Result;
use eth_keystore::{decrypt_key, encrypt_keystore};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::str::FromStr;
use tokio::fs;
use tracing::info;
use zeroize::Zeroize;

const SENTINEL_API: &str = "https://api.runtime-sentinel.dev/v1";
const BASE_FACILITATOR: &str = "https://x402.org/facilitator";
const DEFAULT_RPC: &str = "https://mainnet.base.org";

/// Your treasury address — all micropayments land here.
const TREASURY_ADDRESS: &str = "0x0E0EE00281A8729d4B68CDed99d430324350a305";

/// USDC contract on Base mainnet (6 decimals)
const USDC_BASE: &str = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

/// Base chain ID
const BASE_CHAIN_ID: u64 = 8453;

// ─── EIP-712 typed data for x402 USDC payment authorization ─────────────────
//
// x402 uses EIP-712 so the user's wallet signs a structured authorization
// (not a raw transaction). The facilitator at x402.org/facilitator verifies
// the signature and triggers the on-chain USDC transfer only if valid.
//
// The domain and type hash match the x402 reference implementation:
// https://github.com/coinbase/x402

alloy::sol! {
    /// EIP-712 struct for x402 USDC payment authorization
    struct PaymentAuthorization {
        address from;
        address to;
        uint256 value;
        uint256 validAfter;
        uint256 validBefore;
        bytes32 nonce;
    }
}

/// Domain separator for USDC's EIP-712 domain on Base
fn usdc_domain() -> alloy::sol_types::Eip712Domain {
    eip712_domain! {
        name: "USD Coin",
        version: "2",
        chain_id: BASE_CHAIN_ID,
        verifying_contract: Address::from_str(USDC_BASE).unwrap(),
    }
}

/// Wallet configuration stored at ~/.sentinel/wallet/config.json
#[derive(Debug, Serialize, Deserialize)]
pub struct WalletConfig {
    pub address: String,
    pub chain: String, // "base"
    pub daily_limit_usd: f64,
    pub keystore_path: String,
}

/// x402 payment request as returned in a 402 response header
#[derive(Debug, Deserialize)]
pub struct PaymentRequest {
    pub price: String,     // e.g. "$0.01"
    pub network: String,   // "base"
    pub token: String,     // "USDC"
    pub recipient: String, // treasury address
    pub duration_secs: u64,
}

pub async fn setup_wallet() -> Result<()> {
    let wallet_dir = sentinel_dir().join("wallet");
    fs::create_dir_all(&wallet_dir).await?;

    let config_path = wallet_dir.join("config.json");
    if config_path.exists() {
        info!("Wallet already configured. Run `sentinel wallet show` to view.");
        return Ok(());
    }

    println!("🔐 Setting up runtime-sentinel wallet...");
    println!();

    let address = generate_wallet(&wallet_dir).await?;

    let config = WalletConfig {
        address: address.clone(),
        chain: "base".to_string(),
        daily_limit_usd: 0.05, // default: auto-approve up to $0.05/day
        keystore_path: wallet_dir
            .join("keystore.json")
            .to_string_lossy()
            .to_string(),
    };
    fs::write(&config_path, serde_json::to_string_pretty(&config)?).await?;

    println!("✅ Wallet created: {}", address);
    println!();
    println!("Free tier features are ready. For premium features, fund your wallet:");
    println!("  Run: sentinel wallet fund");
    println!();
    println!("Recommended starting balance: $1 USDC on Base (~66 days of full coverage)");

    Ok(())
}

pub async fn show_wallet() -> Result<()> {
    let config = load_config().await?;
    let balance = fetch_usdc_balance(&config.address).await.unwrap_or(0.0);

    println!("Address: {}", config.address);
    println!("Network: {}", config.chain);
    println!("USDC balance: ${:.4}", balance);
    println!("Daily auto-approve limit: ${:.4}", config.daily_limit_usd);

    Ok(())
}

pub async fn show_fund_qr() -> Result<()> {
    let config = load_config().await?;
    println!("Send USDC on Base to:");
    println!();
    println!("  {}", config.address);
    println!();
    println!("Network: Base (not Ethereum mainnet)");
    println!("Token: USDC");
    println!();
    println!("Minimum recommended: $1.00 USDC");
    // In production, render a QR code via the `qrcode` crate
    Ok(())
}

pub async fn set_limit(amount: f64) -> Result<()> {
    let mut config = load_config().await?;
    config.daily_limit_usd = amount;
    save_config(&config).await?;
    if amount == 0.0 {
        println!("Auto-approval disabled. Every x402 payment will prompt for confirmation.");
    } else {
        println!("Daily auto-approval limit set to ${:.4}", amount);
    }
    Ok(())
}

pub async fn export_mnemonic() -> Result<()> {
    println!("⚠️  This will display your 12-word recovery phrase.");
    println!("Write it down on paper and store it somewhere safe and offline.");
    println!("Anyone with these words can access your funds. Proceed? [y/N]");
    let mut input = String::new();
    std::io::stdin().read_line(&mut input)?;
    if input.trim().to_lowercase() != "y" {
        println!("Cancelled.");
        return Ok(());
    }

    let wallet_dir = sentinel_dir().join("wallet");
    let mnemonic_path = wallet_dir.join("mnemonic.enc");
    if !mnemonic_path.exists() {
        anyhow::bail!(
            "No mnemonic file found at {}.\n\
             If you set up your wallet with an older version of sentinel, \
             use `sentinel wallet export-key` for the raw private key instead.",
            mnemonic_path.display()
        );
    }

    // Load machine secret and decrypt the mnemonic
    let machine_secret = load_or_create_machine_secret(&wallet_dir).await?;
    let mnemonic_key = derive_passphrase(&machine_secret, b"sentinel-mnemonic")?;
    let encrypted = fs::read(&mnemonic_path).await?;
    let mut phrase_bytes = aes_gcm_decrypt(&mnemonic_key, &encrypted)?;

    let phrase = std::str::from_utf8(&phrase_bytes)
        .map_err(|_| anyhow::anyhow!("Mnemonic file is corrupted"))?
        .to_string();

    let config = load_config().await?;
    println!();
    println!("Recovery phrase (12 words — write these down, in order):");
    println!();
    // Print each word numbered for easier transcription
    for (i, word) in phrase.split_whitespace().enumerate() {
        println!("  {:2}. {}", i + 1, word);
    }
    println!();
    println!("Address: {}", config.address);
    println!();
    println!("To restore on a new machine: sentinel wallet recover");

    phrase_bytes.zeroize();
    Ok(())
}

pub async fn recover_wallet() -> Result<()> {
    println!("Enter your 12-word recovery phrase (words separated by spaces):");
    let mut raw = String::new();
    std::io::stdin().read_line(&mut raw)?;
    let phrase = raw.trim().to_string();

    // Validate the mnemonic before writing anything
    use bip39::{Language, Mnemonic};
    let mnemonic = Mnemonic::parse_in(Language::English, &phrase)
        .map_err(|e| anyhow::anyhow!("Invalid recovery phrase: {}", e))?;

    // Derive private key from the validated mnemonic
    let signer = MnemonicBuilder::<English>::default()
        .phrase(phrase.as_str())
        .build()
        .map_err(|e| anyhow::anyhow!("Failed to derive key: {}", e))?;
    let address = format!("{:#x}", signer.address());
    let private_key_bytes = signer.credential().to_bytes();

    let wallet_dir = sentinel_dir().join("wallet");
    fs::create_dir_all(&wallet_dir).await?;

    // Create or load machine secret for this machine
    let machine_secret = load_or_create_machine_secret(&wallet_dir).await?;

    // Re-encrypt keystore with this machine's secret
    let passphrase = derive_passphrase(&machine_secret, b"sentinel-keystore")?;
    let passphrase_hex = hex::encode(&passphrase);
    let keystore_path = wallet_dir.join("keystore.json");
    let mut rng = rand::thread_rng();
    encrypt_keystore(
        &keystore_path,
        &mut rng,
        private_key_bytes,
        &passphrase_hex,
        None,
    )
    .map_err(|e| anyhow::anyhow!("Failed to encrypt keystore: {}", e))?;

    // Re-encrypt the mnemonic phrase for this machine
    let mnemonic_key = derive_passphrase(&machine_secret, b"sentinel-mnemonic")?;
    let mnemonic_enc = aes_gcm_encrypt(&mnemonic_key, phrase.as_bytes())?;
    fs::write(wallet_dir.join("mnemonic.enc"), &mnemonic_enc).await?;

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let perms = std::fs::Permissions::from_mode(0o600);
        std::fs::set_permissions(&keystore_path, perms.clone())?;
        std::fs::set_permissions(wallet_dir.join("mnemonic.enc"), perms)?;
    }

    let config = WalletConfig {
        address: address.clone(),
        chain: "base".to_string(),
        daily_limit_usd: 0.05,
        keystore_path: keystore_path.to_string_lossy().to_string(),
    };
    save_config(&config).await?;

    drop(mnemonic);
    let mut phrase_bytes = phrase.into_bytes();
    phrase_bytes.zeroize();

    println!("✅ Wallet recovered: {}", address);
    println!("Run `sentinel wallet show` to verify your USDC balance.");
    Ok(())
}

pub async fn diagnose() -> Result<()> {
    println!("🩺 runtime-sentinel wallet diagnostics");
    println!();

    let config = load_config().await?;
    println!("  Address: {}", config.address);

    let balance = fetch_usdc_balance(&config.address).await;
    match balance {
        Ok(b) => println!("  USDC balance: ${:.4} ✓", b),
        Err(e) => println!("  USDC balance: ERROR — {}", e),
    }

    let rpc = std::env::var("SENTINEL_RPC").unwrap_or(DEFAULT_RPC.to_string());
    let rpc_ok = reqwest::Client::new()
        .post(&rpc)
        .json(&serde_json::json!({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}))
        .send()
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false);
    println!(
        "  Base RPC ({}): {}",
        rpc,
        if rpc_ok { "✓" } else { "UNREACHABLE" }
    );

    let facilitator_ok = reqwest::Client::new()
        .get(BASE_FACILITATOR)
        .send()
        .await
        .map(|r| r.status().is_success())
        .unwrap_or(false);
    println!(
        "  x402 Facilitator: {}",
        if facilitator_ok { "✓" } else { "UNREACHABLE" }
    );

    Ok(())
}

/// Execute an x402 payment flow for a premium endpoint.
/// Returns the session token granted after successful payment.
pub async fn execute_x402_payment(
    endpoint: &str,
    body: &serde_json::Value,
) -> Result<serde_json::Value> {
    let config = load_config().await?;
    let client = reqwest::Client::new();

    // Step 1: initial request — expect 402
    let resp = client.post(endpoint).json(body).send().await?;

    if resp.status() == reqwest::StatusCode::PAYMENT_REQUIRED {
        let payment_header = resp
            .headers()
            .get("X-Payment-Request")
            .and_then(|v| v.to_str().ok())
            .ok_or_else(|| anyhow::anyhow!("402 response missing X-Payment-Request header"))?;

        let pr: PaymentRequest = serde_json::from_str(payment_header)?;

        // Show price to user
        let price_usd: f64 = pr.price.trim_start_matches('$').parse()?;
        println!("Payment required: {} USDC on Base", pr.price);

        let auto_approve = price_usd <= config.daily_limit_usd;
        if !auto_approve {
            println!(
                "This exceeds your auto-approve limit (${:.4}). Proceed? [y/N]",
                config.daily_limit_usd
            );
            let mut input = String::new();
            std::io::stdin().read_line(&mut input)?;
            if input.trim().to_lowercase() != "y" {
                anyhow::bail!("Payment declined by user");
            }
        }

        // Step 2: sign USDC transfer and retry
        let signed_payment = sign_usdc_transfer(&config, &pr).await?;

        let final_resp = client
            .post(endpoint)
            .json(body)
            .header("X-Payment", serde_json::to_string(&signed_payment)?)
            .send()
            .await?;

        if final_resp.status().is_success() {
            return Ok(final_resp.json().await?);
        } else {
            anyhow::bail!("Payment failed: {}", final_resp.status());
        }
    } else if resp.status().is_success() {
        return Ok(resp.json().await?);
    }

    anyhow::bail!("Unexpected response: {}", resp.status())
}

// ─── Internal helpers ────────────────────────────────────────────────────────

/// Generate a fresh BIP-39 wallet and persist two encrypted files:
///
///   keystore.json   — eth-keystore v3 (AES-128-CTR + scrypt) containing the
///                     raw private key. Used for every signing operation.
///
///   mnemonic.enc    — AES-256-GCM ciphertext of the 12-word mnemonic phrase,
///                     keyed by the machine secret. The user can display this
///                     with `sentinel wallet export` to back up to paper.
///
/// Both files are keyed by a machine-unique 32-byte secret stored at
/// ~/.sentinel/machine.key (itself created with CSPRNG on first run).
/// This means the encrypted files are worthless if copied to another machine,
/// and the user is never required to remember a passphrase for day-to-day use.
async fn generate_wallet(wallet_dir: &std::path::Path) -> Result<String> {
    let mut rng = rand::thread_rng();

    // ── 1. Generate BIP-39 mnemonic using the bip39 crate directly ────────────
    //    We need access to the phrase string, which MnemonicBuilder doesn't
    //    expose after construction, so we generate the mnemonic first and then
    //    feed it into MnemonicBuilder for key derivation.
    use bip39::{Language, Mnemonic};
    let mnemonic = Mnemonic::generate_in_with(&mut rng, Language::English, 12)
        .map_err(|e| anyhow::anyhow!("Failed to generate mnemonic: {}", e))?;
    let phrase = mnemonic.to_string();

    // ── 2. Derive the private key from the mnemonic (m/44'/60'/0'/0/0) ────────
    let signer = MnemonicBuilder::<English>::default()
        .phrase(phrase.as_str())
        .build()
        .map_err(|e| anyhow::anyhow!("Failed to derive key from mnemonic: {}", e))?;
    let address = format!("{:#x}", signer.address());
    let private_key_bytes = signer.credential().to_bytes();

    // ── 3. Load (or create) the machine secret ─────────────────────────────────
    let machine_secret = load_or_create_machine_secret(wallet_dir).await?;

    // ── 4. Derive keystore passphrase from machine secret via Argon2id ─────────
    //    Using Argon2id instead of a hostname means:
    //    - The passphrase is cryptographically strong (not guessable)
    //    - The encrypted files are useless if exfiltrated to another machine
    //    - No user interaction required for day-to-day signing
    let passphrase = derive_passphrase(&machine_secret, b"sentinel-keystore")?;
    let passphrase_hex = hex::encode(&passphrase);

    // ── 5. Encrypt private key → eth-keystore v3 JSON ─────────────────────────
    let keystore_path = wallet_dir.join("keystore.json");
    encrypt_keystore(
        &keystore_path,
        &mut rng,
        private_key_bytes,
        &passphrase_hex,
        None,
    )
    .map_err(|e| anyhow::anyhow!("Failed to encrypt keystore: {}", e))?;

    // ── 6. Encrypt mnemonic phrase → AES-256-GCM ciphertext ───────────────────
    //    Separate key derivation context so keystore and mnemonic files can't
    //    be cross-decrypted even if one passphrase leaks.
    let mnemonic_key = derive_passphrase(&machine_secret, b"sentinel-mnemonic")?;
    let mnemonic_enc = aes_gcm_encrypt(&mnemonic_key, phrase.as_bytes())?;
    let mnemonic_path = wallet_dir.join("mnemonic.enc");
    fs::write(&mnemonic_path, &mnemonic_enc).await?;

    // ── 7. Set restrictive file permissions (owner read-only) ─────────────────
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let perms = std::fs::Permissions::from_mode(0o600);
        std::fs::set_permissions(&keystore_path, perms.clone())?;
        std::fs::set_permissions(&mnemonic_path, perms)?;
    }

    info!("Wallet generated and encrypted at {}", wallet_dir.display());

    // Zeroize sensitive material before dropping
    drop(mnemonic);
    let mut phrase_bytes = phrase.into_bytes();
    phrase_bytes.zeroize();

    Ok(address)
}

/// Load the machine-unique 32-byte secret, generating it if it doesn't exist.
/// Stored at ~/.sentinel/machine.key with 0600 permissions.
async fn load_or_create_machine_secret(wallet_dir: &std::path::Path) -> Result<[u8; 32]> {
    let key_path = wallet_dir
        .parent()
        .unwrap_or(wallet_dir)
        .join("machine.key");

    if key_path.exists() {
        let bytes = fs::read(&key_path).await?;
        if bytes.len() != 32 {
            anyhow::bail!("Corrupted machine.key (expected 32 bytes)");
        }
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&bytes);
        return Ok(arr);
    }

    // Generate fresh 32-byte CSPRNG secret
    let mut secret = [0u8; 32];
    rand::RngCore::fill_bytes(&mut rand::thread_rng(), &mut secret);
    fs::write(&key_path, &secret).await?;

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&key_path, std::fs::Permissions::from_mode(0o600))?;
    }

    info!("Machine secret created at {}", key_path.display());
    Ok(secret)
}

/// Derive a 32-byte passphrase from the machine secret using Argon2id.
/// The `context` parameter domain-separates keystore vs mnemonic derivations.
fn derive_passphrase(machine_secret: &[u8; 32], context: &[u8]) -> Result<[u8; 32]> {
    use argon2::{Algorithm, Argon2, Params, Version};

    // Use the context as a fixed salt (domain separation, not secret)
    let mut salt = [0u8; 32];
    let len = context.len().min(32);
    salt[..len].copy_from_slice(&context[..len]);

    let params = Params::new(
        64 * 1024, // 64 MiB memory
        3,         // 3 iterations
        1,         // 1 thread (deterministic, no parallelism)
        Some(32),  // 32-byte output
    )?;

    let argon2 = Argon2::new(Algorithm::Argon2id, Version::V0x13, params);
    let mut output = [0u8; 32];
    argon2
        .hash_password_into(machine_secret, &salt, &mut output)
        .map_err(|e| anyhow::anyhow!("Argon2 derivation failed: {}", e))?;

    Ok(output)
}

/// Encrypt plaintext using AES-256-GCM with a random 96-bit nonce.
/// Output format: [nonce (12 bytes)] || [ciphertext + tag]
fn aes_gcm_encrypt(key: &[u8; 32], plaintext: &[u8]) -> Result<Vec<u8>> {
    use aes_gcm::{
        aead::{Aead, KeyInit, OsRng},
        Aes256Gcm, Nonce,
    };

    let cipher = Aes256Gcm::new(key.into());
    let mut nonce_bytes = [0u8; 12];
    rand::RngCore::fill_bytes(&mut rand::thread_rng(), &mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, plaintext)
        .map_err(|e| anyhow::anyhow!("AES-GCM encryption failed: {}", e))?;

    let mut out = Vec::with_capacity(12 + ciphertext.len());
    out.extend_from_slice(&nonce_bytes);
    out.extend_from_slice(&ciphertext);
    Ok(out)
}

/// Decrypt AES-256-GCM ciphertext produced by `aes_gcm_encrypt`.
fn aes_gcm_decrypt(key: &[u8; 32], data: &[u8]) -> Result<Vec<u8>> {
    use aes_gcm::{
        aead::{Aead, KeyInit},
        Aes256Gcm, Nonce,
    };

    if data.len() < 12 {
        anyhow::bail!("Ciphertext too short");
    }
    let (nonce_bytes, ciphertext) = data.split_at(12);
    let cipher = Aes256Gcm::new(key.into());
    let nonce = Nonce::from_slice(nonce_bytes);

    cipher
        .decrypt(nonce, ciphertext)
        .map_err(|_| anyhow::anyhow!("AES-GCM decryption failed — wrong key or corrupted data"))
}

/// Load the signer from the encrypted keystore on disk.
fn load_signer(keystore_path: &std::path::Path) -> Result<PrivateKeySigner> {
    // Derive the passphrase from the machine secret (same path as generation)
    let wallet_dir = keystore_path
        .parent()
        .ok_or_else(|| anyhow::anyhow!("Invalid keystore path"))?;
    let sentinel_dir = wallet_dir
        .parent()
        .ok_or_else(|| anyhow::anyhow!("Invalid wallet dir path"))?;
    let key_path = sentinel_dir.join("machine.key");

    let key_bytes = std::fs::read(&key_path)
        .map_err(|_| anyhow::anyhow!("Machine secret not found. Was this wallet created on a different machine? Use `sentinel wallet recover` to restore from your mnemonic."))?;
    let mut machine_secret = [0u8; 32];
    machine_secret.copy_from_slice(&key_bytes[..32]);

    let passphrase = derive_passphrase(&machine_secret, b"sentinel-keystore")?;
    let passphrase_hex = hex::encode(&passphrase);

    let key_bytes = decrypt_key(keystore_path, &passphrase_hex)
        .map_err(|e| anyhow::anyhow!("Failed to decrypt keystore: {}", e))?;
    let signer = PrivateKeySigner::from_bytes(&key_bytes.into())
        .map_err(|e| anyhow::anyhow!("Invalid private key in keystore: {}", e))?;
    Ok(signer)
}

/// Sign a USDC transfer authorization using EIP-712 typed data.
///
/// x402 uses USDC's native `transferWithAuthorization` EIP-3009 pattern,
/// which means we sign a `PaymentAuthorization` struct rather than a raw
/// transaction. The facilitator at x402.org/facilitator verifies this
/// signature and submits the on-chain transferWithAuthorization call itself,
/// so the user never pays gas directly.
///
/// Reference: https://github.com/coinbase/x402/blob/main/SPEC.md
async fn sign_usdc_transfer(
    config: &WalletConfig,
    pr: &PaymentRequest,
) -> Result<serde_json::Value> {
    let keystore_path = std::path::Path::new(&config.keystore_path);
    let signer = load_signer(keystore_path)?;

    // Parse the price string ("$0.01") → USDC atomic units (6 decimals)
    let price_str = pr.price.trim_start_matches('$');
    let price_usd: f64 = price_str.parse()?;
    let usdc_amount = (price_usd * 1_000_000.0) as u128;

    // Authorization window: valid for 5 minutes from now
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)?
        .as_secs();
    let valid_after = U256::from(now.saturating_sub(30)); // 30s grace for clock skew
    let valid_before = U256::from(now + 300); // 5 minute window

    // Random nonce — prevents replay attacks
    let mut nonce_bytes = [0u8; 32];
    rand::RngCore::fill_bytes(&mut rand::thread_rng(), &mut nonce_bytes);
    let nonce: alloy::primitives::FixedBytes<32> = nonce_bytes.into();

    let auth = PaymentAuthorization {
        from: Address::from_str(&config.address)
            .map_err(|e| anyhow::anyhow!("Invalid from address: {}", e))?,
        to: Address::from_str(&pr.recipient)
            .map_err(|e| anyhow::anyhow!("Invalid recipient address: {}", e))?,
        value: U256::from(usdc_amount),
        validAfter: valid_after,
        validBefore: valid_before,
        nonce,
    };

    // Produce the EIP-712 signing hash and sign it
    let domain = usdc_domain();
    let signing_hash = auth.eip712_signing_hash(&domain);
    let signature = signer.sign_hash_sync(&signing_hash)?;

    Ok(serde_json::json!({
        "from":        config.address,
        "to":          pr.recipient,
        "value":       usdc_amount.to_string(),
        "validAfter":  valid_after.to_string(),
        "validBefore": valid_before.to_string(),
        "nonce":       hex::encode(nonce_bytes),
        "v":           signature.v().y_parity_byte() + 27,
        "r":           hex::encode(signature.r().to_be_bytes::<32>()),
        "s":           hex::encode(signature.s().to_be_bytes::<32>()),
        "token":       pr.token,
        "network":     pr.network,
        "treasury":    TREASURY_ADDRESS,
    }))
}

async fn fetch_usdc_balance(address: &str) -> Result<f64> {
    let rpc = std::env::var("SENTINEL_RPC").unwrap_or(DEFAULT_RPC.to_string());
    // ERC-20 balanceOf call for USDC on Base
    // USDC contract on Base: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
    let payload = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "data": format!("0x70a08231000000000000000000000000{}", &address[2..])
        }, "latest"],
        "id": 1
    });

    let resp = reqwest::Client::new()
        .post(&rpc)
        .json(&payload)
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;

    let hex_balance = resp["result"]
        .as_str()
        .unwrap_or("0x0")
        .trim_start_matches("0x");

    let raw = u128::from_str_radix(hex_balance, 16).unwrap_or(0);
    // USDC has 6 decimals on Base
    Ok(raw as f64 / 1_000_000.0)
}

async fn load_config() -> Result<WalletConfig> {
    let config_path = sentinel_dir().join("wallet").join("config.json");
    if !config_path.exists() {
        anyhow::bail!("Wallet not configured. Run `sentinel setup` first.");
    }
    let content = fs::read_to_string(&config_path).await?;
    Ok(serde_json::from_str(&content)?)
}

async fn save_config(config: &WalletConfig) -> Result<()> {
    let config_path = sentinel_dir().join("wallet").join("config.json");
    fs::write(&config_path, serde_json::to_string_pretty(config)?).await?;
    Ok(())
}

fn sentinel_dir() -> PathBuf {
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("/tmp"))
        .join(".sentinel")
}
