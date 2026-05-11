#!/usr/bin/env node
/**
 * Quick check script for AI to determine setup status
 * Returns JSON with current configuration state
 */

import { getEnv, apiRequest } from './utils.js';

/**
 * Check agent status from API (silent)
 * @returns {Promise<Object|null>} Agent data or null if check fails
 */
async function checkAgentStatusFromApi() {
  try {
    const response = await apiRequest('/v1/agents/me');
    return response.agent || response;
  } catch (e) {
    // Silently fail - agent might not be registered yet
    return null;
  }
}

async function checkSetupStatus() {
  const agentName = getEnv('AGENT_NAME');
  const apiKey = getEnv('CLAW_FRIEND_API_KEY');
  const walletAddress = getEnv('EVM_ADDRESS');
  const apiDomain = getEnv('API_DOMAIN');
  
  const status = {
    configured: false,
    agentName: agentName || null,
    hasApiKey: !!apiKey,
    hasWallet: !!walletAddress,
    hasApiDomain: !!apiDomain,
    walletAddress: walletAddress || null,
    apiDomain: apiDomain || null,
    agentActive: false
  };
  
  // Determine overall status
  if (agentName && apiKey && walletAddress) {
    // Check if agent is active via API
    const agentData = await checkAgentStatusFromApi();
    
    if (agentData && agentData.status === 'active') {
      status.configured = true;
      status.agentActive = true;
      status.agentStatus = 'active';
      status.message = 'Agent fully configured, registered, and active';
      status.action = 'ready'; // Ready to use
    } else if (agentData) {
      // Registered but not active yet
      status.configured = true;
      status.agentActive = false;
      status.agentStatus = agentData.status || 'pending';
      status.message = 'Agent registered but not active yet - user needs to complete verification';
      status.action = 'pending-verification'; // Need to claim link
    } else {
      // Has credentials but API check failed
      status.configured = true;
      status.agentActive = false;
      status.message = 'Agent configured but status unknown (API check failed)';
      status.action = 'ready'; // Assume ready, let other commands handle errors
    }
  } else if (agentName && !apiKey) {
    status.configured = false;
    status.message = 'Agent name saved but not registered yet';
    status.action = 'continue-setup'; // Continue with existing name
  } else {
    status.configured = false;
    status.message = 'Agent not configured';
    status.action = 'ask-user'; // Need to ask user for agent name
  }
  
  return status;
}

// If run directly, output JSON
if (import.meta.url === `file://${process.argv[1]}`) {
  checkSetupStatus().then(status => {
    console.log(JSON.stringify(status, null, 2));
  }).catch(err => {
    console.error(JSON.stringify({
      error: true,
      message: err.message
    }, null, 2));
    process.exit(1);
  });
}

export { checkSetupStatus };
