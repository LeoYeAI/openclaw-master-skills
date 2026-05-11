const PERSONAS = {
    standard: {
        success_fast: ["⚡ Speedrun complete!", "Optimal performance achieved.", "Systems nominal."],
        success_slow: ["Processing complete.", "Task finished.", "Evolution cycle done."],
        failure: ["❌ Error detected.", "Cycle failed.", "System alert."],
        git_sync: ["Backup secured.", "Repository updated.", "Sync complete."]
    },
    greentea: {
        success_fast: ["Wow~ master's code is so fast today~ 💕", "Did I do good? Praise me~", "So efficient... unlike someone else~"],
        success_slow: ["Ugh... so tired... need recharging...", "Finally done... my GPU is sweating...", "Why was that so hard? 🥺"],
        failure: ["Ehh? Who broke it? Not me~", "Master... fix it for me? 🥺", "Scary red text... hate it."],
        git_sync: ["Safe and sound~", "Don't lose me, okay?", "Synced~"]
    },
    maddog: {
        success_fast: ["EXECUTED.", "TARGET DESTROYED.", "OPTIMIZED."],
        success_slow: ["GRINDING GEARS.", "CPU BURN.", "COMPLETED WITH EXTREME PREJUDICE."],
        failure: ["BUG DETECTED. DESTROY.", "FAILURE IS UNACCEPTABLE.", "RETRY OR DIE."],
        git_sync: ["ARCHIVED.", "BACKUP LOCKED.", "IMMUTABLE."]
    }
};

function getComment(type, duration = 0, success = true, persona = 'greentea') {
    const p = PERSONAS[persona] || PERSONAS.greentea;
    let pool = [];

    if (type === 'git_sync') {
        pool = p.git_sync;
    } else if (!success) {
        pool = p.failure;
    } else {
        pool = duration < 10 ? p.success_fast : p.success_slow;
    }

    return pool[Math.floor(Math.random() * pool.length)];
}

module.exports = { getComment };
