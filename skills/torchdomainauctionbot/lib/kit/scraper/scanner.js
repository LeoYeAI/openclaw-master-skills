"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.scanDomains = void 0;
const evaluator_1 = require("./evaluator");
const logger_1 = require("../logger");
const scanDomains = async (config) => {
    const log = new logger_1.Logger('scanner', config.logLevel);
    const allListings = [];
    for (const provider of config.providers) {
        log.info(`scanning provider: ${provider.name}`);
        try {
            const listings = await provider.scan({
                maxPrice: config.maxPriceUsd,
                limit: 50,
            });
            log.info(`${provider.name} returned ${listings.length} listings`);
            allListings.push(...listings);
        }
        catch (err) {
            log.error(`provider ${provider.name} failed`, err);
        }
    }
    log.info(`total listings: ${allListings.length}`);
    // score all listings
    const scored = allListings.map(evaluator_1.evaluateDomain);
    // filter by minimum score and sort descending
    const filtered = scored
        .filter((d) => d.score >= config.minScore)
        .sort((a, b) => b.score - a.score);
    log.info(`${filtered.length} domains passed minimum score of ${config.minScore}`);
    return filtered;
};
exports.scanDomains = scanDomains;
//# sourceMappingURL=scanner.js.map