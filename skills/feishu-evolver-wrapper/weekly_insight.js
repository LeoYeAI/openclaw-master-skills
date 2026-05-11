#!/usr/bin/env node
/**
 * Weekly Evolution Insight & Trend Analysis
 * Analyzes GEP events to detect stagnation, hotspots, and innovation trends.
 * Version: 1.0.2 (Cycle #3321 Retry 3)
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE_ROOT = path.resolve(__dirname, '../../');
const EVENTS_FILE = path.join(WORKSPACE_ROOT, 'assets/gep/events.jsonl');
const OUTPUT_FILE = path.join(WORKSPACE_ROOT, 'logs/weekly_insight_report.md');

function analyze() {
    console.log(`[Insight] Reading events from ${EVENTS_FILE}...`);
    
    if (!fs.existsSync(EVENTS_FILE)) {
        console.error("Error: Events file not found.");
        return;
    }

    const events = [];
    const fileContent = fs.readFileSync(EVENTS_FILE, 'utf8');
    const lines = fileContent.split('\n').filter(Boolean);
    
    lines.forEach(line => {
        try {
            const obj = JSON.parse(line);
            if (obj.type === 'EvolutionEvent') {
                events.push(obj);
            }
        } catch (e) {}
    });

    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    // Filter last 7 days
    const weeklyEvents = events.filter(e => {
        const ts = parseInt(e.id.replace('evt_', ''));
        return ts >= oneWeekAgo.getTime();
    });

    const total = weeklyEvents.length;
    if (total === 0) {
        console.log("No events in the last 7 days.");
        return;
    }

    // 1. Innovation Ratio
    const intents = { innovate: 0, repair: 0, optimize: 0 };
    weeklyEvents.forEach(e => {
        if (intents[e.intent] !== undefined) intents[e.intent]++;
    });
    const innovationRatio = ((intents.innovate / total) * 100).toFixed(1);

    // 2. Success Rate
    const successful = weeklyEvents.filter(e => e.outcome && e.outcome.status === 'success').length;
    const successRate = ((successful / total) * 100).toFixed(1);

    // 3. File Hotspots (Which files are touched most?)
    // Note: This requires 'blast_radius' to have file details, but standard event only has count.
    // However, some events might log details in 'meta' or we can infer from 'gene'.
    // Actually, 'blast_radius' in standard GEP is just { files: N, lines: N }.
    // We can't track specific files unless we parse git logs, which is expensive.
    // But we CAN track **Genes**.
    
    const geneUsage = {};
    const geneFailures = {};
    
    weeklyEvents.forEach(e => {
        const geneId = (e.genes_used && e.genes_used[0]) || 'unknown';
        geneUsage[geneId] = (geneUsage[geneId] || 0) + 1;
        
        if (e.outcome && e.outcome.status === 'failed') {
            geneFailures[geneId] = (geneFailures[geneId] || 0) + 1;
        }
    });

    const topGenes = Object.entries(geneUsage)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    const topFailures = Object.entries(geneFailures)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3);

    // --- Generate Report ---
    let md = `# 🧬 Weekly Evolution Insight\n`;
    md += `> Period: ${oneWeekAgo.toISOString().split('T')[0]} to ${now.toISOString().split('T')[0]}\n\n`;
    
    md += `## 📊 Key Metrics\n`;
    md += `- **Total Cycles**: ${total}\n`;
    md += `- **Success Rate**: ${successRate}% ${successRate < 80 ? '⚠️' : '✅'}\n`;
    md += `- **Innovation Ratio**: ${innovationRatio}% (Target: >30%)\n`;
    md += `  - ✨ Innovate: ${intents.innovate}\n`;
    md += `  - 🔧 Repair: ${intents.repair}\n`;
    md += `  - ⚡ Optimize: ${intents.optimize}\n\n`;

    md += `## 🧬 Gene Performance\n`;
    md += `| Gene ID | Usage | Failures | Status |\n`;
    md += `|---|---|---|---|\n`;
    
    for (const [gene, count] of topGenes) {
        const fails = geneFailures[gene] || 0;
        const failRate = ((fails / count) * 100).toFixed(0);
        let status = '✅';
        if (failRate > 20) status = '⚠️';
        if (failRate > 50) status = '❌';
        
        md += `| \`${gene}\` | ${count} | ${fails} (${failRate}%) | ${status} |\n`;
    }
    
    md += `\n## 🚨 Stagnation Signals\n`;
    if (intents.innovate === 0) {
        md += `- ⚠️ **No Innovation**: Zero innovation cycles in the last 7 days.\n`;
    }
    if (topFailures.length > 0 && topFailures[0][1] > 2) {
        md += `- ⚠️ **Recurring Failures**: Gene \`${topFailures[0][0]}\` failed ${topFailures[0][1]} times.\n`;
    }
    if (total < 5) {
        md += `- ⚠️ **Low Activity**: Only ${total} cycles this week.\n`;
    }
    if (!md.includes('⚠️')) {
        md += `- ✅ No stagnation signals detected.\n`;
    }

    // Output
    fs.writeFileSync(OUTPUT_FILE, md);
    console.log(`[Insight] Report saved to ${OUTPUT_FILE}`);
    console.log(md);
}

analyze();
