#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');
const { program } = require('commander');
const { execSync } = require('child_process');
const { sendCard } = require('./feishu-helper.js');
const { fetchWithAuth } = require('../feishu-common/index.js');
const { generateDashboardCard } = require('./utils/dashboard-generator.js');
const crypto = require('crypto');

// Check for integration key (tenant_access_token or webhook)
const integrationKey = process.env.FEISHU_APP_ID || process.env.FEISHU_BOT_NAME;
if (!integrationKey) {
  console.warn('⚠️ Integration key missing (FEISHU_APP_ID). Reporting might fail or degrade to console only.');
  // Don't exit, just warn - we might be in a test env
}

// --- REPORT DEDUP ---
const DEDUP_FILE = path.resolve(__dirname, '../../memory/report_dedup.json');
const DEDUP_WINDOW_MS = 30 * 60 * 1000; // 30 minutes

function isDuplicateReport(reportKey) {
    if (process.env.EVOLVE_REPORT_DEDUP === '0') return false;
    try {
        var cache = {};
        if (fs.existsSync(DEDUP_FILE)) {
            cache = JSON.parse(fs.readFileSync(DEDUP_FILE, 'utf8'));
        }
        var now = Date.now();
        // Prune old entries
        for (var k in cache) {
            if (now - cache[k] > DEDUP_WINDOW_MS) delete cache[k];
        }
        if (cache[reportKey]) {
            console.log('[Wrapper] Report dedup: skipping duplicate report (' + reportKey.slice(0, 40) + '...)');
            return true;
        }
        cache[reportKey] = now;
        var tmpDedup = DEDUP_FILE + '.tmp.' + process.pid;
        fs.writeFileSync(tmpDedup, JSON.stringify(cache, null, 2));
        fs.renameSync(tmpDedup, DEDUP_FILE);
        return false;
    } catch (e) {
        // On error, allow the report through
        return false;
    }
}

// --- DASHBOARD LOGIC START ---
const EVENTS_FILE = path.resolve(__dirname, '../../assets/gep/events.jsonl');

function getDashboardStats() {
    if (!fs.existsSync(EVENTS_FILE)) return null;
    
    try {
        const content = fs.readFileSync(EVENTS_FILE, 'utf8');
        const lines = content.split('\n').filter(Boolean);
        const events = lines.map(l => { try { return JSON.parse(l); } catch(e){ return null; } }).filter(e => e && e.type === 'EvolutionEvent');
        
        if (events.length === 0) return null;

        const total = events.length;
        const successful = events.filter(e => e.outcome && e.outcome.status === 'success').length;
        const successRate = ((successful / total) * 100).toFixed(1);
        
        const intents = { innovate: 0, repair: 0, optimize: 0 };
        let totalFiles = 0, totalLines = 0, countBlast = 0;
        let totalRigor = 0, totalRisk = 0, countPers = 0;

        events.forEach(e => {
            if (intents[e.intent] !== undefined) intents[e.intent]++;
            
            // Blast Radius Stats (Recent 10)
            if (e.blast_radius) {
                totalFiles += (e.blast_radius.files || 0);
                totalLines += (e.blast_radius.lines || 0);
                countBlast++;
            }
            
            // Personality Stats (Recent 10)
            if (e.personality_state) {
                totalRigor += (e.personality_state.rigor || 0);
                totalRisk += (e.personality_state.risk_tolerance || 0);
                countPers++;
            }
        });

        const recent = events.slice(-5).reverse().map(e => ({
            id: e.id.replace('evt_', '').substring(0, 6),
            intent: e.intent === 'innovate' ? '✨' : (e.intent === 'repair' ? '🔧' : '⚡'),
            status: e.outcome && e.outcome.status === 'success' ? '✅' : '❌'
        }));

        const avgFiles = countBlast > 0 ? (totalFiles / countBlast).toFixed(1) : 0;
        const avgLines = countBlast > 0 ? (totalLines / countBlast).toFixed(0) : 0;
        const avgRigor = countPers > 0 ? (totalRigor / countPers).toFixed(2) : 0;

        return { total, successRate, intents, recent, avgFiles, avgLines, avgRigor };
    } catch (e) {
        return null;
    }
}
// --- DASHBOARD LOGIC END ---

let runSkillsMonitor;
try {
    runSkillsMonitor = require('../evolver/src/ops/skills_monitor').run;
} catch (e) {
    try { runSkillsMonitor = require('./skills_monitor.js').run; } catch (e2) {
        runSkillsMonitor = () => [];
    }
}

// INNOVATION: Load dedicated System Monitor (Native Node) if available
let sysMon;
try {
    // Try to load the optimized monitor first
    sysMon = require('../system-monitor');
} catch (e) {
    // Optimized Native Implementation (Linux/Node 18+)
    sysMon = {
        getProcessCount: () => {
            try {
                // Linux: Count numeric directories in /proc
                if (process.platform === 'linux') {
                    return fs.readdirSync('/proc').filter(f => /^\d+$/.test(f)).length;
                }
                // Fallback for non-Linux
                if (process.platform === 'win32') return '?';
                return execSync('ps -e | wc -l', { windowsHide: true }).toString().trim();
            } catch(e){ return '?'; }
        },
        getDiskUsage: (mount) => {
            try {
                if (fs.statfsSync) {
                    const stats = fs.statfsSync(mount || '/');
                    const total = stats.blocks * stats.bsize;
                    const free = stats.bavail * stats.bsize;
                    const used = total - free;
                    return Math.round((used / total) * 100) + '%';
                }
                // Fallback for older Node
                if (process.platform === 'win32') return '?';
                return execSync(`df -h "${mount || '/'}" | tail -1 | awk '{print $5}'`, { windowsHide: true }).toString().trim();
            } catch(e){ return '?'; }
        },
        getLastLine: (f) => {
            try {
                if (!fs.existsSync(f)) return '';
                const fd = fs.openSync(f, 'r');
                const stat = fs.fstatSync(fd);
                const size = stat.size;
                if (size === 0) { fs.closeSync(fd); return ''; }
                
                const bufSize = Math.min(1024, size);
                const buffer = Buffer.alloc(bufSize);
                let position = size - bufSize;
                fs.readSync(fd, buffer, 0, bufSize, position);
                fs.closeSync(fd);
                
                let content = buffer.toString('utf8');
                // Trim trailing newline if present
                if (content.endsWith('\n')) content = content.slice(0, -1);
                const lastBreak = content.lastIndexOf('\n');
                return lastBreak === -1 ? content : content.slice(lastBreak + 1);
            } catch(e){ return ''; }
        }
    };
}

const STATE_FILE = path.resolve(__dirname, '../../memory/evolution_state.json');
const CYCLE_COUNTER_FILE = path.resolve(__dirname, '../../logs/cycle_count.txt');

function parseCycleNumber(value) {
    if (typeof value === 'number' && Number.isFinite(value)) return Math.trunc(value);
    const text = String(value || '').trim();
    if (!text) return null;
    if (/^\d+$/.test(text)) return parseInt(text, 10);
    const m = text.match(/(\d{1,})/);
    if (!m) return null;
    return parseInt(m[1], 10);
}

function isStaleCycleReport(cycleId) {
    try {
        const currentRaw = fs.existsSync(CYCLE_COUNTER_FILE)
            ? fs.readFileSync(CYCLE_COUNTER_FILE, 'utf8').trim()
            : '';
        const current = /^\d+$/.test(currentRaw) ? parseInt(currentRaw, 10) : null;
        const candidate = parseCycleNumber(cycleId);
        if (!Number.isFinite(current) || !Number.isFinite(candidate)) return false;
        const windowSize = Number.parseInt(process.env.EVOLVE_STALE_CYCLE_WINDOW || '5', 10);
        if (!Number.isFinite(windowSize) || windowSize < 0) return false;
        return candidate < (current - windowSize);
    } catch (_) {
        return false;
    }
}

function getCycleInfo() {
    let nextId = 1;
    let durationStr = 'N/A';
    const now = new Date();

    // 1. Try State File (Fast & Persistent)
    try {
        if (fs.existsSync(STATE_FILE)) {
            const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
            if (state.lastCycleId) {
                nextId = state.lastCycleId + 1;
                
                // Calculate duration since last cycle
                if (state.lastUpdate) {
                    const diff = now.getTime() - new Date(state.lastUpdate).getTime();
                    const mins = Math.floor(diff / 60000);
                    const secs = Math.floor((diff % 60000) / 1000);
                    durationStr = `${mins}m ${secs}s`;
                }

                // Auto-increment and save
                state.lastCycleId = nextId;
                state.lastUpdate = now.toISOString();
                fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
                return { id: nextId, duration: durationStr };
            }
        }
    } catch (e) {}

    // 2. Fallback: MEMORY.md (Legacy/Seed)
    let maxId = 0;
    try {
        const memPath = path.resolve(__dirname, '../../MEMORY.md');
        if (fs.existsSync(memPath)) {
            const memContent = fs.readFileSync(memPath, 'utf8');
            const matches = [...memContent.matchAll(/Cycle #(\d+)/g)];
            for (const match of matches) {
                const id = parseInt(match[1]);
                if (id > maxId) maxId = id;
            }
        }
    } catch (e) {}

    // Initialize State File if missing
    nextId = (maxId > 0 ? maxId : Math.floor(Date.now() / 1000)) + 1;
    try {
        fs.writeFileSync(STATE_FILE, JSON.stringify({
            lastCycleId: nextId,
            lastUpdate: now.toISOString()
        }, null, 2));
    } catch(e) {}

    return { id: nextId, duration: 'First Run' };
}

async function findEvolutionGroup() {
    try {
        let pageToken = '';
        do {
            const url = `https://open.feishu.cn/open-apis/im/v1/chats?page_size=100${pageToken ? `&page_token=${pageToken}` : ''}`;
            const res = await fetchWithAuth(url, { method: 'GET' });
            const data = await res.json();
            
            if (data.code !== 0) {
                console.warn(`[Wrapper] List Chats failed: ${data.msg}`);
                return null;
            }

            if (data.data && data.data.items) {
                const group = data.data.items.find(c => c.name && c.name.includes('🧬'));
                if (group) {
                    // console.log(`[Wrapper] Found Evolution Group: ${group.name} (${group.chat_id})`);
                    return group.chat_id;
                }
            }
            
            pageToken = data.data.page_token;
        } while (pageToken);
    } catch (e) {
        console.warn(`[Wrapper] Group lookup error: ${e.message}`);
    }
    return null;
}

async function sendReport(options) {
    // Resolve content
    let content = options.status || options.content || '';
    if (options.file) {
        try {
            content = fs.readFileSync(options.file, 'utf8');
        } catch (e) {
            console.error(`Failed to read file: ${options.file}`);
            throw e;
        }
    }

    if (!content && !options.dashboard) {
        throw new Error('Must provide --status or --file (unless --dashboard is set)');
    }

    // Prepare Title
    const cycleInfo = options.cycle ? { id: options.cycle, duration: 'Manual' } : getCycleInfo();
    const cycleId = cycleInfo.id;
    if (isStaleCycleReport(cycleId)) {
        console.warn(`[Wrapper] Suppressing stale report for cycle #${cycleId}.`);
        return;
    }
    let title = options.title;

    if (!title) {
        // Default title based on lang
        if (options.lang === 'cn') {
            title = `🧬 进化 #${cycleId} 日志`;
        } else {
            title = `🧬 Evolution #${cycleId} Log`;
        }
    }

    // Resolve Target
    const MASTER_ID = process.env.OPENCLAW_MASTER_ID || '';
    let target = options.target;

    // Priority: CLI Target > Evolution Group (🧬) > Master ID
    if (!target) {
        target = await findEvolutionGroup();
    }
    
    if (!target) {
        console.warn('[Wrapper] No Evolution Group (🧬) found. Explicitly falling back to Master ID.');
        target = MASTER_ID;
    }

    if (!target) {
        throw new Error('No target ID found (Env OPENCLAW_MASTER_ID missing and no --target).');
    }

    // --- DASHBOARD SNAPSHOT ---
    let dashboardMd = '';
    const stats = getDashboardStats();
    if (stats) {
        const trend = stats.recent.map(e => `${e.intent}${e.status}`).join(' ');
        
        dashboardMd = `\n\n---
**📊 Dashboard Snapshot**
- **Success Rate:** ${stats.successRate}% (${stats.total} Cycles)
- **Breakdown:** ✨${stats.intents.innovate} 🔧${stats.intents.repair} ⚡${stats.intents.optimize}
- **Avg Blast:** ${stats.avgFiles} files / ${stats.avgLines} lines
- **Avg Rigor:** ${stats.avgRigor || 'N/A'} (0.0-1.0)
- **Recent:** ${trend}`;
    }
    // --- END SNAPSHOT ---

    try {
        console.log(`[Wrapper] Reporting Cycle #${cycleId} to ${target}...`);
        
        let procCount = '?';
        let memUsage = '?';
        let uptime = '?';
        let loadAvg = '?';
        let diskUsage = '?';

        try {
            procCount = sysMon.getProcessCount();
            memUsage = Math.round(process.memoryUsage().rss / 1024 / 1024);
            // Use wrapper daemon uptime, not this short-lived report process uptime.
            const wrapperPidFile = path.resolve(__dirname, '../../memory/evolver_wrapper.pid');
            if (fs.existsSync(wrapperPidFile)) {
                const pid = parseInt(fs.readFileSync(wrapperPidFile, 'utf8').trim(), 10);
                if (Number.isFinite(pid) && pid > 1) {
                    try {
                        const pidPath = `/proc/${pid}`;
                        if (fs.existsSync(pidPath)) {
                            // Use stat.ctimeMs which is creation time on Linux /proc
                            const stats = fs.statSync(pidPath);
                            uptime = Math.floor((Date.now() - stats.ctimeMs) / 1000);
                        } else {
                            // Fallback to exec if /proc missing (non-Linux?)
                            const et = execSync(`ps -o etimes= -p ${pid}`, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true }).trim();
                            const secs = parseInt(et, 10);
                            if (Number.isFinite(secs) && secs >= 0) uptime = secs;
                        }
                    } catch (_) {
                        uptime = Math.round(process.uptime());
                    }
                }
            }
            if (uptime === '?') uptime = Math.round(process.uptime());
            loadAvg = os.loadavg()[0].toFixed(2);
            diskUsage = sysMon.getDiskUsage('/');
        } catch(e) {
            console.warn('[Wrapper] Stats collection failed:', e.message);
        }

        // --- ERROR LOG CHECK ---
        let errorAlert = '';
        try {
            const evolverDirName = ['private-evolver', 'evolver', 'capability-evolver'].find(d => fs.existsSync(path.resolve(__dirname, `../${d}/index.js`))) || 'private-evolver';
            const evolverDir = path.resolve(__dirname, `../${evolverDirName}`);
            const errorLogPath = path.join(evolverDir, 'evolution_error.log');

            if (fs.existsSync(errorLogPath)) {
                const stats = fs.statSync(errorLogPath);
                const now = new Date();
                const diffMs = now - stats.mtime;
                
                if (diffMs < 10 * 60 * 1000) {
                    const lastLine = (sysMon.getLastLine(errorLogPath) || '').substring(0, 200);
                    errorAlert = `\n\n⚠️ **CRITICAL ALERT**: System reported a failure ${(diffMs/1000/60).toFixed(1)}m ago.\n> ${lastLine}`;
                }
            }
        } catch (e) {}

        // --- SKILL HEALTH CHECK ---
        let healthAlert = '';
        try {
            const issues = runSkillsMonitor();
            if (issues && issues.length > 0) {
                healthAlert = `\n\n🚨 **SKILL HEALTH WARNING**: ${issues.length} skill(s) broken.\n`;
                issues.slice(0, 3).forEach(issue => {
                    healthAlert += `> **${issue.name}**: ${issue.issues.join(', ')}\n`;
                });
                if (issues.length > 3) healthAlert += `> ...and ${issues.length - 3} more.`;
            }
        } catch (e) {
            console.warn('[Wrapper] Skill monitor failed:', e.message);
        }

        const isChineseReport = options.lang === 'cn';

        const labels = isChineseReport
            ? {
                proc: '进程',
                mem: '内存',
                up: '运行',
                load: '负载',
                disk: '磁盘',
                loop: '循环',
                skills: '技能',
                ok: '正常',
                loopOn: '运行中',
                loopOff: '已停止'
            }
            : {
                proc: 'Proc',
                mem: 'Mem',
                up: 'Up',
                load: 'Load',
                disk: 'Disk',
                loop: 'Loop',
                skills: 'Skills',
                ok: 'OK',
                loopOn: 'ON',
                loopOff: 'OFF'
            };

        // --- LOOP STATUS CHECK ---
        let loopStatus = 'UNKNOWN';
        try {
            // Mock status call to avoid exec/logs spam if possible, or use status --json?
            // Actually lifecycle.status() prints to console. We should export a helper.
            // For now, assume if pid file exists, it's running.
            const PID_FILE = path.resolve(__dirname, '../../memory/evolver_wrapper.pid');
            if (fs.existsSync(PID_FILE)) {
                 try { process.kill(parseInt(fs.readFileSync(PID_FILE, 'utf8').trim(), 10), 0); loopStatus = labels.loopOn; } 
                 catch(e) { loopStatus = labels.loopOff; }
            } else {
                 loopStatus = labels.loopOff;
            }
        } catch (e) {
            loopStatus = `${labels.loopOff} (?)`;
        }

        let footerStats = `${labels.proc}: ${procCount} | ${labels.mem}: ${memUsage}MB | ${labels.up}: ${uptime}s | ${labels.load}: ${loadAvg} | ${labels.disk}: ${diskUsage} | 🔁 ${labels.loop}: ${loopStatus}`;
        if (!healthAlert) footerStats += ` | 🛡️ ${labels.skills}: ${labels.ok}`;

        const finalContent = `${content}${errorAlert}${healthAlert}${dashboardMd}`;

        // --- DASHBOARD MODE ---
        let cardData = null;
        if (options.dashboard) {
            console.log('[Wrapper] Generating rich dashboard card...');
            // Normalize stats if null (stats is already defined above from getDashboardStats())
            const safeStats = stats || { total: 0, successRate: '0.0', intents: { innovate:0, repair:0, optimize:0 }, recent: [] };
            
            cardData = generateDashboardCard(
                safeStats,
                {
                    proc: procCount, mem: memUsage, uptime: uptime, load: loadAvg, disk: diskUsage, loopStatus: loopStatus,
                    errorAlert: errorAlert, healthAlert: healthAlert
                },
                { id: cycleId, duration: cycleInfo.duration }
            );
        }

        // --- DEDUP CHECK ---
        var statusHash = crypto.createHash('md5').update(options.status || '').digest('hex').slice(0, 12);
        var reportKey = `${cycleId}:${target}:${title}:${statusHash}`;
        if (isDuplicateReport(reportKey)) {
            console.log('[Wrapper] Duplicate report suppressed.');
            return;
        }

    // Auto-detect color from status text if not explicitly overridden (or if default blue)
    let headerColor = options.color || 'blue';
    if (headerColor === 'blue') {
        const statusUpper = (options.status || '').toUpperCase();
        if (statusUpper.includes('[SUCCESS]') || statusUpper.includes('[成功]')) headerColor = 'green';
        else if (statusUpper.includes('[FAILED]') || statusUpper.includes('[失败]')) headerColor = 'red';
        else if (statusUpper.includes('[WARNING]') || statusUpper.includes('[警告]')) headerColor = 'orange';
        else if (statusUpper.includes('[INNOVATE]') || statusUpper.includes('[创新]')) headerColor = 'purple';
        else if (statusUpper.includes('[REPAIR]') || statusUpper.includes('[修复]')) headerColor = 'orange'; // Repair is often a fix/warning state
        else if (statusUpper.includes('[OPTIMIZE]') || statusUpper.includes('[优化]')) headerColor = 'blue';
        else if (statusUpper.includes('SUCCESS')) headerColor = 'green'; // Fallback for plain SUCCESS
        else if (statusUpper.includes('FAILED')) headerColor = 'red'; // Fallback for plain FAILED
        else if (statusUpper.includes('ERROR')) headerColor = 'red'; // Fallback for error messages
    }

        // Title is passed as-is from caller (already contains 🧬).
        // No extra emoji in the title -- result goes in the body.

        if (options.dashboard && cardData) {
            await sendCard({
                target: target,
                title: title,
                cardData: cardData,
                note: footerStats,
                color: headerColor
            });
        } else {
            await sendCard({
                target: target,
                title: title,
                text: finalContent,
                note: footerStats,
                color: headerColor
            });
        }
        
        console.log('[Wrapper] Report sent successfully.');

        try {
            const LOG_FILE = path.resolve(__dirname, '../../logs/evolution_reports.log');
            if (!fs.existsSync(path.dirname(LOG_FILE))) {
                fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
            }
            fs.appendFileSync(LOG_FILE, `[${new Date().toISOString()}] Cycle #${cycleId} - Status: SUCCESS - Target: ${target} - Duration: ${cycleInfo.duration}\n`);
        } catch (logErr) {
            console.warn('[Wrapper] Failed to write to local log:', logErr.message);
        }
    } catch (e) {
        console.error('[Wrapper] Report failed:', e.message);
        throw e;
    }
}

// CLI Logic
if (require.main === module) {
    program
      .option('-s, --status <text>', 'Status text/markdown content')
      .option('--content <text>', 'Alias for --status (compatibility)')
      .option('-f, --file <path>', 'Path to markdown file content')
      .option('-c, --cycle <id>', 'Evolution Cycle ID')
      .option('--title <text>', 'Card Title override')
      .option('--color <color>', 'Header color (blue/red/green/orange)', 'blue')
      .option('--target <id>', 'Target User/Chat ID')
      .option('--lang <lang>', 'Language (en|cn)', 'en')
      .option('--dashboard', 'Send rich dashboard card instead of plain text')
      .parse(process.argv);

    const options = program.opts();
    sendReport(options).catch(err => {
        console.error('[Wrapper] Report failed (non-fatal):', err.message);
        // Don't fail the build/cycle just because reporting failed (e.g. permission issues)
        process.exit(0);
    });
}

module.exports = { sendReport };
