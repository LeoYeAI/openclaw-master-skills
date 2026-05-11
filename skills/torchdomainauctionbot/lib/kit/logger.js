"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = void 0;
const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
class Logger {
    constructor(module, level = 'info') {
        this.child = (module) => {
            const child = new Logger(`${this.module}:${module}`);
            child.level = this.level;
            return child;
        };
        this.debug = (msg, data) => this.log('debug', msg, data);
        this.info = (msg, data) => this.log('info', msg, data);
        this.warn = (msg, data) => this.log('warn', msg, data);
        this.error = (msg, data) => this.log('error', msg, data);
        this.log = (level, msg, data) => {
            if (LEVELS[level] < this.level)
                return;
            const ts = new Date().toISOString().substr(11, 12);
            const prefix = `[${ts}] [${level.toUpperCase()}] [${this.module}]`;
            if (data !== undefined) {
                console.log(`${prefix} ${msg}`, data);
            }
            else {
                console.log(`${prefix} ${msg}`);
            }
        };
        this.module = module;
        this.level = LEVELS[level];
    }
}
exports.Logger = Logger;
//# sourceMappingURL=logger.js.map