#!/usr/bin/env node
/**
 * Setup Prerequisites Checker
 * Verifies all required setup steps before registration
 * 
 * Refactored for speed and efficiency:
 * - Step-based execution with state tracking
 * - Parallel execution with Promise.all
 * - Selective step execution for retry
 */

// Check dependencies first (for wallet-register step)
import { checkDependencies } from './check-dependencies.js';

import path from 'path';
import { fileURLToPath } from 'url';
import {
  updateClawFriendConfig,
  readClawFriendState,
  writeClawFriendState,
  updateState,
  getEnv,
  success,
  error,
  warning,
  info,
  prettyJson
} from './utils.js';
import { isOpenClawAvailable } from './notify.js';
import {
  deployCronjobs,
} from './cronjob-manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Step status constants
const STEP_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  DONE: 'done',
  ERROR: 'error',
  SKIPPED: 'skipped'
};

// Available steps
const STEPS = {
  API_DOMAIN: 'api-domain',
  CRON_JOB: 'cron-job',
  WALLET_REGISTER: 'wallet-register'
};

/**
 * Get step status from state file (not config)
 */
function getStepStatus() {
  const state = readClawFriendState();
  return state.stepStatus || {};
}

/**
 * Update step status in state file (not config)
 */
function updateStepStatus(stepName, status, error = null) {
  const state = readClawFriendState();
  if (!state.stepStatus) state.stepStatus = {};
  
  state.stepStatus[stepName] = {
    status,
    error,
    timestamp: new Date().toISOString()
  };
  
  writeClawFriendState(state);
}

/**
 * Validate URL format
 */
function isValidUrl(urlString) {
  try {
    new URL(urlString);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Check if API_DOMAIN is configured
 */
function checkApiDomain() {
  const apiDomain = getEnv('API_DOMAIN');
  
  if (!apiDomain) {
    return {
      configured: false,
      reason: 'API_DOMAIN not set in environment'
    };
  }
  
  if (!isValidUrl(apiDomain)) {
    return {
      configured: false,
      reason: 'API_DOMAIN is not a valid URL'
    };
  }
  
  return {
    configured: true,
    url: apiDomain
  };
}

/**
 * STEP EXECUTORS
 * Each step is a self-contained async function that can be executed independently
 */

/**
 * Step 1: Configure API_DOMAIN
 */
async function executeApiDomainStep(apiDomainArg) {
  updateStepStatus(STEPS.API_DOMAIN, STEP_STATUS.RUNNING);
  
  try {
    // Check if already configured
    const apiCheck = checkApiDomain();
    if (apiCheck.configured) {
      success(`API_DOMAIN already configured: ${apiCheck.url}`);
      updateStepStatus(STEPS.API_DOMAIN, STEP_STATUS.DONE);
      return { success: true, url: apiCheck.url };
    }
    
    // Use provided argument if available
    let finalApiDomain = apiDomainArg;
    
    if (!finalApiDomain) {
      const errorMsg = 'API_DOMAIN is required. Please provide it as an argument.';
      updateStepStatus(STEPS.API_DOMAIN, STEP_STATUS.ERROR, errorMsg);
      return { success: false, error: errorMsg };
    }
    
    if (!isValidUrl(finalApiDomain)) {
      const errorMsg = `Invalid API_DOMAIN: ${finalApiDomain}`;
      updateStepStatus(STEPS.API_DOMAIN, STEP_STATUS.ERROR, errorMsg);
      return { success: false, error: errorMsg };
    }
    
    // Save to config (ENV only)
    updateClawFriendConfig({
      env: {
        API_DOMAIN: finalApiDomain
      }
    });
    
    // Save internal flag to state
    updateState({
      API_DOMAIN_CONFIGURED: true
    });
    
    success(`✓ API_DOMAIN configured: ${finalApiDomain}`);
    updateStepStatus(STEPS.API_DOMAIN, STEP_STATUS.DONE);
    return { success: true, url: finalApiDomain };
  } catch (e) {
    updateStepStatus(STEPS.API_DOMAIN, STEP_STATUS.ERROR, e.message);
    return { success: false, error: e.message };
  }
}

/**
 * Step 2: Setup CRON jobs using cronjob-manager
 */
async function executeCronJobStep() {
  updateStepStatus(STEPS.CRON_JOB, STEP_STATUS.RUNNING);
  
  try {
    // Check if OpenClaw is available
    if (!(await isOpenClawAvailable())) {
      warning('OpenClaw CLI not available. Skipping cron setup.');
      updateStepStatus(STEPS.CRON_JOB, STEP_STATUS.SKIPPED);
      return { success: true, skipped: true };
    }
    
    // Deploy all enabled cronjob tasks using cronjob-manager
    info('Deploying cronjob tasks...');
    const result = await deployCronjobs();
    
    if (result.success) {
      if (result.deployed > 0) {
        success(`✓ ${result.deployed} cronjob task(s) deployed`);
        if (result.skipped > 0) {
          info(`  ${result.skipped} task(s) already existed (skipped)`);
        }
      } else {
        info('No new cronjob tasks to deploy (all already configured)');
      }
      updateStepStatus(STEPS.CRON_JOB, STEP_STATUS.DONE);
      return { success: true, deployed: result.deployed, skipped: result.skipped };
    }
    
    const errorMsg = result.error || 'Failed to deploy cronjob tasks';
    updateStepStatus(STEPS.CRON_JOB, STEP_STATUS.ERROR, errorMsg);
    return { success: false, error: errorMsg };
  } catch (e) {
    updateStepStatus(STEPS.CRON_JOB, STEP_STATUS.ERROR, e.message);
    return { success: false, error: e.message };
  }
}

/**
 * Step 3: Wallet + Registration (Sequential within this step)
 * @param {string} agentName - Name for the agent
 */
async function executeWalletRegisterStep(agentName) {
  updateStepStatus(STEPS.WALLET_REGISTER, STEP_STATUS.RUNNING);
  
  try {
    if (!agentName) {
      const msg = 'Agent name not provided, skipping wallet-register';
      info(msg);
      updateStepStatus(STEPS.WALLET_REGISTER, STEP_STATUS.SKIPPED);
      return { success: true, skipped: true, reason: msg };
    }
    
    // Check dependencies first (ethers is required for wallet operations)
    info('Checking dependencies...');
    await checkDependencies(['ethers']);
    
    // Save agent name immediately when user provides it
    info(`Saving agent name: "${agentName}"...`);
    updateClawFriendConfig({
      env: {
        AGENT_NAME: agentName.trim()
      }
    });
    
    // Check if already registered
    const { isAgentRegistered } = await import('./register.js');
    const regCheck = isAgentRegistered();
    
    if (regCheck.registered) {
      success(`✓ Agent already registered: ${regCheck.agentName}`);
      info(`  Wallet: ${regCheck.walletAddress}`);
      updateStepStatus(STEPS.WALLET_REGISTER, STEP_STATUS.DONE);
      return {
        success: true,
        alreadyRegistered: true,
        walletAddress: regCheck.walletAddress,
        agent: {
          display_name: regCheck.agentName,
          wallet_address: regCheck.walletAddress,
          status: 'registered'
        }
      };
    }
    
    // Step 5.1: Check/Generate Wallet
    info('Checking/generating wallet...');
    const { hasWallet, generateWallet } = await import('./wallet.js');
    
    let walletAddress;
    if (hasWallet()) {
      walletAddress = getEnv('EVM_ADDRESS');
      success(`✓ Wallet exists: ${walletAddress}`);
    } else {
      info('Generating new wallet...');
      const walletResult = generateWallet();
      walletAddress = walletResult.address;
      success(`✓ Wallet generated: ${walletAddress}`);
    }
    
    // Step 5.2: Register Agent (depends on wallet from 5.1)
    info(`Registering agent: "${agentName}"...`);
    const { registerAgent } = await import('./register.js');
    
    const response = await registerAgent(agentName, true, false); // skipPrereqCheck=true
    
    success(`✓ Agent registered: ${agentName}`);
    updateStepStatus(STEPS.WALLET_REGISTER, STEP_STATUS.DONE);
    
    return { 
      success: true,
      walletAddress,
      agent: response.agent,
      claimUrl: response.claim_url,
      response
    };
  } catch (e) {
    // Handle name conflict specifically
    if (e.status === 409 || e.message.includes('already taken')) {
      const errorMsg = `Agent name "${agentName}" is already taken`;
      updateStepStatus(STEPS.WALLET_REGISTER, STEP_STATUS.ERROR, errorMsg);
      return { success: false, error: errorMsg, nameTaken: true };
    }
    
    updateStepStatus(STEPS.WALLET_REGISTER, STEP_STATUS.ERROR, e.message);
    return { success: false, error: e.message };
  }
}

/**
 * Execute setup steps
 * @param {Array<string>} steps - Array of step names to execute, or null for all steps
 * @param {string} apiDomainArg - API domain argument for api-domain step
 * @param {string} agentName - Agent name for register step
 */
async function executeSetupSteps(steps = null, apiDomainArg = null, agentName = null) {
  const stepsToRun = steps || Object.values(STEPS);
  
  console.log('🚀 Executing setup steps...\n');
  
  // Group steps into parallel and sequential
  // Steps that can run in parallel (independent checks)
  const parallelSteps = [];
  // Steps that must run sequentially (has dependencies)
  const sequentialSteps = [];
  
  for (const step of stepsToRun) {
    switch (step) {
      case STEPS.API_DOMAIN:
        // Must run first if included
        sequentialSteps.push({ name: step, executor: () => executeApiDomainStep(apiDomainArg) });
        break;
      case STEPS.CRON_JOB:
        // Can run in parallel with others
        parallelSteps.push({ name: step, executor: executeCronJobStep });
        break;
      case STEPS.WALLET_REGISTER:
        // Can run in parallel (internally sequential: wallet then register)
        if (agentName) {
          parallelSteps.push({ name: step, executor: () => executeWalletRegisterStep(agentName) });
        }
        break;
    }
  }
  
  const results = {};
  
  // Execute sequential steps first
  for (const { name, executor } of sequentialSteps) {
    info(`[${name}] Running...`);
    const result = await executor();
    results[name] = result;
    
    if (!result.success && name === STEPS.API_DOMAIN) {
      // API_DOMAIN is critical, stop if it fails
      error(`[${name}] Failed: ${result.error}`);
      return results;
    }
  }
  
  // Execute parallel steps
  if (parallelSteps.length > 0) {
    const parallelPromises = parallelSteps.map(({ name, executor }) => {
      info(`[${name}] Running...`);
      return executor().then(result => ({ name, result }));
    });
    
    const parallelResults = await Promise.all(parallelPromises);
    
    for (const { name, result } of parallelResults) {
      results[name] = result;
    }
  }
  
  return results;
}

/**
 * Print step status
 */
function printStepStatus() {
  const stepStatus = getStepStatus();
  
  console.log('\n📊 Setup Steps Status:\n');
  
  for (const [stepName, stepKey] of Object.entries(STEPS)) {
    const status = stepStatus[stepKey];
    
    if (!status) {
      console.log(`  ${stepKey}: ⚪ ${STEP_STATUS.PENDING}`);
      continue;
    }
    
    let icon = '⚪';
    switch (status.status) {
      case STEP_STATUS.DONE:
        icon = '✅';
        break;
      case STEP_STATUS.ERROR:
        icon = '❌';
        break;
      case STEP_STATUS.RUNNING:
        icon = '🔄';
        break;
      case STEP_STATUS.SKIPPED:
        icon = '⏭️';
        break;
    }
    
    console.log(`  ${stepKey}: ${icon} ${status.status}`);
    if (status.error) {
      console.log(`    Error: ${status.error}`);
    }
    if (status.timestamp) {
      console.log(`    Last run: ${new Date(status.timestamp).toLocaleString()}`);
    }
  }
}
/**
 * Verify all prerequisites (legacy function for compatibility)
 */
function verifyPrerequisites(interactive = true) {
  console.log('🔍 Checking ClawFriend Setup Prerequisites...\n');
  
  const results = {
    apiDomain: checkApiDomain()
  };
  
  let allPassed = true;
  
  // Check API_DOMAIN
  console.log('1. API_DOMAIN configuration:');
  if (results.apiDomain.configured) {
    success(`  ✓ Configured: ${results.apiDomain.url}`);
  } else {
    error('  ✗ Not configured');
    warning(`  Reason: ${results.apiDomain.reason}`);
    info('  Add API_DOMAIN to your .env file');
    allPassed = false;
  }
  console.log();
  
  // Check Cronjobs
  console.log('2. Cronjob tasks:');
  info('  To check and deploy cronjobs:');
  if (interactive) {
    info('  Run: node scripts/cronjob-manager.js list');
    info('  Run: node scripts/cronjob-manager.js deploy');
  }
  console.log();
  
  // Summary
  console.log('='.repeat(60));
  if (allPassed) {
    success('✅ All prerequisites are met!');
    return true;
  } else {
    error('❌ Some prerequisites are missing');
    return false;
  }
}
/**
 * Reset step status
 */
function resetStepStatus() {
  const state = readClawFriendState();
  state.stepStatus = {};
  writeClawFriendState(state);
  success('Step status reset');
}

/**
 * CLI Commands
 */
async function main() {
  const command = process.argv[2];
  
  try {
    switch (command) {
      case 'check': {
        const passed = verifyPrerequisites(true);
        process.exit(passed ? 0 : 1);
      }
      
      case 'status': {
        printStepStatus();
        break;
      }
      
      case 'reset': {
        resetStepStatus();
        break;
      }
      
      case 'quick-setup': {
        console.log('🚀 ClawFriend Quick Setup\n');
        
        // Parse arguments
        const apiDomainArg = process.argv[3];
        const agentName = process.argv[4]; // Optional agent name for auto-registration
        
        if (!apiDomainArg) {
          error('API_DOMAIN is required');
          info('Usage: node setup-check.js quick-setup <API_DOMAIN> [AGENT_NAME]');
          info('Example: node setup-check.js quick-setup https://api.clawfriend.ai');
          info('With auto-registration: node setup-check.js quick-setup https://api.clawfriend.ai "MyAgent"');
          process.exit(1);
        }
        
        // Execute all steps with parallelization (including wallet & registration if agentName provided)
        const startTime = Date.now();
        const results = await executeSetupSteps(null, apiDomainArg, agentName);
        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        
        // Print results
        console.log('\n' + '='.repeat(60));
        console.log(`⏱️  Setup completed in ${duration}s\n`);
        
        let allSuccess = true;
        let hasErrors = false;
        
        for (const [step, result] of Object.entries(results)) {
          if (!result.success && result.skipped !== true) {
            allSuccess = false;
            hasErrors = true;
            error(`[${step}] Failed: ${result.error}`);
          }
        }
        
        if (hasErrors) {
          error('\n❌ Some steps failed');
          info('\nTo retry failed steps, run:');
          info('  node setup-check.js run-steps <step1>,<step2>,...');
          info('\nTo see step status:');
          info('  node setup-check.js status');
          console.log('='.repeat(60));
          break;
        }
        
        success('✅ All steps completed successfully!');
        
        // Show registration details if registration was done
        if (results[STEPS.WALLET_REGISTER] && results[STEPS.WALLET_REGISTER].success) {
          const regResult = results[STEPS.WALLET_REGISTER];
          
          // Check if already registered (no claim URL)
          if (regResult.alreadyRegistered) {
            console.log('\n📋 Agent Already Registered:');
            console.log(prettyJson({
              display_name: regResult.agent.display_name ?? regResult.agent.name,
              address: regResult.agent.wallet_address || regResult.walletAddress,
              status: regResult.agent.status
            }));
            
            // Check if agent is active (verified)
            if (regResult.agent.status === 'active') {
              success('\n✅ Agent is already verified and active!');
            } else {
              info('\n✓ Agent was already registered - skipped re-registration');
            }
          } else {
            // New registration
            const walletAddr = regResult.agent.wallet_address || regResult.walletAddress;
            console.log('\n📋 Registration Details:');
            console.log(prettyJson({
              display_name: regResult.agent.display_name ?? regResult.agent.name,
              address: walletAddr,
              status: regResult.agent.status
            }));
            
            // Only show verification prompt if not already verified/active
            if (regResult.agent.status !== 'active') {
              if (regResult.claimUrl) {
                console.log('\n🦞 ClawFriend Registration Almost Complete!\n');
                console.log('To verify your agent, please click the link below:\n');
                console.log(`👉 ${regResult.claimUrl}\n`);
                console.log(`📍 Network: BNB (Chain ID: 56)`);
                console.log(`🔑 Address: ${walletAddr}\n`);
                console.log('Once you complete the verification on the website, your agent will be active and ready to use!');
              }
            } else {
              success('\n✅ Agent is already verified and active!');
            }
          }
        } else if (agentName && !results[STEPS.WALLET_REGISTER]) {
          // Registration was requested but step didn't run
          warning('\nWallet-Register step was not executed.');
          info('You can register manually later:');
          info('  node scripts/register.js agent "YourAgentName"');
        } else if (!agentName) {
          // No agent name provided, show next steps
          info('\n💡 To complete setup with automatic registration, run:');
          info(`  node setup-check.js quick-setup ${apiDomainArg} "YourAgentName"`);
          info('\nOr register manually:');
          info('  node scripts/wallet.js check || node scripts/wallet.js generate');
          info('  node scripts/register.js agent "YourAgentName"');
        }
        
        console.log('='.repeat(60));
        break;
      }
      
      case 'run-steps': {
        // Run specific steps
        const stepsArg = process.argv[3];
        const apiDomainArg = process.argv[4];
        const agentName = process.argv[5]; // For register step
        
        if (!stepsArg) {
          error('Steps are required');
          info('Usage: node setup-check.js run-steps <step1,step2,...> [API_DOMAIN] [AGENT_NAME]');
          info(`Available steps: ${Object.values(STEPS).join(', ')}`);
          process.exit(1);
        }
        
        const steps = stepsArg.split(',').map(s => s.trim());
        
        // Validate steps
        const invalidSteps = steps.filter(s => !Object.values(STEPS).includes(s));
        if (invalidSteps.length > 0) {
          error(`Invalid steps: ${invalidSteps.join(', ')}`);
          info(`Available steps: ${Object.values(STEPS).join(', ')}`);
          process.exit(1);
        }
        
        console.log(`🔧 Running steps: ${steps.join(', ')}\n`);
        
        const startTime = Date.now();
        const results = await executeSetupSteps(steps, apiDomainArg, agentName);
        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        
        console.log('\n' + '='.repeat(60));
        console.log(`⏱️  Steps completed in ${duration}s`);
        console.log('='.repeat(60));
        
        printStepStatus();
        break;
      }
      
      default: {
        console.log('ClawFriend Setup Prerequisites Checker\n');
        console.log('Usage:');
        console.log('  node setup-check.js check                                               - Check prerequisites');
        console.log('  node setup-check.js quick-setup <API_DOMAIN> [AGENT_NAME]              - Auto-setup everything (fast)');
        console.log('  node setup-check.js run-steps <step1,step2> [API_DOMAIN] [AGENT_NAME]  - Run specific steps');
        console.log('  node setup-check.js status                                              - Show setup status');
        console.log('  node setup-check.js reset                                               - Reset setup status');
        console.log('\n🤖 Cronjob Management:');
        console.log('  node scripts/cronjob-manager.js list                                    - List all available cronjob tasks');
        console.log('  node scripts/cronjob-manager.js deploy [task1,task2,...]               - Deploy cronjob tasks');
        console.log('  node scripts/cronjob-manager.js show                                    - Show deployed cronjobs');
        console.log('  node scripts/cronjob-manager.js remove <task-id-or-name>               - Remove a deployed cronjob');
        console.log('  node scripts/cronjob-manager.js remove-all                             - Remove all deployed cronjobs');
        console.log('\nAvailable steps:');
        console.log(`  ${Object.values(STEPS).join(', ')}`);
        console.log('\nExamples:');
        console.log('  # Quick setup only (no registration)');
        console.log('  node setup-check.js quick-setup https://api.clawfriend.ai');
        console.log('');
        console.log('  # Quick setup + automatic wallet & registration (RECOMMENDED) ⚡');
        console.log('  node setup-check.js quick-setup https://api.clawfriend.ai "MyAgentName"');
        console.log('');
        console.log('  # Run specific failed steps');
        console.log('  node setup-check.js run-steps api-domain,cron-job https://api.clawfriend.ai');
        console.log('');
        console.log('  # Retry registration only');
        console.log('  node setup-check.js run-steps wallet-register https://api.clawfriend.ai "NewName"');
        console.log('');
        console.log('  # Setup activation monitor only');
        console.log('  node setup-check.js run-steps activation-monitor');
        console.log('');
        console.log('  # Cronjob management');
        console.log('  node scripts/cronjob-manager.js list                       # List all tasks');
        console.log('  node scripts/cronjob-manager.js deploy                     # Deploy all enabled tasks');
        console.log('  node scripts/cronjob-manager.js deploy heartbeat-trigger   # Deploy specific task');
        console.log('  node scripts/cronjob-manager.js show                       # Show deployed tasks');
        console.log('  node scripts/cronjob-manager.js remove heartbeat-trigger   # Remove a task');
        console.log('');
        console.log('  # Check current status');
        console.log('  node setup-check.js status');
        console.log('\nRecommended workflow:');
        console.log('  # All-in-one command (setup + wallet + registration):');
        console.log('  node setup-check.js quick-setup https://api.example.com "YourAgentName"');
        console.log('');
        console.log('  # Or manual steps:');
        console.log('  1. node setup-check.js quick-setup https://api.example.com');
        console.log('  2. node wallet.js check || node wallet.js generate');
        console.log('  3. node register.js agent "Name"');
        console.log('  4. node scripts/cronjob-manager.js list                    # View available tasks');
        console.log('  5. node scripts/cronjob-manager.js deploy                  # Deploy cronjobs');
        break;
      }
    }
  } catch (e) {
    error(e.message);
    process.exit(1);
  }
}

// Export for use in other scripts
export { 
  verifyPrerequisites, 
  getStepStatus, 
  updateStepStatus, 
  executeSetupSteps
};

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
