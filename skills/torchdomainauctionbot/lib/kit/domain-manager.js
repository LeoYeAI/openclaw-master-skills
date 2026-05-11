"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.updateLeases = exports.checkTopHolder = void 0;
const torchsdk_1 = require("torchsdk");
const utils_1 = require("./utils");
const DEFAULT_LEASE_DURATION_MS = 7 * 24 * 60 * 60 * 1000; // 7 days
const checkTopHolder = async (connection, mint) => {
    const result = await (0, utils_1.withTimeout)((0, torchsdk_1.getHolders)(connection, mint, 1), 30000, 'getHolders');
    if (result.holders.length === 0)
        return null;
    return result.holders[0].address;
};
exports.checkTopHolder = checkTopHolder;
const updateLeases = async (connection, domainTokens, leases, log) => {
    const now = Date.now();
    const updated = [...leases];
    // expire old leases
    for (const lease of updated) {
        if (lease.active && lease.expiresAt <= now) {
            lease.active = false;
            log?.info(`lease expired: ${lease.domain} — lessee=${lease.lessee.slice(0, 8)}...`);
        }
    }
    // check each domain token for new top holder
    for (const dt of domainTokens) {
        const topHolder = await (0, exports.checkTopHolder)(connection, dt.mint);
        if (!topHolder)
            continue;
        const activeLease = updated.find((l) => l.mint === dt.mint && l.active);
        if (activeLease) {
            // if top holder changed, expire current and create new
            if (activeLease.lessee !== topHolder) {
                activeLease.active = false;
                log?.info(`top holder changed for ${dt.domain}: ${activeLease.lessee.slice(0, 8)}... → ${topHolder.slice(0, 8)}...`);
                updated.push({
                    domain: dt.domain,
                    mint: dt.mint,
                    lessee: topHolder,
                    startedAt: now,
                    expiresAt: now + DEFAULT_LEASE_DURATION_MS,
                    active: true,
                });
            }
        }
        else {
            // no active lease — create one for top holder
            log?.info(`new lease: ${dt.domain} → ${topHolder.slice(0, 8)}...`);
            updated.push({
                domain: dt.domain,
                mint: dt.mint,
                lessee: topHolder,
                startedAt: now,
                expiresAt: now + DEFAULT_LEASE_DURATION_MS,
                active: true,
            });
        }
    }
    return updated;
};
exports.updateLeases = updateLeases;
//# sourceMappingURL=domain-manager.js.map