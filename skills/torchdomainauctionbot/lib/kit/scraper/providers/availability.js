"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.availabilityProvider = void 0;
/**
 * Availability provider — checks domain availability via RDAP protocol.
 * RDAP is the replacement for WHOIS and doesn't require API keys.
 * v1: checks a predefined list of interesting short domains.
 */
const CANDIDATE_NAMES = [
    'aibot',
    'solpay',
    'defiai',
    'web3go',
    'chainx',
    'nftlab',
    'cryptox',
    'swapai',
    'payfi',
    'tokenv',
];
const CANDIDATE_TLDS = ['com', 'io', 'ai', 'xyz', 'dev'];
const checkRdap = async (name, tld) => {
    try {
        const rdapUrl = `https://rdap.org/domain/${name}.${tld}`;
        const response = await fetch(rdapUrl, {
            method: 'HEAD',
            signal: AbortSignal.timeout(5000),
        });
        // 404 means domain is available, 200 means registered
        return response.status === 404;
    }
    catch {
        return false;
    }
};
exports.availabilityProvider = {
    name: 'availability',
    scan: async (opts) => {
        const listings = [];
        for (const name of CANDIDATE_NAMES) {
            if (listings.length >= opts.limit)
                break;
            for (const tld of CANDIDATE_TLDS) {
                if (listings.length >= opts.limit)
                    break;
                const available = await checkRdap(name, tld);
                if (available) {
                    // estimate registration cost by TLD
                    const price = tld === 'com' ? 12 : tld === 'ai' ? 25 : tld === 'io' ? 15 : 8;
                    if (price <= opts.maxPrice) {
                        listings.push({
                            name,
                            tld,
                            price,
                            currency: 'USD',
                            provider: 'availability',
                        });
                    }
                }
            }
        }
        return listings;
    },
};
//# sourceMappingURL=availability.js.map