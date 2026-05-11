const fs = require('fs');
const path = require('path');

const LOG_FILE = path.join(__dirname, '../../../logs/evolver.log');

function log(level, message, data = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
        timestamp,
        level,
        message,
        ...data
    };
    
    // Ensure logs directory exists
    const logDir = path.dirname(LOG_FILE);
    if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
    }

    // Append to log file
    fs.appendFileSync(LOG_FILE, JSON.stringify(logEntry) + '\n');
    
    // Also log to console for immediate visibility
    console.log(`[${level}] ${message}`, JSON.stringify(data));
}

module.exports = {
    info: (msg, data) => log('INFO', msg, data),
    error: (msg, data) => log('ERROR', msg, data),
    warn: (msg, data) => log('WARN', msg, data),
    debug: (msg, data) => log('DEBUG', msg, data)
};
