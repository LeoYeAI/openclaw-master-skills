#!/usr/bin/env node

/**
 * Tide Watch CLI
 * Manual capacity checks for OpenClaw sessions
 */

const {
  getAllSessions,
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
  formatRelativeTime,
  parseTimeString,
  archiveSessions,
  DEFAULT_SESSION_DIR
} = require('../lib/capacity');

const path = require('path');

const USAGE = `
Tide Watch 🌊 - OpenClaw Session Capacity Monitor

USAGE:
  tide-watch check [--session <key>]     Check specific session
  tide-watch check --current              Auto-detect and check current session
  tide-watch report [--all]               List all sessions (or above threshold)
  tide-watch dashboard                    Visual dashboard with recommendations
  tide-watch archive --older-than <time>  Archive old sessions (time-based)
  tide-watch archive --session <id>       Archive specific session(s)
  tide-watch resume-prompt <action>      Manage session resumption prompts
  tide-watch status                       Quick status summary
  tide-watch help                         Show this help

OPTIONS:
  --session <key>      Target a specific session (ID, label, channel, or combo)
                       Examples: abc123, "#navi-code-yatta", discord, "discord/#channel"
                       For archive: can be specified multiple times to archive several sessions
  --current            Auto-detect current session (requires OPENCLAW_SESSION_ID env var)
                       Use with check command for heartbeat monitoring
  --all                Show all sessions regardless of capacity
  --threshold <num>    Filter sessions above this percentage (default: 75)
  --active <hours>     Only show sessions active within N hours (e.g., --active 24)
  --older-than <time>  Archive sessions older than time (e.g., 4d, 2w, 1mo)
  --dry-run            Preview archive without making changes
  --exclude-channel    Exclude specific channel from archiving
  --min-capacity <num> Only archive sessions below this capacity (default: no limit)
  --json               Output as JSON instead of table
  --pretty             Pretty-print JSON (requires --json)
  --watch              Live updates (dashboard only, refreshes every 10s)
  --session-dir <path> Custom session directory (default: ~/.openclaw/agents/main/sessions)
  
MULTI-AGENT:
  --all-agents              Multi-agent discovery mode (default, auto-discovers from OpenClaw config)
  --single-agent-only       Single-agent mode (main agent only, disables auto-discovery)
  --agent <id>              Filter to specific agent
  --exclude-agent <id>      Exclude specific agent (can be used multiple times)

CONFIGURATION:
  --refresh-interval <seconds>   Dashboard refresh interval (default: 10, min: 1, max: 300)
  --gateway-interval <seconds>   Gateway status check interval (default: 30, min: 5, max: 600)
  --gateway-timeout <seconds>    Gateway command timeout (default: 3, min: 1, max: 30)
  
  Config file: ~/.config/tide-watch/config.json
  Env vars: TIDE_WATCH_REFRESH_INTERVAL, TIDE_WATCH_GATEWAY_INTERVAL, TIDE_WATCH_GATEWAY_TIMEOUT
  Precedence: CLI flags > env vars > config file > defaults

EXAMPLES:
  tide-watch check                        # Check current session
  tide-watch check --session abc123       # Check specific session
  tide-watch report                       # Show sessions above 75%
  tide-watch report --all                 # Show all sessions
  tide-watch report --threshold 90        # Show sessions above 90%
  tide-watch dashboard                    # Visual dashboard view
  tide-watch dashboard --active 48        # Only sessions active in last 48 hours
  tide-watch dashboard --watch            # Live updating dashboard
  tide-watch archive --older-than 4d --dry-run    # Preview archiving sessions older than 4 days
  tide-watch archive --older-than 2w              # Archive sessions older than 2 weeks
  tide-watch archive --older-than 1mo --exclude-channel discord  # Archive but keep Discord
  tide-watch archive --session abc123             # Archive specific session by ID
  tide-watch archive --session "#navi-code"       # Archive specific session by label
  tide-watch archive --session abc123 --session def456  # Archive multiple sessions
  tide-watch resume-prompt edit                  # Edit resumption prompt for current session
  tide-watch resume-prompt show                  # Show current resumption prompt
  tide-watch resume-prompt list                  # List all resumption prompts
  tide-watch status                       # Quick status summary

RESTORE-PROMPT ACTIONS:
  edit                   Open resumption prompt in editor
  show                   Display current resumption prompt
  info                   Show resumption prompt metadata
  list                   List all resumption prompts
  test                   Test resumption prompt (dry-run)
  delete                 Delete resumption prompt
  enable                 Enable auto-loading for session
  disable                Disable auto-loading for session
  status                 Check enabled/disabled state
  discovery-off          Disable feature discovery globally
  discovery-on           Enable feature discovery globally
  discovery-status       Check discovery enabled/disabled state

`.trim();

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  
  const options = {
    command: args[0] || 'help',
    session: null,
    sessions: [],  // For archive command: multiple sessions
    current: false,  // Auto-detect current session
    all: false,
    threshold: 75,
    activeHours: null,
    olderThan: null,
    dryRun: false,
    excludeChannel: null,
    minCapacity: null,
    json: false,
    pretty: false,
    watch: false,
    sessionDir: null,  // null = auto-discover (not DEFAULT_SESSION_DIR)
    // Multi-agent options
    multiAgent: true,
    singleAgentOnly: false,
    agent: null,
    excludeAgents: [],
    // Config overrides (CLI flags)
    refreshInterval: null,
    gatewayInterval: null,
    gatewayTimeout: null,
    // Display options
    rawSize: false
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--session' && i + 1 < args.length) {
      const sessionValue = args[++i];
      // For archive command: support multiple --session flags
      if (options.command === 'archive') {
        options.sessions.push(sessionValue);
      }
      // For other commands: single session only
      options.session = sessionValue;
    } else if (arg === '--all') {
      options.all = true;
    } else if (arg === '--threshold' && i + 1 < args.length) {
      options.threshold = parseInt(args[++i], 10);
    } else if (arg === '--active' && i + 1 < args.length) {
      options.activeHours = parseInt(args[++i], 10);
    } else if (arg === '--older-than' && i + 1 < args.length) {
      options.olderThan = args[++i];
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--exclude-channel' && i + 1 < args.length) {
      options.excludeChannel = args[++i];
    } else if (arg === '--min-capacity' && i + 1 < args.length) {
      options.minCapacity = parseInt(args[++i], 10);
    } else if (arg === '--json') {
      options.json = true;
    } else if (arg === '--pretty') {
      options.pretty = true;
    } else if (arg === '--watch') {
      options.watch = true;
    } else if (arg === '--session-dir' && i + 1 < args.length) {
      options.sessionDir = args[++i];
    } else if (arg === '--refresh-interval' && i + 1 < args.length) {
      options.refreshInterval = parseInt(args[++i], 10);
    } else if (arg === '--gateway-interval' && i + 1 < args.length) {
      options.gatewayInterval = parseInt(args[++i], 10);
    } else if (arg === '--gateway-timeout' && i + 1 < args.length) {
      options.gatewayTimeout = parseInt(args[++i], 10);
    } else if (arg === '--single-agent-only') {
      options.singleAgentOnly = true;
      options.multiAgent = false;
    } else if (arg === '--all-agents') {
      options.multiAgent = true;
      options.singleAgentOnly = false;
    } else if (arg === '--agent' && i + 1 < args.length) {
      options.agent = args[++i];
    } else if (arg === '--exclude-agent' && i + 1 < args.length) {
      options.excludeAgents.push(args[++i]);
    } else if (arg === '--raw-size') {
      options.rawSize = true;
    } else if (arg === '--current') {
      options.current = true;
    }
  }

  return options;
}

/**
 * Check command: Show capacity for current or specific session
 */
function checkCommand(options) {
  // Handle --current flag
  if (options.current && !options.session) {
    const sessionId = process.env.OPENCLAW_SESSION_ID;
    
    if (!sessionId) {
      console.error('❌ Cannot auto-detect current session');
      console.error('   OPENCLAW_SESSION_ID environment variable not set');
      console.error('');
      console.error('   This feature requires OpenClaw core support (see Issue #36).');
      console.error('   As a workaround, use --session <key> to specify session explicitly.');
      process.exit(1);
    }
    
    options.session = sessionId;
  }
  
  if (options.session) {
    let session;
    
    // For auto-detected sessions, search across all agents
    if (options.current) {
      const allSessions = getAllSessions(options.sessionDir, options.multiAgent, options.excludeAgents);
      session = allSessions.find(s => s.sessionId === options.session || s.sessionId.startsWith(options.session));
    } else {
      // Resolve session ID
      const resolvedSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!resolvedSessionId) {
        process.exit(1);
      }
      
      // Check specific session
      session = getSession(resolvedSessionId, options.sessionDir);
    }
    
    if (!session) {
      console.error(`❌ Session not found: ${resolvedSessionId}`);
      process.exit(1);
    }
    
    if (options.json) {
      console.log(formatJSON([session], options.pretty));
    } else {
      console.log(`\nSession: ${session.sessionId}`);
      console.log(`Channel: ${session.channel}`);
      if (session.label) {
        console.log(`Label:   ${session.label}`);
      }
      console.log(`Model:   ${session.model}`);
      console.log(`Status:  ${session.status}`);
      console.log(`\nCapacity: ${session.percentage}%`);
      console.log(`Tokens:   ${formatTokens(session.tokensUsed, session.tokensMax, options.rawSize)}`);
      console.log(`Messages: ${session.messageCount}`);
      console.log(`Last Activity: ${new Date(session.lastActivity).toLocaleString()}\n`);
      
      // Show recommendations
      if (session.percentage >= 95) {
        console.log('🚨 CRITICAL: Session will lock soon! Save to memory and reset immediately.');
      } else if (session.percentage >= 90) {
        console.log('🔴 HIGH: Recommend finishing current task and resetting session.');
      } else if (session.percentage >= 85) {
        console.log('🟠 ELEVATED: Consider wrapping up soon and switching to a fresh session.');
      } else if (session.percentage >= 75) {
        console.log('🟡 WARNING: Capacity approaching threshold. Plan to reset soon.');
      } else {
        console.log('✅ OK: Plenty of capacity remaining.');
      }
      console.log('');
    }
  } else {
    // Try to auto-detect current session from environment
    const sessionId = process.env.OPENCLAW_SESSION_ID;
    
    if (!sessionId) {
      console.error('❌ Cannot auto-detect current session');
      console.error('   Either:');
      console.error('     1. Use --session <key> to specify session explicitly');
      console.error('     2. Set OPENCLAW_SESSION_ID environment variable');
      console.error('     3. Use --current flag explicitly');
      console.error('');
      console.error('   Note: Auto-detection requires OpenClaw to export session context.');
      console.error('         This feature is pending OpenClaw core support (see Issue #36).');
      process.exit(1);
    }
    
    // Set options and use auto-detection path
    options.session = sessionId;
    options.current = true;
    checkCommand(options);
  }
}

/**
 * Report command: List all sessions with capacity info
 */
function reportCommand(options) {
  let sessions = getAllSessions(options.sessionDir, options.multiAgent, options.excludeAgents);
  
  // Filter by agent if specified
  if (options.agent) {
    sessions = sessions.filter(s => s.agentId === options.agent || s.agentName === options.agent);
  }
  
  if (sessions.length === 0) {
    console.log('No sessions found.');
    return;
  }

  // Filter by activity age if specified
  if (options.activeHours) {
    sessions = filterByActivityAge(sessions, options.activeHours);
  }

  // Filter by threshold unless --all is specified
  if (!options.all) {
    sessions = filterByThreshold(sessions, options.threshold);
  }

  // Sort by capacity (highest first)
  sessions = sortByCapacity(sessions);

  if (sessions.length === 0) {
    const filters = [];
    if (options.activeHours) filters.push(`active in last ${options.activeHours}h`);
    if (!options.all) filters.push(`above ${options.threshold}%`);
    console.log(`No sessions ${filters.join(' and ')}.`);
    return;
  }

  if (options.json) {
    console.log(formatJSON(sessions, options.pretty));
  } else {
    console.log(`\nTide Watch Report 🌊\n`);
    console.log(formatTable(sessions, options.rawSize));
    const filterDesc = options.activeHours ? ` (active in last ${options.activeHours}h)` : '';
    console.log(`\nTotal: ${sessions.length} session(s)${!options.all ? ` above ${options.threshold}%` : ''}${filterDesc}\n`);
  }
}

/**
 * Status command: Quick summary
 */
function statusCommand(options) {
  let sessions = getAllSessions(options.sessionDir, options.multiAgent, options.excludeAgents);
  
  // Filter by agent if specified
  if (options.agent) {
    sessions = sessions.filter(s => s.agentId === options.agent || s.agentName === options.agent);
  }
  
  if (sessions.length === 0) {
    console.log('No active sessions.');
    return;
  }

  const total = sessions.length;
  const critical = sessions.filter(s => s.percentage >= 95).length;
  const high = sessions.filter(s => s.percentage >= 90 && s.percentage < 95).length;
  const elevated = sessions.filter(s => s.percentage >= 85 && s.percentage < 90).length;
  const warning = sessions.filter(s => s.percentage >= 75 && s.percentage < 85).length;
  const ok = sessions.filter(s => s.percentage < 75).length;

  console.log(`\nTide Watch Status 🌊\n`);
  console.log(`Total Sessions: ${total}`);
  console.log(`  🚨 Critical (≥95%):  ${critical}`);
  console.log(`  🔴 High (90-94%):    ${high}`);
  console.log(`  🟠 Elevated (85-89%): ${elevated}`);
  console.log(`  🟡 Warning (75-84%):  ${warning}`);
  console.log(`  ✅ OK (<75%):         ${ok}\n`);

  if (critical > 0 || high > 0) {
    console.log('⚠️  Action needed: Run "tide-watch report" for details\n');
  }
}

/**
 * Dashboard command: Visual overview with recommendations
 */
function dashboardCommand(options) {
  // Apply config to capacity module (gateway intervals/timeout)
  const { setConfig } = require('../lib/capacity');
  setConfig(options.config);
  
  // Track previous session state for change detection (watch mode only)
  let previousSessions = new Map();
  
  const showDashboard = () => {
    let sessions = getAllSessions(options.sessionDir, options.multiAgent, options.excludeAgents);
    
    // Filter by agent if specified
    if (options.agent) {
      sessions = sessions.filter(s => s.agentId === options.agent || s.agentName === options.agent);
    }
    
    if (sessions.length === 0) {
      console.log('\nNo active sessions found.\n');
      return;
    }

    // Filter by activity age if specified
    if (options.activeHours) {
      const beforeFilter = sessions.length;
      sessions = filterByActivityAge(sessions, options.activeHours);
      if (sessions.length === 0) {
        console.log(`\nNo sessions active in the last ${options.activeHours} hours (${beforeFilter} total).\n`);
        return;
      }
    }

    if (options.json) {
      // JSON output includes sessions + recommendations
      const { getRecommendations } = require('../lib/capacity');
      const data = {
        sessions,
        recommendations: getRecommendations(sessions),
        timestamp: new Date().toISOString(),
        filters: {
          activeHours: options.activeHours || null
        }
      };
      console.log(formatJSON(data, options.pretty));
    } else {
      // Compute changes if we're in watch mode and have previous state
      let changes = null;
      if (options.watch && previousSessions.size > 0) {
        changes = computeChanges(previousSessions, sessions);
      }
      
      // Clear screen for watch mode using ANSI escape sequences
      // This provides smooth in-place updates without screen flashing
      if (options.watch) {
        // Move cursor to home position (0,0)
        process.stdout.write('\x1b[H');
        // Clear from cursor to end of screen
        process.stdout.write('\x1b[J');
        console.log(`Last updated: ${new Date().toLocaleString()}\n`);
      }
      
      // Visual dashboard with change highlighting (if available)
      console.log(formatDashboard(sessions, changes, options.rawSize));
      
      // Show filter info if active
      if (options.activeHours) {
        console.log(`Showing sessions active in last ${options.activeHours} hours\n`);
      }
      
      // Update previous state for next iteration (watch mode only)
      if (options.watch) {
        previousSessions.clear();
        sessions.forEach(session => {
          previousSessions.set(session.sessionId, session.percentage);
        });
      }
    }
  };

  // Show dashboard once
  showDashboard();

  // Watch mode: refresh at configured interval
  if (options.watch && !options.json) {
    const intervalSeconds = options.config.refreshInterval;
    console.log(`🔄 Watch mode active (refreshes every ${intervalSeconds}s). Press Ctrl+C to exit.\n`);
    setInterval(showDashboard, intervalSeconds * 1000);
  }
}

/**
 * Compute changes between previous and current session states
 * @param {Map} previous - Map of sessionId -> previous percentage
 * @param {Array} current - Current sessions array
 * @returns {Map} Map of sessionId -> change info
 */
function computeChanges(previous, current) {
  const changes = new Map();
  
  for (const session of current) {
    const prevPercentage = previous.get(session.sessionId);
    
    if (prevPercentage === undefined) {
      // New session appeared
      changes.set(session.sessionId, { type: 'new' });
    } else {
      const delta = session.percentage - prevPercentage;
      
      if (Math.abs(delta) < 0.1) {
        // No significant change (< 0.1%)
        changes.set(session.sessionId, { type: 'unchanged' });
      } else if (delta > 0) {
        // Capacity increased (tokens consumed)
        changes.set(session.sessionId, { 
          type: 'increased', 
          delta: delta 
        });
      } else {
        // Capacity decreased (tokens freed - shouldn't happen but handle it)
        changes.set(session.sessionId, { 
          type: 'decreased', 
          delta: Math.abs(delta)
        });
      }
    }
  }
  
  return changes;
}

/**
 * Archive command: Move old sessions to archive directory
 */
function archiveCommand(options) {
  // Validate: need either --older-than OR --session (not both, not neither)
  const hasOlderThan = !!options.olderThan;
  const hasSessions = options.sessions && options.sessions.length > 0;
  
  if (!hasOlderThan && !hasSessions) {
    console.error('❌ Either --older-than <time> OR --session <id> is required');
    console.error('   Examples:');
    console.error('     tide-watch archive --older-than 4d');
    console.error('     tide-watch archive --session abc123');
    console.error('     tide-watch archive --session abc123 --session def456');
    process.exit(1);
  }
  
  if (hasOlderThan && hasSessions) {
    console.error('❌ Cannot use --session with --older-than (conflicting criteria)');
    console.error('   Use one or the other, not both');
    process.exit(1);
  }
  
  let sessions;
  
  // Mode 1: Session-specific archiving
  if (hasSessions) {
    // Get all sessions first (needed for multi-agent support)
    const allSessions = getAllSessions(options.sessionDir, options.multiAgent, options.excludeAgents);
    
    sessions = [];
    
    for (const sessionInput of options.sessions) {
      let session = null;
      
      // Try direct UUID match first (full ID)
      session = allSessions.find(s => s.sessionId === sessionInput);
      
      // Try partial UUID match (starts with input)
      if (!session && /^[0-9a-f-]+$/.test(sessionInput)) {
        const matches = allSessions.filter(s => s.sessionId.startsWith(sessionInput));
        if (matches.length === 1) {
          session = matches[0];
        } else if (matches.length > 1) {
          console.error(`❌ Ambiguous session ID: ${sessionInput} matches ${matches.length} sessions:`);
          matches.slice(0, 5).forEach(m => {
            console.error(`   ${m.sessionId} (${m.channel}${m.label ? '/' + m.label : ''})`);
          });
          if (matches.length > 5) {
            console.error(`   ... and ${matches.length - 5} more`);
          }
          process.exit(1);
        }
      }
      
      // Try resolving by label/channel if not a UUID pattern
      if (!session) {
        const resolvedId = resolveSessionInput(sessionInput, options.sessionDir);
        if (resolvedId) {
          session = allSessions.find(s => s.sessionId === resolvedId);
        }
      }
      
      if (!session) {
        console.error(`❌ Session not found: ${sessionInput}`);
        process.exit(1);
      }
      
      sessions.push(session);
    }
    
    if (sessions.length === 0) {
      console.log('No sessions to archive.');
      return;
    }
  }
  
  // Mode 2: Time-based archiving (existing behavior)
  else if (hasOlderThan) {
    // Parse time string
    let hours;
    try {
      hours = parseTimeString(options.olderThan);
    } catch (error) {
      console.error(`❌ ${error.message}`);
      process.exit(1);
    }

    // Get all sessions (multi-agent support)
    sessions = getAllSessions(options.sessionDir, options.multiAgent, options.excludeAgents);
    
    // Filter by agent if specified
    if (options.agent) {
      sessions = sessions.filter(s => s.agentId === options.agent || s.agentName === options.agent);
    }
    
    if (sessions.length === 0) {
      console.log('No sessions found.');
      return;
    }

    // Filter to sessions older than threshold
    sessions = getSessionsOlderThan(sessions, hours);
    
    if (sessions.length === 0) {
      console.log(`No sessions older than ${options.olderThan}.`);
      return;
    }
  }

  // Apply exclusion filters
  if (options.excludeChannel) {
    sessions = sessions.filter(s => s.channel !== options.excludeChannel);
  }

  if (options.minCapacity !== null) {
    sessions = sessions.filter(s => s.percentage < options.minCapacity);
  }

  if (sessions.length === 0) {
    console.log(`No sessions match archive criteria.`);
    return;
  }

  // Show what will be/was archived
  let archiveDescription;
  if (hasSessions) {
    archiveDescription = sessions.length === 1 
      ? 'specified session' 
      : `${sessions.length} specified session(s)`;
  } else {
    archiveDescription = `${sessions.length} session(s) older than ${options.olderThan}`;
  }
  
  if (options.dryRun) {
    console.log(`\nWould archive ${archiveDescription}:\n`);
  } else {
    console.log(`\nArchiving ${archiveDescription}...\n`);
  }

  // Display table of sessions to archive
  console.log('Session ID  Channel/Label     Last Active  Capacity  Tokens');
  console.log('─'.repeat(65));
  
  sessions.forEach(session => {
    const id = session.sessionId.substring(0, 10).padEnd(11);
    const channelLabel = `${session.channel}${session.label ? '/' + session.label : ''}`.substring(0, 16).padEnd(17);
    const lastActive = formatRelativeTime(session.lastActivity).padEnd(11);
    const capacity = `${session.percentage.toFixed(1)}%`.padEnd(9);
    const tokens = session.tokensUsed.toLocaleString();
    
    console.log(`${id} ${channelLabel} ${lastActive} ${capacity} ${tokens}`);
  });
  
  console.log('─'.repeat(65));
  console.log('');

  if (options.dryRun) {
    console.log('🔍 Dry run mode - no files were modified');
    console.log('   Run without --dry-run to archive\n');
    return;
  }

  // Perform archive
  const results = archiveSessions(sessions, options.sessionDir, options.dryRun);

  // Show results
  if (results.archived.length > 0) {
    console.log(`✅ Archived ${results.archived.length} session(s)`);
    
    // Show archive locations (may be multiple in multi-agent mode)
    const archiveDirs = new Set();
    results.archived.forEach(archived => {
      if (archived.archivedTo) {
        archiveDirs.add(path.dirname(archived.archivedTo));
      }
    });
    
    if (archiveDirs.size === 1) {
      console.log(`   Location: ${archiveDirs.values().next().value}/\n`);
    } else if (archiveDirs.size > 1) {
      console.log(`   Locations:`);
      archiveDirs.forEach(dir => {
        console.log(`     ${dir}/`);
      });
      console.log('');
    }
  }

  if (results.failed.length > 0) {
    console.log(`❌ Failed to archive ${results.failed.length} session(s):`);
    results.failed.forEach(f => {
      console.log(`   ${f.sessionId}: ${f.reason}`);
    });
    console.log('');
  }
}

/**
 * Helper: Resolve session ID from user input
 * Handles UUIDs, labels, channels, and provides helpful error messages
 * @param {string} input - User-provided session identifier
 * @param {string} sessionDir - Session directory
 * @returns {string|null} Resolved session ID or null if error
 */
function resolveSessionInput(input, sessionDir) {
  const result = resolveSessionId(input, sessionDir);
  
  if (result.sessionId) {
    // Successful resolution
    return result.sessionId;
  }
  
  if (result.ambiguous) {
    // Multiple matches
    console.error(`❌ ${result.error}\n`);
    console.error('Matching sessions:');
    result.matches.forEach((match, idx) => {
      const label = match.label ? `/${match.label}` : '';
      const id = match.sessionId.substring(0, 8);
      console.error(`  ${idx + 1}. ${match.channel}${label} (${id})`);
    });
    console.error('\nPlease specify:');
    result.matches.forEach(match => {
      const label = match.label ? `/${match.label}` : '';
      console.error(`  tide-watch resume-prompt <action> --session "${match.channel}${label}"`);
      console.error(`  tide-watch resume-prompt <action> --session ${match.sessionId.substring(0, 8)}`);
    });
    console.error('');
    return null;
  }
  
  // No matches
  console.error(`❌ ${result.error}`);
  console.error('Available sessions:');
  
  const sessions = getAllSessions(sessionDir);
  if (sessions.length === 0) {
    console.error('  (No sessions found)');
  } else {
    sessions.slice(0, 10).forEach(s => {
      const label = s.label ? `/${s.label}` : '';
      const id = s.sessionId.substring(0, 8);
      console.error(`  ${s.channel}${label} (${id})`);
    });
    if (sessions.length > 10) {
      console.error(`  ... and ${sessions.length - 10} more`);
    }
  }
  console.error('');
  return null;
}

/**
 * Restore-prompt command: Manage session resumption prompts
 */
function resumePromptCommand(options) {
  const {
    hasResumePrompt,
    loadResumePrompt,
    deleteResumePrompt,
    listResumePrompts,
    editResumePrompt,
    getResumePromptInfo,
    formatResumePromptInfo,
    isResumePromptEnabled,
    disableResumePrompt,
    enableResumePrompt,
    getResumePromptStatus,
    formatResumePromptStatus,
    isDiscoveryEnabled,
    disableDiscovery,
    enableDiscovery,
    getDiscoveryStatus,
    formatDiscoveryStatus
  } = require('../lib/resumption');

  const action = process.argv[3]; // resume-prompt <action>
  
  if (!action) {
    console.error('❌ Action required for resume-prompt command');
    console.error('   Available actions: edit, show, info, list, test, delete');
    console.error('   Example: tide-watch resume-prompt edit');
    process.exit(1);
  }

  switch (action) {
    case 'edit':
      // Edit resumption prompt
      if (!options.session) {
        console.error('❌ --session <key> required for edit command');
        console.error('   Example: tide-watch resume-prompt edit --session abc123');
        console.error('   Example: tide-watch resume-prompt edit --session "#navi-code-yatta"');
        console.error('   Example: tide-watch resume-prompt edit --session discord');
        process.exit(1);
      }

      // Resolve session ID
      const editSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!editSessionId) {
        process.exit(1);
      }

      console.log(`Opening editor for session ${editSessionId}...\n`);
      const success = editResumePrompt(editSessionId, options.sessionDir + '/resume-prompts');
      
      if (success) {
        console.log(`\n✅ Resumption prompt saved for session ${editSessionId}`);
        console.log(`   Location: ${options.sessionDir}/resume-prompts/${editSessionId}.md\n`);
      }
      break;

    case 'show':
      // Show resumption prompt
      if (!options.session) {
        console.error('❌ --session <key> required for show command');
        console.error('   Example: tide-watch resume-prompt show --session abc123');
        console.error('   Example: tide-watch resume-prompt show --session "#navi-code-yatta"');
        process.exit(1);
      }

      // Resolve session ID
      const showSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!showSessionId) {
        process.exit(1);
      }

      const prompt = loadResumePrompt(showSessionId, options.sessionDir + '/resume-prompts');
      
      if (!prompt) {
        console.log(`No resumption prompt found for session ${showSessionId}`);
        console.log(`Create one with: tide-watch resume-prompt edit --session ${showSessionId}\n`);
      } else {
        console.log(`\nResumption Prompt for ${showSessionId}:\n`);
        console.log('─'.repeat(70));
        console.log(prompt);
        console.log('─'.repeat(70));
        console.log('');
      }
      break;

    case 'info':
      // Show resumption prompt metadata
      if (!options.session) {
        console.error('❌ --session <key> required for info command');
        console.error('   Example: tide-watch resume-prompt info --session abc123');
        console.error('   Example: tide-watch resume-prompt info --session discord');
        process.exit(1);
      }

      // Resolve session ID
      const infoSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!infoSessionId) {
        process.exit(1);
      }

      const info = getResumePromptInfo(infoSessionId, options.sessionDir + '/resume-prompts');
      
      if (!info) {
        console.log(`No resumption prompt found for session ${infoSessionId}\n`);
      } else {
        console.log(`\nResumption Prompt Info:\n`);
        console.log(formatResumePromptInfo(info));
        console.log('');
      }
      break;

    case 'list':
      // List all resumption prompts
      const prompts = listResumePrompts(options.sessionDir + '/resume-prompts');
      
      if (prompts.length === 0) {
        console.log('No resumption prompts found.');
        console.log('Create one with: tide-watch resume-prompt edit --session <session-id>\n');
      } else {
        const disabledCount = prompts.filter(p => !p.enabled).length;
        
        console.log(`\nResumption Prompts:\n`);
        console.log('Session ID        Size       Modified    Status');
        console.log('─'.repeat(70));
        
        prompts.forEach(p => {
          const id = p.sessionId.substring(0, 16).padEnd(17);
          const size = `${p.size} bytes`.padEnd(10);
          const modified = p.modified.toLocaleDateString().padEnd(11);
          const status = p.enabled ? '✅ Enabled' : '⏸️  Disabled';
          console.log(`${id} ${size} ${modified} ${status}`);
        });
        
        console.log('');
        
        if (disabledCount > 0) {
          console.log(`Total: ${prompts.length} resumption prompt(s) (${disabledCount} disabled)\n`);
        } else {
          console.log(`Total: ${prompts.length} resumption prompt(s)\n`);
        }
      }
      break;

    case 'test':
      // Test resumption prompt (dry-run)
      if (!options.session) {
        console.error('❌ --session <key> required for test command');
        console.error('   Example: tide-watch resume-prompt test --session abc123');
        console.error('   Example: tide-watch resume-prompt test --session webchat');
        process.exit(1);
      }

      // Resolve session ID
      const testSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!testSessionId) {
        process.exit(1);
      }

      const testPrompt = loadResumePrompt(testSessionId, options.sessionDir + '/resume-prompts');
      
      if (!testPrompt) {
        console.log(`No resumption prompt found for session ${testSessionId}\n`);
      } else {
        console.log(`\n🧪 Testing resumption prompt for ${testSessionId}:\n`);
        console.log('─'.repeat(70));
        console.log(testPrompt);
        console.log('─'.repeat(70));
        
        const tokenEstimate = Math.ceil(testPrompt.length / 4);
        console.log(`\nEstimated tokens: ~${tokenEstimate}`);
        
        if (tokenEstimate > 1000) {
          console.log('⚠️  Warning: Prompt is large (>1000 tokens). Consider shortening.');
        } else {
          console.log('✅ Prompt size looks good.');
        }
        console.log('');
      }
      break;

    case 'delete':
      // Delete resumption prompt
      if (!options.session) {
        console.error('❌ --session <key> required for delete command');
        console.error('   Example: tide-watch resume-prompt delete --session abc123');
        console.error('   Example: tide-watch resume-prompt delete --session telegram');
        process.exit(1);
      }

      // Resolve session ID
      const deleteSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!deleteSessionId) {
        process.exit(1);
      }

      const deleted = deleteResumePrompt(deleteSessionId, options.sessionDir + '/resume-prompts');
      
      if (deleted) {
        console.log(`✅ Deleted resumption prompt for session ${deleteSessionId}\n`);
      } else {
        console.log(`No resumption prompt found for session ${deleteSessionId}\n`);
      }
      break;

    case 'enable':
      // Enable resumption prompt
      if (!options.session) {
        console.error('❌ --session <key> required for enable command');
        console.error('   Example: tide-watch resume-prompt enable --session abc123');
        console.error('   Example: tide-watch resume-prompt enable --session slack');
        process.exit(1);
      }

      // Resolve session ID
      const enableSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!enableSessionId) {
        process.exit(1);
      }

      const enabled = enableResumePrompt(enableSessionId, options.sessionDir + '/resume-prompts');
      
      if (enabled) {
        console.log(`✅ Enabled resumption prompt for session ${enableSessionId}`);
        console.log(`   Auto-load will activate on session reset`);
        console.log(`   Location: ${options.sessionDir}/resume-prompts/${enableSessionId}.md\n`);
      } else {
        console.log(`No resumption prompt found for session ${enableSessionId}`);
        console.log(`Create one with: tide-watch resume-prompt edit --session ${enableSessionId}\n`);
      }
      break;

    case 'disable':
      // Disable resumption prompt
      if (!options.session) {
        console.error('❌ --session <key> required for disable command');
        console.error('   Example: tide-watch resume-prompt disable --session abc123');
        console.error('   Example: tide-watch resume-prompt disable --session "#navi-code-yatta"');
        process.exit(1);
      }

      // Resolve session ID
      const disableSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!disableSessionId) {
        process.exit(1);
      }

      const disabled = disableResumePrompt(disableSessionId, options.sessionDir + '/resume-prompts');
      
      if (disabled) {
        console.log(`✅ Disabled resumption prompt for session ${disableSessionId}`);
        console.log(`   Prompt file preserved: ${options.sessionDir}/resume-prompts/${disableSessionId}.md`);
        console.log(`   Auto-load will be skipped on session reset`);
        console.log('');
        console.log(`   To re-enable: tide-watch resume-prompt enable --session ${disableSessionId}\n`);
      } else {
        console.log(`No resumption prompt found for session ${disableSessionId}\n`);
      }
      break;

    case 'status':
      // Show resumption prompt status
      if (!options.session) {
        console.error('❌ --session <key> required for status command');
        console.error('   Example: tide-watch resume-prompt status --session abc123');
        console.error('   Example: tide-watch resume-prompt status --session discord');
        process.exit(1);
      }

      // Resolve session ID
      const statusSessionId = resolveSessionInput(options.session, options.sessionDir);
      if (!statusSessionId) {
        process.exit(1);
      }

      const statusInfo = getResumePromptStatus(statusSessionId, options.sessionDir + '/resume-prompts');
      
      if (!statusInfo) {
        console.log(`\nNo resumption prompt found for session ${statusSessionId}`);
        console.log(`Create one with: tide-watch resume-prompt edit --session ${statusSessionId}\n`);
      } else {
        console.log(`\nResumption Prompt Status:\n`);
        console.log(formatResumePromptStatus(statusInfo));
        console.log('');
      }
      break;

    case 'discovery-off':
      // Disable feature discovery
      disableDiscovery(options.sessionDir + '/resume-prompts');
      console.log(`✅ Feature discovery disabled globally`);
      console.log(`   Agents will no longer offer to create resumption prompts`);
      console.log('');
      console.log(`   Auto-loading and manual triggers still work`);
      console.log(`   Existing prompts continue to function normally`);
      console.log('');
      console.log(`   To re-enable: tide-watch resume-prompt discovery-on\n`);
      break;

    case 'discovery-on':
      // Enable feature discovery
      enableDiscovery(options.sessionDir + '/resume-prompts');
      console.log(`✅ Feature discovery enabled globally`);
      console.log(`   Agents will offer to create resumption prompts after resets`);
      console.log(`   Capacity warnings will include resumption prompt reminders\n`);
      break;

    case 'discovery-status':
      // Show discovery status
      const discoveryStatus = getDiscoveryStatus(options.sessionDir + '/resume-prompts');
      console.log('');
      console.log(formatDiscoveryStatus(discoveryStatus));
      console.log('');
      break;

    default:
      console.error(`Unknown resume-prompt action: ${action}`);
      console.error('Available actions: edit, show, info, list, test, delete, enable, disable, status, discovery-off, discovery-on, discovery-status');
      process.exit(1);
  }
}

/**
 * Main entry point
 */
function main() {
  const options = parseArgs();

  // Load configuration (merge CLI flags > env vars > config file > defaults)
  const { loadConfig } = require('../lib/config');
  const cliFlags = {};
  if (options.refreshInterval !== null) cliFlags.refreshInterval = options.refreshInterval;
  if (options.gatewayInterval !== null) cliFlags.gatewayInterval = options.gatewayInterval;
  if (options.gatewayTimeout !== null) cliFlags.gatewayTimeout = options.gatewayTimeout;
  
  try {
    options.config = loadConfig(cliFlags);
  } catch (error) {
    console.error(`❌ Configuration error: ${error.message}`);
    process.exit(1);
  }

  switch (options.command) {
    case 'check':
      checkCommand(options);
      break;
    case 'report':
      reportCommand(options);
      break;
    case 'dashboard':
      dashboardCommand(options);
      break;
    case 'archive':
      archiveCommand(options);
      break;
    case 'resume-prompt':
      resumePromptCommand(options);
      break;
    case 'status':
      statusCommand(options);
      break;
    case 'help':
    case '--help':
    case '-h':
      console.log(USAGE);
      break;
    default:
      console.error(`Unknown command: ${options.command}`);
      console.log(USAGE);
      process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { main, parseArgs };
