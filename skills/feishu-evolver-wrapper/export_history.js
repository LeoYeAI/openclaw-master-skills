#!/usr/bin/env node
// Export evolution history to a Feishu Doc.
// Moved from evolver core to feishu-evolver-wrapper (Feishu-specific, should not live in core).
//
// Usage: FEISHU_EVOLVER_DOC_TOKEN=xxx node export_history.js
//
const fs = require('fs');
const path = require('path');

const WORKSPACE_ROOT = path.resolve(__dirname, '../..');
try {
    require('dotenv').config({ path: path.join(WORKSPACE_ROOT, '.env') });
} catch (e) {}

const DOC_TOKEN = process.env.FEISHU_EVOLVER_DOC_TOKEN || '';
const LOG_FILE = path.join(WORKSPACE_ROOT, 'memory', 'mad_dog_evolution.log');
const TOKEN_FILE = path.join(WORKSPACE_ROOT, 'memory', 'feishu_token.json');

async function exportEvolutionHistory() {
    if (!DOC_TOKEN) return console.error("Error: FEISHU_EVOLVER_DOC_TOKEN env var not set");

    let token;
    try { token = JSON.parse(fs.readFileSync(TOKEN_FILE)).token; } catch(e) {}
    if (!token) return console.error("Error: No Feishu access token in " + TOKEN_FILE);

    let logContent = '';
    try { logContent = fs.readFileSync(LOG_FILE, 'utf8'); } catch(e) { return console.error("No log file: " + LOG_FILE); }

    // Parse evolution cycles from log
    const cycles = [];
    const regex = /Evolution Cycle #(\d+)([\s\S]*?)(?:Cycle End|System:)/g;
    let match;
    while ((match = regex.exec(logContent)) !== null) {
        let details = match[2].trim();
        details = details.replace(/\[.*?\]/g, '').replace(/\n+/g, '\n').trim();
        if (details.length > 500) details = details.substring(0, 500) + '...';
        cycles.push({ id: match[1], content: details });
    }

    if (cycles.length === 0) {
        cycles.push({ id: "Unknown", content: logContent.split('\n').slice(-50).join('\n') });
    }

    cycles.reverse();

    // Format for Feishu Doc
    let markdown = "# Evolution History\n\n> Auto-generated report of self-improvement cycles.\n\n";
    const chunks = [];
    let currentChunk = markdown;

    for (const cycle of cycles) {
        const entry = `### Cycle #${cycle.id}\n${cycle.content}\n\n---\n\n`;
        if (currentChunk.length + entry.length > 8000) {
            chunks.push(currentChunk);
            currentChunk = entry;
        } else {
            currentChunk += entry;
        }
    }
    chunks.push(currentChunk);

    console.log(`Exporting ${chunks.length} chunks to Feishu Doc ${DOC_TOKEN}...`);

    for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        console.log(`Uploading Chunk ${i+1}/${chunks.length}...`);

        const blocks = [{
            block_type: 14,
            code: {
                style: { language: 1 },
                elements: [{ text_run: { content: chunk, text_element_style: {} } }]
            }
        }];

        const res = await fetch(`https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks/${DOC_TOKEN}/children`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({ children: blocks })
        });

        const data = await res.json();
        if (data.code !== 0) console.error(`Chunk ${i+1} failed:`, JSON.stringify(data));
        else console.log(`Chunk ${i+1} success.`);

        await new Promise(r => setTimeout(r, 500));
    }

    console.log('Export complete.');
}

if (require.main === module) {
    exportEvolutionHistory();
}

module.exports = { exportEvolutionHistory };
