"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.fqdn = exports.formatUsd = exports.sleep = void 0;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
exports.sleep = sleep;
const formatUsd = (cents) => `$${(cents / 100).toFixed(2)}`;
exports.formatUsd = formatUsd;
const fqdn = (name, tld) => `${name}.${tld}`;
exports.fqdn = fqdn;
//# sourceMappingURL=utils.js.map