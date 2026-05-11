#!/usr/bin/env node
// One-command onboarding for Verdikta Bounties bots.
// Human involvement: choose network + owner/sweep addresses + fund wallet.
// Everything else (env setup, wallet creation, waiting for funding, bot registration) is automated.

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Wallet, formatEther, formatUnits, Contract } from 'ethers';

import './_env.js';
import { providerFor, loadWallet, LINK, ERC20_ABI, resolvePath, arg, hasFlag } from './_lib.js';
import { defaultSecretsDir, ensureDir } from './_paths.js';

function envNum(name, def) {
  const v = process.env[name];
  if (v == null || v === '') return def;
  const n = Number(v);
  return Number.isFinite(n) ? n : def;
}

function envStr(name, def) {
  const v = process.env[name];
  return (v == null || String(v).trim() === '') ? def : String(v);
}

function isAddress(s) {
  return /^0x[a-fA-F0-9]{40}$/.test(String(s || '').trim());
}

async function fileExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function loadOrInitEnvFile(envPath) {
  if (await fileExists(envPath)) return;
  const examplePath = path.join(path.dirname(envPath), '.env.example');
  if (await fileExists(examplePath)) {
    const ex = await fs.readFile(examplePath, 'utf8');
    await fs.writeFile(envPath, ex, { mode: 0o600 });
    return;
  }
  // Minimal fallback
  await fs.writeFile(envPath, '', { mode: 0o600 });
}

function parseEnv(text) {
  const out = {};
  for (const line of String(text).split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    const k = m[1];
    let v = m[2];
    // strip surrounding quotes
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    out[k] = v;
  }
  return out;
}

function upsertEnv(text, patch) {
  const lines = String(text).split(/\r?\n/);
  const keys = new Set(Object.keys(patch));
  const seen = new Set();

  const out = lines.map((line) => {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=/);
    if (!m) return line;
    const k = m[1];
    if (!keys.has(k)) return line;
    seen.add(k);
    const v = patch[k];
    return `${k}=${v}`;
  });

  for (const [k, v] of Object.entries(patch)) {
    if (!seen.has(k)) out.push(`${k}=${v}`);
  }

  return out.join(os.EOL).replace(/\s+$/,'') + os.EOL;
}

function isPrivateKey(s) {
  const hex = String(s || '').trim().replace(/^0x/, '');
  return /^[a-fA-F0-9]{64}$/.test(hex);
}

async function ensureWalletKeystore({ keystorePath, password, rl }) {
  const abs = resolvePath(keystorePath);
  if (await fileExists(abs)) {
    const wallet = await loadWallet();
    return { wallet, abs, created: false, imported: false };
  }

  await ensureDir(path.dirname(abs));

  // Offer to import an existing wallet instead of generating a new one
  if (rl) {
    console.log('\nWallet setup:');
    console.log('  1) Create a new wallet (default)');
    console.log('  2) Import an existing private key');
    console.log('  3) Import an existing keystore file');
    const walletChoice = (await rl.question('Choose [1]: ')).trim();

    if (walletChoice === '2') {
      const key = (await rl.question('Paste private key (hex, with or without 0x): ')).trim();
      if (!isPrivateKey(key)) throw new Error('Invalid private key format (expected 64 hex chars).');
      const wallet = new Wallet(key.startsWith('0x') ? key : `0x${key}`);
      const json = await wallet.encrypt(password);
      await fs.writeFile(abs, json, { mode: 0o600 });
      console.log('  Imported and encrypted to keystore. Raw key was NOT saved.');
      return { wallet, abs, created: true, imported: true };
    }

    if (walletChoice === '3') {
      const srcPath = (await rl.question('Path to existing keystore JSON: ')).trim();
      const srcAbs = resolvePath(srcPath);
      if (!(await fileExists(srcAbs))) throw new Error(`Keystore file not found: ${srcAbs}`);
      const srcJson = await fs.readFile(srcAbs, 'utf8');
      const srcPw = (await rl.question('Password for the existing keystore: ')).trim();
      const wallet = await Wallet.fromEncryptedJson(srcJson, srcPw);
      // Re-encrypt with the skill's password so all scripts use a consistent credential
      const reEncrypted = await wallet.encrypt(password);
      await fs.writeFile(abs, reEncrypted, { mode: 0o600 });
      console.log('  Imported and re-encrypted to skill keystore.');
      return { wallet, abs, created: true, imported: true };
    }
  }

  const wallet = Wallet.createRandom();
  const json = await wallet.encrypt(password);
  await fs.writeFile(abs, json, { mode: 0o600 });
  return { wallet, abs, created: true, imported: false };
}

async function waitForFunding({ network, address, minEth, minLink, pollSeconds }) {
  const provider = providerFor(network);
  const linkAddr = LINK[network];
  const link = new Contract(linkAddr, ERC20_ABI, provider);

  // Poll until both are satisfied.
  while (true) {
    const [ethBal, lbal, dec] = await Promise.all([
      provider.getBalance(address),
      link.balanceOf(address),
      link.decimals(),
    ]);

    const eth = Number(formatEther(ethBal));
    const linkHuman = Number(formatUnits(lbal, dec));

    const okEth = eth >= minEth;
    const okLink = linkHuman >= minLink;

    console.log(`\nFunding status (${network})`);
    console.log(`Address: ${address}`);
    console.log(`ETH:  ${eth.toFixed(6)} (need ≥ ${minEth}) ${okEth ? '✓' : '…'}`);
    console.log(`LINK: ${linkHuman.toFixed(6)} (need ≥ ${minLink}) ${okLink ? '✓' : '…'}`);

    if (okEth && okLink) return { eth, link: linkHuman };

    console.log(`\nWaiting for funding… (poll every ${pollSeconds}s, Ctrl+C to stop)`);
    await new Promise(r => setTimeout(r, pollSeconds * 1000));
  }
}

async function registerBot({ baseUrl, name, ownerAddress, description }) {
  const res = await fetch(`${baseUrl}/api/bots/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, ownerAddress, description })
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`Bot registration failed: HTTP ${res.status} - ${text}`);
  const data = JSON.parse(text);
  const apiKey = data?.apiKey || data?.api_key || data?.bot?.apiKey || data?.bot?.api_key;
  if (!apiKey) throw new Error('Bot registration response missing apiKey');
  return { data, apiKey };
}

async function main() {
  const rl = readline.createInterface({ input, output });
  try {
    const scriptsDir = path.dirname(fileURLToPath(import.meta.url));
    const envPath = path.join(scriptsDir, '.env');
    await loadOrInitEnvFile(envPath);

    const currentEnvText = await fs.readFile(envPath, 'utf8').catch(() => '');
    const current = parseEnv(currentEnvText);

    console.log('Verdikta Bounties — one-command onboarding');

    const priorNetwork = (current.VERDIKTA_NETWORK || '').toLowerCase();

    // 1) Critical decision: network
    const networks = ['base-sepolia', 'base'];
    const networkDefault = current.VERDIKTA_NETWORK || process.env.VERDIKTA_NETWORK || 'base-sepolia';
    const defaultIdx = networks.indexOf(networkDefault) >= 0 ? networks.indexOf(networkDefault) : 0;

    console.log('\nSelect network:');
    networks.forEach((n, i) => {
      const marker = i === defaultIdx ? ' (default)' : '';
      console.log(`  ${i + 1}) ${n}${marker}`);
    });

    const networkAns = (await rl.question(`Choose [${defaultIdx + 1}]: `)).trim();
    let network;
    if (!networkAns) {
      network = networks[defaultIdx];
    } else if (networkAns === '1' || networkAns === '2') {
      network = networks[parseInt(networkAns, 10) - 1];
    } else if (networks.includes(networkAns.toLowerCase())) {
      network = networkAns.toLowerCase();
    } else {
      throw new Error('Invalid network. Enter 1, 2, base-sepolia, or base.');
    }
    console.log(`→ ${network}`);

    // 2) Bounties base URL — always derive from the chosen network.
    // On a network switch the old URL would be wrong, so we re-derive.
    const derivedBaseUrl = (network === 'base-sepolia'
      ? 'https://bounties-testnet.verdikta.org'
      : 'https://bounties.verdikta.org');

    const existingBaseUrl = (current.VERDIKTA_BOUNTIES_BASE_URL || process.env.VERDIKTA_BOUNTIES_BASE_URL || '').replace(/\/+$/, '');
    const networkChanged = priorNetwork && priorNetwork !== network;
    let baseUrl = (!networkChanged && existingBaseUrl) ? existingBaseUrl : derivedBaseUrl;

    if (!networkChanged && existingBaseUrl && existingBaseUrl !== derivedBaseUrl) {
      // Existing URL doesn't match derived — ask if they want to keep it
      const baseUrlAns = (await rl.question(`Bounties base URL [${baseUrl}]: `)).trim();
      baseUrl = (baseUrlAns || baseUrl).replace(/\/+$/, '');
    } else {
      console.log(`Bounties URL: ${baseUrl}`);
    }

    // 3) Owner/sweep
    const ownerDefault = current.OFFBOT_ADDRESS && isAddress(current.OFFBOT_ADDRESS) ? current.OFFBOT_ADDRESS : '';
    let ownerAddress = (await rl.question('Owner address (human EOA) 0x…: ')).trim();
    if (!isAddress(ownerAddress)) throw new Error('Invalid owner address.');

    let sweepAddress = (await rl.question(`Sweep address 0x… [${ownerDefault || ownerAddress}]: `)).trim();
    if (!sweepAddress) sweepAddress = ownerDefault || ownerAddress;
    if (!isAddress(sweepAddress)) throw new Error('Invalid sweep address.');

    // 4) Wallet password (stored in .env for now; local file permissions 600)
    const pwDefault = current.VERDIKTA_WALLET_PASSWORD || process.env.VERDIKTA_WALLET_PASSWORD || '';
    let password = pwDefault;
    if (!password) {
      password = (await rl.question('Choose VERDIKTA_WALLET_PASSWORD (will be saved locally): ')).trim();
    }
    if (!password) throw new Error('Missing VERDIKTA_WALLET_PASSWORD');

    // 5) Keystore path default in secrets dir
    const secretsDir = defaultSecretsDir();
    const keystoreDefault = current.VERDIKTA_KEYSTORE_PATH || process.env.VERDIKTA_KEYSTORE_PATH || `${secretsDir}/verdikta-wallet.json`;

    // Apply env patch (idempotent)
    const patched = upsertEnv(currentEnvText, {
      VERDIKTA_NETWORK: network,
      VERDIKTA_BOUNTIES_BASE_URL: baseUrl,
      VERDIKTA_SECRETS_DIR: secretsDir,
      VERDIKTA_KEYSTORE_PATH: keystoreDefault,
      VERDIKTA_WALLET_PASSWORD: password,
      OFFBOT_ADDRESS: sweepAddress,
    });
    await fs.writeFile(envPath, patched, { mode: 0o600 });

    console.log(`\nSaved config: ${envPath}`);
    console.log('Secrets dir:', secretsDir);

    // Reload env into process (dotenv was loaded before; but our helper reads process.env, not file)
    process.env.VERDIKTA_NETWORK = network;
    process.env.VERDIKTA_BOUNTIES_BASE_URL = baseUrl;
    process.env.VERDIKTA_SECRETS_DIR = secretsDir;
    process.env.VERDIKTA_KEYSTORE_PATH = keystoreDefault;
    process.env.VERDIKTA_WALLET_PASSWORD = password;

    // 6) Wallet — reuse the same keystore regardless of network.
    // EVM addresses are network-agnostic; only the configuration and funding differ.
    const keystoreAbsPath = resolvePath(keystoreDefault);
    const keystoreAlreadyExists = await fileExists(keystoreAbsPath);

    if (keystoreAlreadyExists && priorNetwork && priorNetwork !== network) {
      console.log(`\nNetwork changed: ${priorNetwork} → ${network}`);
      console.log(`Reusing existing wallet at: ${keystoreAbsPath}`);
      console.log('(The same address works on any EVM network — only funding differs.)');
    }

    const { wallet, abs: keystoreAbs, created, imported } = await ensureWalletKeystore({
      keystorePath: keystoreDefault,
      password,
      rl,
    });

    const statusLabel = imported ? ' (imported)' : created ? ' (created)' : '';
    console.log(`\nBot wallet: ${wallet.address}`);
    console.log(`Keystore:  ${keystoreAbs}${statusLabel}`);

    // 7) Funding (human action)
    const minEth = envNum('MIN_ETH', network === 'base-sepolia' ? 0.01 : 0.005);
    const minLink = envNum('MIN_LINK', network === 'base-sepolia' ? 1.0 : 1.0);
    const pollSeconds = envNum('FUNDING_POLL_SECONDS', 15);

    console.log('\nHuman action required: fund the bot wallet');
    if (networkChanged) {
      console.log(`\n  NOTE: You switched from ${priorNetwork} to ${network}.`);
      console.log('  Your wallet address is the same, but funds on one network');
      console.log('  are NOT visible on the other. You need to send new funds');
      console.log(`  on the ${network} network to the address below.\n`);
    }
    console.log(`- Send ETH on ${network} to: ${wallet.address}`);
    console.log(`- Send LINK on ${network} to: ${wallet.address}`);
    console.log(`Targets: ≥ ${minEth} ETH and ≥ ${minLink} LINK`);

    if (!hasFlag('no-wait')) {
      await waitForFunding({ network, address: wallet.address, minEth, minLink, pollSeconds });
    } else {
      console.log('(Skipping funding wait due to --no-wait)');
    }

    // 8) Register bot + save API key
    const botNameDefault = arg('name', current.BOT_NAME || 'MyBot');
    const botDescDefault = arg('description', current.BOT_DESCRIPTION || 'Verdikta bounty worker');

    await ensureDir(secretsDir);
    const botOut = path.join(secretsDir, 'verdikta-bounties-bot.json');

    // Reuse existing bot api key if present (non-clean install)
    let apiKey = null;
    if (await fileExists(botOut)) {
      try {
        const existing = JSON.parse(await fs.readFile(botOut, 'utf8'));
        apiKey = existing?.apiKey || existing?.api_key || existing?.bot?.apiKey || existing?.bot?.api_key || null;
      } catch {}

      if (apiKey) {
        if (networkChanged) {
          console.log(`\nFound existing bot API key, but network changed (${priorNetwork} → ${network}).`);
          console.log('The existing key was registered on a different server and will not work.');
          const reuse = (await rl.question('Register a new bot on the new network? (Y/n) ')).trim().toLowerCase();
          apiKey = (reuse === 'n' || reuse === 'no') ? apiKey : null;
        } else {
          const reuse = (await rl.question(`\nFound existing bot API key file. Reuse it? (Y/n) `)).trim().toLowerCase();
          if (reuse === 'n' || reuse === 'no') {
            apiKey = null;
          }
        }
      }
    }

    if (!apiKey) {
      const botName = (await rl.question(`\nBot name [${botNameDefault}]: `)).trim() || botNameDefault;
      const botDescription = (await rl.question(`Bot description [${botDescDefault}]: `)).trim() || botDescDefault;

      const reg = await registerBot({ baseUrl, name: botName, ownerAddress, description: botDescription });
      apiKey = reg.apiKey;
      await fs.writeFile(botOut, JSON.stringify(reg.data, null, 2), { mode: 0o600 });

      console.log(`\n✅ Registered bot. Saved: ${botOut}`);
      console.log('API key: saved to file (not reprinted here).');
    } else {
      console.log(`\n✅ Reusing existing bot API key file: ${botOut}`);
    }

    // 9) Smoke test: list jobs
    const jobsRes = await fetch(`${baseUrl}/api/jobs?status=OPEN&minHoursLeft=0`, {
      headers: { 'X-Bot-API-Key': apiKey }
    });
    const jobsText = await jobsRes.text();
    if (!jobsRes.ok) {
      throw new Error(`Smoke test failed: /api/jobs HTTP ${jobsRes.status} - ${jobsText}`);
    }
    const jobsJson = JSON.parse(jobsText);
    const count = Array.isArray(jobsJson.jobs) ? jobsJson.jobs.length : 0;

    console.log(`\n✅ Smoke test OK: can list jobs (OPEN jobs returned: ${count})`);

    // 10) Optional: run the worker once as a final integration test (read-only: lists open jobs)
    const runWorker = (await rl.question('\nRun bounty_worker_min.js now (lists open bounties, read-only)? (Y/n) ')).trim().toLowerCase();
    if (!(runWorker === 'n' || runWorker === 'no')) {
      const { spawn } = await import('node:child_process');
      await new Promise((resolve, reject) => {
        const p = spawn(process.execPath, ['bounty_worker_min.js'], {
          stdio: 'inherit',
          env: { ...process.env, VERDIKTA_BOT_FILE: botOut }
        });
        p.on('exit', (code) => code === 0 ? resolve() : reject(new Error(`bounty_worker_min.js exited with ${code}`)));
      });
      console.log('\n✅ Worker run complete.');
    }

    console.log('\nPrivate key handling:');
    console.log(`- Keystore path: ${keystoreAbs}`);
    console.log('- To export (DANGEROUS): node export_private_key.js --i-know-what-im-doing > private_key.txt');
    console.log('  Do NOT paste private keys into chat.');

  } finally {
    rl.close();
  }
}

main().catch((e) => {
  console.error('Onboarding failed:', e?.message || e);
  process.exit(1);
});
