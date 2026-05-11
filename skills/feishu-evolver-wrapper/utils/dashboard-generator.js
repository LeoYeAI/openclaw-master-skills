const fs = require('fs');
const path = require('path');

function generateDashboardCard(stats, systemInfo, cycleInfo) {
    const { total, successRate, intents, recent, avgFiles, avgLines, avgRigor } = stats;
    const { proc, mem, uptime, load, disk, loopStatus } = systemInfo;
    const { id, duration } = cycleInfo;

    // --- ALERTS ---
    const alerts = [];
    if (systemInfo.errorAlert) alerts.push(systemInfo.errorAlert);
    if (systemInfo.healthAlert) alerts.push(systemInfo.healthAlert);

    // Header color based on success rate and loop status
    let headerColor = 'blue';
    if (loopStatus.includes('STOPPED') || loopStatus.includes('OFF')) headerColor = 'grey';
    else if (parseFloat(successRate) < 80) headerColor = 'orange';
    else if (parseFloat(successRate) < 50) headerColor = 'red';
    else headerColor = 'green'; // Healthy and running

    const elements = [];

    if (alerts.length > 0) {
        elements.push({
            tag: 'div',
            text: {
                tag: 'lark_md',
                content: alerts.join('\n\n')
            }
        });
        elements.push({ tag: 'hr' });
        headerColor = 'red'; // Override color
    }

    // 1. System Vital Signs (Fields)
    elements.push({
        tag: 'div',
        fields: [
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Status**: ${loopStatus}` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Uptime**: ${Math.floor(uptime / 3600)}h` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Memory**: ${mem}MB` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Load**: ${load}` }
            }
        ]
    });

    elements.push({ tag: 'hr' });

    // 2. Evolution Stats (Fields) - ENHANCED
    elements.push({
        tag: 'div',
        fields: [
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Total Cycles**: ${total}` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Success Rate**: ${successRate}%` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Intents**: ✨${intents.innovate} 🔧${intents.repair} ⚡${intents.optimize}` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Last Cycle**: #${id} (${duration})` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Avg Blast**: ${avgFiles}f / ${avgLines}L` }
            },
            {
                is_short: true,
                text: { tag: 'lark_md', content: `**Avg Rigor**: ${avgRigor || 'N/A'}` }
            }
        ]
    });

    elements.push({ tag: 'hr' });

    // 3. Recent Activity Timeline
    let timelineMd = recent.map(e => {
        const icon = e.intent === 'innovate' ? '✨' : (e.intent === 'repair' ? '🔧' : '⚡');
        const statusIcon = e.status === 'success' ? '✅' : '❌';
        return `${statusIcon} **#${e.id}** ${icon} ${e.summary || 'No summary'}`;
    }).join('\n');

    if (!timelineMd) timelineMd = '_No recent activity_';

    elements.push({
        tag: 'div',
        text: {
            tag: 'lark_md',
            content: `**Recent Activity**:\n${timelineMd}`
        }
    });

    // 4. Action hint (if needed)
    if (loopStatus.includes('STOPPED')) {
        elements.push({
            tag: 'note',
            elements: [{ tag: 'plain_text', content: '⚠️ Evolver loop is stopped. Run "lifecycle.js start" to resume.' }]
        });
    }

    return {
        header: {
            template: headerColor,
            title: { tag: 'plain_text', content: '🧬 Evolver Capability Dashboard' }
        },
        elements: elements
    };
}

module.exports = { generateDashboardCard };
