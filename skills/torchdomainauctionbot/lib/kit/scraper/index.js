#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = exports.generateTicker = exports.evaluateDomain = exports.scanDomains = void 0;
const config_1 = require("./config");
const scanner_1 = require("./scanner");
const expired_domains_1 = require("./providers/expired-domains");
const availability_1 = require("./providers/availability");
const logger_1 = require("../logger");
var scanner_2 = require("./scanner");
Object.defineProperty(exports, "scanDomains", { enumerable: true, get: function () { return scanner_2.scanDomains; } });
var evaluator_1 = require("./evaluator");
Object.defineProperty(exports, "evaluateDomain", { enumerable: true, get: function () { return evaluator_1.evaluateDomain; } });
var ticker_1 = require("./ticker");
Object.defineProperty(exports, "generateTicker", { enumerable: true, get: function () { return ticker_1.generateTicker; } });
var logger_2 = require("../logger");
Object.defineProperty(exports, "Logger", { enumerable: true, get: function () { return logger_2.Logger; } });
const main = async () => {
    const config = (0, config_1.loadConfig)([expired_domains_1.expiredDomainsProvider, availability_1.availabilityProvider]);
    const log = new logger_1.Logger('scraper', config.logLevel);
    log.info('torch domain scraper starting');
    log.info(`config: maxPrice=$${config.maxPriceUsd}, minScore=${config.minScore}`);
    const results = await (0, scanner_1.scanDomains)(config);
    if (results.length === 0) {
        log.info('no domains found matching criteria');
        return;
    }
    log.info(`found ${results.length} candidate domains:\n`);
    for (const d of results) {
        console.log(`  [${d.score}] ${d.listing.name}.${d.listing.tld} — $${d.listing.price} — ticker: ${d.ticker} — ${d.reasoning}`);
    }
};
// only run CLI when executed directly
if (require.main === module) {
    main().catch((err) => {
        console.error('FATAL:', err);
        process.exit(1);
    });
}
//# sourceMappingURL=index.js.map