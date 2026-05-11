const fs = require('fs');
const path = require('path');

const WAKE_FILE = path.resolve(__dirname, '../../memory/evolver_wake.signal');

try {
    fs.writeFileSync(WAKE_FILE, 'WAKE');
    console.log(`[Evolver Trigger] Wake signal sent to ${WAKE_FILE}. The wrapper should wake up shortly.`);
} catch (e) {
    console.error(`[Evolver Trigger] Failed to send wake signal: ${e.message}`);
    process.exit(1);
}
