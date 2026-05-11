#!/usr/bin/env node
// Team Builder - OpenClaw Reusable Multi-Agent Team Template Deployer v1.3
// Usage:
//   node deploy.js [--team <prefix>]
//   node deploy.js --config <jsonFile> [--team <prefix>]
//   node deploy.js --verify --config <jsonFile> [--team <prefix>]

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const home = process.env.HOME || process.env.USERPROFILE;
const args = process.argv.slice(2);
const teamFlagIdx = args.indexOf('--team');
const teamPrefix = (teamFlagIdx !== -1 && args[teamFlagIdx + 1]) ? args[teamFlagIdx + 1] + '-' : '';
const configIdx = args.indexOf('--config');
const verifyMode = args.includes('--verify');
const configPath = configIdx !== -1 ? args[configIdx + 1] : null;
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = q => new Promise(r => rl.question(q, r));
const w = (fp, c) => { fs.mkdirSync(path.dirname(fp), { recursive: true }); fs.writeFileSync(fp, c, 'utf8'); };

function detectModels() {
  try {
    const confPath = path.join(home, '.openclaw', 'openclaw.json');
    const raw = fs.readFileSync(confPath, 'utf8');
    const cleaned = raw.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
    const conf = JSON.parse(cleaned);
    return Object.keys((conf.models && conf.models.providers) || conf.modelProviders || {});
  } catch { return []; }
}
function suggestModel(type, provs) {
  const patterns = { think: /glm.?5|opus|o1|deepthink/i, exec: /glm.?4(?!.*flash)|sonnet|gpt-4/i };
  const p = patterns[type]; if (!p) return null;
  for (const k of provs) if (p.test(k)) return k;
  return null;
}
const ROLES = [
  { id: 'chief-of-staff', dname: 'Chief of Staff', pos: 'dispatch+strategy+efficiency', think: true },
  { id: 'data-analyst', dname: 'Data Analyst', pos: 'data+user research', think: false },
  { id: 'growth-lead', dname: 'Growth Lead', pos: 'GEO+SEO+community+social', think: true },
  { id: 'content-chief', dname: 'Content Chief', pos: 'strategy+writing+copy+i18n', think: true },
  { id: 'intel-analyst', dname: 'Intel Analyst', pos: 'competitors+market trends', think: false },
  { id: 'product-lead', dname: 'Product Lead', pos: 'product mgmt+clarification+acceptance', think: true },
  { id: 'devops', dname: 'DevOps', pos: 'delivery+deploy+qa gate+deep dive', think: false },
  { id: 'fullstack-dev', dname: 'Fullstack Dev', pos: 'implementation+module deep dive+Claude direct acpx/session continuity', think: false },
];
function chiefSoul(name, team) { return `# SOUL.md - ${name} (chief-of-staff)\n\n- Role ID: chief-of-staff\n- Team Router for ${team}\n- Routes implementation vs delivery and controls token waste\n`; }
function dataSoul(name) { return `# SOUL.md - ${name} (data-analyst)\n\n- Role ID: data-analyst\n- Data hub + user research\n`; }
function growthSoul(name) { return `# SOUL.md - ${name} (growth-lead)\n\n- Role ID: growth-lead\n- GEO + SEO + community + social\n`; }
function contentSoul(name) { return `# SOUL.md - ${name} (content-chief)\n\n- Role ID: content-chief\n- Content strategy + writing + copy + i18n\n`; }
function intelSoul(name) { return `# SOUL.md - ${name} (intel-analyst)\n\n- Role ID: intel-analyst\n- Competitor intelligence + market trends\n`; }
function productSoul(name) { return `# SOUL.md - ${name} (product-lead)\n\n- Role ID: product-lead\n- Product management + clarification + PRD + acceptance + knowledge governance\n- Direct reports: devops, fullstack-dev\n- Delivery-oriented Deep Dive goes to devops\n- Module-level implementation follow-up goes to fullstack-dev\n`; }
function devopsSoul(name) { return `# SOUL.md - ${name} (devops)\n\n- Role ID: devops\n- Delivery / deploy / environment / QA gate / delivery-oriented Deep Dive\n`; }
function fullstackSoul(name) { return `# SOUL.md - ${name} (fullstack-dev)\n\n- Role ID: fullstack-dev\n- Implementation / module deep dive / Claude coding / dev docs\n- Coding behavior: if coding-lead is loaded, follow it as the primary execution authority\n- If coding-lead is not loaded, read references/coding-behavior-fallback.md\n`; }
const SOUL_FN = {
  'chief-of-staff': chiefSoul,
  'data-analyst': dataSoul,
  'growth-lead': growthSoul,
  'content-chief': contentSoul,
  'intel-analyst': intelSoul,
  'product-lead': productSoul,
  'devops': devopsSoul,
  'fullstack-dev': fullstackSoul,
};

function buildConfigFromJson(p) {
  const raw = fs.readFileSync(p, 'utf8');
  const json = JSON.parse(raw);
  const roleIds = json.roles && json.roles.length ? json.roles : ROLES.map(r => r.id);
  const selectedRoles = ROLES.filter(r => roleIds.includes(r.id));
  const names = {};
  for (const r of selectedRoles) names[r.id] = (json.roleNames && json.roleNames[r.id]) || r.dname;
  return {
    teamName: json.teamName || 'Alpha Team',
    workDir: json.workspaceDir || path.join(home, '.openclaw', 'workspace-team'),
    tz: json.timezone || 'Asia/Shanghai',
    mh: json.morningHour || 8,
    eh: json.eveningHour || 18,
    tm: json.thinkingModel || suggestModel('think', detectModels()) || 'zai/glm-5',
    em: json.executionModel || suggestModel('exec', detectModels()) || 'zai/glm-4.7',
    ceoTitle: json.ceoTitle || 'Boss',
    selectedRoles,
    names,
  };
}

async function buildConfigInteractive() {
  console.log('\n========================================');
  console.log('  OpenClaw Team Builder Template v1.3');
  console.log('========================================\n');
  const teamName = await ask('Team name [Alpha Team]: ') || 'Alpha Team';
  console.log('\nAvailable roles:');
  ROLES.forEach((r, i) => console.log('  ' + (i + 1) + '. ' + r.dname + ' (' + r.id + ') - ' + r.pos));
  const roleInput = await ask('\nSelect roles (comma-separated numbers, or Enter for all): ');
  let selectedRoles;
  if (!roleInput.trim()) selectedRoles = ROLES;
  else {
    const indices = roleInput.split(',').map(s => parseInt(s.trim()) - 1).filter(i => i >= 0 && i < ROLES.length);
    selectedRoles = indices.map(i => ROLES[i]);
    if (selectedRoles.length < 2) selectedRoles = ROLES;
  }
  const defDir = path.join(home, '.openclaw', 'workspace-team');
  const workDir = await ask(`Workspace dir [${defDir}]: `) || defDir;
  const tz = await ask('Timezone [Asia/Shanghai]: ') || 'Asia/Shanghai';
  const mh = parseInt(await ask('Morning brief hour [8]: ') || '8');
  const eh = parseInt(await ask('Evening brief hour [18]: ') || '18');
  const provs = detectModels();
  const tm = await ask('Thinking model [' + (suggestModel('think', provs) || 'zai/glm-5') + ']: ') || (suggestModel('think', provs) || 'zai/glm-5');
  const em = await ask('Execution model [' + (suggestModel('exec', provs) || 'zai/glm-4.7') + ']: ') || (suggestModel('exec', provs) || 'zai/glm-4.7');
  const ceoTitle = await ask('CEO title [Boss]: ') || 'Boss';
  const names = {};
  console.log('\n--- Role names (Enter for default) ---');
  for (const r of selectedRoles) names[r.id] = await ask(`  ${r.id} [${r.dname}]: `) || r.dname;
  await ask('\nSetup Telegram? (y/n) [n]: '); // reserved, currently ignored in verify path
  return { teamName, workDir, tz, mh, eh, tm, em, ceoTitle, selectedRoles, names };
}

function generate(cfg) {
  const prefixedRoles = cfg.selectedRoles.map(r => ({ ...r, pid: teamPrefix + r.id }));
  const dirs = ['shared/briefings','shared/inbox','shared/decisions','shared/kanban','shared/knowledge','shared/products','shared/products/_template','shared/data','shared/status'];
  prefixedRoles.forEach(r => dirs.push(`agents/${r.pid}/memory`));
  dirs.push('references');
  dirs.forEach(d => fs.mkdirSync(path.join(cfg.workDir, d), { recursive: true }));

  const rows = prefixedRoles.map(r => `| ${cfg.names[r.id]} | ${r.pid} | ${r.pos} |`).join('\n');
  w(path.join(cfg.workDir, 'AGENTS.md'), `# AGENTS.md - ${cfg.teamName}\n\n## Role Lookup\n| Name | ID | Position |\n|------|-----|----------|\n${rows}\n\n## Product Knowledge\nThese files are generated through the dual-dev pipeline and governed by product-lead.\nAll agents READ. Devops writes delivery-oriented scan outputs. Fullstack-dev supplements implementation follow-up knowledge. Product-lead REVIEWS. Matched skills win; agent fallback applies only when the skill is absent. Context hygiene defaults: active cap 60, lifecycle window 100, verify before declare-done, confirm cwd before writing/spawning.\n`);
  w(path.join(cfg.workDir, 'README.md'), `# ${cfg.teamName}\n\n## Quick Start\n1. node apply-config.js\n2. Run create-crons.ps1 / create-crons.sh\n3. openclaw gateway restart\n4. Fill shared/decisions/active.md and shared/products/_index.md\n\n## This Template\nThis workspace is a reusable multi-agent team template. It is one standard implementation of this collaboration style, not the only valid source of such a team.\n\n## Dual-Dev Model\n- product-lead: clarification / PRD / acceptance / routing\n- devops: delivery / deploy / env / QA gate / delivery-oriented Deep Dive\n- fullstack-dev: implementation / module deep dive / Claude coding / dev docs\n  - simple: direct\n  - medium: Claude ACP run or direct acpx\n  - complex: existing-session continuity + context files\n  - ACP unavailable: direct fallback, do not block\n- Context hygiene: active cap 60, lifecycle window 100, verify before declare-done, confirm cwd before writing/spawning\n\n## Product Matrix + Deep Dive\n- product-lead triggers the dual-dev Deep Dive flow\n- devops generates shared delivery-oriented knowledge\n- fullstack-dev supplements module-level implementation follow-up\n`);
  w(path.join(cfg.workDir, 'SOUL.md'), `# ${cfg.teamName} Values\n`);
  w(path.join(cfg.workDir, 'USER.md'), `# CEO Info\n- Title: ${cfg.ceoTitle}\n- Timezone: ${cfg.tz}\n`);
  for (const r of prefixedRoles) {
    const fn = SOUL_FN[r.id];
    const soul = r.id === 'chief-of-staff' ? fn(cfg.names[r.id], cfg.teamName) : fn(cfg.names[r.id]);
    w(path.join(cfg.workDir, `agents/${r.pid}/SOUL.md`), soul);
    w(path.join(cfg.workDir, `agents/${r.pid}/MEMORY.md`), `# Memory - ${cfg.names[r.id]}\n`);
    w(path.join(cfg.workDir, `shared/inbox/to-${r.pid}.md`), `# Inbox - ${cfg.names[r.id]}\n`);
  }
  w(path.join(cfg.workDir, 'shared/decisions/active.md'), `# Active Decisions\n- Team: ${cfg.teamName}\n`);
  w(path.join(cfg.workDir, 'shared/products/_index.md'), `# Product Matrix\n\n> After adding a product, send a message to product-lead to trigger the dual-dev Deep Dive flow.\n`);
  w(path.join(cfg.workDir, 'shared/products/_template/README.md'), `# Product Knowledge Directory Template\n\nWhen the dual-dev Deep Dive flow runs, files are generated here per product.\nDevops owns delivery-oriented scans and shared knowledge generation. Fullstack-dev supplements module-level implementation follow-up when needed.\n`);
  w(path.join(cfg.workDir, 'shared/status/team-dashboard.md'), `# Team Dashboard\n`);
  w(path.join(cfg.workDir, 'shared/knowledge/tech-standards.md'), `# Tech Standards\n`);
  w(path.join(cfg.workDir, 'shared/knowledge/team-workflow.md'), `# Team Workflow Rules\n\n> Applies to this multi-agent collaboration structure. It is not limited to one generator source.\n\n## Task handoff minimum fields\n- Task\n- Scope\n- Acceptance Criteria\n- Priority\n- Complexity\n- Project Path\n- Constraints / No-go\n\n## Done chain\n1. dispatchable with clear scope and acceptance\n2. execution + self-check complete\n3. delivery / regression / verification written down when applicable\n4. status written back to inbox / dashboard / shared outputs\n\n## Minimal read order\n1. your SOUL\n2. team dashboard\n3. your inbox\n4. product index + manifest + 1-3 relevant files only\n5. memory / history only as needed\n\n## Memory boundaries\nWrite durable notes inside your role boundary. Do not dump generic noise into shared memory.\n`);
  w(path.join(cfg.workDir, 'references/coding-behavior-fallback.md'), `# Coding Behavior Fallback\n\nUse this only when \`coding-lead\` is not loaded.\n\n## Task Routing\n- Simple: direct in current session\n- Medium: prefer Claude ACP run or direct acpx\n- Complex: continue in the existing fullstack-dev session with context files\n- Do not rely on IM-bound ACP session persistence\n- ACP unavailable: fall back to direct execution, do not block\n\n## Context Hygiene\n- Keep active context files under <project>/.openclaw/\n- Reuse the same context file for the same code chain when possible\n- Naming pattern: context-<task-slug>.md\n- Active context file cap per project: 60\n- Context-file lifecycle window per project: 100 total files across active + archive\n- Completed or stale context files should be deleted or archived under .openclaw/archive/\n\n## Safety & Completion\n- Verify against task + acceptance criteria before declaring done\n- Confirm the target working directory before writing or spawning\n- Read relevant product knowledge files before touching project code\n- Reuse over reinvention; ask product-lead when boundaries are unclear\n`);

  const wsPath = cfg.workDir.replace(/\\/g, '/').replace(home.replace(/\\/g, '/'), '~');
  const agentList = prefixedRoles.map(r => `    { id: "${r.pid}", name: "${cfg.names[r.id]}", workspace: "${wsPath}", model: { primary: "${r.think ? cfg.tm : cfg.em}" }, identity: { name: "${cfg.names[r.id]}" } }`).join(',\n');
  const allIds = ['main', ...prefixedRoles.map(r => `"${r.pid}"`)].join(', ');
  w(path.join(cfg.workDir, 'apply-config.js'), `#!/usr/bin/env node\nconst fs = require('fs');\nconst path = require('path');\nconst cfgPath = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw', 'openclaw.json');\nlet config = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));\nif (!config.agents) config.agents = {};\nif (!Array.isArray(config.agents.list)) config.agents.list = [];\nif (!config.bindings) config.bindings = [];\nconst newAgents = [\n${agentList}\n];\nconst existing = new Set(config.agents.list.map(a => a.id));\nfor (const a of newAgents) if (!existing.has(a.id)) config.agents.list.push(a);\nif (!config.tools) config.tools = {};\nconfig.tools.agentToAgent = { enabled: true, allow: [${allIds}] };\nfs.writeFileSync(cfgPath, JSON.stringify(config, null, 2));\nconsole.log('Done! Run: openclaw gateway restart');\n`);

  const crons = [
    { name: `${teamPrefix}chief-morning-brief`, cron: `0 ${cfg.mh} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--announce', msg: 'Morning router scan + dashboard + brief.' },
    { name: `${teamPrefix}chief-midday-patrol`, cron: `0 ${cfg.mh+4} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--no-deliver', msg: 'Midday router scan only.' },
    { name: `${teamPrefix}chief-afternoon-patrol`, cron: `0 ${cfg.mh+7} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--no-deliver', msg: 'Afternoon router scan only.' },
    { name: `${teamPrefix}chief-evening-brief`, cron: `0 ${cfg.eh} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--announce', msg: 'Evening summary + dashboard.' },
    { name: `${teamPrefix}data-daily-pull`, cron: `0 ${cfg.mh-1} * * *`, agent: `${teamPrefix}data-analyst`, deliver: '--no-deliver', msg: 'Data pull + feedback scan.' },
    { name: `${teamPrefix}growth-daily-work`, cron: `0 ${cfg.mh+1} * * *`, agent: `${teamPrefix}growth-lead`, deliver: '--no-deliver', msg: 'GEO + SEO + community.' },
    { name: `${teamPrefix}product-lead-daily`, cron: `0 ${cfg.mh+1} * * *`, agent: `${teamPrefix}product-lead`, deliver: '--no-deliver', msg: 'Clarification/PRD/acceptance + route work to devops/fullstack-dev.' },
    { name: `${teamPrefix}content-daily-work`, cron: `0 ${cfg.mh+2} * * 1-5`, agent: `${teamPrefix}content-chief`, deliver: '--no-deliver', msg: 'Content production.' },
    { name: `${teamPrefix}devops-daily`, cron: `0 ${cfg.mh+2} * * *`, agent: `${teamPrefix}devops`, deliver: '--no-deliver', msg: 'Delivery Deep Dive + env + QA gate.' },
    { name: `${teamPrefix}fullstack-daily`, cron: `30 ${cfg.mh+2} * * *`, agent: `${teamPrefix}fullstack-dev`, deliver: '--no-deliver', msg: 'Implementation + module deep dive follow-up.' },
    { name: `${teamPrefix}intel-scan`, cron: `5 ${cfg.mh-1} * * 1,3,5`, agent: `${teamPrefix}intel-analyst`, deliver: '--no-deliver', msg: 'Competitor scan.' },
  ];
  let ps = `# ${cfg.teamName} Cron Jobs\n\n`;
  let sh = `#!/bin/bash\n# ${cfg.teamName} Cron Jobs\n\n`;
  for (const c of crons) {
    const line = `openclaw cron add --name \"${c.name}\" --cron \"${c.cron}\" --tz \"${cfg.tz}\" --session isolated --agent ${c.agent} ${c.deliver} --exact --timeout-seconds 600 --message \"${c.msg}\"`;
    ps += line + `\n\n`;
    sh += line + `\n\n`;
  }
  w(path.join(cfg.workDir, 'create-crons.ps1'), ps);
  w(path.join(cfg.workDir, 'create-crons.sh'), sh);
  return { prefixedRoles };
}

function runVerify(cfg) {
  const checks = [];
  const read = rel => fs.readFileSync(path.join(cfg.workDir, rel), 'utf8');
  const mustContain = (group, rel, text, label) => {
    const content = read(rel);
    checks.push({
      group,
      rel,
      label: label || `contains: ${text}`,
      expected: text,
      ok: content.includes(text)
    });
  };

  mustContain('core', 'README.md', 'Dual-Dev Model', 'README includes dual-dev section');
  mustContain('core', 'README.md', 'reusable multi-agent team template', 'README marks this as a reusable template');
  mustContain('core', 'AGENTS.md', 'Devops writes delivery-oriented scan outputs', 'AGENTS describes dual-dev ownership');
  mustContain('core', 'shared/products/_index.md', 'dual-dev Deep Dive flow', 'product index points to Deep Dive flow');

  mustContain('roles', 'agents/product-lead/SOUL.md', 'Direct reports: devops, fullstack-dev', 'product-lead owns dev routing');
  mustContain('roles', 'agents/devops/SOUL.md', 'Delivery / deploy / environment / QA gate / delivery-oriented Deep Dive', 'devops delivery role present');
  mustContain('roles', 'agents/fullstack-dev/SOUL.md', 'Implementation / module deep dive / Claude coding / dev docs', 'fullstack-dev implementation role present');
  mustContain('roles', 'agents/fullstack-dev/SOUL.md', 'If coding-lead is not loaded, read references/coding-behavior-fallback.md', 'fullstack-dev fallback reference present');

  mustContain('fallback', 'references/coding-behavior-fallback.md', 'Active context file cap per project: 60', 'fallback has active context cap 60');
  mustContain('fallback', 'references/coding-behavior-fallback.md', 'Context-file lifecycle window per project: 100 total files across active + archive', 'fallback has lifecycle window 100');
  mustContain('fallback', 'references/coding-behavior-fallback.md', 'Verify against task + acceptance criteria before declaring done', 'fallback requires verification before done');
  mustContain('fallback', 'references/coding-behavior-fallback.md', 'Confirm the target working directory before writing or spawning', 'fallback requires cwd confirmation');

  mustContain('hygiene', 'README.md', 'Context hygiene: active cap 60, lifecycle window 100, verify before declare-done, confirm cwd before writing/spawning', 'README includes context hygiene summary');
  mustContain('workflow', 'shared/knowledge/team-workflow.md', 'Task handoff minimum fields', 'team workflow includes task handoff fields');
  mustContain('workflow', 'shared/knowledge/team-workflow.md', 'Done chain', 'team workflow includes done chain');
  mustContain('workflow', 'shared/knowledge/team-workflow.md', 'Minimal read order', 'team workflow includes minimal read order');
  mustContain('workflow', 'shared/knowledge/team-workflow.md', 'Memory boundaries', 'team workflow includes memory boundaries');
  mustContain('hygiene', 'AGENTS.md', 'Context hygiene defaults: active cap 60, lifecycle window 100, verify before declare-done, confirm cwd before writing/spawning.', 'AGENTS includes context hygiene defaults');

  mustContain('cron', 'create-crons.ps1', 'devops-daily', 'Windows cron includes devops daily');
  mustContain('cron', 'create-crons.ps1', 'fullstack-daily', 'Windows cron includes fullstack daily');

  const failed = checks.filter(c => !c.ok);
  const grouped = checks.reduce((acc, check) => {
    if (!acc[check.group]) acc[check.group] = [];
    acc[check.group].push(check);
    return acc;
  }, {});

  const report = {
    ok: failed.length === 0,
    summary: {
      total: checks.length,
      passed: checks.length - failed.length,
      failed: failed.length,
      workspace: cfg.workDir
    },
    groups: Object.fromEntries(Object.entries(grouped).map(([group, items]) => [group, {
      total: items.length,
      passed: items.filter(i => i.ok).length,
      failed: items.filter(i => !i.ok).length,
      checks: items.map(i => ({
        file: i.rel,
        label: i.label,
        ok: i.ok,
        expected: i.expected
      }))
    }]))
  };

  console.log(JSON.stringify(report, null, 2));
  if (failed.length) process.exit(2);
}

(async function main() {
  const cfg = configPath ? buildConfigFromJson(configPath) : await buildConfigInteractive();
  generate(cfg);
  if (verifyMode) runVerify(cfg);
  console.log(`${cfg.teamName} deployed to ${cfg.workDir}`);
  rl.close();
})().catch(e => { console.error(e); rl.close(); process.exit(1); });
