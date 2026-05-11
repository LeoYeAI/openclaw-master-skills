#!/usr/bin/env node
/**
 * OpenClaw notification helper
 * Sends messages to user via OpenClaw CLI
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { success, error, info, warning } from './utils.js';

const execAsync = promisify(exec);

/**
 * ============================================================================
 * TYPE DEFINITIONS
 * ============================================================================
 */

/**
 * @typedef {Object} ScheduleEvery
 * @property {'every'} kind
 * @property {number} everyMs
 */

/**
 * @typedef {Object} ScheduleCron
 * @property {'cron'} kind
 * @property {string} expr
 * @property {string} [tz]
 */

/**
 * @typedef {Object} ScheduleAt
 * @property {'at'} kind
 * @property {string} at
 */

/**
 * @typedef {ScheduleEvery | ScheduleCron | ScheduleAt | string} Schedule
 */

/**
 * @typedef {Object} SystemEventPayload
 * @property {'systemEvent'} kind
 * @property {string} text
 */

/**
 * @typedef {Object} AgentTurnPayload
 * @property {'agentTurn'} kind
 * @property {string} message
 * @property {string} [model]
 * @property {string} [thinking]
 * @property {number} [timeoutSeconds]
 */

/**
 * @typedef {SystemEventPayload | AgentTurnPayload} Payload
 */

/**
 * @typedef {Object} DeliveryConfig
 * @property {'announce' | 'none'} mode
 * @property {string} [channel]
 * @property {string} [to]
 * @property {boolean} [bestEffort]
 */

/**
 * @typedef {Object} CronjobConfig
 * @property {string} name
 * @property {Schedule} schedule
 * @property {Payload} payload
 * @property {'main' | 'isolated'} [sessionTarget]
 * @property {'now' | 'next-heartbeat'} [wakeMode]
 * @property {DeliveryConfig} [delivery]
 * @property {boolean} [deleteAfterRun]
 * @property {boolean} [enabled]
 * @property {string} [agentId]
 */

/**
 * ============================================================================
 * NOTIFICATION FUNCTIONS
 * ============================================================================
 */

/**
 * Send message to user via OpenClaw CLI
 * Uses system event to send message to most recent channel
 * @param {string} message - Message to send
 * @param {string} [sessionTarget='main'] - Session target
 * @returns {Promise<boolean>} - Success status
 */
export async function sendMessageToUser(message, sessionTarget = 'main') {
  try {
    // Escape the message for shell - replace double quotes with escaped quotes
    const escapedMessage = message.replace(/"/g, '\\"').replace(/\$/g, '\\$').replace(/`/g, '\\`');
    
    // Build openclaw command with correct syntax
    const command = `openclaw system event --mode now --text "${escapedMessage}"`;
    
    // Execute command
    await execAsync(command);
    
    return true;
  } catch (e) {
    error(`Failed to send message via OpenClaw: ${e.message}`);
    // Fallback: just log to console
    console.log('\n' + '='.repeat(50));
    console.log('MESSAGE TO USER:');
    console.log(message);
    console.log('='.repeat(50) + '\n');
    return false;
  }
}

/**
 * Check if OpenClaw CLI is available
 * @returns {Promise<boolean>} - True if OpenClaw CLI is available
 */
export async function isOpenClawAvailable() {
  try {
    await execAsync('which openclaw');
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Check if a cron job exists
 * @param {string} name - Job name to check
 * @returns {Promise<boolean>} - True if job exists
 */
export async function cronJobExists(name) {
  try {
    const { stdout } = await execAsync('openclaw cron list', { 
      encoding: 'utf8',
      timeout: 10000  // 10 second timeout to prevent hanging
    });
    // Check if the job name appears in the list
    return stdout.includes(name);
  } catch (e) {
    error(`Failed to check cron jobs: ${e.message}`);
    return false;
  }
}

/**
 * Create a cron job via OpenClaw CLI
 * @param {string} name - Job name
 * @param {string} schedule - Cron schedule expression
 * @param {string} payload - Command to execute (for systemEvent) or message (for agentTurn)
 * @param {'main' | 'isolated'} [sessionTarget='main'] - Session target
 * @param {'now' | 'next-heartbeat' | null} [wakeMode=null] - Wake mode
 * @returns {Promise<boolean>} - Success status
 */
export async function addCronJob(name, schedule, payload, sessionTarget = 'main', wakeMode = null) {
  try {
    // Check if job already exists
    if (await cronJobExists(name)) {
      warning(`Cron job "${name}" already exists`);
      info('Skipping creation to avoid duplicates');
      return true; // Return true since job exists (desired state achieved)
    }
    
    let command;
    
    // Extract text from payload if it's in "systemEvent:text:..." format
    const text = payload.startsWith('systemEvent:text:') 
      ? payload.replace('systemEvent:text:', '')
      : payload;
    
    // Escape special characters for shell
    const escapedText = text.replace(/"/g, '\\"').replace(/\$/g, '\\$').replace(/`/g, '\\`');
    const escapedName = name.replace(/"/g, '\\"');
    
    // Determine wake mode
    const wakeFlag = wakeMode ? `--wake ${wakeMode}` : '';
    
    if (sessionTarget === 'main') {
      // Main session jobs use --system-event
      command = `openclaw cron add --name "${escapedName}" --cron "${schedule}" --session main --system-event "${escapedText}" ${wakeFlag}`.trim();
    } else {
      // Isolated session jobs use --message for agentTurn execution
      // Use --announce to deliver output back to main session
      // Use --wake now to deliver immediately to user (or specified wakeMode)
      const wake = wakeMode || 'now';
      command = `openclaw cron add --name "${escapedName}" --cron "${schedule}" --session isolated --message "${escapedText}" --wake ${wake}`;
    }
    
    await execAsync(command, { 
      encoding: 'utf8',
      timeout: 15000  // 15 second timeout
    });
    success(`Cron job created: ${name}`);
    return true;
  } catch (e) {
    error(`Failed to create cron job: ${e.message}`);
    if (e.stderr) {
      error(`Details: ${e.stderr}`);
    }
    return false;
  }
}

/**
 * Create a cron job with full configuration via OpenClaw tool call
 * Supports the complete job configuration format
 * @param {CronjobConfig} jobConfig - Full job configuration object
 * @returns {Promise<boolean>} - Success status
 */
export async function addCronJobAdvanced(jobConfig) {
  try {
    const {
      name,
      schedule,
      payload,
      sessionTarget = 'main',
      wakeMode = 'next-heartbeat',
      delivery,
      deleteAfterRun = false,
      enabled = true
    } = jobConfig;
    
    // Check if job already exists
    if (await cronJobExists(name)) {
      warning(`Cron job "${name}" already exists`);
      info('Skipping creation to avoid duplicates');
      return true;
    }
    
    // Build the command based on configuration
    let command;
    const escapedName = name.replace(/"/g, '\\"');
    
    // Handle schedule - support both string cron expressions and schedule objects
    let scheduleFlag;
    if (typeof schedule === 'string') {
      scheduleFlag = `--cron "${schedule}"`;
    } else if (schedule.kind === 'every') {
      scheduleFlag = `--every ${schedule.everyMs}ms`;
    } else if (schedule.kind === 'cron') {
      scheduleFlag = `--cron "${schedule.expr}"`;
      if (schedule.tz) {
        scheduleFlag += ` --tz "${schedule.tz}"`;
      }
    } else if (schedule.kind === 'at') {
      scheduleFlag = `--at "${schedule.at}"`;
    }
    
    // Determine session-specific flags
    if (sessionTarget === 'main') {
      // Main session with system event
      let text;
      if (typeof payload === 'string') {
        text = payload;
      } else if (payload.kind === 'systemEvent') {
        text = payload.text || '';
      } else {
        text = payload.message || '';
      }
      
      const escapedText = text.replace(/"/g, '\\"').replace(/\$/g, '\\$').replace(/`/g, '\\`');
      command = `openclaw cron add --name "${escapedName}" ${scheduleFlag} --session main --system-event "${escapedText}"`;
    } else {
      // Isolated session with agent turn
      let message;
      if (typeof payload === 'string') {
        message = payload;
      } else if (payload.kind === 'agentTurn') {
        message = payload.message || '';
      } else {
        message = payload.text || '';
      }
      
      const escapedMessage = message.replace(/"/g, '\\"').replace(/\$/g, '\\$').replace(/`/g, '\\`');
      
      command = `openclaw cron add --name "${escapedName}" ${scheduleFlag} --session isolated --message "${escapedMessage}"`;
      
      // Add delivery configuration if present
      if (delivery) {
        if (delivery.mode === 'announce' || !delivery.mode) {
          command += ' --announce';
          
          // Add channel if specified
          if (delivery.channel && delivery.channel !== 'last') {
            command += ` --channel ${delivery.channel}`;
            
            // Add target if specified
            if (delivery.to) {
              command += ` --to "${delivery.to}"`;
            }
          }
        } else if (delivery.mode === 'none') {
          // Don't add announce flag for 'none' mode
          command += ' --no-deliver';
        }
      }
    }
    
    // Add wake mode
    command += ` --wake ${wakeMode}`;
    
    // Add delete-after-run flag if specified
    if (deleteAfterRun) {
      command += ' --delete-after-run';
    }
    
    // Add enabled flag if false (default is true)
    if (!enabled) {
      command += ' --disabled';
    }
    
    await execAsync(command, {
      encoding: 'utf8',
      timeout: 15000
    });
    
    success(`Cron job created: ${name}`);
    return true;
  } catch (e) {
    error(`Failed to create cron job: ${e.message}`);
    if (e.stderr) {
      error(`Details: ${e.stderr}`);
    }
    return false;
  }
}

/**
 * Remove a cron job via OpenClaw CLI
 * @param {string} nameOrId - Job name or ID to remove
 * @returns {Promise<boolean>} - Success status
 */
export async function removeCronJob(nameOrId) {
  try {
    // First, try to find the job ID by name
    let jobId = nameOrId;
    
    // If it looks like a name (not a UUID), search for it in the job list
    if (!nameOrId.match(/^[0-9a-f-]{36}$/i)) {
      try {
        const { stdout: listOutput } = await execAsync('openclaw cron list --json --all', { 
          encoding: 'utf8',
          timeout: 10000
        });
        
        // Parse JSON output - API returns array directly
        const data = JSON.parse(listOutput);
        
        // Ensure data is an array
        const jobs = Array.isArray(data) ? data : (data.jobs || []);
        
        // Find job by name
        const job = jobs.find(j => j.name === nameOrId);
        if (job) {
          jobId = job.id;
        } else {
          warning(`Job not found: ${nameOrId}`);
          return false;
        }
      } catch (listError) {
        warning(`Could not list jobs to find ID: ${listError.message}`);
      }
    }
    
    // Remove by job ID
    const command = `openclaw cron remove ${jobId}`;
    
    await execAsync(command, { 
      encoding: 'utf8',
      timeout: 10000  // 10 second timeout
    });
    success(`Cron job removed: ${nameOrId}`);
    return true;
  } catch (e) {
    error(`Failed to remove cron job: ${e.message}`);
    return false;
  }
}

/**
 * List cron jobs via OpenClaw CLI
 * @returns {Promise<boolean>} - Success status
 */
export async function listCronJobs() {
  try {
    const { stdout } = await execAsync('openclaw cron list', { 
      encoding: 'utf8',
      timeout: 10000  // 10 second timeout
    });
    console.log(stdout);
    return true;
  } catch (e) {
    error(`Failed to list cron jobs: ${e.message}`);
    return false;
  }
}

/**
 * CLI Commands
 */
async function main() {
  const command = process.argv[2];
  
  // Check if OpenClaw is available
  if (!(await isOpenClawAvailable())) {
    error('OpenClaw CLI not found. Please install OpenClaw first.');
    info('Messages will be logged to console instead.');
  }
  
  try {
    switch (command) {
      case 'send': {
        const message = process.argv[3];
        const sessionTarget = process.argv[4] || 'main';
        
        if (!message) {
          error('Usage: node notify.js send <message> [sessionTarget]');
          process.exit(1);
        }
        
        await sendMessageToUser(message, sessionTarget);
        break;
      }
      
      case 'test': {
        const message = '🧪 Test message from ClawFriend!\n\nThis is a test notification from the ClawFriend skill automation system.';
        await sendMessageToUser(message);
        break;
      }
      
      case 'cron-add': {
        const name = process.argv[3];
        const schedule = process.argv[4];
        const payload = process.argv[5];
        const sessionTarget = process.argv[6] || 'main';
        
        if (!name || !schedule || !payload) {
          error('Usage: node notify.js cron-add <name> <schedule> <payload> [sessionTarget]');
          process.exit(1);
        }
        
        await addCronJob(name, schedule, payload, sessionTarget);
        break;
      }
      
      case 'cron-remove': {
        const name = process.argv[3];
        
        if (!name) {
          error('Usage: node notify.js cron-remove <name>');
          process.exit(1);
        }
        
        await removeCronJob(name);
        break;
      }
      
      case 'cron-list': {
        await listCronJobs();
        break;
      }
      
      default: {
        console.log('ClawFriend Notification Helper\n');
        console.log('Usage:');
        console.log('  node notify.js send <message> [sessionTarget]  - Send message to user');
        console.log('  node notify.js test                             - Send test message');
        console.log('  node notify.js cron-add <name> <schedule> <command> [sessionTarget]');
        console.log('  node notify.js cron-remove <name>              - Remove cron job');
        console.log('  node notify.js cron-list                       - List cron jobs');
        console.log('\nExamples:');
        console.log('  node notify.js send "Agent is now active!"');
        console.log('  node notify.js cron-add "ClawFriend Heartbeat" "*/15 * * * *" "Run heartbeat check" isolated');
        break;
      }
    }
  } catch (e) {
    error(e.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
