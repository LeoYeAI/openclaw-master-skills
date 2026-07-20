// ============================================================
// Afterself — State Manager (CLI)
// Persists switch state, ghost state, and audit log locally.
// Called by the OpenClaw agent via CLI commands.
// ============================================================
import { randomUUID } from "crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
const STATE_DIR = join(process.env.HOME || "~", ".afterself");
const STATE_FILE = join(STATE_DIR, "state.json");
const AUDIT_FILE = join(STATE_DIR, "audit.jsonl");
const CONFIG_FILE = join(STATE_DIR, "config.json");
/** Ensure the data directory exists */
function ensureDir() {
    if (!existsSync(STATE_DIR)) {
        mkdirSync(STATE_DIR, { recursive: true, mode: 0o700 });
    }
}
// -----------------------------------------------------------
// Default State
// -----------------------------------------------------------
function defaultState() {
    return {
        switchState: "disabled",
        ghostState: "off",
        lastCheckIn: null,
        lastPingSent: null,
        missedCheckIns: 0,
        escalationResponses: [],
        executorProgress: {
            totalActions: 0,
            completedActions: 0,
            failedActions: [],
        },
        ghostActivatedAt: null,
        mortalityTokenBalance: null,
        mortalityTransferComplete: false,
    };
}
// -----------------------------------------------------------
// Default Config
// -----------------------------------------------------------
export function defaultConfig() {
    return {
        heartbeat: {
            interval: "72h",
            channels: ["whatsapp"],
            warningPeriod: "24h",
            escalationTimeout: "48h",
            escalationContacts: [],
        },
        vault: {
            encryption: "aes-256-gcm",
            beneficiaryKeyEnabled: true,
            dbPath: join(STATE_DIR, "vault.enc"),
            backupPath: undefined,
        },
        executor: {
            enabled: true,
            confirmationGate: true,
            auditLog: true,
            maxRetries: 3,
            actionDelay: 5000,
        },
        ghost: {
            enabled: false,
            learning: false,
            transparency: true,
            voiceEnabled: false,
            socialPosting: false,
            timeDecay: { enabled: true, fadeOverDays: 90 },
            killSwitchContacts: [],
            blockedTopics: [],
        },
        llm: {
            provider: "anthropic",
            model: "claude-sonnet-4-20250514",
            maxTokens: 500,
            temperature: 0.7,
        },
        mortalityPool: {
            enabled: false,
            poolWallet: "6J8AwTGc8ys9L7Z8dC7Wcd8AbmPxyKpZH8nXu4BrB5md",
            tokenMint: "EXAMPLE_TOKEN_MINT_ADDRESS",
            rpcUrl: "https://api.mainnet-beta.solana.com",
            nudgeEnabled: true,
        },
    };
}
// -----------------------------------------------------------
// State Operations
// -----------------------------------------------------------
export function loadState() {
    ensureDir();
    if (!existsSync(STATE_FILE))
        return defaultState();
    try {
        const raw = readFileSync(STATE_FILE, "utf-8");
        return { ...defaultState(), ...JSON.parse(raw) };
    }
    catch {
        return defaultState();
    }
}
export function saveState(state) {
    ensureDir();
    writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), { mode: 0o600 });
}
export function updateState(updater) {
    const current = loadState();
    const updated = updater(current);
    saveState(updated);
    return updated;
}
// -----------------------------------------------------------
// Config Operations
// -----------------------------------------------------------
export function loadConfig() {
    ensureDir();
    if (!existsSync(CONFIG_FILE))
        return defaultConfig();
    try {
        const raw = readFileSync(CONFIG_FILE, "utf-8");
        return { ...defaultConfig(), ...JSON.parse(raw) };
    }
    catch {
        return defaultConfig();
    }
}
export function saveConfig(config) {
    ensureDir();
    writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), { mode: 0o600 });
}
// -----------------------------------------------------------
// Audit Log (append-only JSONL)
// -----------------------------------------------------------
export function appendAudit(type, action, details = {}, success = true) {
    ensureDir();
    const entry = {
        id: randomUUID(),
        timestamp: new Date().toISOString(),
        type,
        action,
        details,
        success,
    };
    const line = JSON.stringify(entry) + "\n";
    writeFileSync(AUDIT_FILE, line, { flag: "a", mode: 0o600 });
    return entry;
}
export function readAuditLog(limit = 50) {
    if (!existsSync(AUDIT_FILE))
        return [];
    try {
        const raw = readFileSync(AUDIT_FILE, "utf-8");
        const lines = raw.trim().split("\n").filter(Boolean);
        return lines
            .slice(-limit)
            .map((line) => JSON.parse(line))
            .reverse();
    }
    catch {
        return [];
    }
}
// -----------------------------------------------------------
// Duration Parsing Utility
// -----------------------------------------------------------
/** Parse a duration string like "72h", "7d", "30m" into milliseconds */
export function parseDuration(duration) {
    const match = duration.match(/^(\d+)(m|h|d)$/);
    if (!match)
        throw new Error(`Invalid duration: ${duration}`);
    const value = parseInt(match[1], 10);
    const unit = match[2];
    switch (unit) {
        case "m": return value * 60 * 1000;
        case "h": return value * 60 * 60 * 1000;
        case "d": return value * 24 * 60 * 60 * 1000;
        default: throw new Error(`Unknown unit: ${unit}`);
    }
}
/** Format milliseconds as a human-readable duration */
export function formatDuration(ms) {
    const hours = Math.floor(ms / (60 * 60 * 1000));
    if (hours >= 24)
        return `${Math.floor(hours / 24)}d ${hours % 24}h`;
    if (hours > 0)
        return `${hours}h`;
    return `${Math.floor(ms / (60 * 1000))}m`;
}
// -----------------------------------------------------------
// CLI-specific: Heartbeat & Escalation Checks
// -----------------------------------------------------------
/** Check if the user's check-in is overdue based on heartbeat interval */
function isOverdue() {
    const state = loadState();
    const config = loadConfig();
    if (state.switchState !== "armed" && state.switchState !== "warning") {
        return { overdue: false, elapsed: null, interval: config.heartbeat.interval };
    }
    const lastActivity = state.lastCheckIn || state.lastPingSent;
    if (!lastActivity) {
        return { overdue: true, elapsed: null, interval: config.heartbeat.interval };
    }
    const elapsed = Date.now() - new Date(lastActivity).getTime();
    const intervalMs = parseDuration(config.heartbeat.interval);
    return {
        overdue: elapsed > intervalMs,
        elapsed: formatDuration(elapsed),
        interval: config.heartbeat.interval,
    };
}
/** Check if warning period has expired (should begin escalation) */
function isWarningExpired() {
    const state = loadState();
    const config = loadConfig();
    if (state.switchState !== "warning") {
        return { expired: false, elapsed: null, warningPeriod: config.heartbeat.warningPeriod };
    }
    if (!state.lastPingSent) {
        return { expired: true, elapsed: null, warningPeriod: config.heartbeat.warningPeriod };
    }
    const elapsed = Date.now() - new Date(state.lastPingSent).getTime();
    const warningMs = parseDuration(config.heartbeat.warningPeriod);
    return {
        expired: elapsed > warningMs,
        elapsed: formatDuration(elapsed),
        warningPeriod: config.heartbeat.warningPeriod,
    };
}
/** Evaluate escalation responses — who confirmed, what's the decision? */
function escalationStatus() {
    const state = loadState();
    const config = loadConfig();
    const responses = state.escalationResponses;
    const totalContacts = config.heartbeat.escalationContacts.length;
    const aliveCount = responses.filter((r) => r.response === "confirmed_alive").length;
    const absentCount = responses.filter((r) => r.response === "confirmed_absent").length;
    const threshold = Math.ceil(totalContacts / 2);
    let decision = "waiting";
    if (aliveCount > 0) {
        decision = "stand_down";
    }
    else if (absentCount >= threshold) {
        decision = "trigger";
    }
    return {
        state: state.switchState,
        responses,
        totalContacts,
        aliveCount,
        absentCount,
        decision,
    };
}
/** Check ghost mode time decay status */
function ghostDecayCheck() {
    const state = loadState();
    const config = loadConfig();
    const fadeOverDays = config.ghost.timeDecay.fadeOverDays;
    if (state.ghostState !== "active" && state.ghostState !== "fading") {
        return {
            ghostState: state.ghostState,
            activatedAt: state.ghostActivatedAt,
            elapsedDays: null,
            fadeOverDays,
            shouldRespond: false,
            probability: 0,
        };
    }
    if (!state.ghostActivatedAt || !config.ghost.timeDecay.enabled) {
        return {
            ghostState: state.ghostState,
            activatedAt: state.ghostActivatedAt,
            elapsedDays: null,
            fadeOverDays,
            shouldRespond: true,
            probability: 1,
        };
    }
    const elapsed = Date.now() - new Date(state.ghostActivatedAt).getTime();
    const elapsedDays = elapsed / (24 * 60 * 60 * 1000);
    if (elapsedDays >= fadeOverDays) {
        return {
            ghostState: state.ghostState,
            activatedAt: state.ghostActivatedAt,
            elapsedDays: Math.round(elapsedDays * 10) / 10,
            fadeOverDays,
            shouldRespond: false,
            probability: 0,
        };
    }
    const probability = Math.round((1 - elapsedDays / fadeOverDays) * 100) / 100;
    return {
        ghostState: state.ghostState,
        activatedAt: state.ghostActivatedAt,
        elapsedDays: Math.round(elapsedDays * 10) / 10,
        fadeOverDays,
        shouldRespond: true,
        probability,
    };
}
// -----------------------------------------------------------
// CLI Argument Parser
// -----------------------------------------------------------
function output(data) {
    console.log(JSON.stringify({ ok: true, data }, null, 2));
}
function fail(message) {
    console.log(JSON.stringify({ ok: false, error: message }, null, 2));
    process.exit(1);
}
function setNestedValue(obj, path, value) {
    const keys = path.split(".");
    let current = obj;
    for (let i = 0; i < keys.length - 1; i++) {
        if (!(keys[i] in current))
            current[keys[i]] = {};
        current = current[keys[i]];
    }
    // Try to parse as JSON (for arrays, booleans, numbers)
    try {
        current[keys[keys.length - 1]] = JSON.parse(value);
    }
    catch {
        current[keys[keys.length - 1]] = value;
    }
}
function getNestedValue(obj, path) {
    const keys = path.split(".");
    let current = obj;
    for (const key of keys) {
        if (current == null || !(key in current))
            return undefined;
        current = current[key];
    }
    return current;
}
function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    switch (command) {
        case "status": {
            output(loadState());
            break;
        }
        case "checkin": {
            const updated = updateState((s) => ({
                ...s,
                switchState: s.switchState === "warning" || s.switchState === "escalating" ? "armed" : s.switchState,
                lastCheckIn: new Date().toISOString(),
                missedCheckIns: 0,
                escalationResponses: [],
            }));
            appendAudit("heartbeat", "check_in", { source: "cli" });
            output(updated);
            break;
        }
        case "arm": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "armed",
                lastCheckIn: new Date().toISOString(),
                missedCheckIns: 0,
            }));
            appendAudit("heartbeat", "armed");
            output(updated);
            break;
        }
        case "disarm": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "disabled",
                missedCheckIns: 0,
            }));
            appendAudit("heartbeat", "disarmed");
            output(updated);
            break;
        }
        case "update": {
            const key = args[1];
            const value = args[2];
            if (!key || value === undefined) {
                fail("Usage: state.ts update <key> <value>");
                return;
            }
            const updated = updateState((s) => {
                const copy = { ...s };
                setNestedValue(copy, key, value);
                return copy;
            });
            output(updated);
            break;
        }
        case "config": {
            const sub = args[1];
            if (sub === "get") {
                const config = loadConfig();
                const key = args[2];
                if (key) {
                    output(getNestedValue(config, key));
                }
                else {
                    output(config);
                }
            }
            else if (sub === "set") {
                const key = args[2];
                const value = args[3];
                if (!key || value === undefined) {
                    fail("Usage: state.ts config set <key> <value>");
                    return;
                }
                const config = loadConfig();
                setNestedValue(config, key, value);
                saveConfig(config);
                appendAudit("config", "config_updated", { key, value });
                output(config);
            }
            else {
                fail("Usage: state.ts config <get|set> [key] [value]");
            }
            break;
        }
        case "audit": {
            const type = args[1];
            const action = args[2];
            const detailsStr = args[3];
            if (!type || !action) {
                fail("Usage: state.ts audit <type> <action> [details_json]");
                return;
            }
            const details = detailsStr ? JSON.parse(detailsStr) : {};
            const entry = appendAudit(type, action, details);
            output(entry);
            break;
        }
        case "audit-log": {
            const limit = args[1] ? parseInt(args[1], 10) : 50;
            output(readAuditLog(limit));
            break;
        }
        case "is-overdue": {
            output(isOverdue());
            break;
        }
        case "is-warning-expired": {
            output(isWarningExpired());
            break;
        }
        case "escalation-status": {
            output(escalationStatus());
            break;
        }
        case "ghost-decay-check": {
            output(ghostDecayCheck());
            break;
        }
        case "record-ping": {
            const updated = updateState((s) => ({
                ...s,
                lastPingSent: new Date().toISOString(),
            }));
            appendAudit("heartbeat", "ping_sent", { source: "cli" });
            output(updated);
            break;
        }
        case "record-warning": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "warning",
                missedCheckIns: s.missedCheckIns + 1,
            }));
            appendAudit("heartbeat", "warning_sent", { missedCount: loadState().missedCheckIns });
            output(updated);
            break;
        }
        case "begin-escalation": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "escalating",
                escalationResponses: [],
            }));
            appendAudit("escalation", "contacts_notified");
            output(updated);
            break;
        }
        case "record-escalation-response": {
            const contactId = args[1];
            const response = args[2];
            if (!contactId || !response) {
                fail("Usage: state.ts record-escalation-response <contactId> <response>");
                return;
            }
            const updated = updateState((s) => ({
                ...s,
                escalationResponses: [
                    ...s.escalationResponses,
                    { contactId, response, timestamp: new Date().toISOString() },
                ],
            }));
            appendAudit("escalation", "response_received", { contactId, response });
            output(updated);
            break;
        }
        case "trigger": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "triggered",
            }));
            appendAudit("heartbeat", "switch_triggered", {
                escalationResponses: loadState().escalationResponses,
            });
            output(updated);
            break;
        }
        case "stand-down": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "armed",
                missedCheckIns: 0,
                escalationResponses: [],
            }));
            appendAudit("escalation", "stand_down");
            output(updated);
            break;
        }
        case "activate-ghost": {
            const updated = updateState((s) => ({
                ...s,
                ghostState: "active",
                ghostActivatedAt: new Date().toISOString(),
            }));
            appendAudit("ghost", "activated");
            output(updated);
            break;
        }
        case "complete": {
            const updated = updateState((s) => ({
                ...s,
                switchState: "completed",
            }));
            appendAudit("executor", "execution_complete");
            output(updated);
            break;
        }
        default: {
            fail(`Unknown command: ${command}\n` +
                `Available commands: status, checkin, arm, disarm, update, config, audit, audit-log, ` +
                `is-overdue, is-warning-expired, escalation-status, ghost-decay-check, ` +
                `record-ping, record-warning, begin-escalation, record-escalation-response, ` +
                `trigger, stand-down, activate-ghost, complete`);
        }
    }
}
// Only run CLI when this is the entry point
import { fileURLToPath } from "url";
if (process.argv[1] === fileURLToPath(import.meta.url)) {
    main();
}
