#!/usr/bin/env node

/**
 * Monitoring utilities for Tide Watch
 * Helpers for parsing configuration and generating warnings
 */

/**
 * Parse monitoring configuration from AGENTS.md content
 * @param {string} content - AGENTS.md file content
 * @returns {Object} Parsed configuration
 */
function parseMonitoringConfig(content) {
  const config = {
    checkFrequency: 60, // default: 1 hour in minutes
    thresholds: [75, 85, 90, 95], // default thresholds
    autoBackup: {
      enabled: true,
      triggerAt: [90, 95],
      retention: 7,
      compress: false
    }
  };

  // Parse check frequency
  const frequencyMatch = content.match(/Check frequency:\s*\*\*Every\s+(\d+)\s+(min(?:ute)?s?|h(?:ou)?rs?)\*\*/i);
  if (frequencyMatch) {
    const value = parseInt(frequencyMatch[1], 10);
    const unit = frequencyMatch[2].toLowerCase();
    
    if (unit.startsWith('h')) {
      config.checkFrequency = value * 60;
    } else {
      config.checkFrequency = value;
    }
  }
  
  // Check for manual mode
  if (content.match(/Check frequency:\s*\*\*manual\*\*/i)) {
    config.checkFrequency = null; // null = manual mode
  }

  // Parse warning thresholds
  const thresholdMatches = content.matchAll(/\*\*(\d+)%\*\*\s*[:\-]?\s*(?:🟡|🟠|🔴|🚨)/g);
  const parsedThresholds = [];
  
  for (const match of thresholdMatches) {
    const threshold = parseInt(match[1], 10);
    if (threshold >= 50 && threshold <= 99) {
      parsedThresholds.push(threshold);
    }
  }
  
  if (parsedThresholds.length >= 2) {
    // Validate ascending order
    const sorted = [...parsedThresholds].sort((a, b) => a - b);
    if (JSON.stringify(sorted) === JSON.stringify(parsedThresholds)) {
      config.thresholds = parsedThresholds;
    }
  }

  // Parse auto-backup settings
  const backupEnabledMatch = content.match(/Enabled:\s*(true|false)/i);
  if (backupEnabledMatch) {
    config.autoBackup.enabled = backupEnabledMatch[1].toLowerCase() === 'true';
  }

  const backupThresholdsMatch = content.match(/Trigger at thresholds:\s*\[([^\]]+)\]/);
  if (backupThresholdsMatch) {
    const triggers = backupThresholdsMatch[1]
      .split(',')
      .map(s => parseInt(s.trim(), 10))
      .filter(n => !isNaN(n));
    
    if (triggers.length > 0) {
      config.autoBackup.triggerAt = triggers;
    }
  }

  const retentionMatch = content.match(/Retention:\s*(\d+)\s*days?/i);
  if (retentionMatch) {
    config.autoBackup.retention = parseInt(retentionMatch[1], 10);
  }

  const compressMatch = content.match(/Compress:\s*(true|false)/i);
  if (compressMatch) {
    config.autoBackup.compress = compressMatch[1].toLowerCase() === 'true';
  }

  return config;
}

/**
 * Determine which threshold was crossed (if any)
 * @param {number} currentPercentage - Current capacity percentage
 * @param {Array<number>} thresholds - Configured thresholds
 * @param {Array<number>} warnedThresholds - Thresholds already warned about
 * @returns {number|null} Threshold that was crossed, or null
 */
function checkThresholdCrossed(currentPercentage, thresholds, warnedThresholds = []) {
  // Find the highest threshold that's been crossed but not yet warned
  for (let i = thresholds.length - 1; i >= 0; i--) {
    const threshold = thresholds[i];
    if (currentPercentage >= threshold && !warnedThresholds.includes(threshold)) {
      return threshold;
    }
  }
  return null;
}

/**
 * Generate warning message for a threshold
 * @param {number} threshold - Threshold percentage
 * @param {Array<number>} thresholds - All configured thresholds
 * @param {number} tokensUsed - Tokens used
 * @param {number} tokensMax - Maximum tokens
 * @param {string} channel - Channel name (optional)
 * @returns {string} Warning message
 */
function generateWarningMessage(threshold, thresholds, tokensUsed, tokensMax, channel = null) {
  const thresholdIndex = thresholds.indexOf(threshold);
  const isFirst = thresholdIndex === 0;
  const isLast = thresholdIndex === thresholds.length - 1;
  const isSecondToLast = thresholdIndex === thresholds.length - 2;
  
  // Determine severity emoji
  let emoji;
  if (isLast) {
    emoji = '🚨';
  } else if (isSecondToLast) {
    emoji = '🔴';
  } else if (isFirst) {
    emoji = '🟡';
  } else {
    emoji = '🟠';
  }
  
  // Build message
  const lines = [];
  
  // Header
  if (isLast) {
    lines.push(`${emoji} **CRITICAL: Context at ${threshold}%!**`);
  } else if (isSecondToLast) {
    lines.push(`${emoji} **Context at ${threshold}%!**`);
  } else if (isFirst) {
    lines.push(`${emoji} Heads up: Context at ${threshold}%.`);
  } else {
    lines.push(`${emoji} Context at ${threshold}%.`);
  }
  
  // Capacity details
  lines.push(`Tokens: ${tokensUsed.toLocaleString()} / ${tokensMax.toLocaleString()}`);
  if (channel) {
    lines.push(`Session: ${channel}`);
  }
  
  lines.push(''); // blank line
  
  // Recommendations based on severity
  if (isLast) {
    lines.push('**Save important info to memory NOW and reset.**');
    lines.push('Session will lock at 100% capacity.');
  } else if (isSecondToLast) {
    lines.push('**Session will lock soon! Ready to help you reset?**');
    lines.push('Recommend finishing current task and resetting session.');
  } else if (thresholdIndex === thresholds.length - 3) {
    lines.push('**Recommend finishing current task and resetting session.**');
  } else if (isFirst) {
    lines.push('Consider wrapping up or switching channels soon.');
  } else {
    lines.push('Consider wrapping up soon and switching to a fresh session.');
  }
  
  return lines.join('\n');
}

/**
 * Determine if auto-backup should be triggered
 * @param {number} currentPercentage - Current capacity percentage
 * @param {Object} autoBackupConfig - Auto-backup configuration
 * @param {Array<number>} backedUpThresholds - Thresholds already backed up
 * @returns {number|null} Threshold that should trigger backup, or null
 */
function shouldTriggerBackup(currentPercentage, autoBackupConfig, backedUpThresholds = []) {
  if (!autoBackupConfig.enabled) {
    return null;
  }
  
  // Find the highest backup trigger threshold that's been crossed but not yet backed up
  for (let i = autoBackupConfig.triggerAt.length - 1; i >= 0; i--) {
    const threshold = autoBackupConfig.triggerAt[i];
    if (currentPercentage >= threshold && !backedUpThresholds.includes(threshold)) {
      return threshold;
    }
  }
  
  return null;
}

/**
 * Generate session reset prompt with context preservation
 * @param {string} sessionId - Session identifier
 * @param {Object} sessionData - Current session data
 * @returns {string} Reset prompt
 */
function generateResetPrompt(sessionId, sessionData = {}) {
  const lines = [];
  
  lines.push('## Session Reset with Context Preservation');
  lines.push('');
  lines.push('**Before resetting:**');
  lines.push('1. ✅ Save current work to memory/YYYY-MM-DD.md');
  lines.push('2. ✅ Backup session file (if not already backed up)');
  lines.push('3. ✅ Note any pending tasks or decisions');
  lines.push('');
  lines.push('**Reset command:**');
  lines.push('```');
  lines.push('New session, please');
  lines.push('```');
  lines.push('');
  lines.push('**After reset:**');
  lines.push('1. Review memory/YYYY-MM-DD.md for context');
  lines.push('2. Continue from where you left off');
  
  if (sessionData.channel) {
    lines.push('');
    lines.push(`**Alternative:** Switch to lower-capacity session`);
    lines.push(`Current session: ${sessionData.channel} (${sessionData.percentage}%)`);
  }
  
  return lines.join('\n');
}

module.exports = {
  parseMonitoringConfig,
  checkThresholdCrossed,
  generateWarningMessage,
  shouldTriggerBackup,
  generateResetPrompt
};
