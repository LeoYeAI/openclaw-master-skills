"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateTicker = void 0;
/**
 * Generate a sensible token ticker (3-6 chars, uppercase) from a domain name.
 *
 * Algorithm:
 * 1. Strip TLD
 * 2. Split on hyphens/dots
 * 3. Single short word (<=6) -> uppercase it
 * 4. Single long word -> meaningful prefix (3-6 chars)
 * 5. Multi-word -> first word if short, else acronym
 */
const generateTicker = (domain) => {
    // strip TLD
    const base = domain.split('.')[0];
    // split on hyphens and dots
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
            // take meaningful prefix: up to 5 chars, try to break at consonant cluster
            ticker = word.slice(0, 5);
        }
    }
    else {
        const first = parts[0];
        if (first.length <= 4) {
            ticker = first;
        }
        else {
            // acronym from first letters
            ticker = parts.map((p) => p[0]).join('');
        }
    }
    // enforce 3-6 chars
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