// ============================================================
// Afterself — Encrypted Vault (CLI)
// Stores action plans locally with AES-256-GCM encryption.
// Called by the OpenClaw agent via CLI commands.
// ============================================================
import { randomBytes, createCipheriv, createDecipheriv, scryptSync, randomUUID, } from "crypto";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { loadConfig, appendAudit } from "./state.js";
// -----------------------------------------------------------
// Encryption Primitives
// -----------------------------------------------------------
const ALGORITHM = "aes-256-gcm";
const KEY_LENGTH = 32;
const IV_LENGTH = 16;
const SALT_LENGTH = 32;
const TAG_LENGTH = 16;
/** Derive an encryption key from a password using scrypt */
function deriveKey(password, salt) {
    return scryptSync(password, salt, KEY_LENGTH);
}
/** Encrypt plaintext with AES-256-GCM */
function encrypt(plaintext, password) {
    const salt = randomBytes(SALT_LENGTH);
    const iv = randomBytes(IV_LENGTH);
    const key = deriveKey(password, salt);
    const cipher = createCipheriv(ALGORITHM, key, iv);
    const encrypted = Buffer.concat([
        cipher.update(plaintext, "utf8"),
        cipher.final(),
    ]);
    const tag = cipher.getAuthTag();
    // Format: salt(32) + iv(16) + tag(16) + ciphertext
    return Buffer.concat([salt, iv, tag, encrypted]);
}
/** Decrypt ciphertext with AES-256-GCM */
function decrypt(data, password) {
    const salt = data.subarray(0, SALT_LENGTH);
    const iv = data.subarray(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
    const tag = data.subarray(SALT_LENGTH + IV_LENGTH, SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    const encrypted = data.subarray(SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    const key = deriveKey(password, salt);
    const decipher = createDecipheriv(ALGORITHM, key, iv);
    decipher.setAuthTag(tag);
    const decrypted = Buffer.concat([
        decipher.update(encrypted),
        decipher.final(),
    ]);
    return decrypted.toString("utf8");
}
// -----------------------------------------------------------
// Vault Class
// -----------------------------------------------------------
class Vault {
    dbPath;
    masterPassword;
    plans = [];
    loaded = false;
    constructor(masterPassword) {
        const config = loadConfig();
        this.dbPath = config.vault.dbPath;
        this.masterPassword = masterPassword;
    }
    /** Load and decrypt the vault from disk */
    load() {
        if (!existsSync(this.dbPath)) {
            this.plans = [];
            this.loaded = true;
            return;
        }
        try {
            const raw = readFileSync(this.dbPath);
            const json = decrypt(raw, this.masterPassword);
            this.plans = JSON.parse(json);
            this.loaded = true;
        }
        catch (err) {
            throw new Error(`Failed to decrypt vault. Wrong password or corrupted file. Error: ${err}`);
        }
    }
    /** Encrypt and save the vault to disk */
    save() {
        const json = JSON.stringify(this.plans, null, 2);
        const encrypted = encrypt(json, this.masterPassword);
        writeFileSync(this.dbPath, encrypted, { mode: 0o600 });
    }
    /** Ensure vault is loaded */
    ensureLoaded() {
        if (!this.loaded)
            this.load();
    }
    // ---------------------------------------------------------
    // CRUD Operations
    // ---------------------------------------------------------
    /** List all action plans (metadata only) */
    listPlans() {
        this.ensureLoaded();
        return this.plans.map((p) => ({
            id: p.id,
            name: p.name,
            actionCount: p.actions.length,
            updatedAt: p.updatedAt,
        }));
    }
    /** Get a full action plan by ID */
    getPlan(id) {
        this.ensureLoaded();
        return this.plans.find((p) => p.id === id);
    }
    /** Get all plans */
    getAllPlans() {
        this.ensureLoaded();
        return [...this.plans];
    }
    /** Create a new action plan */
    createPlan(name, actions) {
        this.ensureLoaded();
        const plan = {
            id: randomUUID(),
            name,
            actions,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
        };
        this.plans.push(plan);
        this.save();
        appendAudit("config", "plan_created", { planId: plan.id, name, actionCount: actions.length });
        return plan;
    }
    /** Update an existing action plan */
    updatePlan(id, updates) {
        this.ensureLoaded();
        const index = this.plans.findIndex((p) => p.id === id);
        if (index === -1)
            throw new Error(`Plan not found: ${id}`);
        const plan = this.plans[index];
        if (updates.name)
            plan.name = updates.name;
        if (updates.actions)
            plan.actions = updates.actions;
        plan.updatedAt = new Date().toISOString();
        this.plans[index] = plan;
        this.save();
        appendAudit("config", "plan_updated", { planId: id });
        return plan;
    }
    /** Delete an action plan */
    deletePlan(id) {
        this.ensureLoaded();
        const before = this.plans.length;
        this.plans = this.plans.filter((p) => p.id !== id);
        if (this.plans.length < before) {
            this.save();
            appendAudit("config", "plan_deleted", { planId: id });
            return true;
        }
        return false;
    }
    /** Export the vault as an encrypted backup */
    exportBackup(backupPassword) {
        this.ensureLoaded();
        const json = JSON.stringify(this.plans, null, 2);
        return encrypt(json, backupPassword);
    }
    /** Import from an encrypted backup */
    importBackup(data, backupPassword) {
        const json = decrypt(data, backupPassword);
        const plans = JSON.parse(json);
        for (const plan of plans) {
            if (!plan.id || !plan.name || !Array.isArray(plan.actions)) {
                throw new Error("Invalid backup format");
            }
        }
        this.plans = plans;
        this.save();
        appendAudit("config", "vault_imported", { planCount: plans.length });
    }
    /** Wipe the vault completely */
    wipe() {
        this.plans = [];
        this.save();
        appendAudit("config", "vault_wiped");
    }
}
// -----------------------------------------------------------
// CLI
// -----------------------------------------------------------
function output(data) {
    console.log(JSON.stringify({ ok: true, data }, null, 2));
}
function fail(message) {
    console.log(JSON.stringify({ ok: false, error: message }, null, 2));
    process.exit(1);
}
function getPassword() {
    // Check --password flag
    const idx = process.argv.indexOf("--password");
    if (idx !== -1 && process.argv[idx + 1]) {
        return process.argv[idx + 1];
    }
    // Fall back to env var
    const envPassword = process.env.AFTERSELF_VAULT_PASSWORD;
    if (envPassword)
        return envPassword;
    fail("Vault password required. Use --password <pw> or set AFTERSELF_VAULT_PASSWORD env var.");
    return ""; // unreachable
}
function main() {
    const args = process.argv.slice(2).filter((a) => !a.startsWith("--password"));
    // Also filter out the value after --password
    const pwIdx = process.argv.indexOf("--password");
    if (pwIdx !== -1) {
        const valIdx = args.indexOf(process.argv[pwIdx + 1]);
        if (valIdx !== -1)
            args.splice(valIdx, 1);
    }
    const command = args[0];
    const password = command === undefined ? "" : getPassword();
    switch (command) {
        case "list": {
            const vault = new Vault(password);
            vault.load();
            output(vault.listPlans());
            break;
        }
        case "get": {
            const id = args[1];
            if (!id) {
                fail("Usage: vault.ts get <plan-id>");
                return;
            }
            const vault = new Vault(password);
            vault.load();
            const plan = vault.getPlan(id);
            if (!plan) {
                fail(`Plan not found: ${id}`);
                return;
            }
            output(plan);
            break;
        }
        case "get-all": {
            const vault = new Vault(password);
            vault.load();
            output(vault.getAllPlans());
            break;
        }
        case "create": {
            const planJson = args[1];
            if (!planJson) {
                fail("Usage: vault.ts create '<json>'");
                return;
            }
            const { name, actions } = JSON.parse(planJson);
            if (!name || !actions) {
                fail("JSON must have 'name' and 'actions' fields");
                return;
            }
            const vault = new Vault(password);
            vault.load();
            const plan = vault.createPlan(name, actions);
            output(plan);
            break;
        }
        case "update": {
            const id = args[1];
            const updatesJson = args[2];
            if (!id || !updatesJson) {
                fail("Usage: vault.ts update <id> '<json>'");
                return;
            }
            const updates = JSON.parse(updatesJson);
            const vault = new Vault(password);
            vault.load();
            const plan = vault.updatePlan(id, updates);
            output(plan);
            break;
        }
        case "delete": {
            const id = args[1];
            if (!id) {
                fail("Usage: vault.ts delete <plan-id>");
                return;
            }
            const vault = new Vault(password);
            vault.load();
            const deleted = vault.deletePlan(id);
            output({ deleted, id });
            break;
        }
        case "export": {
            const exportPassword = args[1] || password;
            const outFile = args[2] || "vault-backup.enc";
            const vault = new Vault(password);
            vault.load();
            const backup = vault.exportBackup(exportPassword);
            writeFileSync(outFile, backup);
            output({ file: outFile, size: backup.length });
            break;
        }
        case "import": {
            const inFile = args[1];
            const importPassword = args[2] || password;
            if (!inFile) {
                fail("Usage: vault.ts import <file> [backup-password]");
                return;
            }
            const data = readFileSync(inFile);
            const vault = new Vault(password);
            vault.load();
            vault.importBackup(data, importPassword);
            output({ imported: true, file: inFile });
            break;
        }
        case "wipe": {
            const vault = new Vault(password);
            vault.load();
            vault.wipe();
            output({ wiped: true });
            break;
        }
        default: {
            fail(`Unknown command: ${command}\n` +
                `Available commands: list, get, get-all, create, update, delete, export, import, wipe\n` +
                `Password: --password <pw> or AFTERSELF_VAULT_PASSWORD env var`);
        }
    }
}
// Only run CLI when this is the entry point
import { fileURLToPath } from "url";
if (process.argv[1] === fileURLToPath(import.meta.url)) {
    main();
}
