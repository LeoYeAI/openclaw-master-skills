#!/usr/bin/env node
// issue_tracker.js -- Track evolution issues in a Feishu Doc
//
// Creates a persistent Feishu document on first run, then appends
// new issues discovered by the evolver in each cycle.
//
// Config (env vars):
//   EVOLVER_ISSUE_DOC_TOKEN  -- Feishu doc token (auto-created if not set)
//   OPENCLAW_MASTER_ID       -- Master's open_id for edit permission grant
//
// Usage from wrapper:
//   const tracker = require('./issue_tracker');
//   await tracker.recordIssues(signals, cycleTag, sessionSummary);
//
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const WORKSPACE_ROOT = path.resolve(__dirname, '../..');
const STATE_FILE = path.join(WORKSPACE_ROOT, 'memory', 'evolver_issue_doc.json');
const CREATE_SCRIPT = path.join(WORKSPACE_ROOT, 'skills', 'feishu-doc', 'create.js');
const APPEND_SCRIPT = path.join(WORKSPACE_ROOT, 'skills', 'feishu-doc', 'append_simple.js');

function loadState() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
        }
    } catch (e) {}
    return null;
}

function saveState(state) {
    try {
        const dir = path.dirname(STATE_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    } catch (e) {
        console.error('[IssueTracker] Failed to save state:', e.message);
    }
}

function ensureDoc() {
    // Check if we already have a doc token
    let state = loadState();
    if (state && state.doc_token) return state.doc_token;

    // Check env var
    const envToken = process.env.EVOLVER_ISSUE_DOC_TOKEN;
    if (envToken) {
        saveState({ doc_token: envToken, created_at: new Date().toISOString() });
        return envToken;
    }

    // Create new doc
    if (!fs.existsSync(CREATE_SCRIPT)) {
        console.error('[IssueTracker] feishu-doc/create.js not found, cannot create issue doc');
        return null;
    }

    try {
        const masterId = process.env.OPENCLAW_MASTER_ID || '';
        const grantArg = masterId ? ` --grant "${masterId}"` : '';
        const result = execSync(
            `node "${CREATE_SCRIPT}" --title "Evolver Issue Tracker"${grantArg}`,
            { encoding: 'utf8', timeout: 30000, cwd: WORKSPACE_ROOT, windowsHide: true }
        );
        const doc = JSON.parse(result);
        const token = doc.doc_token;
        if (!token) throw new Error('No doc_token in response');

        console.log(`[IssueTracker] Created issue doc: ${doc.url}`);
        saveState({
            doc_token: token,
            url: doc.url,
            created_at: new Date().toISOString(),
            granted_to: doc.granted_to
        });
        return token;
    } catch (e) {
        console.error('[IssueTracker] Failed to create doc:', e.message);
        return null;
    }
}

function appendToDoc(docToken, markdown) {
    if (!fs.existsSync(APPEND_SCRIPT)) {
        console.error('[IssueTracker] feishu-doc/append_simple.js not found');
        return false;
    }

    try {
        const os = require('os');
        const tmpFile = path.join(os.tmpdir(), `evolver_issue_${Date.now()}.md`);
        fs.writeFileSync(tmpFile, markdown);
        execSync(
            `node "${APPEND_SCRIPT}" --doc_token "${docToken}" --file "${tmpFile}"`,
            { encoding: 'utf8', timeout: 30000, cwd: WORKSPACE_ROOT, windowsHide: true }
        );
        try { fs.unlinkSync(tmpFile); } catch (_) {}
        return true;
    } catch (e) {
        console.error('[IssueTracker] Failed to append:', e.message);
        return false;
    }
}

async function recordIssues(signals, cycleTag, extraContext) {
    if (!signals || signals.length === 0) return;

    // Only record actionable signals (skip cosmetic ones)
    const actionable = signals.filter(s =>
        s !== 'stable_success_plateau' &&
        s !== 'user_missing' &&
        s !== 'memory_missing'
    );
    if (actionable.length === 0) return;

    const docToken = ensureDoc();
    if (!docToken) return;

    const now = new Date().toISOString();
    const lines = [
        `### Cycle #${cycleTag} | ${now}`,
        '',
        '**Signals detected:**',
        ...actionable.map(s => `- \`${s}\``),
    ];

    if (extraContext) {
        lines.push('', '**Context:**', extraContext.slice(0, 500));
    }

    lines.push('', '---', '');

    const markdown = lines.join('\n');
    const ok = appendToDoc(docToken, markdown);
    if (ok) {
        console.log(`[IssueTracker] Recorded ${actionable.length} issues for Cycle #${cycleTag}`);
    }
}

function getDocUrl() {
    const state = loadState();
    return state && state.url ? state.url : null;
}

if (require.main === module) {
    // CLI test: node issue_tracker.js --test
    const args = process.argv.slice(2);
    if (args.includes('--test')) {
        recordIssues(
            ['log_error', 'unsupported_input_type', 'errsig:test error'],
            'TEST',
            'Manual test of issue tracker'
        ).then(() => console.log('Done. Doc URL:', getDocUrl()));
    } else {
        console.log('Usage: node issue_tracker.js --test');
        console.log('State:', JSON.stringify(loadState(), null, 2));
    }
}

module.exports = { recordIssues, getDocUrl, ensureDoc };
