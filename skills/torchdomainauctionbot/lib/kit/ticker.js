"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateTicker = void 0;
/**
 * Generate a sensible token ticker (3-6 chars, uppercase) from a domain name.
 */
const generateTicker = (domain) => {
    const base = domain.split('.')[0];
    const parts = base.split(/[-.]/).filter((p) => p.length > 0);
    let ticker;
    if (parts.length === 0) {
        ticker = 'TKN';
    }
    else if (parts.length === 1) {
        const word = parts[0];
        if (word.length <= 6) {
            ticker = word;
        }
        else {
            ticker = word.slice(0, 5);
        }
    }
    else {
        const first = parts[0];
        if (first.length <= 4) {
            ticker = first;
        }
        else {
            ticker = parts.map((p) => p[0]).join('');
        }
    }
    if (ticker.length < 3) {
        ticker = ticker.padEnd(3, 'X');
    }
    else if (ticker.length > 6) {
        ticker = ticker.slice(0, 6);
    }
    return ticker.toUpperCase();
};
exports.generateTicker = generateTicker;
//# sourceMappingURL=ticker.js.map