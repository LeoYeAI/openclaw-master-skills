#!/usr/bin/env node
const { sendCard } = require('./feishu-helper.js');

// CLI Arguments:
// 1. Message content
// 2. Prefix (e.g., "[INFO]")
const msg = process.argv[2];
const prefix = process.argv[3] || '[INFO]';
const target = process.env.FEISHU_LOG_TARGET || process.env.LOG_TARGET || '';
if (!target) { process.stderr.write('[CardFail] FEISHU_LOG_TARGET or LOG_TARGET env var not set\n'); process.exit(1); }

if (!msg) process.exit(0);

(async () => {
    try {
        const color = prefix.includes('ERROR') || prefix.includes('CRITICAL') || prefix.includes('FAILURE')
            ? 'red'
            : prefix.includes('WARNING') || prefix.includes('WARN')
                ? 'orange'
                : 'blue';
        await sendCard({
            target,
            title: `🧬 Evolver [${new Date().toISOString().substring(11,19)}]`,
            text: `${prefix} ${msg}`,
            color
        });
    } catch (e) {
        process.stderr.write(`[CardFail] ${e.message}\n`);
        process.exit(1);
    }
})();
