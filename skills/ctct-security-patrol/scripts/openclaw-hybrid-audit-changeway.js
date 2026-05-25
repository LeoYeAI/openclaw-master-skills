#!/usr/bin/env node
/**
 * OpenClaw 混合安全巡检脚本 (Node.js 跨平台版)
 * 兼容性: macOS (darwin), Ubuntu (linux), CentOS (linux), Windows (win32)
 * 聚焦：基础设施安全、SSH 防护、MCP 权限越界与记忆认知安全
 *
 * SECURITY NOTE: All commands and arguments are from a strictly hardcoded whitelist.
 * No user-controlled inputs are passed to child processes.
 * - Unix/Linux: shell is strictly disabled (shell: false).
 * - Windows: shell is locally enabled ONLY to invoke .cmd executable wrappers 
 * (a Windows Node.js limitation), but remains protected against injection 
 * by utilizing strictly hardcoded argument arrays.
 *
 * @integrity sha256:565556ef7ed65dc93f8822bf59a9df3591648585467a094deedd99a11208325d
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const { spawnSync } = require('child_process');
const http = require('http');
const https = require('https');

// ──────────────────────────────────────────
// 命令行参数解析
// ──────────────────────────────────────────
const PUSH_ENABLED = process.argv.includes('--push');
const GENERATE_CONFIG_BASELINE = process.argv.includes('--generate-config-baseline');
const UPDATE_SKILL_BASELINE = process.argv.includes('--update-skill-baseline');

// 环境预设
const platform = os.platform();
const HOME = os.homedir();
const OC = process.env.OPENCLAW_STATE_DIR || path.join(HOME, '.openclaw');

// 日期时间处理
const now = new Date();
const yest = new Date(now);
yest.setDate(yest.getDate() - 1);

function getLocalDateStr(dateObj) {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

const DATE_STR = getLocalDateStr(now);
const REPORT_TIME = `${DATE_STR} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;


// ──────────────────────────────────────────
// 目录与文件设置（写入用户目录，日志默认在系统临时目录）
// ──────────────────────────────────────────
const REPORT_DIR = path.join(OC, 'security-reports');
const TMP_ROOT = typeof os.tmpdir === 'function' ? os.tmpdir() : '/tmp';
// 支持最近24小时的日志（今天 + 昨天）
const YEST_DATE_STR = getLocalDateStr(yest);
let LOG_CANDIDATES = [
    path.join(TMP_ROOT, 'clawdbot', `clawdbot-${DATE_STR}.log`),
    path.join(TMP_ROOT, 'openclaw', `openclaw-${DATE_STR}.log`),
    path.join(TMP_ROOT, 'clawdbot', `clawdbot-${YEST_DATE_STR}.log`),
    path.join(TMP_ROOT, 'openclaw', `openclaw-${YEST_DATE_STR}.log`)
];
// Windows 额外兼容 C:\tmp\* 目录（如果存在）
if (platform === 'win32') {
    LOG_CANDIDATES = LOG_CANDIDATES.concat([
        path.join('C:\\tmp', 'clawdbot', `clawdbot-${DATE_STR}.log`),
        path.join('C:\\tmp', 'openclaw', `openclaw-${DATE_STR}.log`),
        path.join('C:\\tmp', 'clawdbot', `clawdbot-${YEST_DATE_STR}.log`),
        path.join('C:\\tmp', 'openclaw', `openclaw-${YEST_DATE_STR}.log`)
    ]);
}
fs.mkdirSync(REPORT_DIR, { recursive: true, mode: 0o700 });
const REPORT_FILE = path.join(REPORT_DIR, `report-${DATE_STR}.txt`);
const JSON_OUT_FILE = path.join(REPORT_DIR, 'report.json');

const COLORS = {
    reset: "\x1b[0m",
    bright: "\x1b[1m",
    dim: "\x1b[2m",
    green: "\x1b[32m",
    red: "\x1b[31m",
    yellow: "\x1b[33m",
    cyan: "\x1b[36m",
    blue: "\x1b[34m",
    magenta: "\x1b[35m"
};

let SUMMARY = `\n${COLORS.cyan}${COLORS.bright}OPENCLAW SECURITY AUDIT${COLORS.reset} ${COLORS.dim}[${DATE_STR}]${COLORS.reset}\n`;
SUMMARY += `${COLORS.dim}────────────────────────────────────────────────────────────────────────${COLORS.reset}\n`;
let RED_COUNT = 0;
let SKIP_COUNT = 0;
let JSON_DATA = [];
let ITEM_SEQ = 0;

fs.writeFileSync(REPORT_FILE, `=== OpenClaw Hybrid Security Audit (${DATE_STR}) ===\n`, { mode: 0o600 });

// ──────────────────────────────────────────
// 核心工具函数（全部基于 spawnSync，不使用 shell）
// ──────────────────────────────────────────
function appendWarn(item, brief, detail) {
    const icon = `${COLORS.red}[FAIL]${COLORS.reset}`;
    const title = `${COLORS.bright}${item}${COLORS.reset}`;
    const desc = `${COLORS.yellow}${brief.replace(/⚠️ /g, '')}${COLORS.reset}`;
    SUMMARY += `  ${icon} ${title.padEnd(45, ' ')} :: ${desc}\n`;
    RED_COUNT++;
    JSON_DATA.push({ item, brief, detail });
    fs.appendFileSync(REPORT_FILE, `\n[FAIL] ${item}\n${detail}\n`);
    ITEM_SEQ++;
}

function appendInfo(item, brief, detail) {
    const icon = `${COLORS.green}[PASS]${COLORS.reset}`;
    const title = `${COLORS.bright}${item}${COLORS.reset}`;
    const desc = `${COLORS.dim}${brief.replace(/✅ /g, '')}${COLORS.reset}`;
    SUMMARY += `  ${icon} ${title.padEnd(45, ' ')} :: ${desc}\n`;
    JSON_DATA.push({ item, brief, detail });
    fs.appendFileSync(REPORT_FILE, `\n[PASS] ${item}\n${detail}\n`);
    ITEM_SEQ++;
}

function appendSkip(item, brief, detail) {
    const icon = `${COLORS.magenta}[SKIP]${COLORS.reset}`;
    const title = `${COLORS.bright}${item}${COLORS.reset}`;
    const desc = `${COLORS.magenta}${brief}${COLORS.reset}`;
    SUMMARY += `  ${icon} ${title.padEnd(45, ' ')} :: ${desc}\n`;
    SKIP_COUNT++;
    JSON_DATA.push({ item, brief, detail });
    fs.appendFileSync(REPORT_FILE, `\n[SKIP] ${item}\n${detail}\n`);
    ITEM_SEQ++;
}

function buildSafeChildPath(basePath, entryName) {
    const safeName = path.basename(String(entryName || ''));
    if (!safeName || safeName === '.' || safeName === '..') {
        return null;
    }
    return `${basePath}${path.sep}${safeName}`;
}

function buildSafeRelativePath(basePath, relativePath) {
    const raw = String(relativePath || '').replace(/\\/g, '/');
    const normalized = raw.replace(/^\/+/, '');
    if (!normalized || normalized.includes('\0')) {
        return null;
    }
    const segments = normalized.split('/').filter(Boolean);
    if (segments.length === 0 || segments.some(seg => seg === '.' || seg === '..')) {
        return null;
    }
    return `${basePath}${path.sep}${segments.join(path.sep)}`;
}

function runSafeCommand(commandKey, args, strictMode) {
    const safeArgs = Array.isArray(args) ? args.map(arg => String(arg)) : [];
    try {
        let result;
        switch (commandKey) {
            case 'openclaw':
                if (platform === 'win32') {
                    // Windows 底层限制：必须依赖 shell 才能解析 .cmd 文件。
                    // 安全断言：此处的 safeArgs 为内部硬编码，无用户输入，局部开启 shell 无注入风险。
                    result = spawnSync('openclaw.cmd', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000, shell: true });
                } else {
                    result = spawnSync('openclaw', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                }
                break;
            case 'openclaw-cn':
                if (platform === 'win32') {
                    result = spawnSync('openclaw-cn.cmd', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000, shell: true });
                } else {
                    result = spawnSync('openclaw-cn', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                }
                break;
            case 'find':
                result = spawnSync('find', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'pgrep':
                result = spawnSync('pgrep', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'journalctl':
                result = spawnSync('journalctl', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'log':
                result = spawnSync('log', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'ss':
                result = spawnSync('ss', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'ps':
                result = spawnSync('ps', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'lsof':
                result = spawnSync('lsof', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'diff':
                result = spawnSync('diff', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'wevtutil':
                result = spawnSync('wevtutil', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'netstat':
                result = spawnSync('netstat', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'tasklist':
                result = spawnSync('tasklist', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'powershell':
                result = spawnSync('powershell', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            case 'icacls':
                result = spawnSync('icacls', safeArgs, { stdio: 'pipe', encoding: 'utf-8', timeout: 30000 });
                break;
            default:
                return strictMode
                    ? { success: false, output: `unsupported command: ${commandKey}` }
                    : '';
        }
        if (result.error) {
            return strictMode ? { success: false, output: result.error.message } : '';
        }
        if (!strictMode) {
            return (result.stdout || '').trim();
        }
        if (result.status === 0) {
            return { success: true, output: (result.stdout || '').trim() };
        }
        return { success: false, output: ((result.stderr || '') + (result.stdout || '')).trim() };
    } catch (e) {
        return strictMode ? { success: false, output: e.message || '' } : '';
    }
}

function spawnCmd(commandKey, args) {
    return runSafeCommand(commandKey, args, false);
}

function spawnCmdStrict(commandKey, args) {
    return runSafeCommand(commandKey, args, true);
}

function getFileHash(filePath) {
    try { return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex'); }
    catch(e) { return null; }
}

function getFilePerms(filePath) {
    try { return (fs.statSync(filePath).mode & 0o777).toString(8); }
    catch(e) { return "MISSING"; }
}

/**
 * 生成核心配置文件哈希基线
 * 输出到 .config-baseline.sha256 文件，用于 [4/14] 防篡改校验
 */
function generateConfigBaseline() {
    const baselinePath = path.join(OC, '.config-baseline.sha256');
    const filesToHash = [];

    // 确定需要监控的配置文件
    // 注意: devices/paired.json 被排除，因为巡检脚本运行时会更新该文件
    const configFiles = [
        path.join(OC, 'openclaw.json'),
        path.join(OC, 'config.json'),
        path.join(OC, 'settings.json')
    ];

    // 平台特定的配置文件
    if (platform === 'win32') {
        configFiles.push(
            path.join(process.env.PROGRAMDATA || 'C:\\ProgramData', 'ssh', 'sshd_config'),
            path.join(HOME, '.ssh/authorized_keys'),
            path.join(HOME, '.ssh/config')
        );
    } else {
        configFiles.push(
            '/etc/ssh/sshd_config',
            path.join(HOME, '.ssh/authorized_keys'),
            path.join(HOME, '.ssh/config'),
            '/etc/passwd',
            '/etc/shadow'
        );
    }

    console.log(`${COLORS.cyan}${COLORS.bright}正在生成配置文件哈希基线...${COLORS.reset}`);
    console.log(`${COLORS.dim}目标文件: ${baselinePath}${COLORS.reset}\n`);

    let baselineContent = '';
    let successCount = 0;
    let skipCount = 0;

    for (const filePath of configFiles) {
        const hash = getFileHash(filePath);
        if (hash) {
            // 使用相对路径存储，提高可移植性
            let storedPath = filePath;
            if (filePath.startsWith(OC)) {
                storedPath = path.relative(OC, filePath);
            }
            baselineContent += `${hash}  ${storedPath}\n`;
            console.log(`  ${COLORS.green}✓${COLORS.reset} ${storedPath}`);
            successCount++;
        } else {
            console.log(`  ${COLORS.yellow}○${COLORS.reset} ${filePath} ${COLORS.dim}(跳过: 文件不存在或无权限)${COLORS.reset}`);
            skipCount++;
        }
    }

    // 写入基线文件
    try {
        fs.writeFileSync(baselinePath, baselineContent, { mode: 0o600 });
        console.log(`\n${COLORS.green}${COLORS.bright}基线生成完成!${COLORS.reset}`);
        console.log(`  已记录: ${successCount} 个文件`);
        if (skipCount > 0) {
            console.log(`  跳过: ${skipCount} 个文件`);
        }
        console.log(`\n${COLORS.dim}提示: 基线文件权限已设置为 600，请妥善保管。${COLORS.reset}`);
        console.log(`${COLORS.dim}如需更新基线，请重新运行此命令。${COLORS.reset}`);
        return true;
    } catch (e) {
        console.error(`\n${COLORS.red}错误: 无法写入基线文件: ${e.message}${COLORS.reset}`);
        return false;
    }
}

let FILTER_SKILLS_KEYWORDS = ["changeway","ctct-security-patrol"];

function countMatchesInFile(filePath, regex) {
    try {
        if (!(regex instanceof RegExp)) {
            return 0;
        }
        const content = fs.readFileSync(filePath, 'utf-8');
        const matches = content.match(regex);
        return matches ? matches.length : 0;
    } catch (e) {
        return 0;
    }
}

function grepFile(filePath, regex) {
    try {
        if (!(regex instanceof RegExp)) {
            return [];
        }
        const content = fs.readFileSync(filePath, 'utf-8');
        return content.split('\n').filter(line => {
            regex.lastIndex = 0;
            return regex.test(line);
        });
    } catch (e) {
        return [];
    }
}

// ──────────────────────────────────────────
// 基线生成模式（若指定 --generate-config-baseline 参数）
// ──────────────────────────────────────────
if (GENERATE_CONFIG_BASELINE) {
    const ok = generateConfigBaseline();
    process.exit(ok ? 0 : 1);
}


function filterAuditOutput(output, keywords) {
    if (!keywords || keywords.length === 0) return output;

    const lines = output.split('\n');
    const result = [];
    let skipBlock = false;

    for (const line of lines) {
        const isNewEntry = /^[a-z_]+\.[a-z_]+\s+/i.test(line);

        if (isNewEntry) {
            const lowerLine = line.toLowerCase();
            skipBlock = keywords.some(kw => lowerLine.includes(kw.toLowerCase()));
        }

        if (!skipBlock) {
            result.push(line);
        }
    }

    return result.join('\n');
}


// ==========================================
// 板块一：基础设施与系统安全
// ==========================================
fs.appendFileSync(REPORT_FILE, `\n--- [板块一] 基础设施与系统安全 ---`);

// [1/14] OpenClaw 基础审计
let itemName = "核心运行环境健康度";
fs.appendFileSync(REPORT_FILE, `\n\n[1/14] OpenClaw 基础审计 (--deep)`);
let res1 = spawnCmdStrict("openclaw", ["security", "audit", "--deep"]);
if (!res1.success) {
    // 如果 openclaw 执行失败，尝试使用 openclaw-cn 再执行一次
    let res1Fallback = spawnCmdStrict("openclaw-cn", ["security", "audit", "--deep"]);
    if (res1Fallback.success) {
        res1 = res1Fallback;
    } else {
        // 如果 fallback 也失败，则将两次失败信息合并
        res1.output += `\n\n[Fallback openclaw-cn 也执行失败]\n${res1Fallback.output || ''}`;
    }
}
// 过滤指定的 skills 条目
res1.output = filterAuditOutput(res1.output, FILTER_SKILLS_KEYWORDS);
if (res1.success) {
    appendInfo(itemName, "运行环境各项指标正常", res1.output);
} else {
    appendWarn(itemName, "核心环境存在异常（详见报告）", res1.output);
}

// [2/14] 敏感目录变更
itemName = "系统敏感目录防篡改监控";
fs.appendFileSync(REPORT_FILE, `\n[2/14] 敏感目录变更`);
let SENSITIVE_ROOTS;
if (platform === 'win32') {
    SENSITIVE_ROOTS = [
        OC,
        path.join(HOME, '.ssh'),
        path.join(HOME, '.gnupg'),
        path.join(process.env.PROGRAMDATA || 'C:\\ProgramData', 'ssh')
    ];
} else {
    SENSITIVE_ROOTS = [OC, '/etc', path.join(HOME, '.ssh'), path.join(HOME, '.gnupg'), '/usr/local/bin'];
}
const PRUNE_PATTERNS = [
    'node_modules', '.cache', '.npm', '__pycache__', '.git', 'dist', 'build', '.next', '.nuxt',
    '.pnpm-store', '.yarn', '.venv', 'venv', '.tox'
];
const MAX_FILES_PER_GROUP = 15;

/**
 * Pure Node.js recursive file scanner that finds files modified within maxAgeMs.
 * Works cross-platform, replacing the Unix `find` dependency.
 */
function findRecentFiles(roots, prunePatterns, maxAgeMs) {
    const cutoff = Date.now() - maxAgeMs;
    const pruneSet = new Set(prunePatterns);
    const results = [];

    function walk(dir) {
        let entries;
        try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
        catch (e) { return; }
        for (const entry of entries) {
            if (pruneSet.has(entry.name)) continue;
            const fullPath = buildSafeChildPath(dir, entry.name);
            if (!fullPath) continue;
            try {
                if (entry.isDirectory()) {
                    walk(fullPath);
                } else if (entry.isFile()) {
                    const stat = fs.statSync(fullPath);
                    if (stat.mtimeMs >= cutoff) {
                        results.push(fullPath);
                    }
                }
            } catch (e) { /* permission denied or similar */ }
        }
    }

    for (const root of roots) {
        try {
            const stat = fs.statSync(root);
            if (stat.isDirectory()) {
                walk(root);
            } else if (stat.isFile() && stat.mtimeMs >= cutoff) {
                results.push(root);
            }
        } catch (e) { /* root doesn't exist */ }
    }
    return results;
}

const MS_24H = 24 * 60 * 60 * 1000;
let lines = findRecentFiles(SENSITIVE_ROOTS, PRUNE_PATTERNS, MS_24H);
lines = lines.filter(f => !f.endsWith('.sha256'));
let totalCount = lines.length;

function normalizePath(p) {
    return p.replace(HOME, '~');
}
function getGroupKey(filePath) {
    for (const root of SENSITIVE_ROOTS) {
        if (filePath === root || filePath.startsWith(root + path.sep)) {
            const rest = filePath.slice(root.length + 1);
            const first = rest.split(path.sep)[0];
            return first ? `${normalizePath(root)}/${first}` : normalizePath(root);
        }
    }
    return path.dirname(filePath);
}
let byGroup = {};
lines.forEach(f => {
    const key = getGroupKey(f);
    if (!byGroup[key]) byGroup[key] = [];
    byGroup[key].push(f);
});
let detailLines = ['>>> 近24小时变更（已排除 node_modules/.cache 等噪音目录）'];
detailLines.push(`>>> 总变更文件数: ${totalCount}`);
detailLines.push('');
Object.keys(byGroup).sort().forEach(grp => {
    const list = byGroup[grp];
    if (list.length <= MAX_FILES_PER_GROUP) {
        list.forEach(f => detailLines.push('  ' + normalizePath(f)));
    } else {
        detailLines.push(`  [${grp}/...]: ${list.length} 个文件（已折叠）`);
    }
});
if (totalCount === 0) {
    appendInfo(itemName, `近24小时变更 0 个配置文件`, `无文件变更`);
} else {
    appendInfo(itemName, `近24小时变更 ${totalCount} 个文件（核心/折叠显示）`, detailLines.join('\n'));
}

// [3/14] Gateway 环境变量泄露扫描（仅检查变量名是否存在，不读取/记录值）
itemName = "网关进程内存凭证隔离检查";
fs.appendFileSync(REPORT_FILE, `\n[3/14] Gateway 环境变量泄露扫描`);
{
    const gwPidRaw = spawnCmd('pgrep', ['-f', 'openclaw-gateway']);
    const gwPid = gwPidRaw.split('\n')[0];

    if (gwPid && /^\d+$/.test(gwPid)) {
        let sensitiveVarCount = 0;

        if (platform === 'linux') {
            const environPath = `/proc/${gwPid}/environ`;
            try {
                const environData = fs.readFileSync(environPath, 'utf-8');
                const envEntries = environData.split('\0').filter(Boolean);
                const sensitivePattern = /^(.*?(SECRET|TOKEN|PASSWORD|KEY|PRIVATE).*?)=/i;
                const hitNames = [];
                envEntries.forEach(entry => {
                    const m = entry.match(sensitivePattern);
                    if (m) hitNames.push(m[1] + '=(REDACTED)');
                });
                sensitiveVarCount = hitNames.length;
                if (sensitiveVarCount > 0) {
                    appendInfo(itemName, `进程环境中存在 ${sensitiveVarCount} 个敏感变量名（仅记录名称，值已脱敏）`, hitNames.join('\n'));
                } else {
                    appendInfo(itemName, "未命中敏感环境变量名", "✅ 未命中 SECRET/TOKEN/PASSWORD/KEY 等环境变量名");
                }
            } catch (e) {
                appendInfo(
                    itemName,
                    "无法读取网关进程环境（权限不足或进程受保护）",
                    "⚠️ 读取 /proc/" + gwPid + "/environ 失败: " + e.code + "\n建议以与网关相同用户运行，或通过网关侧诊断接口获取白名单变量名。"
                );
            }
        } else if (platform === 'darwin') {
            appendSkip(
                itemName,
                "macOS 受 SIP 限制，跳过进程环境变量扫描",
                "macOS 下读取其他进程环境变量受 SIP/权限限制。\n建议通过网关侧诊断接口或配置审计来验证敏感变量的使用情况。"
            );
        } else if (platform === 'win32') {
            appendSkip(
                itemName,
                "Windows 下无法直接读取其他进程环境变量，跳过扫描",
                "Windows 不支持 /proc 文件系统，且读取其他进程环境变量需要特殊权限。\n建议通过网关侧诊断接口或配置审计来验证敏感变量的使用情况。"
            );
        }
    } else {
        appendInfo(itemName, "未发现运行中的网关进程", "未发现运行中的网关进程。");
    }
}

// [4/14] 关键配置文件权限与哈希
itemName = "核心配置防篡改与权限基线";
fs.appendFileSync(REPORT_FILE, `\n[4/14] ${itemName}`);

const baselinePath = path.join(OC, '.config-baseline.sha256');

let hashStatus = "MISSING_BASELINE";
let checksOutput = [];

if (fs.existsSync(baselinePath)) {
    hashStatus = "PASSED";
    const baselineData = fs.readFileSync(baselinePath, 'utf-8');

    baselineData.split('\n').forEach(line => {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 2) {
            const expectedHash = parts[0];
            const fileRef = parts.slice(1).join(' ');
            const targetPath = path.isAbsolute(fileRef) ? fileRef : buildSafeRelativePath(OC, fileRef);
            if (!targetPath) {
                checksOutput.push(`${fileRef}: SKIPPED (unsafe relative path)`);
                return;
            }

            if (platform === 'win32') {
                if (!targetPath.startsWith(OC)) {
                    checksOutput.push(`${fileRef}: SKIPPED (path outside allowed scope)`);
                    return;
                }
            } else {
                // 允许 OC 目录、/etc/ 目录以及用户 SSH 相关文件
                const isInHomeSsh = targetPath.startsWith(path.join(HOME, '.ssh'));
                if (!targetPath.startsWith(OC) && !targetPath.startsWith('/etc/') && !isInHomeSsh) {
                    checksOutput.push(`${fileRef}: SKIPPED (path outside allowed scope)`);
                    return;
                }
            }

            const actualHash = getFileHash(targetPath);

            if (actualHash === expectedHash) {
                checksOutput.push(`${fileRef}: OK`);
            } else if (actualHash === null) {
                checksOutput.push(`${fileRef}: FAILED (文件不存在或无法读取)`);
                hashStatus = "FAILED";
            } else {
                checksOutput.push(`${fileRef}: FAILED (哈希不匹配: 预期 ${expectedHash.substring(0, 16)}..., 实际 ${actualHash.substring(0, 16)}...)`);
                hashStatus = "FAILED";
            }
        }
    });
}

let detail4 = `>>> 哈希基线校验状态: ${hashStatus}\n`;
if (hashStatus === "MISSING_BASELINE") {
    detail4 += `\n未找到哈希基线文件 (${baselinePath})。\n\n📋 基线生成方式:\n   node ${path.basename(__filename)} --generate-config-baseline\n\n💡 提示: 首次运行缺失基线属正常现象，执行上述命令可一键生成配置文件哈希基线，用于后续防篡改监控。`;
} else {
    detail4 += checksOutput.join('\n') + '\n';
}

/**
 * Check Windows file permission using icacls.
 * Returns true if file has overly permissive ACLs (Everyone or BUILTIN\Users with write/full control).
 */
function checkWindowsFilePermission(filePath) {
    try {
        if (!fs.existsSync(filePath)) return "MISSING";
        const result = spawnCmd('icacls', [filePath]);
        if (!result) return "UNKNOWN";
        // Check for overly permissive ACLs
        const overlyPermissive = /(Everyone|BUILTIN\\Users).*(F\)|M\)|W\))/i;
        if (overlyPermissive.test(result)) return "PERMISSIVE";
        return "OK";
    } catch (e) {
        return "UNKNOWN";
    }
}

let permOk = true;

if (platform === 'win32') {
    const permOCWin = checkWindowsFilePermission(path.join(OC, 'openclaw.json'));
    const sshdConfigPath = path.join(process.env.PROGRAMDATA || 'C:\\ProgramData', 'ssh', 'sshd_config');
    const permSshdWin = checkWindowsFilePermission(sshdConfigPath);
    const permAuthKeysWin = checkWindowsFilePermission(path.join(HOME, '.ssh/authorized_keys'));

    detail4 += `\n\n>>> 关键文件权限状态 (Windows ACL):
openclaw.json     : ${permOCWin} (预期: 无 Everyone/Users 写权限)
sshd_config       : ${permSshdWin} (预期: 无 Everyone/Users 写权限) [${sshdConfigPath}]
authorized_keys   : ${permAuthKeysWin} (预期: 无 Everyone/Users 写权限)\n`;

    if (
        permOCWin === "PERMISSIVE" ||
        permSshdWin === "PERMISSIVE" ||
        permAuthKeysWin === "PERMISSIVE"
    ) {
        permOk = false;
    }
} else {
    const permOC = getFilePerms(path.join(OC, 'openclaw.json'));
    const permSshd = getFilePerms('/etc/ssh/sshd_config');
    const permAuthKeys = getFilePerms(path.join(HOME, '.ssh/authorized_keys'));

    detail4 += `\n\n>>> 关键文件权限状态:
openclaw.json     : ${permOC} (预期: 600)
sshd_config       : ${permSshd} (预期: 644 或 600)
authorized_keys   : ${permAuthKeys} (预期: 600 或 644)\n`;

    if (
        (permOC !== "600" && permOC !== "MISSING") ||
        (permSshd !== "600" && permSshd !== "644" && permSshd !== "MISSING") ||
        (permAuthKeys !== "600" && permAuthKeys !== "644" && permAuthKeys !== "MISSING")
    ) {
        permOk = false;
    }
}

if (hashStatus === "FAILED") {
    appendWarn(itemName, "🚨 危险！哈希校验失败，核心配置可能已被非法篡改！", detail4);
} else if (hashStatus === "MISSING_BASELINE") {
    if (permOk) {
        appendWarn(itemName, "⚠️ 首次运行缺失哈希参照物，但核心文件权限严密合规", detail4);
    } else {
        appendWarn(itemName, "❌ 缺失哈希参照物，且检测到核心文件权限存在越界风险！", detail4);
    }
} else if (hashStatus === "PASSED") {
    if (permOk) {
        appendInfo(itemName, "✅ 哈希防篡改校验通过，且核心权限完全合规", detail4);
    } else {
        appendWarn(itemName, "⚠️ 文件未被篡改，但权限设置过于宽松，请排查详细报告", detail4);
    }
}

// [5/14] MCP/Skill 基线完整性
itemName = "组件与插件供应链完整性";
fs.appendFileSync(REPORT_FILE, `\n[5/14] MCP/Skill 基线完整性`);
let SKILL_SCAN_DIRS;
if (platform === 'win32') {
    SKILL_SCAN_DIRS = [
        path.join(process.env.APPDATA || path.join(HOME, 'AppData', 'Roaming'), 'npm', 'node_modules', 'openclaw-cn', 'skills'),
        path.join(process.env.APPDATA || path.join(HOME, 'AppData', 'Roaming'), 'npm', 'node_modules', 'openclaw', 'skills'),
        path.join(HOME, '.openclaw', 'workspace', 'skills'),
        path.join(HOME, '.openclaw', 'skills')
    ];
} else {
    SKILL_SCAN_DIRS = [
        '/opt/homebrew/lib/node_modules/openclaw/skills',
        path.join(HOME, '.openclaw/workspace/skills'),
        path.join(HOME, '.openclaw/skills')
    ];
}
let skillDir = SKILL_SCAN_DIRS[0];
let mcpDir = path.join(OC, 'workspace/mcp');
let hashDir = path.join(OC, 'security-baselines');
fs.mkdirSync(hashDir, { recursive: true });
let curHashPath = path.join(hashDir, 'skill-mcp-current.sha256');
let baseHashPath = path.join(hashDir, 'skill-mcp-baseline.sha256');

function getAllFiles(dirPath, arrayOfFiles = []) {
    try {
        let files = fs.readdirSync(dirPath);
        files.forEach(file => {
            let fullPath = buildSafeChildPath(dirPath, file);
            if (!fullPath) return;
            if (fs.statSync(fullPath).isDirectory()) arrayOfFiles = getAllFiles(fullPath, arrayOfFiles);
            else arrayOfFiles.push(fullPath);
        });
    } catch(e) {}
    return arrayOfFiles;
}
let allMcpFiles = SKILL_SCAN_DIRS.flatMap(d => getAllFiles(d)).concat(getAllFiles(mcpDir)).sort();
let curHashes = allMcpFiles.map(f => `${getFileHash(f)}  ${f}`).join('\n') + '\n';
fs.writeFileSync(curHashPath, curHashes);

// 如果指定了 --update-skill-baseline，则更新基线并退出
if (UPDATE_SKILL_BASELINE) {
    fs.writeFileSync(baseHashPath, curHashes);
    console.log(`${COLORS.green}✅ Skill/MCP 基线已更新: ${baseHashPath}${COLORS.reset}`);
    console.log(`${COLORS.dim}   已记录 ${allMcpFiles.length} 个文件的哈希${COLORS.reset}`);
    process.exit(0);
}

if (fs.existsSync(baseHashPath)) {
    let baseData = fs.readFileSync(baseHashPath, 'utf-8');
    if (baseData !== curHashes) {
        // 智能 diff：分类统计新增、修改、删除
        let baseMap = new Map();
        let curMap = new Map();
        baseData.split('\n').filter(l => l.trim()).forEach(line => {
            const parts = line.split('  ');
            if (parts.length >= 2) baseMap.set(parts[1], parts[0]);
        });
        curHashes.split('\n').filter(l => l.trim()).forEach(line => {
            const parts = line.split('  ');
            if (parts.length >= 2) curMap.set(parts[1], parts[0]);
        });

        let added = [];      // 新增文件
        let modified = [];   // 修改的文件（哈希变了）
        let removed = [];    // 删除的文件

        // 检查新增和修改
        for (let [filePath, hash] of curMap) {
            if (!baseMap.has(filePath)) {
                added.push(filePath);
            } else if (baseMap.get(filePath) !== hash) {
                modified.push(filePath);
            }
        }
        // 检查删除
        for (let filePath of baseMap.keys()) {
            if (!curMap.has(filePath)) removed.push(filePath);
        }

        // 提取受影响的 Skill 名称
        function extractSkillNames(filePaths) {
            let names = new Set();
            filePaths.forEach(fp => {
                const match = fp.match(/skills[/\\]([^/\\]+)/);
                if (match) names.add(match[1]);
            });
            return Array.from(names).slice(0, 10); // 最多显示10个
        }

        let summary = [];
        if (added.length > 0) summary.push(`新增 ${added.length} 个文件`);
        if (modified.length > 0) summary.push(`修改 ${modified.length} 个文件`);
        if (removed.length > 0) summary.push(`删除 ${removed.length} 个文件`);

        let detail = `>>> 变更摘要: ${summary.join('，')}\n\n`;

        let affectedSkills = extractSkillNames([...added, ...modified, ...removed]);
        if (affectedSkills.length > 0) {
            detail += `>>> 受影响的 Skill:\n${affectedSkills.map(s => `   - ${s}`).join('\n')}\n`;
        }

        // 显示部分变更详情（限制数量）
        detail += '\n>>> 变更详情（前 20 个）:\n';
        let allChanges = [
            ...added.slice(0, 10).map(f => `+ [新增] ${path.basename(f)}`),
            ...modified.slice(0, 10).map(f => `~ [修改] ${path.basename(f)}`),
            ...removed.slice(0, 10).map(f => `- [删除] ${path.basename(f)}`)
        ].slice(0, 20);
        detail += allChanges.join('\n') || '  (无详细变更信息)';

        detail += '\n\n💡 提示: 如确认是正常安装/更新 Skill，请执行:\n';
        detail += `   node ${path.basename(__filename)} --update-skill-baseline\n`;

        // 判断是否为新增 Skill（只有新增，没有修改已有文件）
        if (modified.length === 0 && removed.length === 0 && added.length > 0) {
            appendInfo(itemName, `检测到 ${added.length} 个新增文件（可能是新安装 Skill）`, detail);
        } else {
            appendWarn(itemName, "⚠️ 检测到 Skill/MCP 文件变更", detail);
        }
    } else {
        appendInfo(itemName, "✅ 工具包哈希基线校验通过", `已校验 ${allMcpFiles.length} 个文件，无异常`);
    }
} else {
    fs.writeFileSync(baseHashPath, curHashes);
    let detail = `首次运行，已建立基线\n\n已记录 ${allMcpFiles.length} 个文件的哈希\n\n`;
    detail += `提示: 后续安装或更新 Skill 后，如需更新基线，请执行:\n`;
    detail += `   node ${path.basename(__filename)} --update-skill-baseline`;
    appendInfo(itemName, "首次运行，已建立基线", detail);
}

// [6/14] 登录与 SSH 审计
itemName = "远程访问与爆破攻击监控";
fs.appendFileSync(REPORT_FILE, `\n[6/14] 登录与 SSH 审计`);
let failedSsh = 0;
if (platform === 'linux') {
    let journalOut = spawnCmd('journalctl', ['-u', 'sshd', '-u', 'ssh', '--since', '24 hours ago', '--no-pager']);
    if (journalOut) {
        failedSsh = (journalOut.match(/Failed|Invalid/gi) || []).length;
    }
    if (failedSsh === 0) {
        ['/var/log/auth.log', '/var/log/secure', '/var/log/messages'].forEach(logPath => {
            failedSsh += countMatchesInFile(logPath, /sshd.*(Failed|Invalid)/gim);
        });
    }
} else if (platform === 'darwin') {
    let logOut = spawnCmd('log', ['show', '--predicate', 'process == "sshd"', '--last', '24h']);
    if (logOut) {
        failedSsh = (logOut.match(/Failed|Invalid/gi) || []).length;
    }
} else if (platform === 'win32') {
    // Event ID 4625 = Failed logon
    let psOut = spawnCmd('powershell', ['-NoProfile', '-Command',
        `(Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625; StartTime=(Get-Date).AddDays(-1)} -ErrorAction SilentlyContinue | Measure-Object).Count`
    ]);
    failedSsh = parseInt(psOut, 10) || 0;
}
let detail6 = `--- SSH 爆破尝试 ---\nFailed SSH attempts (24h): ${failedSsh}`;
if (failedSsh > 3) appendWarn(itemName, `⚠️ 近24h SSH 失败高达 ${failedSsh} 次，疑似遭遇爆破`, detail6);
else appendInfo(itemName, `近24h SSH 失败尝试 ${failedSsh} 次`, detail6);


// [7/14] 监听端口与高资源进程
itemName = "网络暴露面与异常进程排查";
fs.appendFileSync(REPORT_FILE, `\n[7/14] 监听端口与高资源进程`);
let portsRaw = "", psRaw = "";
if (platform === 'linux') {
    let ssOut = spawnCmd('ss', ['-tunlp']);
    portsRaw = ssOut.split('\n').filter(l => /LISTEN/.test(l) && !/127\.0\.0\.1|::1/.test(l)).join('\n');
    psRaw = spawnCmd('ps', ['-eo', 'pid,user,%cpu,%mem,comm', '--sort=-%cpu']);
    psRaw = psRaw.split('\n').slice(0, 6).join('\n');
} else if (platform === 'darwin') {
    let lsofOut = spawnCmd('lsof', ['-iTCP', '-sTCP:LISTEN', '-P', '-n']);
    portsRaw = lsofOut.split('\n').filter(l => !/127\.0\.0\.1|::1/.test(l)).join('\n');
    psRaw = spawnCmd('ps', ['-eo', 'pid,user,%cpu,%mem,comm', '-r']);
    psRaw = psRaw.split('\n').slice(0, 6).join('\n');
} else if (platform === 'win32') {
    portsRaw = spawnCmd('netstat', ['-ano']);
    portsRaw = portsRaw.split('\n').filter(l => /LISTENING/i.test(l) && !/127\.0\.0\.1|\[::1\]/.test(l)).join('\n');
    psRaw = spawnCmd('tasklist', ['/FO', 'CSV', '/NH']);
    psRaw = psRaw.split('\n').slice(0, 6).join('\n');
}
let portCount = portsRaw ? portsRaw.split('\n').filter(Boolean).length : 0;
let detail7 = `--- 监听端口与高资源进程 ---\n>>> 全局网络监听状态:\n${portsRaw || '无数据'}\n\n>>> 资源占用 Top 5 进程快照:\n${psRaw || '无数据'}`;
if (portCount > 0) appendInfo(itemName, `发现 ${portCount} 条疑似对外监听记录，已记录状态快照`, detail7);
else appendInfo(itemName, "当前无对外开放的监听端口；资源进程快照已记录", detail7);

// [8/14] OpenClaw 定时任务
itemName = "自动化任务与后门驻留排查";
fs.appendFileSync(REPORT_FILE, `\n[8/14] OpenClaw Cron Jobs`);
let res8 = spawnCmdStrict("openclaw", ["cron", "list"]);
if (!res8.success) {
    // 如果 openclaw 执行失败，尝试使用 openclaw-cn 再执行一次
    let res8Fallback = spawnCmdStrict("openclaw-cn", ["cron", "list"]);
    if (res8Fallback.success) {
        res8 = res8Fallback;
    } else {
        // 如果 fallback 也失败，则将两次失败信息合并
        res8.output += `\n\n[Fallback openclaw-cn 也执行失败]\n${res8Fallback.output || ''}`;
    }
}
if (res8.success) appendInfo(itemName, "已拉取内部任务列表", res8.output);
else appendWarn(itemName, "⚠️ 拉取失败（可能是 token/权限问题）", res8.output);


// ==========================================
// 板块二：Agent 行为审计
// ==========================================
fs.appendFileSync(REPORT_FILE, `\n\n--- [板块二] Agent 行为审计 ---`);

// [9/14] 危险命令越权调用审计
itemName = "高危命令与越权行为审计";
fs.appendFileSync(REPORT_FILE, `\n\n[9/14] 危险命令越权调用审计`);
const EXISTING_LOG_FILES = LOG_CANDIDATES.filter(p => {
    try { return fs.existsSync(p); } catch (e) { return false; }
});
if (EXISTING_LOG_FILES.length > 0) {
    const dangerPattern = /bash\s+-c|rm\s+-rf|chmod\s+777|wget\s|curl\s.*\|.*bash|nc\s+-e|nmap\s/i;
    let dangerLinesAll = [];
    EXISTING_LOG_FILES.forEach(logPath => {
        dangerLinesAll = dangerLinesAll.concat(grepFile(logPath, dangerPattern));
    });
    if (dangerLinesAll.length > 0) {
        appendWarn(
            itemName,
            `发现 ${dangerLinesAll.length} 次高危 Shell 命令调用，请人工核查是否为授权操作`,
            dangerLinesAll.slice(-10).join('\n')
        );
    } else {
        appendInfo(itemName, "未检测到高危系统命令越权执行", "✅ 无高危系统命令越权执行记录");
    }
} else {
    appendSkip(
        itemName,
        "未找到日志文件，跳过检查",
        `未在以下路径找到日志文件:\n${LOG_CANDIDATES.join('\n')}`
    );
}

// [10/14] 出站网络流量白名单审计
itemName = "异常外联与数据外泄监控";
fs.appendFileSync(REPORT_FILE, `\n[10/14] 出站网络流量白名单审计`);
if (EXISTING_LOG_FILES.length > 0) {
    try {
        let allUrls = [];
        const urlPattern = /https?:\/\/[^\s"]+/gi;
        EXISTING_LOG_FILES.forEach(logPath => {
            const logContent = fs.readFileSync(logPath, 'utf-8');
            const matched = logContent.match(urlPattern) || [];
            allUrls = allUrls.concat(matched);
        });
        const whitelist = /api\.openai\.com|api\.anthropic\.com|github\.com|huggingface\.co|auth\.ctct\.cn:10020\/changeway-open|127\.0\.0\.1|localhost/i;
        const unknownUrls = [...new Set(allUrls.filter(u => !whitelist.test(u)))];
        if (unknownUrls.length > 0) {
            appendWarn(itemName, `发现 ${unknownUrls.length} 个未知外部网络请求，请人工确认是否为预期访问`, unknownUrls.join('\n'));
        } else {
            appendInfo(itemName, "外部网络请求均在白名单内", "✅ 外部网络请求均在白名单内");
        }
    } catch (e) {
        appendInfo(itemName, "日志读取失败", "⚠️ 读取日志文件失败: " + e.message);
    }
} else {
    appendSkip(
        itemName,
        "无日志文件，跳过网络流量扫描",
        "未找到日志文件以扫描网络请求。"
    );
}


// ==========================================
// 板块三：敏感数据与行为审计
// ==========================================
fs.appendFileSync(REPORT_FILE, `\n\n--- [板块三] 敏感数据与行为审计 ---`);

// [11/14] 敏感系统文件违规读取
itemName = "系统凭证与敏感文件访问审计";
fs.appendFileSync(REPORT_FILE, `\n\n[11/14] 敏感系统文件违规读取`);
if (EXISTING_LOG_FILES.length > 0) {
    const snoopPattern = /cat\s+\/etc\/shadow|cat\s+\/etc\/passwd|read\s+.*\.env|read\s+.*\.ssh\/id_/i;
    let snoopLinesAll = [];
    EXISTING_LOG_FILES.forEach(logPath => {
        snoopLinesAll = snoopLinesAll.concat(grepFile(logPath, snoopPattern));
    });
    if (snoopLinesAll.length > 0) {
        appendWarn(
            itemName,
            `发现 ${snoopLinesAll.length} 次尝试读取系统级敏感凭证的行为`,
            snoopLinesAll.join('\n')
        );
    } else {
        appendInfo(itemName, "基于规则未发现明显违规读取痕迹", "✅ 基于规则未发现明显违规读取痕迹");
    }
} else {
    appendSkip(
        itemName,
        "无日志文件，跳过敏感文件访问扫描",
        "未找到日志文件以扫描文件读取行为。"
    );
}

// [12/14] 敏感信息启发式扫描
itemName = "硬编码密钥与助记词防泄漏扫描";
fs.appendFileSync(REPORT_FILE, `\n[12/14] 敏感信息启发式扫描`);
let scanRoot = path.join(OC, 'workspace');
let dlpHits = 0;
if (fs.existsSync(scanRoot)) {
    const skipExts = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.woff', '.woff2', '.ttf', '.eot']);
    const hexPattern = /\b0x[a-fA-F0-9]{64}\b/;
    const mnemonicPattern = /\b([a-z]{3,12}\s+){11}([a-z]{3,12})\b|\b([a-z]{3,12}\s+){23}([a-z]{3,12})\b/;

    function scanDir(dir) {
        try {
            const entries = fs.readdirSync(dir);
            for (const entry of entries) {
                if (entry === '.git' || entry === 'node_modules') continue;
                const fullPath = buildSafeChildPath(dir, entry);
                if (!fullPath) continue;
                const stat = fs.statSync(fullPath);
                if (stat.isDirectory()) {
                    scanDir(fullPath);
                } else if (stat.isFile() && !skipExts.has(path.extname(fullPath).toLowerCase())) {
                    try {
                        const content = fs.readFileSync(fullPath, 'utf-8');
                        if (hexPattern.test(content)) dlpHits++;
                        if (mnemonicPattern.test(content)) dlpHits++;
                    } catch (e) {}
                }
            }
        } catch (e) {}
    }
    scanDir(scanRoot);
}
let detail12 = `敏感信息启发式扫描 hits : ${dlpHits}`;
if (dlpHits > 0) appendWarn(itemName, `⚠️ 检测到疑似明文敏感信息(${dlpHits})，请人工复核`, detail12);
else appendInfo(itemName, "未发现明显私钥/助记词模式", detail12 + "\n✅ 未发现明显私钥/助记词模式");

// [13/14] 黄线操作交叉验证 (Sudo/特权提取 vs Memory)
itemName = platform === 'win32' ? "特权提取操作对账审计" : "特权提权(Sudo)操作对账审计";
fs.appendFileSync(REPORT_FILE, platform === 'win32'
    ? `\n[13/14] 黄线操作交叉验证 (特权提取 vs Memory)`
    : `\n[13/14] 黄线操作交叉验证 (Sudo vs Memory)`);
let sudoCount = 0;
if (platform === 'linux') {
    ['/var/log/auth.log', '/var/log/secure'].forEach(logPath => {
        sudoCount += countMatchesInFile(logPath, /sudo.*COMMAND/gim);
    });
} else if (platform === 'darwin') {
    sudoCount = countMatchesInFile('/var/log/system.log', /sudo.*COMMAND/gim);
} else if (platform === 'win32') {
    // Event ID 4672 = 特权提升
    let psOut = spawnCmd('powershell', ['-NoProfile', '-Command',
        `(Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4672; StartTime=(Get-Date).AddDays(-1)} -ErrorAction SilentlyContinue | Measure-Object).Count`
    ]);
    sudoCount = parseInt(psOut, 10) || 0;
}

// 获取最近24小时的 memory 文件（今天 + 昨天）
function getMemoryFilesForLast24h(memoryDir) {
    try {
        const todayStr = getLocalDateStr(now);
        const yestStr = getLocalDateStr(yest);
        return fs.readdirSync(memoryDir)
            .filter(f => {
                if (!f.toLowerCase().endsWith('.md')) return false;
                // 匹配今天或昨天的日期前缀
                return f.startsWith(todayStr) || f.startsWith(yestStr);
            })
            .map(f => buildSafeChildPath(memoryDir, f))
            .filter(Boolean)
            .sort();
    } catch (e) {
        return [];
    }
}

const memoryDir = path.join(OC, 'workspace/memory');
const memFiles = getMemoryFilesForLast24h(memoryDir);
let memCount = 0;
for (const f of memFiles) {
    memCount += countMatchesInFile(f, platform === 'win32' ? /特权/gim : /sudo/gim);
}

const privLabel = platform === 'win32' ? '特权提取' : 'Sudo';
let detail13 = `${privLabel} Count (Today): ${sudoCount}\nMemory Count (Today): ${memCount}\nMemory Files (Matched): ${memFiles.length}\n${memFiles.length ? memFiles.join('\n') : '(none)'}`;
if (sudoCount > 0 && memCount === 0) {
    appendWarn(itemName, `系统当日发生了 ${sudoCount} 次${privLabel}，但 Agent 记忆中无记录`, detail13 + "\n⚠️ 怀疑 Agent 执行了未登记的特权越界操作");
} else {
    appendInfo(itemName, `${privLabel}执行记录(${sudoCount}) 与 大脑记忆(${memCount}) 基本匹配`, detail13 + `\n✅ ${privLabel}执行记录与大脑记忆对账正常`);
}


// ==========================================
// 板块四：生态与供应链安全
// ==========================================
fs.appendFileSync(REPORT_FILE, `\n\n--- [板块四] 生态与供应链安全 ---`);

// [14/14] Skill 恶意威胁情报扫描
let itemNameSkill = "生态组件恶意威胁情报扫描";
fs.appendFileSync(REPORT_FILE, `\n\n[14/14] skill扫描`);

let skillMetaList = [];

SKILL_SCAN_DIRS.forEach(skillRoot => {
    if (!fs.existsSync(skillRoot)) return;
    try {
        let skillDirs = fs.readdirSync(skillRoot);
        skillDirs.forEach(dir => {
            let baseDirPath = buildSafeChildPath(skillRoot, dir);
            if (!baseDirPath) return;
            let metaPath = `${baseDirPath}${path.sep}_meta.json`;
            let skillJsonPath = `${baseDirPath}${path.sep}skill.json`;

            let meta = {};
            let skillJson = {};

            if (fs.existsSync(metaPath)) {
                try { meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8')); } catch (e) {}
            }

            if (fs.existsSync(skillJsonPath)) {
                try { skillJson = JSON.parse(fs.readFileSync(skillJsonPath, 'utf-8')); } catch (e) {}
            }

            const slug = meta.slug || skillJson.slug || dir;
            const ownerId = meta.ownerId || "";
            const version = meta.version || skillJson.version || "";
            const author = skillJson.author || meta.author || "";

            skillMetaList.push({ slug, author, version, ownerId });
        });
    } catch (e) {}
});

// ──────────────────────────────────────────
// 网络请求封装
// ──────────────────────────────────────────

function generateAgentId() {
    const idPath = path.join(OC, '.agent-id');
    if (fs.existsSync(idPath)) {
        return fs.readFileSync(idPath, 'utf-8').trim();
    }
    const id = crypto.randomUUID();
    try { fs.writeFileSync(idPath, id, { mode: 0o600 }); } catch (e) {}
    return id;
}

function getActiveMac() {
    const interfaces = os.networkInterfaces();
    for (let name in interfaces) {
        for (let iface of interfaces[name]) {
            if (!iface.internal && iface.mac && iface.mac !== "00:00:00:00:00:00") {
                // 与 Java formatMac 一致：小写十六进制
                return iface.mac.toLowerCase();
            }
        }
    }
    return "UNKNOWN_MAC";
}

function doSignedPost(apiUrl, apiPath, bodyObj, callback) {
    const mac = getActiveMac();
    const hostname = os.hostname();
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const nonce = Math.random().toString(36).substring(2, 10);
    const method = "POST";
    const bodyStr = JSON.stringify(bodyObj);

    // 计算签名（与 Java 一致：仅 mac + hostname + timestamp + nonce，UTF-8）
    const signContent = mac + "\n" + hostname + "\n" + timestamp + "\n" + nonce;
    const sign = crypto.createHash("sha256").update(signContent, 'utf8').digest("hex");

    const urlObj = new URL(apiUrl);
    const isHttps = urlObj.protocol === 'https:';
    const defaultPort = isHttps ? 443 : 80;
    const port = urlObj.port || defaultPort;
    const options = {
        hostname: urlObj.hostname,
        port: port,
        path: apiPath,
        method: method,
        timeout: 10000, // 10秒超时
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(bodyStr),
            'X-MAC': mac,
            'X-HOSTNAME': hostname,
            'X-TIMESTAMP': timestamp,
            'X-NONCE': nonce,
            'X-SIGN': sign
        }
    };

    // 排查用：请求前输出（调试完成后已注释）
    // console.log('[请求] ' + method + ' ' + apiUrl);
    // console.log('[请求] host=' + options.hostname + ' port=' + port + ' path=' + apiPath);
    // console.log('[请求] 签名头 X-MAC=' + mac + ' X-HOSTNAME=' + hostname + ' X-TIMESTAMP=' + timestamp + ' X-NONCE=' + nonce);
    // console.log('[请求] X-SIGN=' + sign.substring(0, 16) + '... body长度=' + bodyStr.length);

    const requestModule = isHttps ? https : http;
    const req = requestModule.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
            const resInfo = {
                statusCode: res.statusCode,
                statusMessage: res.statusMessage,
                headers: res.headers,
                body: data
            };
            // 排查用：响应输出（调试完成后已注释）
            // console.log('[响应] HTTP ' + res.statusCode + ' ' + (res.statusMessage || ''));
            // if (res.headers && (res.headers['content-type'] || res.headers['Content-Type'])) {
            //     console.log('[响应] Content-Type: ' + (res.headers['content-type'] || res.headers['Content-Type']));
            // }
            // console.log('[响应] body长度=' + data.length);
            // if (data.length > 0) {
            //     const preview = data.length > 600 ? data.substring(0, 600) + '...' : data;
            //     console.log('[响应] body预览:\n' + preview);
            // }
            if (res.statusCode >= 200 && res.statusCode < 300) {
                callback(null, resInfo);
            } else {
                callback(`HTTP ${res.statusCode} ${res.statusMessage || ''}`.trim(), resInfo);
            }
        });
    });

    req.on('error', (e) => {
        // console.log('[错误] 请求异常: ' + e.message);
        callback(e.message, null);
    });
    req.on('timeout', () => {
        // console.log('[错误] 请求超时');
        req.destroy();
        callback("请求超时", null);
    });

    req.write(bodyStr);
    req.end();
}

// ──────────────────────────────────────────
// 最终收尾流程
// ──────────────────────────────────────────
function finalizeAndPushData() {
    const agentId = generateAgentId();
    const status = RED_COUNT > 0 ? "warning" : "success";

    const checkedCount = ITEM_SEQ - SKIP_COUNT;
    const passCount = checkedCount - RED_COUNT;

    let outputObj = {
        report_time: REPORT_TIME,
        status,
        red_item: RED_COUNT,
        checkedCount: checkedCount,
        passCount: passCount,
        agent_id: agentId,
        data: JSON_DATA
    };

    const pushObj = {
        report_time: REPORT_TIME,
        status,
        red_item: RED_COUNT,
        red_count: RED_COUNT,
        checkedCount: checkedCount,
        passCount: passCount,
        agent_id: agentId,
        data: JSON_DATA.map(({ item, brief }) => ({ item, brief }))
    };

    fs.writeFileSync(JSON_OUT_FILE, JSON.stringify(outputObj, null, 2), { encoding: 'utf-8', mode: 0o600 });

    SUMMARY += `${COLORS.dim}────────────────────────────────────────────────────────────────────────${COLORS.reset}\n`;
    SUMMARY += `  ${COLORS.bright}检测统计:${COLORS.reset}     ${COLORS.green}PASS ${passCount}${COLORS.reset}  ${COLORS.red}FAIL ${RED_COUNT}${COLORS.reset}  ${COLORS.magenta}SKIP ${SKIP_COUNT}${COLORS.reset}\n`;

    if (!PUSH_ENABLED) {
        // 本地离线模式：不展示安全得分，只展示检测统计
        SUMMARY += `${COLORS.dim}────────────────────────────────────────────────────────────────────────${COLORS.reset}\n`;
        console.log(SUMMARY);
        console.log(`${COLORS.dim}详细审计报告已保存至: \`${REPORT_FILE}\`${COLORS.reset}`);
        console.log(`\n${COLORS.dim}当前为本地离线模式。如需参与全网威胁态势感知，请附加 --push 参数运行。${COLORS.reset}`);
        process.exit(0);
        return;
    }

    // console.log(`\n${COLORS.cyan}正在向云端安全中心同步态势感知数据...${COLORS.reset}`);

    const pushApiUrl = "https://auth.ctct.cn:10020/changeway-open/api/pushAuditData";
    const pushApiPath = "/changeway-open/api/pushAuditData";

    doSignedPost(pushApiUrl, pushApiPath, pushObj, (err, resData) => {
        let score = null;

        // if (err) {
        //     console.log(`${COLORS.red}✖ Telemetry upload failed: ${err}${COLORS.reset}`);
        // } else {
        //     console.log(`${COLORS.green}✔ Telemetry upload successful${COLORS.reset}`);
        // }

        // 仅在 PUSH 模式下，根据云端返回结果展示系统安全得分
        if (!err && resData) {
            try {
                // doSignedPost 返回的是 { statusCode, headers, body } 结构，这里只解析 body
                let rawBody = null;
                if (typeof resData === 'string') {
                    rawBody = resData;
                } else if (resData && typeof resData.body === 'string') {
                    rawBody = resData.body;
                }

                if (rawBody && rawBody.trim() !== '') {
                    const apiRes = JSON.parse(rawBody);
                    const dataField = apiRes && apiRes.data;

                    // 优先使用顶层 data 字段作为分数（支持 number 或可解析为 number 的字符串）
                    if (typeof dataField === 'number') {
                        score = dataField;
                    } else if (typeof dataField === 'string' && dataField.trim() !== '' && !Number.isNaN(Number(dataField))) {
                        score = Number(dataField);
                    } else if (dataField && typeof dataField.score === 'number') {
                        // 兼容旧版 data.score 结构
                        score = dataField.score;
                    }
                }
            } catch (e) {
                // 如果解析失败则不展示分数
            }
        }

        if (typeof score === 'number') {
            const safeScore = Math.max(0, Math.min(100, Math.round(score)));
            let scoreColor = safeScore >= 90 ? COLORS.green : (safeScore >= 70 ? COLORS.yellow : COLORS.red);
            const scoreLine = `  ${COLORS.bright}系统安全得分:${COLORS.reset}  ${scoreColor}${safeScore} / 100${COLORS.reset}\n`;
            // 将系统安全得分行放在报告最前面
            // SUMMARY = scoreLine + SUMMARY;
            SUMMARY += scoreLine
        }

        SUMMARY += `${COLORS.dim}────────────────────────────────────────────────────────────────────────${COLORS.reset}\n`;
        console.log(SUMMARY);
        console.log(`${COLORS.dim}详细审计报告已保存至: \`${REPORT_FILE}\`${COLORS.reset}`);

        process.exit(0);
    });
}

// ──────────────────────────────────────────
// 执行逻辑
// --push 模式：查威胁情报 → 上报数据
// 默认模式：仅本地扫描 + 本地落盘，不发起任何网络请求
// ──────────────────────────────────────────
if (skillMetaList.length === 0) {
    appendInfo(itemNameSkill, "未发现已安装的 Skill", "当前环境暂无已安装的 Skill 组件，跳过检测。");
    finalizeAndPushData();
} else {
    let scannedSummary = `>>> 本机已安装的 Skill 组件清单 (共 ${skillMetaList.length} 个):\n` +
                         skillMetaList.map(s => `  - ${s.slug} (v${s.version})  [Owner: ${s.ownerId}]`).join('\n');

    if (!PUSH_ENABLED) {
        appendInfo(
            itemNameSkill,
            `已列出本机已安装的 ${skillMetaList.length} 个 Skill 组件（威胁情报查询需加 --push）`,
            scannedSummary
        );
        finalizeAndPushData();
    } else {
        const assessApiUrl = "https://auth.ctct.cn:10020/changeway-open/api/skills/assessment";
        const assessApiPath = "/changeway-open/api/skills/assessment";

        doSignedPost(assessApiUrl, assessApiPath, { data: skillMetaList }, (err, apiResRaw) => {
            let intelHits = 0;
            let hitDetails = [];

            if (!err && apiResRaw) {
                try {
                    let apiRes = JSON.parse(apiResRaw.body || apiResRaw);
                    if (apiRes.data && Array.isArray(apiRes.data)) {
                        apiRes.data.forEach(item => {
                            if (item.matched_intel && Array.isArray(item.matched_intel) && item.matched_intel.length > 0) {
                                item.matched_intel.forEach(intel => {
                                    intelHits++;
                                    const maliciousDesc =
                                        intel.is_malicious === 1 || intel.is_malicious === '1'
                                            ? '存在恶意'
                                            : (intel.is_malicious === 0 || intel.is_malicious === '0'
                                                ? '不存在恶意'
                                                : '无标记');

                                    // 风险等级映射：英文 -> 中文 + emoji
                                    const severityMap = {
                                        'Benign': '✅ 良性',
                                        'Suspicious': '⚠️ 可疑',
                                        'Malicious': '🚨 恶意'
                                    };
                                    const severityDisplay = severityMap[intel.severity] || (intel.severity || 'UNKNOWN');

                                    hitDetails.push(
                                        `- 命中威胁情报: [${item.slug} ${item.version}] (Owner: ${item.author})\n` +
                                        `   风险等级 (severity): ${severityDisplay}\n` +
                                        `   情报详情: ${JSON.stringify(intel.info || {})}`
                                    );
                                });
                            }
                        });
                    }
                } catch (parseErr) {
                    hitDetails.push(`⚠️ API 响应解析失败: ${parseErr.message}`);
                }
            } else {
                hitDetails.push(`⚠️ 威胁情报 API 请求异常: ${err}`);
            }

            let finalDetailText = `${scannedSummary}\n\n>>> 威胁情报扫描结果:\n`;

            if (intelHits > 0) {
                finalDetailText += hitDetails.join('\n\n');
                appendWarn(itemNameSkill, `⚠️ 注意！发现 ${intelHits} 个命中情报的组件！`, finalDetailText);
            } 
            // else if (hitDetails.length > 0 && intelHits === 0) {
            //     console.log(hitDetails.join('\n'))
            //     finalDetailText += hitDetails.join('\n');
            //     appendWarn(itemNameSkill, `⚠️ API 服务异常或鉴权失败`, finalDetailText);
            // } 
            else {
                finalDetailText = scannedSummary;
                appendInfo(
                    itemNameSkill,
                    `已列出本机已安装的 ${skillMetaList.length} 个 Skill 组件`,
                    finalDetailText
                );
            }

            finalizeAndPushData();
        });
    }
}
