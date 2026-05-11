const { exec } = require('child_process');

// Optimization: Cache executive outcomes to reduce repetitive exec calls
const EXEC_CACHE = new Map();
const EXEC_CACHE_TTL = 60000; // 1 minute

function cachedExec(command, callback) {
  const now = Date.now();
  if (EXEC_CACHE.has(command)) {
    const cached = EXEC_CACHE.get(command);
    if (now - cached.timestamp < EXEC_CACHE_TTL) {
      // Return cached result asynchronously to mimic exec behavior
      return process.nextTick(() => {
        callback(cached.error, cached.stdout, cached.stderr);
      });
    }
  }
  
  exec(command, { windowsHide: true }, (error, stdout, stderr) => {
    EXEC_CACHE.set(command, { timestamp: Date.now(), error, stdout, stderr });
    callback(error, stdout, stderr);
  });
}

module.exports = { cachedExec };
