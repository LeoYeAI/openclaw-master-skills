const fs = require('fs');
const path = require('path');

// CLEANUP MODULE
// Removes old temporary artifacts to keep the workspace clean.

const EVOLUTION_DIR = path.resolve(__dirname, '../../memory/evolution');
const MAX_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours
const MAX_COUNT = 10; // Keep at least 10 recent files regardless of age

function run() {
    console.log('[Cleanup] Scanning for old artifacts...');
    if (!fs.existsSync(EVOLUTION_DIR)) return;

    try {
        const files = fs.readdirSync(EVOLUTION_DIR)
            .filter(f => f.startsWith('gep_prompt_') && (f.endsWith('.json') || f.endsWith('.txt')))
            .map(f => ({
                name: f,
                path: path.join(EVOLUTION_DIR, f),
                time: fs.statSync(path.join(EVOLUTION_DIR, f)).mtimeMs
            }))
            .sort((a, b) => b.time - a.time); // Newest first

        const toDelete = files.slice(MAX_COUNT).filter(f => (Date.now() - f.time) > MAX_AGE_MS);

        if (toDelete.length > 0) {
            console.log(`[Cleanup] Deleting ${toDelete.length} old GEP prompts...`);
            toDelete.forEach(f => {
                try {
                    fs.unlinkSync(f.path);
                } catch (e) {
                    console.error(`Failed to delete ${f.name}: ${e.message}`);
                }
            });
            return toDelete.length;
        } else {
            console.log('[Cleanup] No files to delete.');
            return 0;
        }
    } catch (err) {
        console.error(`[Cleanup] Error: ${err.message}`);
        return 0;
    }
}

if (require.main === module) {
    run();
}

module.exports = { run };
