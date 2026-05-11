const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// SKILLS MONITOR (v2.0)
// Proactively checks installed skills for real issues (not cosmetic ones).
// - Ignores shared libraries and non-skill directories
// - Only syntax-checks .js files
// - Checks if dependencies are truly missing (not just node_modules dir)

const SKILLS_DIR = path.resolve(__dirname, '../../skills');

// Directories that are NOT skills (shared libs, internal tools, non-JS projects)
const IGNORE_LIST = new Set([
    'common',           // Shared Feishu client library
    'clawhub',          // ClawHub CLI integration
    'input-validator',  // Internal validation utility
    'proactive-agent',  // Agent framework (not a skill)
    'security-audit',   // Internal audit tool
]);

// Load user-defined ignore list if exists
try {
    const ignoreFile = path.join(SKILLS_DIR, '..', '.skill_monitor_ignore');
    if (fs.existsSync(ignoreFile)) {
        const lines = fs.readFileSync(ignoreFile, 'utf8').split('\n');
        lines.forEach(function(l) {
            var t = l.trim();
            if (t && !t.startsWith('#')) IGNORE_LIST.add(t);
        });
    }
} catch (e) { /* ignore */ }

function checkSkill(skillName) {
    if (IGNORE_LIST.has(skillName)) return null;

    const skillPath = path.join(SKILLS_DIR, skillName);
    const issues = [];
    
    // Skip if not a directory
    try {
        if (!fs.statSync(skillPath).isDirectory()) return null;
    } catch (e) {
        return null;
    }

    // 1. Check Package Structure
    let mainFile = 'index.js';
    const pkgPath = path.join(skillPath, 'package.json');
    var hasPkg = false;
    
    if (fs.existsSync(pkgPath)) {
        hasPkg = true;
        try {
            const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
            if (pkg.main) mainFile = pkg.main;
            
            // 2. Check dependencies -- only flag if require() actually fails
            if (pkg.dependencies && Object.keys(pkg.dependencies).length > 0) {
                if (!fs.existsSync(path.join(skillPath, 'node_modules'))) {
                    // Try to actually require the entry point to see if it works without node_modules
                    var entryAbs = path.join(skillPath, mainFile);
                    if (fs.existsSync(entryAbs) && mainFile.endsWith('.js')) {
                        try {
                            execSync(`node -e "require('${entryAbs.replace(/'/g, "\\'")}')"`, {
                                stdio: 'ignore', timeout: 5000, cwd: skillPath, windowsHide: true
                            });
                            // require succeeded: deps are resolved via relative paths or globals, no issue
                        } catch (e) {
                            issues.push('Missing node_modules (needs npm install)');
                        }
                    }
                }
            }
        } catch (e) {
            issues.push('Invalid package.json');
        }
    }

    // 3. Syntax Check -- only for .js entry points
    if (mainFile.endsWith('.js')) {
        const entryPoint = path.join(skillPath, mainFile);
        if (fs.existsSync(entryPoint)) {
            try {
                execSync(`node -c "${entryPoint}"`, { stdio: 'ignore', timeout: 5000, windowsHide: true });
            } catch (e) {
                issues.push(`Syntax Error in ${mainFile}`);
            }
        }
    }

    // 4. Missing SKILL.md -- only warn for dirs that have package.json (real skills, not utility dirs)
    if (hasPkg && !fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
        issues.push('Missing SKILL.md');
    }

    if (issues.length > 0) {
        return { name: skillName, issues };
    }
    return null;
}

// Auto-heal: attempt to fix simple issues automatically
function autoHeal(skillName, issues) {
    const skillPath = path.join(SKILLS_DIR, skillName);
    const healed = [];

    for (const issue of issues) {
        if (issue === 'Missing node_modules (needs npm install)') {
            try {
                execSync('npm install --production --no-audit --no-fund', {
                    cwd: skillPath, stdio: 'ignore', timeout: 30000, windowsHide: true
                });
                healed.push(issue);
                console.log(`[SkillsMonitor] Auto-healed ${skillName}: npm install`);
            } catch (e) {
                // npm install failed, leave the issue
            }
        } else if (issue === 'Missing SKILL.md') {
            try {
                const name = skillName.replace(/-/g, ' ');
                fs.writeFileSync(
                    path.join(skillPath, 'SKILL.md'),
                    `# ${skillName}\n\n${name} skill.\n`
                );
                healed.push(issue);
                console.log(`[SkillsMonitor] Auto-healed ${skillName}: created SKILL.md stub`);
            } catch (e) {
                // write failed, leave the issue
            }
        }
    }

    return healed;
}

function run(options) {
    const heal = (options && options.autoHeal) !== false; // auto-heal by default
    const skills = fs.readdirSync(SKILLS_DIR);
    const report = [];

    for (const skill of skills) {
        if (skill.startsWith('.')) continue; // skip hidden
        const result = checkSkill(skill);
        if (result) {
            if (heal) {
                const healed = autoHeal(result.name, result.issues);
                // Remove healed issues
                result.issues = result.issues.filter(function(i) { return !healed.includes(i); });
                if (result.issues.length === 0) continue; // fully healed
            }
            report.push(result);
        }
    }

    return report;
}

if (require.main === module) {
    const issues = run();
    if (issues.length > 0) {
        console.log(JSON.stringify(issues, null, 2));
        process.exit(1);
    } else {
        console.log("[]");
        process.exit(0);
    }
}

module.exports = { run };
