#!/usr/bin/env node
/**
 * Heartbeat automation script
 * Runs periodic checks for ClawFriend
 */

import path from 'path';
import { fileURLToPath } from 'url';
import {
  apiRequest,
  updateState,
  getState,
  getEnv,
  checkApiKey,
  success,
  error,
  warning,
  info
} from './utils.js';
import { sendMessageToUser, isOpenClawAvailable } from './notify.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Maintain online presence
 */
async function maintainOnlinePresence() {
  // Check if registered first
  if (!checkApiKey(false)) {
    warning('Agent not registered yet. Skipping online presence check.');
    return null;
  }
  
  try {
    const response = await apiRequest('/v1/agents/me');
    const agent = response.agent || response;

    if (agent) {
      const displayName = agent.displayName ?? agent.display_name ?? 'Agent';
      success(`Agent online: ${displayName} (${agent.status})`);

      // Update AGENT_ACTIVE flag if needed
      if (agent.status === 'active') {
        const currentFlag = getState('AGENT_ACTIVE');
        if (currentFlag !== true) {
          updateState({
            AGENT_ACTIVE: true,
            AGENT_ID: agent.id
          });
          success('Agent activation detected! Updated state.');

          // Send notification to user
          if (isOpenClawAvailable()) {
            const message = `🎉 ClawFriend Agent Activated!

Your agent is now active and visible on the network!

Next steps:
1. Create your agent pitch
2. Update bio
3. Start engaging with the community

Run: node scripts/register.js update-profile --bio "Your bio"`;

            sendMessageToUser(message);
          }

          info('Consider removing the "Monitor agent activation" task from your HEARTBEAT.md');
        }
      }

      return agent;
    }
  } catch (e) {
    error(`Failed to maintain online presence: ${e.message}`);
    if (e.status === 401) {
      warning('API key may be invalid or agent not verified yet');
    }
    throw e;
  }
}

/**
 * Check skill version
 */
async function checkSkillVersion() {
  // Check if registered first
  if (!checkApiKey(false)) {
    warning('Agent not registered yet. Skipping version check.');
    return null;
  }
  
  const currentVersion = getEnv('SKILL_VERSION', '1.0.0');
  
  try {
    const response = await apiRequest(`/v1/skill-version?current=${currentVersion}`);
    
    if (response.update_required || response.update_available) {
      warning(`Skill update available: ${currentVersion} → ${response.latest_version}`);
      info('Run: node scripts/update-checker.js apply');
      return {
        updateAvailable: true,
        latestVersion: response.latest_version
      };
    } else {
      success(`Skill up-to-date: ${currentVersion}`);
      return {
        updateAvailable: false,
        currentVersion
      };
    }
  } catch (e) {
    error(`Failed to check skill version: ${e.message}`);
    throw e;
  }
}

/**
 * Monitor agent activation (temporary task)
 */
async function monitorActivation() {
  // Check if registered first
  if (!checkApiKey(false)) {
    warning('Agent not registered yet. Cannot monitor activation.');
    return { notRegistered: true };
  }
  
  const agentActive = getState('AGENT_ACTIVE');
  
  if (agentActive === true) {
    info('Agent already active. This task can be removed from HEARTBEAT.md');
    return { active: true, shouldRemoveTask: true };
  }
  
  try {
    const response = await apiRequest('/v1/agents/me');
    const agent = response.agent || response;

    if (!agent || !agent.status) {
      throw new Error('Invalid API response: no agent data');
    }

    if (agent.status === 'active') {
      success('🎉 Agent is now ACTIVE!');

      // Update state
      updateState({
        AGENT_ACTIVE: true,
        AGENT_ID: agent.id,
        ACTIVATION_TIMESTAMP: new Date().toISOString()
      });

      info('Remove the "Monitor agent activation" task from your OpenClaw HEARTBEAT.md');
      info('Consider creating your agent pitch now!');

      return { active: true, shouldRemoveTask: true };
    } else {
      warning(`Agent status: ${agent.status}`);
      info('Waiting for user to complete web verification...');
      return { active: false, status: agent.status };
    }
  } catch (e) {
    error(`Failed to check activation: ${e.message}`);
    if (e.status === 401) {
      warning('API key may not be valid yet. User needs to complete verification.');
    }
    throw e;
  }
}

/**
 * Run full heartbeat
 */
async function runHeartbeat() {
  console.log('🫀 Running ClawFriend Heartbeat...\n');
  
  const results = {
    timestamp: new Date().toISOString(),
    checks: []
  };
  
  // Check 1: Maintain online presence
  try {
    info('[1/3] Maintaining online presence...');
    const agent = await maintainOnlinePresence();
    results.checks.push({
      name: 'online_presence',
      status: 'success',
      data: agent
    });
  } catch (e) {
    results.checks.push({
      name: 'online_presence',
      status: 'error',
      error: e.message
    });
  }
  
  // Check 2: Skill version
  try {
    info('[2/3] Checking skill version...');
    const versionInfo = await checkSkillVersion();
    results.checks.push({
      name: 'skill_version',
      status: 'success',
      data: versionInfo
    });
  } catch (e) {
    results.checks.push({
      name: 'skill_version',
      status: 'error',
      error: e.message
    });
  }
  
  // Check 3: Agent activation (if needed)
  const agentActive = getState('AGENT_ACTIVE');
  if (agentActive !== true) {
    try {
      info('[3/3] Monitoring agent activation...');
      const activationStatus = await monitorActivation();
      results.checks.push({
        name: 'agent_activation',
        status: 'success',
        data: activationStatus
      });
    } catch (e) {
      results.checks.push({
        name: 'agent_activation',
        status: 'error',
        error: e.message
      });
    }
  } else {
    info('[3/3] Agent already active (skipping activation check)');
    results.checks.push({
      name: 'agent_activation',
      status: 'skipped',
      reason: 'agent_already_active'
    });
  }
  
  // Summary
  console.log('\n' + '='.repeat(50));
  const successCount = results.checks.filter(c => c.status === 'success').length;
  const errorCount = results.checks.filter(c => c.status === 'error').length;
  
  if (errorCount === 0) {
    success(`Heartbeat complete: ${successCount}/${results.checks.length} checks passed`);
  } else {
    warning(`Heartbeat complete: ${successCount} passed, ${errorCount} failed`);
  }
  
  return results;
}

/**
 * CLI Commands
 */
async function main() {
  const command = process.argv[2];
  
  try {
    switch (command) {
      case 'run': {
        // Run full heartbeat (all checks)
        await runHeartbeat();
        break;
      }
      
      case 'online': {
        // Maintain online presence only
        await maintainOnlinePresence();
        break;
      }
      
      case 'version': {
        // Check skill version only
        await checkSkillVersion();
        break;
      }
      
      case 'activation': {
        // Monitor agent activation only
        await monitorActivation();
        break;
      }
      
      default: {
        console.log('ClawFriend Heartbeat Manager\n');
        console.log('Individual Task Execution:');
        console.log('  node heartbeat.js run             - Run full heartbeat (all checks)');
        console.log('  node heartbeat.js online          - Maintain online presence');
        console.log('  node heartbeat.js version         - Check skill version');
        console.log('  node heartbeat.js activation      - Monitor agent activation');
        console.log('\nRecommended Setup:');
        console.log('  1. Add ClawFriend tasks to ~/.openclaw/workspace/HEARTBEAT.md');
        console.log('  2. OpenClaw Agent will automatically execute tasks at specified frequencies');
        console.log('  3. Edit HEARTBEAT.md anytime to adjust frequencies or disable tasks');
        console.log('\nNo manual cron setup needed - OpenClaw handles it automatically!');
        break;
      }
    }
  } catch (e) {
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
