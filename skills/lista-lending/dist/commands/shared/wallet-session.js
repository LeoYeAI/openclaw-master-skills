import { existsSync, readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";
const WALLET_SESSIONS_FILE = join(homedir(), ".agent-wallet", "sessions.json");
function parseAccountAddress(account) {
    return account.split(":").slice(2).join(":");
}
export function inferLatestTopicByAddress(address) {
    if (!existsSync(WALLET_SESSIONS_FILE))
        return null;
    try {
        const sessions = JSON.parse(readFileSync(WALLET_SESSIONS_FILE, "utf-8"));
        const needle = address.toLowerCase();
        const matches = Object.entries(sessions)
            .filter(([, session]) => (session.accounts || []).some((account) => parseAccountAddress(account).toLowerCase() === needle))
            .map(([topic, session]) => ({
            topic,
            sortKey: session.updatedAt || session.createdAt || "",
        }))
            .sort((a, b) => b.sortKey.localeCompare(a.sortKey));
        if (matches.length === 0)
            return null;
        return matches[0].topic;
    }
    catch {
        return null;
    }
}
