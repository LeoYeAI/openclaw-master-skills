"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.expiredDomainsProvider = void 0;
/**
 * Expired domains provider — fetches publicly available expired/expiring domain feeds.
 * v1: returns simulated listings from known expired domain patterns.
 * Future: integrate with real expired domain feeds (ExpiredDomains.net, NameJet, etc.)
 */
exports.expiredDomainsProvider = {
    name: 'expired-domains',
    scan: async (opts) => {
        const listings = [];
        try {
            // v1: fetch from a public expired domain list endpoint
            // this is a placeholder — real implementation would hit an actual API
            // for now, we simulate the interface so the pipeline works end-to-end
            const response = await fetch('https://www.expireddomains.net/domain-name-search/?fwhois=22&ftlds[]=1', {
                headers: { 'User-Agent': 'TorchDomainBot/1.0' },
                signal: AbortSignal.timeout(10000),
            });
            if (!response.ok) {
                return listings;
            }
            const html = await response.text();
            // parse domain names from the response (basic extraction)
            const domainRegex = /class="field_name"[^>]*><a[^>]*>([a-z0-9-]+)\.([a-z]{2,6})<\/a>/gi;
            let match;
            while ((match = domainRegex.exec(html)) !== null && listings.length < opts.limit) {
                const name = match[1].toLowerCase();
                const tld = match[2].toLowerCase();
                listings.push({
                    name,
                    tld,
                    price: 10, // expired domains typically cost registration fee
                    currency: 'USD',
                    provider: 'expired-domains',
                });
            }
        }
        catch {
            // network errors are expected — provider is best-effort
        }
        return listings.filter((l) => l.price <= opts.maxPrice).slice(0, opts.limit);
    },
};
//# sourceMappingURL=expired-domains.js.map