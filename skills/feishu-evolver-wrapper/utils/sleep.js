
function sleepSync(ms) {
    if (ms <= 0) return;
    try {
        const sab = new SharedArrayBuffer(4);
        const int32 = new Int32Array(sab);
        Atomics.wait(int32, 0, 0, ms);
    } catch (e) {
        // Fallback for environments without SharedArrayBuffer (rare in Node 22)
        const end = Date.now() + ms;
        while (Date.now() < end) {}
    }
}

module.exports = { sleepSync };
