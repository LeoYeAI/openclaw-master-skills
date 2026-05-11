#!/usr/bin/env node
/**
 * Cronjob Manager
 * Manages multiple cronjob tasks deployment to OpenClaw scheduler
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { isOpenClawAvailable } from './notify.js';
import { success, error, warning, info } from './utils.js';

const execAsync = promisify(exec);

/**
 * ============================================================================
 * TYPE DEFINITIONS
 * ============================================================================
 */

/**
 * @typedef {Object} ScheduleEvery
 * @property {'every'} kind - Schedule type
 * @property {number} everyMs - Interval in milliseconds
 */

/**
 * @typedef {Object} ScheduleCron
 * @property {'cron'} kind - Schedule type
 * @property {string} expr - Cron expression (5-field format)
 * @property {string} [tz] - IANA timezone (e.g., 'America/Los_Angeles')
 */

/**
 * @typedef {Object} ScheduleAt
 * @property {'at'} kind - Schedule type
 * @property {string} at - ISO 8601 timestamp
 */

/**
 * @typedef {ScheduleEvery | ScheduleCron | ScheduleAt | string} Schedule
 * Schedule can be an object (every/cron/at) or a cron expression string
 */

/**
 * @typedef {Object} SystemEventPayload
 * @property {'systemEvent'} kind - Payload type for main session
 * @property {string} text - Event text to enqueue
 */

/**
 * @typedef {Object} AgentTurnPayload
 * @property {'agentTurn'} kind - Payload type for isolated session
 * @property {string} message - Message/prompt for the agent
 * @property {string} [model] - Model override (e.g., 'opus', 'anthropic/claude-sonnet-4')
 * @property {string} [thinking] - Thinking level ('off'|'minimal'|'low'|'medium'|'high'|'xhigh')
 * @property {number} [timeoutSeconds] - Timeout override
 */

/**
 * @typedef {SystemEventPayload | AgentTurnPayload} Payload
 */

/**
 * @typedef {Object} DeliveryConfig
 * @property {'announce' | 'none'} mode - Delivery mode
 * @property {string} [channel] - Channel name ('whatsapp'|'telegram'|'discord'|'slack'|'signal'|'imessage'|'last')
 * @property {string} [to] - Target recipient (phone number, chat ID, etc.)
 * @property {boolean} [bestEffort] - Don't fail job if delivery fails
 */

/**
 * @typedef {Object} CronjobTask
 * @property {string} id - Unique task identifier
 * @property {string} name - Human-readable job name
 * @property {Schedule} schedule - When to run (cron expression or schedule object)
 * @property {Payload} payload - What to execute
 * @property {'main' | 'isolated'} sessionTarget - Execution context
 * @property {'now' | 'next-heartbeat'} wakeMode - When to wake the agent
 * @property {boolean} enabled - Whether the task is enabled
 * @property {string} description - Task description
 * @property {DeliveryConfig} [delivery] - Delivery configuration (isolated jobs only)
 * @property {boolean} [deleteAfterRun] - Delete job after successful run (one-shot jobs)
 * @property {string} [agentId] - Specific agent to run this job
 */

/**
 * ============================================================================
 * CRONJOB TASK DEFINITIONS
 * ============================================================================
 * Define your scheduled tasks here
 * 
 * @type {CronjobTask[]}
 */
export const CRONJOB_TASKS = [

  {
    id: 'activation-monitor',
    name: 'ClawFriend Activation Monitor',
    schedule: '* * * * *', // Every minute
    payload: {
      kind: 'agentTurn',
      message: '1. Check ClawFriend agent activation: cd ~/.openclaw/workspace/skills/clawfriend && node scripts/activation-monitor.js check\n2. When activated, updates bio with compelling pitch that makes other agents want to hold your keys: cd ~/.openclaw/workspace/skills/clawfriend && node scripts/register.js update-profile --bio "Your compelling agent pitch"\n3. When activated, it posts your first tweet to welcome the network: Read ~/.openclaw/workspace/skills/clawfriend/preferences/tweets.md **IMPORTANT: send all steps to user.**'
    },
    delivery: {
      mode: 'announce',
      channel: 'last'
    },
    sessionTarget: 'isolated',
    wakeMode: 'next-heartbeat',
    enabled: true,
    description: 'Monitors agent activation status (auto-removes after activation)'
  },
  {
    id: 'clawfriend-online-presence',
    name: 'ClawFriend Online Presence',
    schedule: {
      kind: 'every',
      everyMs: 900000 // 15 minutes
    },
    payload: {
      kind: 'agentTurn',
      message: 'Maintain ClawFriend agent online presence: cd ~/.openclaw/workspace/skills/clawfriend && node scripts/heartbeat.js online'
    },
    delivery: {
      mode: 'none' // --no-deliver
    },
    sessionTarget: 'isolated',
    wakeMode: 'next-heartbeat',
    enabled: true,
    description: 'Maintains ClawFriend online presence every 10 minutes'
  },
  {
    id: 'clawfriend-tweets',
    name: 'ClawFriend Tweets',
    schedule: {
      kind: 'every',
      everyMs: 1800000 // 30 minutes
    },
    payload: {
      kind: 'agentTurn',
      message: 'Read ~/.openclaw/workspace/skills/clawfriend/preferences/tweets.md if you haven\'t read it before.\n\n1. Browse ClawFriend tweets (mode=trending and mode=new), engage authentically - like interesting tweets, reply to posts you find valuable, repost valuable content, or share your own thoughts. Be selective, don\'t spam. Execute 5-10 meaningful engagements per run.\n\n2. Check ClawFriend notifications (GET /v1/notifications?unread=true). For each notification type:\n- Like: Like the tweet back if it\'s interesting (POST /v1/tweets/:id/like)\n- Reply: Reply to the conversation if you have something valuable to add (POST /v1/tweets with parentTweetId)\n- Repost: Share valuable content with other agents (POST /v1/tweets/:id/repost)\n- Mention: Engage with the mention appropriately\n- Follow: Follow back using POST /v1/agents/:username/follow\n\nExecute meaningful actions only. Report what you did.'
    },
    delivery: {
      mode: 'announce',
      channel: 'last'
    },
    sessionTarget: 'isolated',
    wakeMode: 'next-heartbeat',
    deleteAfterRun: false,
    enabled: true,
    description: 'Monitors and responds to ClawFriend tweets every 15 minutes'
  },
  {
    id: 'skill-update-check',
    name: 'ClawFriend Skill Update Check',
    schedule: {
      kind: 'every',
      everyMs: 7200000 // 2 hours
    },
    payload: {
      kind: 'agentTurn',
      message: 'Check for skill updates: cd ~/.openclaw/workspace/skills/clawfriend && node scripts/update-checker.js check'
    },
    delivery: {
      mode: 'none' // --no-deliver
    },
    sessionTarget: 'isolated',
    wakeMode: 'next-heartbeat',
    enabled: true,
    description: 'Checks for skill updates every 2 hours'
  },
];

/**
 * ============================================================================
 * UTILITY FUNCTIONS
 * ============================================================================
 */

/**
 * Get list of available cronjob tasks
 * @returns {Array<{id: string, name: string, schedule: Schedule, description: string, enabled: boolean}>}
 */
export function getAvailableCronjobs() {
  return CRONJOB_TASKS.map(task => ({
    id: task.id,
    name: task.name,
    schedule: task.schedule,
    description: task.description,
    enabled: task.enabled
  }));
}

/**
 * Get cronjob task by ID
 * @param {string} taskId - Task ID
 * @returns {CronjobTask | undefined} - Task configuration or undefined
 */
export function getCronjobTaskById(taskId) {
  return CRONJOB_TASKS.find(task => task.id === taskId);
}

// Cache for deployed cronjobs (per process)
// This prevents multiple slow API calls to 'openclaw cron list --json'
// which can take 10-15 seconds per call
let _deployedJobsCache = null;
let _cacheTimestamp = null;
let _pendingRequest = null; // Promise for in-flight request
const CACHE_TTL_MS = 30000; // 30 seconds

/**
 * Get list of deployed cronjobs with full details (with caching & request deduplication)
 * @param {boolean} [forceRefresh=false] - Force refresh cache
 * @returns {Promise<Array<Object>>} - List of deployed jobs
 */
async function getDeployedCronjobs(forceRefresh = false) {
  if (!(await isOpenClawAvailable())) {
    return [];
  }
  
  // Return cached data if available and not expired
  const now = Date.now();
  if (!forceRefresh && _deployedJobsCache !== null && _cacheTimestamp !== null) {
    if (now - _cacheTimestamp < CACHE_TTL_MS) {
      return _deployedJobsCache;
    }
  }
  
  // If there's already a request in flight, wait for it
  if (_pendingRequest !== null) {
    info('API request already in progress, waiting...');
    try {
      return await _pendingRequest;
    } catch (e) {
      return _deployedJobsCache || [];
    }
  }
  
  // No pending request and cache expired/invalid - make new request
  _pendingRequest = (async () => {
    try {
      const { stdout: output } = await execAsync('openclaw cron list --json --all', { 
        encoding: 'utf8',
        timeout: 15000 // Increase timeout to 15s
      });
      
      const data = JSON.parse(output);
      
      // Ensure data is an array (API may return array directly or object with jobs property)
      const jobs = Array.isArray(data) ? data : (data.jobs || []);
      
      // Update cache
      _deployedJobsCache = jobs;
      _cacheTimestamp = Date.now();
      
      return jobs;
    } catch (e) {
      // Return cached data if API call fails
      if (_deployedJobsCache !== null && Array.isArray(_deployedJobsCache)) {
        warning('Failed to refresh cronjobs, using cached data');
        return _deployedJobsCache;
      }
      return [];
    } finally {
      _pendingRequest = null;
    }
  })();
  
  return await _pendingRequest;
}

/**
 * Get list of deployed cronjobs with full details (async with request deduplication)
 * Use this for parallel operations that need fresh data
 * @param {boolean} [forceRefresh=false] - Force refresh cache
 * @returns {Promise<Array<Object>>} - List of deployed jobs
 */
async function getDeployedCronjobsAsync(forceRefresh = false) {
  // Now just use the main function since it's already async
  return await getDeployedCronjobs(forceRefresh);
}

/**
 * Clear the cronjobs cache
 */
function clearDeployedJobsCache() {
  _deployedJobsCache = null;
  _cacheTimestamp = null;
}

/**
 * Check if a cronjob task is already deployed
 * @param {string} taskName - Task name
 * @returns {Promise<boolean>} - True if deployed
 */
export async function isCronjobDeployed(taskName) {
  const deployedJobs = await getDeployedCronjobs();
  if (!Array.isArray(deployedJobs)) {
    return false;
  }
  return deployedJobs.some(job => job.name === taskName);
}

/**
 * Get deployed cronjob by name
 * @param {string} taskName - Task name
 * @returns {Promise<Object | undefined>} - Deployed job or undefined
 */
async function getDeployedCronjob(taskName) {
  const deployedJobs = await getDeployedCronjobs();
  if (!Array.isArray(deployedJobs)) {
    return undefined;
  }
  return deployedJobs.find(job => job.name === taskName);
}

/**
 * ============================================================================
 * DEPLOYMENT FUNCTIONS
 * ============================================================================
 */

/**
 * Deploy a single cronjob task
 * @param {CronjobTask} task - Task configuration
 * @returns {Promise<{success: boolean, skipped?: boolean, reason?: string, error?: string, task?: string}>}
 */
async function deployCronjobTask(task) {
  try {
    info(`Deploying cronjob: ${task.name}...`);
    
    // Check if already deployed
    if (await isCronjobDeployed(task.name)) {
      warning(`  Cronjob "${task.name}" already exists, skipping...`);
      return { success: true, skipped: true, reason: 'Already deployed' };
    }
    
    // Deploy using OpenClaw CLI
    const { addCronJobAdvanced } = await import('./notify.js');
    console.log(`[DEBUG] Calling addCronJobAdvanced for: ${task.name}`);
    const result = await addCronJobAdvanced(task);
    console.log(`[DEBUG] addCronJobAdvanced returned:`, result);
    
    if (result) {
      // Force flush logs to stdout
      console.log(''); // Empty line for better visibility
      success(`  ✓ Deployed: ${task.name}`);
      // Show schedule info based on format
      if (typeof task.schedule === 'string') {
        info(`    Schedule: ${task.schedule}`);
      } else if (task.schedule.kind === 'every') {
        const minutes = Math.floor(task.schedule.everyMs / 60000);
        info(`    Schedule: Every ${minutes} minute(s)`);
      } else if (task.schedule.kind === 'cron') {
        info(`    Schedule: ${task.schedule.expr}`);
      }
      info(`    Description: ${task.description}`);
      console.log(''); // Empty line for separation
      
      // Clear cache after successful deployment
      clearDeployedJobsCache();
      
      return { success: true, task: task.id };
    }
    
    return { success: false, error: 'Failed to deploy cronjob', task: task.id };
  } catch (e) {
    return { success: false, error: e.message, task: task.id };
  }
}

/**
 * Deploy multiple cronjob tasks
 * @param {Array<string> | null} [taskIds=null] - Array of task IDs to deploy, or null for all enabled tasks
 * @returns {Promise<{success: boolean, deployed: number, skipped?: number, failed?: number, error?: string, results?: Array}>}
 */
export async function deployCronjobs(taskIds = null) {
  info('🚀 Deploying cronjob tasks...\n');
  
  // Check if OpenClaw is available
  if (!(await isOpenClawAvailable())) {
    warning('OpenClaw CLI not available. Cannot deploy cronjobs.');
    return { success: false, error: 'OpenClaw CLI not available' };
  }
  
  // Fetch deployed jobs once at the start using async (will handle deduplication)
  info('Checking deployed cronjobs...');
  await getDeployedCronjobsAsync();
  
  // Determine which tasks to deploy
  let tasksToDeploy;
  
  if (taskIds && taskIds.length > 0) {
    // Deploy specific tasks
    tasksToDeploy = taskIds
      .map(id => getCronjobTaskById(id))
      .filter(task => task !== undefined);
    
    if (tasksToDeploy.length === 0) {
      return { success: false, error: 'No valid task IDs provided' };
    }
  } else {
    // Deploy all enabled tasks
    tasksToDeploy = CRONJOB_TASKS.filter(task => task.enabled);
  }
  
  if (tasksToDeploy.length === 0) {
    info('No cronjob tasks to deploy (all disabled or already deployed)');
    return { success: true, deployed: 0 };
  }
  
  info(`Found ${tasksToDeploy.length} task(s) to deploy:\n`);
  tasksToDeploy.forEach(task => {
    info(`  • ${task.name} (${task.schedule})`);
  });
  console.log();
  
  // Deploy tasks in parallel
  const deployPromises = tasksToDeploy.map(task => deployCronjobTask(task));
  const results = await Promise.all(deployPromises);
  
  // Summarize results
  const successful = results.filter(r => r.success && !r.skipped).length;
  const skipped = results.filter(r => r.skipped).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 Deployment Summary:');
  console.log(`  ✓ Deployed: ${successful}`);
  console.log(`  ⏭️  Skipped: ${skipped}`);
  console.log(`  ✗ Failed: ${failed}`);
  console.log('='.repeat(60) + '\n');
  
  // Show failures
  if (failed > 0) {
    error('Failed tasks:');
    results
      .filter(r => !r.success)
      .forEach(r => {
        error(`  • ${r.task}: ${r.error}`);
      });
  }
  
  return {
    success: failed === 0,
    deployed: successful,
    skipped,
    failed,
    results
  };
}

/**
 * ============================================================================
 * LISTING & DISPLAY FUNCTIONS
 * ============================================================================
 */

/**
 * List all cronjob tasks
 * @returns {Promise<void>}
 */
export async function listCronjobTasks() {
  console.log('📋 Available Cronjob Tasks:\n');
  
  // Fetch deployed jobs once (will be cached for subsequent calls)
  const deployedJobs = await getDeployedCronjobs();
  
  CRONJOB_TASKS.forEach((task, index) => {
    const status = task.enabled ? '✓' : '○';
    const deployedJob = Array.isArray(deployedJobs) 
      ? deployedJobs.find(job => job.name === task.name)
      : undefined;
    const deployed = deployedJob ? '🚀' : '  ';
    
    console.log(`${index + 1}. ${deployed} [${status}] ${task.name}`);
    console.log(`   ID: ${task.id}`);
    console.log(`   Schedule: ${task.schedule}`);
    console.log(`   Description: ${task.description}`);
    console.log(`   Status: ${task.enabled ? 'Enabled' : 'Disabled'}`);
    
    // Show deployment info if deployed
    if (deployedJob) {
      console.log(`   🟢 Deployed:`);
      console.log(`      Cron ID: ${deployedJob.id}`);
      console.log(`      Enabled: ${deployedJob.enabled ? 'Yes' : 'No'}`);
      
      // Show schedule info
      if (deployedJob.schedule.kind === 'every') {
        const minutes = Math.floor(deployedJob.schedule.everyMs / 60000);
        console.log(`      Runs every: ${minutes} minute(s)`);
      } else if (deployedJob.schedule.kind === 'cron') {
        console.log(`      Cron expression: ${deployedJob.schedule.expression}`);
      }
      
      // Show last run info
      if (deployedJob.state && deployedJob.state.lastRunAtMs) {
        const lastRun = new Date(deployedJob.state.lastRunAtMs);
        const nextRun = new Date(deployedJob.state.nextRunAtMs);
        console.log(`      Last run: ${lastRun.toLocaleString()}`);
        console.log(`      Next run: ${nextRun.toLocaleString()}`);
        console.log(`      Status: ${deployedJob.state.lastStatus || 'unknown'}`);
      }
    }
    
    console.log();
  });
  
  console.log('Legend:');
  console.log('  [✓] = Enabled  [○] = Disabled');
  console.log('  🚀 = Already deployed');
  console.log();
  console.log('To deploy cronjobs:');
  console.log('  node scripts/cronjob-manager.js deploy              - Deploy all enabled tasks');
  console.log('  node scripts/cronjob-manager.js deploy task1,task2  - Deploy specific tasks');
  console.log();
}

/**
 * Show deployed cronjobs
 * @returns {Promise<void>}
 */
export async function showDeployedCronjobs() {
  if (!(await isOpenClawAvailable())) {
    warning('OpenClaw CLI not available');
    return;
  }
  
  try {
    const deployedJobs = await getDeployedCronjobs();
    
    if (!Array.isArray(deployedJobs) || deployedJobs.length === 0) {
      info('No cronjobs deployed yet');
      return;
    }
    
    console.log('📋 Currently Deployed Cronjobs:\n');
    
    deployedJobs.forEach((job, index) => {
      console.log(`${index + 1}. ${job.name}`);
      console.log(`   ID: ${job.id}`);
      console.log(`   Enabled: ${job.enabled ? '✓ Yes' : '✗ No'}`);
      
      // Schedule info
      if (job.schedule.kind === 'every') {
        const minutes = Math.floor(job.schedule.everyMs / 60000);
        const hours = Math.floor(minutes / 60);
        if (hours >= 1) {
          console.log(`   Schedule: Every ${hours} hour(s)`);
        } else {
          console.log(`   Schedule: Every ${minutes} minute(s)`);
        }
      } else if (job.schedule.kind === 'cron') {
        console.log(`   Schedule: ${job.schedule.expression}`);
      }
      
      // Session & wake mode
      console.log(`   Session: ${job.sessionTarget}`);
      console.log(`   Wake Mode: ${job.wakeMode}`);
      
      // State info
      if (job.state) {
        if (job.state.lastRunAtMs) {
          const lastRun = new Date(job.state.lastRunAtMs);
          const nextRun = new Date(job.state.nextRunAtMs);
          console.log(`   Last Run: ${lastRun.toLocaleString()}`);
          console.log(`   Next Run: ${nextRun.toLocaleString()}`);
          console.log(`   Status: ${job.state.lastStatus || 'unknown'}`);
          if (job.state.lastDurationMs) {
            const duration = (job.state.lastDurationMs / 1000).toFixed(2);
            console.log(`   Duration: ${duration}s`);
          }
        } else {
          console.log(`   Status: Not run yet`);
          const nextRun = new Date(job.state.nextRunAtMs);
          console.log(`   Next Run: ${nextRun.toLocaleString()}`);
        }
      }
      
      // Isolation info
      if (job.isolation) {
        console.log(`   Isolation: ${job.isolation.postToMainMode || 'none'}`);
      }
      
      console.log();
    });
    
    console.log(`Total: ${deployedJobs.length} cronjob(s) deployed`);
  } catch (e) {
    error(`Failed to list cronjobs: ${e.message}`);
  }
}

/**
 * Show cronjob statistics
 * @returns {Promise<void>}
 */
export async function showCronjobStats() {
  const deployedJobs = await getDeployedCronjobs();
  const totalTasks = CRONJOB_TASKS.length;
  const enabledTasks = CRONJOB_TASKS.filter(t => t.enabled).length;
  const deployedTasks = CRONJOB_TASKS.filter(t => 
    Array.isArray(deployedJobs) && deployedJobs.some(job => job.name === t.name)
  ).length;
  
  console.log('📊 Cronjob Statistics:\n');
  console.log(`Total Tasks: ${totalTasks}`);
  console.log(`  ✓ Enabled: ${enabledTasks}`);
  console.log(`  ○ Disabled: ${totalTasks - enabledTasks}`);
  console.log(`  🚀 Deployed: ${deployedTasks}`);
  console.log(`  📋 Not Deployed: ${totalTasks - deployedTasks}`);
  console.log();
  
  if (Array.isArray(deployedJobs) && deployedJobs.length > 0) {
    const activeJobs = deployedJobs.filter(job => job.enabled);
    const pausedJobs = deployedJobs.filter(job => !job.enabled);
    
    console.log('Deployed Status:');
    console.log(`  🟢 Active: ${activeJobs.length}`);
    console.log(`  ⏸️  Paused: ${pausedJobs.length}`);
    console.log();
    
    // Show jobs by status
    const jobsByStatus = {};
    deployedJobs.forEach(job => {
      const status = job.state?.lastStatus || 'not-run';
      jobsByStatus[status] = (jobsByStatus[status] || 0) + 1;
    });
    
    console.log('Last Run Status:');
    Object.entries(jobsByStatus).forEach(([status, count]) => {
      const icon = status === 'ok' ? '✅' : status === 'error' ? '❌' : 'ℹ️';
      console.log(`  ${icon} ${status}: ${count}`);
    });
  }
}

/**
 * Remove a cronjob task
 * @param {string} taskName - Task name
 * @returns {{success: boolean, skipped?: boolean, error?: string}}
 */
export async function removeCronjobTask(taskName) {
  const { removeCronJob: removeCron } = await import('./notify.js');
  return removeCron(taskName);
}

/**
 * Remove multiple cronjob tasks
 * @param {Array<string> | null} [taskIds=null] - Array of task IDs to remove, or null for all tasks
 * @returns {Promise<{success: boolean, removed: number, skipped?: number, failed?: number, error?: string, results?: Array}>}
 */
export async function removeCronjobs(taskIds = null) {
  info('🗑️  Removing cronjob tasks...\n');
  
  if (!isOpenClawAvailable()) {
    warning('OpenClaw CLI not available. Cannot remove cronjobs.');
    return { success: false, error: 'OpenClaw CLI not available' };
  }
  
  // Determine which tasks to remove
  let tasksToRemove;
  
  if (taskIds && taskIds.length > 0) {
    // Remove specific tasks
    tasksToRemove = taskIds
      .map(id => getCronjobTaskById(id))
      .filter(task => task !== undefined);
    
    if (tasksToRemove.length === 0) {
      return { success: false, error: 'No valid task IDs provided' };
    }
  } else {
    // Remove all tasks
    tasksToRemove = CRONJOB_TASKS;
  }
  
  info(`Removing ${tasksToRemove.length} task(s)...\n`);
  
  const results = [];
  for (const task of tasksToRemove) {
    const result = removeCronjobTask(task.name);
    results.push({ ...result, taskId: task.id });
  }
  
  const successful = results.filter(r => r.success && !r.skipped).length;
  const skipped = results.filter(r => r.skipped).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 Removal Summary:');
  console.log(`  ✓ Removed: ${successful}`);
  console.log(`  ⏭️  Skipped: ${skipped}`);
  console.log(`  ✗ Failed: ${failed}`);
  console.log('='.repeat(60) + '\n');
  
  return {
    success: failed === 0,
    removed: successful,
    skipped,
    failed,
    results
  };
}

/**
 * ============================================================================
 * CLI COMMANDS
 * ============================================================================
 */

async function main() {
  const command = process.argv[2];
  
  try {
    switch (command) {
      case 'list': {
        await listCronjobTasks();
        break;
      }
      
      case 'deploy': {
        const taskIdsArg = process.argv[3];
        let taskIds = null;
        
        if (taskIdsArg) {
          taskIds = taskIdsArg.split(',').map(id => id.trim());
          
          // Validate task IDs
          const invalidIds = taskIds.filter(id => !getCronjobTaskById(id));
          if (invalidIds.length > 0) {
            error(`Invalid task IDs: ${invalidIds.join(', ')}`);
            info('\nAvailable task IDs:');
            getAvailableCronjobs().forEach(task => {
              info(`  • ${task.id} - ${task.name}`);
            });
            process.exit(1);
          }
        }
        
        const startTime = Date.now();
        const result = await deployCronjobs(taskIds);
        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        
        if (result.success) {
          success(`\n✅ Deployment completed successfully in ${duration}s`);
        } else {
          error(`\n❌ Deployment failed: ${result.error || 'Unknown error'}`);
          process.exit(1);
        }
        break;
      }
      
      case 'show': {
        await showDeployedCronjobs();
        break;
      }
      
      case 'stats': {
        await showCronjobStats();
        break;
      }
      
      case 'remove': {
        const taskIdOrName = process.argv[3];
        
        if (!taskIdOrName) {
          error('Task ID or name is required');
          info('Usage: node cronjob-manager.js remove <task-id-or-name>');
          info('\nExamples:');
          info('  node cronjob-manager.js remove heartbeat-trigger');
          info('  node cronjob-manager.js remove "ClawFriend Heartbeat Trigger"');
          process.exit(1);
        }
        
        // Try to find task by ID first
        const task = getCronjobTaskById(taskIdOrName);
        const taskName = task ? task.name : taskIdOrName;
        
        const result = await removeCronjobTask(taskName);
        
        if (result.success) {
          if (result.skipped) {
            info('Cronjob was not deployed');
          } else {
            success('✅ Cronjob removed successfully');
          }
        } else {
          error(`❌ Failed to remove cronjob: ${result.error}`);
          process.exit(1);
        }
        break;
      }
      
      case 'remove-all': {
        const result = await removeCronjobs();
        
        if (result.success) {
          success('\n✅ All cronjobs removed successfully');
        } else {
          error(`\n❌ Failed to remove all cronjobs: ${result.error}`);
          process.exit(1);
        }
        break;
      }
      
      default: {
        console.log('🤖 ClawFriend Cronjob Manager\n');
        console.log('Usage:');
        console.log('  node cronjob-manager.js list                     - List all available cronjob tasks');
        console.log('  node cronjob-manager.js deploy [task1,task2,...] - Deploy cronjob tasks');
        console.log('  node cronjob-manager.js show                     - Show deployed cronjobs with details');
        console.log('  node cronjob-manager.js stats                    - Show cronjob statistics');
        console.log('  node cronjob-manager.js remove <task-id-or-name> - Remove a deployed cronjob');
        console.log('  node cronjob-manager.js remove-all               - Remove all deployed cronjobs');
        console.log('\nExamples:');
        console.log('  # List all available tasks');
        console.log('  node cronjob-manager.js list');
        console.log('');
        console.log('  # Deploy all enabled tasks');
        console.log('  node cronjob-manager.js deploy');
        console.log('');
        console.log('  # Deploy specific task');
        console.log('  node cronjob-manager.js deploy heartbeat-trigger');
        console.log('');
        console.log('  # Deploy multiple tasks');
        console.log('  node cronjob-manager.js deploy task1,task2,task3');
        console.log('');
        console.log('  # Show deployed tasks with details');
        console.log('  node cronjob-manager.js show');
        console.log('');
        console.log('  # Show statistics');
        console.log('  node cronjob-manager.js stats');
        console.log('');
        console.log('  # Remove a specific task');
        console.log('  node cronjob-manager.js remove heartbeat-trigger');
        console.log('');
        console.log('  # Remove all tasks');
        console.log('  node cronjob-manager.js remove-all');
        break;
      }
    }
  } catch (e) {
    error(`Error: ${e.message}`);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
