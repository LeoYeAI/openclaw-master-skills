#!/usr/bin/env node

/**
 * Capacity monitoring core logic for Tide Watch
 * Parses OpenClaw session files and calculates token usage
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Default OpenClaw session directory
 */
const DEFAULT_SESSION_DIR = path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions');

/**
 * Load session registry from sessions.json
 * @param {string} sessionDir - Path to sessions directory
 * @returns {Object} Session registry mapping sessionId -> metadata
 */
function loadSessionRegistry(sessionDir = DEFAULT_SESSION_DIR) {
  const registryPath = path.join(sessionDir, 'sessions.json');
  
  try {
    if (!fs.existsSync(registryPath)) {
      return {};
    }
    
    const content = fs.readFileSync(registryPath, 'utf8');
    const registry = JSON.parse(content);
    
    // Build a reverse map: sessionId -> metadata
    const sessionMap = {};
    for (const [key, value] of Object.entries(registry)) {
      if (value.sessionId) {
        // Extract channel from multiple possible locations
        const channel = value.channel || 
                       value.deliveryContext?.channel || 
                       value.lastChannel || 
                       'unknown';
        
        // Extract label from groupChannel or origin.label
        const label = value.groupChannel || value.origin?.label || null;
        
        sessionMap[value.sessionId] = {
          channel,
          label,
          displayName: value.displayName || null
        };
      }
    }
    
    return sessionMap;
  } catch (error) {
    console.error('Error loading session registry:', error.message);
    return {};
  }
}

/**
 * Parse a session JSONL file and extract capacity data
 * @param {string} sessionPath - Path to the session .jsonl file
 * @param {Object} registry - Optional session registry from sessions.json
 * @returns {Object} Session capacity data
 */
function parseSession(sessionPath, registry = null) {
  try {
    const content = fs.readFileSync(sessionPath, 'utf8');
    const lines = content.trim().split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
      return null;
    }

    // Find the last message with usage data (totalTokens)
    // User messages don't have usage, so we need to scan backwards
    let tokensUsed = 0;
    let breakdown = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };
    let sessionId = null;
    let channel = 'unknown';
    let label = null;
    let model = 'unknown';
    let lastTimestamp = null;
    
    for (let i = lines.length - 1; i >= 0; i--) {
      try {
        const entry = JSON.parse(lines[i]);
        const usage = entry.message?.usage || entry.usage || {};
        
        // Update metadata
        sessionId = sessionId || entry.sessionKey || path.basename(sessionPath, '.jsonl');
        channel = channel === 'unknown' ? (entry.channel || 'unknown') : channel;
        label = label || entry.label || null;
        model = model === 'unknown' ? (entry.message?.model || entry.model || 'unknown') : model;
        lastTimestamp = lastTimestamp || entry.timestamp;
        
        // Use totalTokens from first message with usage data we find (scanning backwards)
        if (usage.totalTokens && tokensUsed === 0) {
          tokensUsed = usage.totalTokens;
          breakdown = {
            input: usage.input || 0,
            output: usage.output || 0,
            cacheRead: usage.cacheRead || 0,
            cacheWrite: usage.cacheWrite || 0
          };
          break;
        }
      } catch (err) {
        continue;
      }
    }
    
    // If no metadata found, use session file name
    sessionId = sessionId || path.basename(sessionPath, '.jsonl');
    lastTimestamp = lastTimestamp || new Date().toISOString();
    
    // Override with registry data if available (more reliable than JSONL)
    if (registry && registry[sessionId]) {
      channel = registry[sessionId].channel || channel;
      label = registry[sessionId].label || label;
    }
    
    const tokensMax = getModelMaxTokens(model);
    const percentage = tokensMax > 0 ? (tokensUsed / tokensMax) * 100 : 0;
    
    return {
      sessionId,
      channel,
      label,
      model,
      tokensUsed,
      tokensMax,
      percentage: Math.round(percentage * 10) / 10, // Round to 1 decimal
      status: getStatus(percentage),
      lastActivity: lastTimestamp,
      messageCount: lines.length,
      breakdown
    };
  } catch (error) {
    console.error(`Error parsing session ${sessionPath}:`, error.message);
    return null;
  }
}

/**
 * Get context limit from OpenClaw CLI (primary method)
 * @param {string} model - Model identifier
 * @returns {number|null} Context limit or null if not found
 */
function getContextFromCLI(model) {
  const { execSync } = require('child_process');
  
  try {
    const output = execSync('openclaw models list', { 
      encoding: 'utf8',
      timeout: 5000,
      stdio: ['ignore', 'pipe', 'ignore'] // Suppress stderr
    });
    
    // Parse table format:
    // Model                          Input      Ctx      Local
    // anthropic/claude-sonnet-4-5    text+image 195k     no
    
    const lines = output.split('\n');
    for (const line of lines) {
      // Check if line contains the model (handle both full and partial matches)
      if (line.includes(model)) {
        // Extract context window: look for pattern like "195k" or "1000k"
        const match = line.match(/\s+(\d+)k\s+/);
        if (match) {
          return parseInt(match[1]) * 1000;
        }
      }
    }
  } catch (error) {
    // CLI not available or command failed - fall through to next method
  }
  
  return null;
}

/**
 * Get context limit from OpenClaw config file (secondary method)
 * @param {string} model - Model identifier
 * @returns {number|null} Context limit or null if not found
 */
function getContextFromConfig(model) {
  const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
  
  try {
    if (!fs.existsSync(configPath)) {
      return null;
    }
    
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const providers = config.models?.providers || {};
    
    // Search all providers for matching model
    for (const provider of Object.values(providers)) {
      const models = provider.models || [];
      for (const modelDef of models) {
        // Match by exact ID or partial match
        const modelId = modelDef.id || '';
        if (modelId === model || 
            modelId.includes(model) || 
            model.includes(modelId)) {
          if (modelDef.contextWindow) {
            return modelDef.contextWindow;
          }
        }
      }
    }
  } catch (error) {
    // Config file missing or parse error - fall through to defaults
  }
  
  return null;
}

/**
 * Get context limit from hardcoded defaults (tertiary fallback)
 * @param {string} model - Model identifier
 * @returns {number} Context limit (never null, always returns a value)
 */
function getContextFromDefaults(model) {
  // Common model context windows (fallback only)
  const modelLimits = {
    'anthropic/claude-sonnet-4-5': 200000,
    'anthropic/claude-sonnet-4-6': 200000,
    'anthropic/claude-opus-4-5': 200000,
    'anthropic/claude-opus-4-6': 200000,
    'anthropic/claude-haiku-4-5': 200000,
    'openai/gpt-4': 128000,
    'openai/gpt-4-turbo': 128000,
    'openai/gpt-5.2': 200000,
    'openai/o1': 200000,
    'google/gemini-2.5-flash': 1000000,
    'google/gemini-3.1-pro': 2000000,
    'gemini-2.5-flash': 1000000,
    'gemini-3.1-pro': 2000000,
    'gemini-3.1-pro-preview': 2000000,
    'deepseek/deepseek-chat': 64000,
    'ollama/llama3.2': 128000,
    'ollama/qwen2.5:14b': 128000,
  };
  
  // Check exact match
  if (modelLimits[model]) {
    return modelLimits[model];
  }
  
  // Check partial match (e.g., "claude-sonnet" matches "anthropic/claude-sonnet-4-5")
  for (const [key, value] of Object.entries(modelLimits)) {
    if (key.includes(model) || model.includes(key)) {
      return value;
    }
  }
  
  // Conservative default for unknown models
  return 200000;
}

/**
 * Get maximum tokens for a model (three-tier fallback)
 * @param {string} model - Model identifier
 * @returns {number} Max tokens
 */
function getModelMaxTokens(model) {
  // Tier 1: Try OpenClaw CLI (most reliable, includes all configured models)
  const cliLimit = getContextFromCLI(model);
  if (cliLimit !== null) {
    return cliLimit;
  }
  
  // Tier 2: Try config file (works offline, structured data)
  const configLimit = getContextFromConfig(model);
  if (configLimit !== null) {
    return configLimit;
  }
  
  // Tier 3: Hardcoded defaults (graceful fallback)
  return getContextFromDefaults(model);
}

/**
 * Format a number as human-readable size (k/M notation)
 * @param {number} num - Number to format
 * @returns {string} Formatted size (e.g., "18.7k", "1.0M", "171k")
 */
function formatSize(num) {
  if (num >= 1000000) {
    // 1M+ -> show as M with one decimal
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 100000) {
    // 100k+ -> show as k without decimal
    return Math.round(num / 1000) + 'k';
  } else if (num >= 1000) {
    // 1k-100k -> show as k with one decimal
    return (num / 1000).toFixed(1) + 'k';
  } else {
    // < 1k -> show raw number
    return num.toString();
  }
}

/**
 * Format token count for display
 * @param {number} used - Tokens used
 * @param {number} max - Maximum tokens
 * @param {boolean} rawSize - If true, show exact numbers with commas
 * @returns {string} Formatted token string (e.g., "171k/195k" or "171,030/195,000")
 */
function formatTokens(used, max, rawSize = false) {
  if (rawSize) {
    // Raw mode: full precision with commas
    return `${used.toLocaleString()}/${max.toLocaleString()}`;
  }
  
  // Relative mode: human-readable
  return `${formatSize(used)}/${formatSize(max)}`;
}

/**
 * Get status emoji/text based on percentage
 * @param {number} percentage - Capacity percentage
 * @returns {string} Status indicator
 */
function getStatus(percentage) {
  if (percentage >= 95) return '🚨 CRITICAL';
  if (percentage >= 90) return '🔴 HIGH';
  if (percentage >= 85) return '🟠 ELEVATED';
  if (percentage >= 75) return '🟡 WARNING';
  return '✅ OK';
}

/**
 * Discover all configured agents from OpenClaw config
 * @returns {Array} List of agent configs with session directories
 */
function discoverAgents() {
  const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
  
  // Graceful degradation if config doesn't exist
  if (!fs.existsSync(configPath)) {
    return [{
      id: 'main',
      name: 'main',
      sessionDir: DEFAULT_SESSION_DIR
    }];
  }
  
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const agentsList = config.agents?.list || [];
    
    if (agentsList.length === 0) {
      // Fallback to main agent if no agents defined
      return [{
        id: 'main',
        name: 'main',
        sessionDir: DEFAULT_SESSION_DIR
      }];
    }
    
    return agentsList.map(agent => ({
      id: agent.id,
      name: agent.name || agent.id,
      identity: agent.identity || {},
      sessionDir: resolveSessionDir(agent)
    }));
  } catch (error) {
    console.warn(`Warning: Could not load OpenClaw config: ${error.message}`);
    // Fallback to main agent
    return [{
      id: 'main',
      name: 'main',
      sessionDir: DEFAULT_SESSION_DIR
    }];
  }
}

/**
 * Resolve session directory for an agent
 * @param {Object} agent - Agent configuration object
 * @returns {string} Path to agent's session directory
 */
function resolveSessionDir(agent) {
  const agentsBase = path.join(os.homedir(), '.openclaw', 'agents');
  
  // Try multiple possible locations
  const possiblePaths = [];
  
  // 1. agentDir/sessions (if agentDir is specified)
  if (agent.agentDir) {
    possiblePaths.push(path.join(agent.agentDir, 'sessions'));
  }
  
  // 2. Parent of agentDir if agentDir ends with /agent
  if (agent.agentDir && agent.agentDir.endsWith('/agent')) {
    const parentDir = path.dirname(agent.agentDir);
    possiblePaths.push(path.join(parentDir, 'sessions'));
  }
  
  // 3. Standard location: ~/.openclaw/agents/{agentId}/sessions
  possiblePaths.push(path.join(agentsBase, agent.id, 'sessions'));
  
  // Return first path that exists
  for (const dir of possiblePaths) {
    try {
      if (fs.existsSync(dir)) {
        return fs.realpathSync(dir);
      }
    } catch {
      // Continue to next path
    }
  }
  
  // None exist, return the most likely default
  return possiblePaths[possiblePaths.length - 1];
}

/**
 * Get sessions from a specific directory
 * @param {string} sessionDir - Path to sessions directory
 * @param {string} agentId - Optional agent ID for metadata
 * @param {string} agentName - Optional agent name for metadata
 * @returns {Array} Array of session objects
 */
function getSessionsFromDir(sessionDir, agentId = null, agentName = null) {
  try {
    if (!fs.existsSync(sessionDir)) {
      return [];
    }

    // Load session registry for metadata enrichment
    const registry = loadSessionRegistry(sessionDir);

    const files = fs.readdirSync(sessionDir);
    const sessions = [];

    for (const file of files) {
      if (file.endsWith('.jsonl')) {
        const sessionPath = path.join(sessionDir, file);
        const session = parseSession(sessionPath, registry);
        if (session) {
          // Annotate with agent metadata if provided
          if (agentId) {
            session.agentId = agentId;
            session.agentName = agentName || agentId;
          }
          // IMPORTANT: Track source directory for archiving
          session.sessionDir = sessionDir;
          sessions.push(session);
        }
      }
    }

    return sessions;
  } catch (error) {
    console.error(`Error reading sessions from ${sessionDir}:`, error.message);
    return [];
  }
}

/**
 * Get all sessions from the OpenClaw sessions directory
 * @param {string} sessionDir - Path to sessions directory (explicit override)
 * @param {boolean} multiAgent - Enable multi-agent discovery (default: true)
 * @param {Array} excludeAgents - Agent IDs to exclude
 * @returns {Array} Array of session objects
 */
function getAllSessions(sessionDir = null, multiAgent = true, excludeAgents = []) {
  // Explicit directory override (backward compatible)
  if (sessionDir) {
    return getSessionsFromDir(sessionDir);
  }
  
  // Single-agent mode (opt-out)
  if (!multiAgent) {
    return getSessionsFromDir(DEFAULT_SESSION_DIR, 'main', 'main');
  }
  
  // Multi-agent discovery (new default)
  const agents = discoverAgents();
  const allSessions = [];
  
  for (const agent of agents) {
    // Skip excluded agents
    if (excludeAgents.includes(agent.id)) {
      continue;
    }
    
    const sessions = getSessionsFromDir(agent.sessionDir, agent.id, agent.name);
    allSessions.push(...sessions);
  }
  
  return allSessions;
}

/**
 * Resolve session identifier to full session ID
 * Supports:
 * - Full session ID (UUID)
 * - Session label (#channel-name)
 * - Channel name (discord, webchat, etc.)
 * - Channel/label combo (discord/#channel-name)
 * 
 * @param {string} input - Session identifier (ID, label, or channel)
 * @param {string} sessionDir - Path to sessions directory
 * @returns {Object} Resolution result { sessionId, matches, ambiguous, error }
 */
function resolveSessionId(input, sessionDir = DEFAULT_SESSION_DIR) {
  // If it looks like a UUID (starts with hex pattern), use as-is
  if (/^[0-9a-f]{8}-/.test(input)) {
    return { sessionId: input, matches: null, ambiguous: false };
  }
  
  // Load session registry
  const registry = loadSessionRegistry(sessionDir);
  const allSessions = getAllSessions(sessionDir);
  
  // Build a searchable index
  const matches = [];
  
  for (const session of allSessions) {
    const sessionData = registry[session.sessionId] || {};
    
    // Match by exact label
    if (session.label && session.label === input) {
      matches.push({
        sessionId: session.sessionId,
        channel: session.channel,
        label: session.label,
        matchType: 'exact-label'
      });
      continue;
    }
    
    // Match by channel
    if (session.channel === input) {
      matches.push({
        sessionId: session.sessionId,
        channel: session.channel,
        label: session.label,
        matchType: 'channel'
      });
      continue;
    }
    
    // Match by channel/label combo
    const combo = session.label ? `${session.channel}/${session.label}` : session.channel;
    if (combo === input || combo.includes(input)) {
      matches.push({
        sessionId: session.sessionId,
        channel: session.channel,
        label: session.label,
        matchType: 'combo'
      });
      continue;
    }
    
    // Match by display name
    if (sessionData.displayName && sessionData.displayName.includes(input)) {
      matches.push({
        sessionId: session.sessionId,
        channel: session.channel,
        label: session.label,
        matchType: 'display-name'
      });
    }
  }
  
  // Handle results
  if (matches.length === 0) {
    return {
      sessionId: null,
      matches: null,
      ambiguous: false,
      error: `No sessions found matching: ${input}`
    };
  }
  
  if (matches.length === 1) {
    return {
      sessionId: matches[0].sessionId,
      matches: matches,
      ambiguous: false
    };
  }
  
  // Multiple matches - ambiguous
  return {
    sessionId: null,
    matches: matches,
    ambiguous: true,
    error: `Multiple sessions match "${input}". Please be more specific.`
  };
}

/**
 * Get a specific session by key
 * @param {string} sessionKey - Session identifier
 * @param {string} sessionDir - Path to sessions directory
 * @returns {Object|null} Session object or null
 */
function getSession(sessionKey, sessionDir = DEFAULT_SESSION_DIR) {
  const sessionPath = path.join(sessionDir, `${sessionKey}.jsonl`);
  if (!fs.existsSync(sessionPath)) {
    return null;
  }
  
  // Load session registry for metadata enrichment
  const registry = loadSessionRegistry(sessionDir);
  
  return parseSession(sessionPath, registry);
}

/**
 * Filter sessions by threshold
 * @param {Array} sessions - Array of session objects
 * @param {number} threshold - Minimum percentage to include
 * @returns {Array} Filtered sessions
 */
function filterByThreshold(sessions, threshold) {
  return sessions.filter(s => s.percentage >= threshold);
}

/**
 * Sort sessions by percentage (descending)
 * @param {Array} sessions - Array of session objects
 * @returns {Array} Sorted sessions
 */
function sortByCapacity(sessions) {
  return sessions.sort((a, b) => b.percentage - a.percentage);
}

/**
 * Filter sessions by activity age
 * @param {Array} sessions - Array of session objects
 * @param {number} hours - Maximum age in hours
 * @returns {Array} Filtered sessions
 */
function filterByActivityAge(sessions, hours) {
  const cutoffMs = Date.now() - (hours * 60 * 60 * 1000);
  return sessions.filter(s => new Date(s.lastActivity).getTime() >= cutoffMs);
}

/**
 * Get sessions older than specified age
 * @param {Array} sessions - Array of session objects
 * @param {number} hours - Minimum age in hours
 * @returns {Array} Sessions older than threshold
 */
function getSessionsOlderThan(sessions, hours) {
  const cutoffMs = Date.now() - (hours * 60 * 60 * 1000);
  return sessions.filter(s => new Date(s.lastActivity).getTime() < cutoffMs);
}

/**
 * Archive sessions to archive directory
 * @param {Array} sessions - Array of session objects to archive
 * @param {string} sessionDir - Session directory path
 * @param {boolean} dryRun - If true, don't actually move files
 * @returns {Object} Archive results
 */
function archiveSessions(sessions, sessionDir = null, dryRun = false) {
  const results = {
    archived: [],
    failed: [],
    dryRun
  };
  
  // Group sessions by their source directory (for multi-agent support)
  const sessionsByDir = new Map();
  
  for (const session of sessions) {
    // Use session's own sessionDir if available, otherwise fall back to provided sessionDir
    const dir = session.sessionDir || sessionDir || DEFAULT_SESSION_DIR;
    if (!sessionsByDir.has(dir)) {
      sessionsByDir.set(dir, []);
    }
    sessionsByDir.get(dir).push(session);
  }
  
  // Archive each group to its respective directory
  for (const [dir, dirSessions] of sessionsByDir) {
    const archiveDir = path.join(dir, 'archive', new Date().toISOString().split('T')[0]);
    
    if (!dryRun) {
      // Create archive directory
      try {
        fs.mkdirSync(archiveDir, { recursive: true });
      } catch (error) {
        console.error(`Failed to create archive directory ${archiveDir}: ${error.message}`);
        dirSessions.forEach(session => {
          results.failed.push({
            sessionId: session.sessionId,
            reason: `Failed to create archive directory: ${error.message}`
          });
        });
        continue;
      }
    }
    
    for (const session of dirSessions) {
      const sourcePath = path.join(dir, `${session.sessionId}.jsonl`);
      const targetPath = path.join(archiveDir, `${session.sessionId}.jsonl`);
      
      if (!fs.existsSync(sourcePath)) {
        results.failed.push({
          sessionId: session.sessionId,
          reason: 'File not found'
        });
        continue;
      }
      
      if (!dryRun) {
        try {
          // Move file to archive
          fs.renameSync(sourcePath, targetPath);
          
          // Update sessions.json registry
          updateSessionRegistry(dir, session.sessionId, 'remove');
          
          results.archived.push({
            sessionId: session.sessionId,
            channel: session.channel,
            label: session.label,
            lastActivity: session.lastActivity,
            capacity: session.percentage,
            archivedTo: targetPath
          });
        } catch (error) {
          results.failed.push({
            sessionId: session.sessionId,
            reason: error.message
          });
        }
      } else {
        // Dry run - just record what would happen
        results.archived.push({
          sessionId: session.sessionId,
          channel: session.channel,
          label: session.label,
          lastActivity: session.lastActivity,
          capacity: session.percentage,
          wouldArchiveTo: targetPath
        });
      }
    }
  }
  
  return results;
}

/**
 * Update sessions.json registry (remove or update entry)
 * @param {string} sessionDir - Session directory path
 * @param {string} sessionId - Session ID to update
 * @param {string} action - Action to perform ('remove')
 */
function updateSessionRegistry(sessionDir, sessionId, action) {
  const registryPath = path.join(sessionDir, 'sessions.json');
  
  try {
    if (!fs.existsSync(registryPath)) {
      return;
    }
    
    const content = fs.readFileSync(registryPath, 'utf8');
    const registry = JSON.parse(content);
    
    if (action === 'remove') {
      // Find and remove entries with this sessionId
      for (const key in registry) {
        if (registry[key].sessionId === sessionId) {
          delete registry[key];
        }
      }
      
      // Write back
      fs.writeFileSync(registryPath, JSON.stringify(registry, null, 2));
    }
  } catch (error) {
    console.error(`Warning: Could not update sessions.json: ${error.message}`);
  }
}

/**
 * Format session data as a table row
 * @param {Object} session - Session object
 * @param {boolean} rawSize - If true, show exact token counts
 * @returns {string} Formatted table row
 */
function formatTableRow(session, rawSize = false) {
  const sessionId = session.sessionId.substring(0, 8);
  const channel = session.channel.padEnd(12);
  const model = (session.model || 'unknown').substring(0, 25).padEnd(25);
  const capacity = `${session.percentage.toFixed(1)}%`.padStart(6);
  const tokens = formatTokens(session.tokensUsed, session.tokensMax, rawSize).padStart(rawSize ? 20 : 13);
  const status = session.status.padEnd(15);
  
  return `${sessionId}  ${channel}  ${model}  ${capacity}  ${tokens}  ${status}`;
}

/**
 * Format sessions as a table
 * @param {Array} sessions - Array of session objects
 * @param {boolean} rawSize - If true, show exact token counts
 * @returns {string} Formatted table
 */
function formatTable(sessions, rawSize = false) {
  const header = 'Session   Channel       Model                      Cap %              Tokens  Status';
  const separator = '-'.repeat(header.length);
  
  const rows = sessions.map(s => formatTableRow(s, rawSize));
  
  return [header, separator, ...rows].join('\n');
}

/**
 * Format sessions as JSON
 * @param {Array} sessions - Array of session objects
 * @param {boolean} pretty - Pretty print JSON
 * @returns {string} JSON string
 */
function formatJSON(sessions, pretty = false) {
  return pretty ? JSON.stringify(sessions, null, 2) : JSON.stringify(sessions);
}

/**
 * Get capacity indicator emoji
 * @param {number} percentage - Capacity percentage
 * @returns {string} Emoji indicator
 */
function getCapacityEmoji(percentage) {
  if (percentage >= 95) return '🔴';
  if (percentage >= 85) return '🟠';
  if (percentage >= 75) return '🟡';
  return '🟢';
}

/**
 * Create a visual capacity bar
 * @param {number} percentage - Capacity percentage
 * @param {number} width - Width of the bar in characters
 * @returns {string} Visual capacity bar
 */
function getCapacityBar(percentage, width = 20) {
  const filled = Math.round((percentage / 100) * width);
  const empty = width - filled;
  const bar = '█'.repeat(filled) + '░'.repeat(empty);
  return bar;
}

/**
 * Generate recommendations based on session capacities
 * @param {Array} sessions - Array of session objects
 * @returns {Array} Array of recommendation strings
 */
function getRecommendations(sessions) {
  const recommendations = [];
  
  const critical = sessions.filter(s => s.percentage >= 95);
  const high = sessions.filter(s => s.percentage >= 90 && s.percentage < 95);
  const elevated = sessions.filter(s => s.percentage >= 85 && s.percentage < 90);
  
  // Critical sessions
  if (critical.length > 0) {
    critical.forEach(s => {
      const id = s.sessionId.substring(0, 8);
      recommendations.push(`🚨 URGENT: Reset ${s.channel}/${id} immediately (${s.percentage}%)`);
    });
  }
  
  // High capacity sessions
  if (high.length > 0) {
    high.forEach(s => {
      const id = s.sessionId.substring(0, 8);
      recommendations.push(`🔴 Reset ${s.channel}/${id} soon (${s.percentage}%)`);
    });
  }
  
  // Elevated sessions
  if (elevated.length > 0) {
    elevated.forEach(s => {
      const id = s.sessionId.substring(0, 8);
      recommendations.push(`🟠 Consider wrapping up ${s.channel}/${id} (${s.percentage}%)`);
    });
  }
  
  // Suggest switching to low-capacity session (same-agent only)
  const highOrCritical = [...critical, ...high];
  if (highOrCritical.length > 0) {
    // Group by agent to find same-agent alternatives
    const agentsNeedingShift = new Set(highOrCritical.map(s => s.agentId || 'main'));
    
    for (const agentId of agentsNeedingShift) {
      // Find low-capacity sessions for this agent only
      const sameAgentLowCapacity = sessions.filter(s => 
        (s.agentId || 'main') === agentId && 
        s.percentage < 50
      ).sort((a, b) => a.percentage - b.percentage);
      
      if (sameAgentLowCapacity.length > 0) {
        const best = sameAgentLowCapacity[0];
        const id = best.sessionId.substring(0, 8);
        const agentName = best.agentName || agentId;
        recommendations.push(`💡 Switch active work to ${best.channel}/${id} (${agentName}, ${best.percentage}%)`);
      }
    }
  }
  
  // All good
  if (recommendations.length === 0) {
    recommendations.push('✅ All sessions have healthy capacity');
  }
  
  return recommendations;
}

/**
 * Format channel and label for display
 * @param {string} channel - Channel name
 * @param {string|null} label - Optional label
 * @returns {string} Formatted channel/label string
 */
function formatChannelLabel(channel, label) {
  if (label) {
    return `${channel}/${label}`;
  }
  return channel;
}

/**
 * Format timestamp as relative time (e.g., "2 hours ago", "3 days ago")
 * @param {string} timestamp - ISO timestamp
 * @returns {string} Relative time string
 */
function formatRelativeTime(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  
  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  
  if (seconds < 60) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  if (weeks < 4) return `${weeks}w ago`;
  if (months < 12) return `${months}mo ago`;
  return `${years}y ago`;
}

/**
 * Parse time string to hours (e.g., "4d" -> 96, "2w" -> 336)
 * @param {string} timeStr - Time string (e.g., "4d", "2w", "1mo", "1y")
 * @returns {number} Hours
 */
function parseTimeString(timeStr) {
  const match = timeStr.match(/^(\d+)(m|h|d|w|mo|y)$/);
  if (!match) {
    throw new Error(`Invalid time format: ${timeStr}. Use format like: 4d, 2w, 1mo, 1y`);
  }
  
  const value = parseInt(match[1], 10);
  const unit = match[2];
  
  const hoursPerUnit = {
    'm': 1/60,      // minutes
    'h': 1,         // hours
    'd': 24,        // days
    'w': 24 * 7,    // weeks
    'mo': 24 * 30,  // months (approximate)
    'y': 24 * 365   // years (approximate)
  };
  
  return value * hoursPerUnit[unit];
}

/**
 * Format sessions as a dashboard
 * @param {Array} sessions - Array of session objects
 * @param {Map} changes - Optional map of sessionId -> change info (for watch mode)
 * @returns {string} Formatted dashboard
 */
function formatDashboard(sessions, changes = null, rawSize = false) {
  const sorted = sortByCapacity(sessions);
  const gatewayStatus = checkGatewayStatus();
  
  // Check if we have multi-agent sessions
  const hasMultiAgent = sorted.some(s => s.agentName && s.agentName !== 'main');
  
  // ANSL color codes
  const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',      // Capacity increasing (bad)
    green: '\x1b[32m',    // Capacity decreasing (good)
    yellow: '\x1b[33m',   // New session
    dim: '\x1b[2m',       // Unchanged
  };
  
  const lines = [];
  lines.push('');
  lines.push('TIDE WATCH DASHBOARD 🌊');
  lines.push(`Gateway Status: ${gatewayStatus.emoji} ${gatewayStatus.status}`);
  
  // Adjust layout for multi-agent mode
  let separatorLength, header;
  if (hasMultiAgent) {
    separatorLength = changes ? 155 : 140;
    header = changes 
      ? 'Session ID  Agent        Channel/Label     Model                      Capacity                    Tokens        Last Active  Trend'
      : 'Session ID  Agent        Channel/Label     Model                      Capacity                    Tokens        Last Active';
  } else {
    separatorLength = changes ? 135 : 120;
    header = changes 
      ? 'Session ID  Channel/Label     Model                      Capacity                    Tokens        Last Active  Trend'
      : 'Session ID  Channel/Label     Model                      Capacity                    Tokens        Last Active';
  }
  
  lines.push('─'.repeat(separatorLength));
  lines.push(header);
  lines.push('─'.repeat(separatorLength));
  
  sorted.forEach(session => {
    const id = session.sessionId.substring(0, 10).padEnd(10);
    const agentName = hasMultiAgent ? (session.agentName || 'main').substring(0, 11).padEnd(11) : '';
    const channelLabel = formatChannelLabel(session.channel, session.label).substring(0, 16).padEnd(16);
    const model = (session.model || 'unknown').substring(0, 25).padEnd(25);
    const emoji = getCapacityEmoji(session.percentage);
    const bar = getCapacityBar(session.percentage, 10);
    const pct = `${session.percentage.toFixed(1)}%`.padStart(6);
    const tokens = formatTokens(session.tokensUsed, session.tokensMax, rawSize).padStart(rawSize ? 20 : 13);
    const lastActive = formatRelativeTime(session.lastActivity).padStart(10);
    
    let line = hasMultiAgent 
      ? `${id}  ${agentName}  ${channelLabel}  ${model}  ${emoji} ${bar} ${pct}  ${tokens}  ${lastActive}`
      : `${id}  ${channelLabel}  ${model}  ${emoji} ${bar} ${pct}  ${tokens}  ${lastActive}`;
    
    // Add trend information if we have changes
    if (changes && changes.has(session.sessionId)) {
      const change = changes.get(session.sessionId);
      let trend = '';
      
      if (change.type === 'new') {
        trend = `${colors.yellow}NEW${colors.reset}`;
      } else if (change.type === 'increased') {
        const arrow = '↑';
        const delta = `+${change.delta.toFixed(1)}%`;
        trend = `${colors.red}${arrow} ${delta}${colors.reset}`;
      } else if (change.type === 'decreased') {
        const arrow = '↓';
        const delta = `-${change.delta.toFixed(1)}%`;
        trend = `${colors.green}${arrow} ${delta}${colors.reset}`;
      } else {
        trend = `${colors.dim}─${colors.reset}`;
      }
      
      line += `  ${trend}`;
    }
    
    lines.push(line);
  });
  
  // Match separator to header length (already defined above)
  lines.push('─'.repeat(separatorLength));
  
  // Summary
  const critical = sorted.filter(s => s.percentage >= 95).length;
  const high = sorted.filter(s => s.percentage >= 90 && s.percentage < 95).length;
  const elevated = sorted.filter(s => s.percentage >= 85 && s.percentage < 90).length;
  const warning = sorted.filter(s => s.percentage >= 75 && s.percentage < 85).length;
  
  const summary = [];
  if (critical > 0) summary.push(`${critical} critical`);
  if (high > 0) summary.push(`${high} high`);
  if (elevated > 0) summary.push(`${elevated} elevated`);
  if (warning > 0) summary.push(`${warning} warning`);
  
  if (summary.length > 0) {
    lines.push(`⚠️  ${summary.join(', ')}`);
  } else {
    lines.push('✅ All sessions healthy');
  }
  
  // Multi-agent summary
  if (hasMultiAgent) {
    lines.push('');
    lines.push('Summary by Agent:');
    
    // Group sessions by agent
    const byAgent = new Map();
    sorted.forEach(session => {
      const agentName = session.agentName || 'main';
      if (!byAgent.has(agentName)) {
        byAgent.set(agentName, []);
      }
      byAgent.get(agentName).push(session);
    });
    
    // Display per-agent stats
    for (const [agentName, agentSessions] of byAgent) {
      const count = agentSessions.length;
      const avgCapacity = agentSessions.reduce((sum, s) => sum + s.percentage, 0) / count;
      const maxCapacity = Math.max(...agentSessions.map(s => s.percentage));
      
      const agentDisplay = agentName.padEnd(10);
      const countDisplay = `${count} session${count !== 1 ? 's' : ''}`.padEnd(12);
      const avgDisplay = `avg ${avgCapacity.toFixed(1)}%`.padEnd(10);
      const maxDisplay = `max ${maxCapacity.toFixed(1)}%`;
      
      lines.push(`  ${agentDisplay} ${countDisplay} ${avgDisplay} ${maxDisplay}`);
    }
  }
  
  lines.push('');
  
  // Recommendations
  const recommendations = getRecommendations(sorted);
  if (recommendations.length > 0) {
    lines.push('RECOMMENDED ACTIONS:');
    recommendations.forEach(rec => lines.push(`  ${rec}`));
    lines.push('');
  }
  
  return lines.join('\n');
}

// Gateway status cache (async, non-blocking)
let gatewayStatusCache = null;
let lastGatewayCheck = 0;
let gatewayCheckInProgress = false;
// Configurable gateway check parameters (can be updated via setConfig)
let GATEWAY_REFRESH_INTERVAL = 30000; // Check every 30 seconds (default)
let GATEWAY_TIMEOUT = 3000; // 3 seconds (default)

/**
 * Check OpenClaw gateway status (fully async, never blocks)
 * @returns {Object} Gateway status { online: boolean, status: string, emoji: string }
 */
function checkGatewayStatus() {
  const now = Date.now();
  
  // Start background check if cache is stale and no check in progress
  if (!gatewayCheckInProgress && 
      (!gatewayStatusCache || (now - lastGatewayCheck > GATEWAY_REFRESH_INTERVAL))) {
    startBackgroundGatewayCheck();
  }
  
  // ALWAYS return immediately (never block)
  return gatewayStatusCache || {
    online: false,
    status: 'Checking...',
    emoji: '⏳'
  };
}

/**
 * Start background gateway status check (async, non-blocking)
 */
function startBackgroundGatewayCheck() {
  gatewayCheckInProgress = true;
  
  const { exec } = require('child_process');
  
  // Async, non-blocking check
  exec('openclaw gateway status', { 
    timeout: GATEWAY_TIMEOUT,  // Configurable timeout (default 3s)
    encoding: 'utf8' 
  }, (error, stdout) => {
    // Callback runs when check completes (doesn't block dashboard)
    if (!error && stdout) {
      const isRunning = stdout.toLowerCase().includes('online') || 
                        stdout.toLowerCase().includes('running') ||
                        stdout.toLowerCase().includes('active');
      
      gatewayStatusCache = {
        online: isRunning,
        status: isRunning ? 'Online' : 'Offline',
        emoji: isRunning ? '🟢' : '🔴',
        lastUpdated: Date.now()
      };
      lastGatewayCheck = Date.now();
    } else if (!gatewayStatusCache) {
      // First check failed, set to unknown
      gatewayStatusCache = {
        online: false,
        status: 'Unknown',
        emoji: '❓',
        error: error?.message
      };
      lastGatewayCheck = Date.now();
    }
    // If check fails but we have cache, keep existing cache
    
    gatewayCheckInProgress = false;
  });
}

/**
 * Update configuration values (for gateway check intervals/timeout)
 * @param {Object} config - Configuration object
 * @param {number} config.gatewayInterval - Gateway check interval in seconds
 * @param {number} config.gatewayTimeout - Gateway command timeout in seconds
 */
function setConfig(config) {
  if (config.gatewayInterval) {
    GATEWAY_REFRESH_INTERVAL = config.gatewayInterval * 1000; // Convert seconds to milliseconds
  }
  if (config.gatewayTimeout) {
    GATEWAY_TIMEOUT = config.gatewayTimeout * 1000; // Convert seconds to milliseconds
  }
}

module.exports = {
  loadSessionRegistry,
  parseSession,
  getAllSessions,
  getSessionsFromDir,
  discoverAgents,
  resolveSessionDir,
  getSession,
  resolveSessionId,
  filterByThreshold,
  filterByActivityAge,
  getSessionsOlderThan,
  sortByCapacity,
  formatTable,
  formatJSON,
  formatDashboard,
  formatTokens,
  formatChannelLabel,
  formatRelativeTime,
  parseTimeString,
  archiveSessions,
  updateSessionRegistry,
  getRecommendations,
  getCapacityEmoji,
  getCapacityBar,
  checkGatewayStatus,
  setConfig,
  DEFAULT_SESSION_DIR
};
