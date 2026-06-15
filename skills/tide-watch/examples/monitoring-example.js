#!/usr/bin/env node

/**
 * Example: Using Tide Watch monitoring utilities
 * 
 * This demonstrates how to use the monitoring functions in your own
 * OpenClaw agent scripts or heartbeat implementations.
 */

const fs = require('fs');
const path = require('path');
const {
  parseMonitoringConfig,
  checkThresholdCrossed,
  generateWarningMessage,
  shouldTriggerBackup,
  generateResetPrompt
} = require('../lib/monitoring');

// Example 1: Parse configuration from AGENTS.md
console.log('=== Example 1: Parse Configuration ===\n');

const agentsContent = fs.readFileSync(
  path.join(__dirname, '..', 'AGENTS.md.template'),
  'utf8'
);

const config = parseMonitoringConfig(agentsContent);
console.log('Parsed configuration:');
console.log('- Check frequency:', config.checkFrequency, 'minutes');
console.log('- Thresholds:', config.thresholds.join(', ') + '%');
console.log('- Auto-backup enabled:', config.autoBackup.enabled);
console.log('- Backup triggers:', config.autoBackup.triggerAt.join(', ') + '%');
console.log('- Retention:', config.autoBackup.retention, 'days');
console.log('');

// Example 2: Check if threshold was crossed
console.log('=== Example 2: Check Threshold Crossing ===\n');

const currentPercentage = 87.5;
const warnedThresholds = [75, 85]; // Already warned about these

const crossedThreshold = checkThresholdCrossed(
  currentPercentage,
  config.thresholds,
  warnedThresholds
);

if (crossedThreshold) {
  console.log(`Threshold crossed: ${crossedThreshold}%`);
  console.log(`Current capacity: ${currentPercentage}%`);
  console.log('');
  
  // Example 3: Generate warning message
  console.log('=== Example 3: Generate Warning Message ===\n');
  
  const warning = generateWarningMessage(
    crossedThreshold,
    config.thresholds,
    175000,
    200000,
    'discord/#dev-work'
  );
  
  console.log(warning);
  console.log('');
} else {
  console.log('No new thresholds crossed.');
  console.log('');
}

// Example 4: Check if backup should be triggered
console.log('=== Example 4: Check Backup Trigger ===\n');

const backedUpThresholds = []; // No backups yet
const backupThreshold = shouldTriggerBackup(
  currentPercentage,
  config.autoBackup,
  backedUpThresholds
);

if (backupThreshold) {
  console.log(`Backup should be triggered at ${backupThreshold}%`);
  console.log('');
} else {
  console.log('No backup needed at current capacity.');
  console.log('');
}

// Example 5: Generate reset prompt
console.log('=== Example 5: Generate Reset Prompt ===\n');

const resetPrompt = generateResetPrompt('test-session-123', {
  channel: 'discord/#dev-work',
  percentage: 87.5
});

console.log(resetPrompt);
console.log('');

// Example 6: Simulated monitoring workflow
console.log('=== Example 6: Complete Monitoring Workflow ===\n');

// Simulate session state
let sessionState = {
  tokensUsed: 150000,
  tokensMax: 200000,
  warnedThresholds: [],
  backedUpThresholds: []
};

function checkAndWarn() {
  const percentage = (sessionState.tokensUsed / sessionState.tokensMax) * 100;
  
  console.log(`Current capacity: ${percentage.toFixed(1)}%`);
  console.log(`Tokens: ${sessionState.tokensUsed.toLocaleString()} / ${sessionState.tokensMax.toLocaleString()}`);
  
  // Check if threshold crossed
  const threshold = checkThresholdCrossed(
    percentage,
    config.thresholds,
    sessionState.warnedThresholds
  );
  
  if (threshold) {
    console.log(`\nThreshold crossed: ${threshold}%`);
    sessionState.warnedThresholds.push(threshold);
    
    const warning = generateWarningMessage(
      threshold,
      config.thresholds,
      sessionState.tokensUsed,
      sessionState.tokensMax
    );
    
    console.log('\n' + warning + '\n');
    
    // Check if backup needed
    const backupTrigger = shouldTriggerBackup(
      percentage,
      config.autoBackup,
      sessionState.backedUpThresholds
    );
    
    if (backupTrigger) {
      console.log(`✅ Backup triggered at ${backupTrigger}%`);
      sessionState.backedUpThresholds.push(backupTrigger);
    }
  } else {
    console.log('No new threshold crossed.');
  }
  
  console.log('');
}

// Simulate capacity increasing over time
console.log('Initial check:');
checkAndWarn();

sessionState.tokensUsed = 170000;
console.log('After more conversation:');
checkAndWarn();

sessionState.tokensUsed = 180000;
console.log('After intensive work:');
checkAndWarn();

sessionState.tokensUsed = 190000;
console.log('Critical capacity:');
checkAndWarn();

console.log('=== End of Examples ===');
