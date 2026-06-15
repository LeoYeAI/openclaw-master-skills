#!/usr/bin/env node

/**
 * Session resumption prompt management
 * Helps recover context after session resets
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

/**
 * Default resumption prompts directory
 */
const DEFAULT_RESUME_DIR = path.join(
  os.homedir(),
  '.openclaw',
  'agents',
  'main',
  'sessions',
  'resume-prompts'
);

/**
 * Path to global discovery marker file
 */
const DISCOVERY_MARKER = '.no-discovery';

/**
 * Get resumption prompt path for a session
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {string} Path to resumption prompt file
 */
function getResumePromptPath(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  return path.join(resumeDir, `${sessionId}.md`);
}

/**
 * Get default resumption prompt path
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {string} Path to default resumption prompt file
 */
function getDefaultResumePromptPath(resumeDir = DEFAULT_RESUME_DIR) {
  return path.join(resumeDir, 'default.md');
}

/**
 * Check if resumption prompt exists for session
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if prompt exists
 */
function hasResumePrompt(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  return fs.existsSync(promptPath);
}

/**
 * Load resumption prompt for session
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {string|null} Resumption prompt content, or null if not found
 */
function loadResumePrompt(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  // Try session-specific prompt first
  const sessionPromptPath = getResumePromptPath(sessionId, resumeDir);
  if (fs.existsSync(sessionPromptPath)) {
    return fs.readFileSync(sessionPromptPath, 'utf8');
  }
  
  // Fall back to default prompt
  const defaultPromptPath = getDefaultResumePromptPath(resumeDir);
  if (fs.existsSync(defaultPromptPath)) {
    return fs.readFileSync(defaultPromptPath, 'utf8');
  }
  
  return null;
}

/**
 * Save resumption prompt for session
 * @param {string} sessionId - Session identifier
 * @param {string} content - Prompt content
 * @param {string} resumeDir - Resumption prompts directory
 */
function saveResumePrompt(sessionId, content, resumeDir = DEFAULT_RESUME_DIR) {
  // Ensure directory exists
  if (!fs.existsSync(resumeDir)) {
    fs.mkdirSync(resumeDir, { recursive: true });
  }
  
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  fs.writeFileSync(promptPath, content, 'utf8');
}

/**
 * Delete resumption prompt for session
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if deleted, false if didn't exist
 */
function deleteResumePrompt(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  
  if (!fs.existsSync(promptPath)) {
    return false;
  }
  
  fs.unlinkSync(promptPath);
  return true;
}

/**
 * List all resumption prompts
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {Array} Array of {sessionId, path, size, modified, enabled}
 */
function listResumePrompts(resumeDir = DEFAULT_RESUME_DIR) {
  if (!fs.existsSync(resumeDir)) {
    return [];
  }
  
  const files = fs.readdirSync(resumeDir);
  const prompts = [];
  
  for (const file of files) {
    if (!file.endsWith('.md')) {
      continue;
    }
    
    const filePath = path.join(resumeDir, file);
    const stats = fs.statSync(filePath);
    const sessionId = file === 'default.md' ? 'default' : path.basename(file, '.md');
    const enabled = isResumePromptEnabled(sessionId, resumeDir);
    
    prompts.push({
      sessionId,
      path: filePath,
      size: stats.size,
      modified: stats.mtime,
      enabled
    });
  }
  
  return prompts.sort((a, b) => b.modified - a.modified);
}

/**
 * Open resumption prompt in editor
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if editor opened successfully
 */
function editResumePrompt(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  // Ensure directory exists
  if (!fs.existsSync(resumeDir)) {
    fs.mkdirSync(resumeDir, { recursive: true });
  }
  
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  
  // Create template if doesn't exist
  if (!fs.existsSync(promptPath)) {
    const template = generateResumePromptTemplate(sessionId);
    fs.writeFileSync(promptPath, template, 'utf8');
  }
  
  // Determine editor
  const editor = process.env.VISUAL || process.env.EDITOR || 'nano';
  
  try {
    // Use spawnSync with array args to prevent shell injection
    // This avoids shell metacharacter expansion in sessionId/promptPath
    const result = spawnSync(editor, [promptPath], { 
      stdio: 'inherit',
      shell: false  // Explicitly disable shell to prevent injection
    });
    
    if (result.error) {
      throw result.error;
    }
    
    return true;
  } catch (error) {
    console.error(`Failed to open editor: ${error.message}`);
    return false;
  }
}

/**
 * Generate resumption prompt template
 * @param {string} sessionId - Session identifier
 * @returns {string} Template content
 */
function generateResumePromptTemplate(sessionId) {
  return `# Session Restoration Prompt

**Session ID:** ${sessionId}
**Created:** ${new Date().toISOString().split('T')[0]}

## Project Context

**Project Name:** [Your project name]
**Description:** [Brief description]

## Technical Details

**Tech Stack:** [Technologies, languages, frameworks]
**Environment:** [Development environment, tools]

## Current Focus

**Phase:** [Current project phase]
**Last Completed:** [What was recently finished]
**Next Steps:** [What's coming up]

## Important Files & Locations

**Code:** [Path to code directory]
**Docs:** [Path to documentation]
**Data:** [Path to data/assets]

## Active Work

**Current Tasks:**
- [Task 1]
- [Task 2]
- [Task 3]

**Blockers:** [Any current blockers or dependencies]

## Team & Communication

**Team Members:** [If applicable]
**Communication Channels:** [Discord, Slack, etc.]
**Schedule:** [Stand-ups, meetings, etc.]

## Custom Instructions

[Any specific instructions for how the agent should behave in this session]

---

**Tips:**
- Keep this updated as your project evolves
- Be concise but thorough (aim for < 1000 tokens)
- Include only essential context for quick recovery
- Update after major project milestones
`;
}

/**
 * Get resumption prompt metadata
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {Object|null} Metadata or null if not found
 */
function getResumePromptInfo(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  
  if (!fs.existsSync(promptPath)) {
    return null;
  }
  
  const stats = fs.statSync(promptPath);
  const content = fs.readFileSync(promptPath, 'utf8');
  
  // Estimate token count (rough approximation: 1 token ≈ 4 characters)
  const estimatedTokens = Math.ceil(content.length / 4);
  
  return {
    sessionId,
    path: promptPath,
    size: stats.size,
    lines: content.split('\n').length,
    estimatedTokens,
    modified: stats.mtime,
    created: stats.birthtime
  };
}

/**
 * Format resumption prompt info for display
 * @param {Object} info - Prompt metadata
 * @returns {string} Formatted display text
 */
function formatResumePromptInfo(info) {
  const lines = [];
  
  lines.push(`Session: ${info.sessionId}`);
  lines.push(`Path: ${info.path}`);
  lines.push(`Size: ${info.size} bytes (${info.lines} lines)`);
  lines.push(`Estimated tokens: ~${info.estimatedTokens}`);
  lines.push(`Modified: ${info.modified.toLocaleString()}`);
  
  if (info.estimatedTokens > 1000) {
    lines.push('');
    lines.push('⚠️  Warning: Prompt is large (>1000 tokens). Consider shortening for better efficiency.');
  }
  
  return lines.join('\n');
}

/**
 * Check if resumption prompt is enabled
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if enabled (no .disabled marker)
 */
function isResumePromptEnabled(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  const disabledPath = `${promptPath}.disabled`;
  
  // Enabled if prompt exists and no .disabled marker
  return fs.existsSync(promptPath) && !fs.existsSync(disabledPath);
}

/**
 * Disable resumption prompt for session
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if disabled, false if prompt doesn't exist
 */
function disableResumePrompt(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  
  if (!fs.existsSync(promptPath)) {
    return false;
  }
  
  const disabledPath = `${promptPath}.disabled`;
  fs.writeFileSync(disabledPath, '', 'utf8');
  return true;
}

/**
 * Enable resumption prompt for session
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if enabled, false if prompt doesn't exist
 */
function enableResumePrompt(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  
  if (!fs.existsSync(promptPath)) {
    return false;
  }
  
  const disabledPath = `${promptPath}.disabled`;
  
  if (fs.existsSync(disabledPath)) {
    fs.unlinkSync(disabledPath);
  }
  
  return true;
}

/**
 * Get resumption prompt status
 * @param {string} sessionId - Session identifier
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {Object|null} Status object or null if prompt doesn't exist
 */
function getResumePromptStatus(sessionId, resumeDir = DEFAULT_RESUME_DIR) {
  const promptPath = getResumePromptPath(sessionId, resumeDir);
  
  if (!fs.existsSync(promptPath)) {
    return null;
  }
  
  const info = getResumePromptInfo(sessionId, resumeDir);
  const enabled = isResumePromptEnabled(sessionId, resumeDir);
  
  return {
    ...info,
    enabled,
    autoLoad: enabled,
    disabledMarkerPath: enabled ? null : `${promptPath}.disabled`
  };
}

/**
 * Format resumption prompt status for display
 * @param {Object} status - Status object
 * @returns {string} Formatted status text
 */
function formatResumePromptStatus(status) {
  const lines = [];
  
  lines.push(`Session: ${status.sessionId}`);
  lines.push(`Prompt: ✅ Exists (${status.size} bytes, ${status.lines} lines)`);
  lines.push(`Status: ${status.enabled ? '✅ Enabled' : '⏸️  Disabled'}`);
  lines.push(`Auto-load: ${status.autoLoad ? '✅ Will auto-load on session reset' : '❌ Will NOT auto-load'}`);
  
  if (!status.enabled) {
    lines.push(`Marker file: ${status.disabledMarkerPath}`);
  }
  
  lines.push(`Modified: ${status.modified.toLocaleString()}`);
  lines.push(`Estimated tokens: ~${status.estimatedTokens}`);
  
  return lines.join('\n');
}

/**
 * Check if feature discovery is enabled
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if discovery enabled (no .no-discovery marker)
 */
function isDiscoveryEnabled(resumeDir = DEFAULT_RESUME_DIR) {
  const markerPath = path.join(resumeDir, DISCOVERY_MARKER);
  return !fs.existsSync(markerPath);
}

/**
 * Disable feature discovery globally
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if disabled successfully
 */
function disableDiscovery(resumeDir = DEFAULT_RESUME_DIR) {
  // Ensure directory exists
  if (!fs.existsSync(resumeDir)) {
    fs.mkdirSync(resumeDir, { recursive: true });
  }
  
  const markerPath = path.join(resumeDir, DISCOVERY_MARKER);
  fs.writeFileSync(markerPath, '# Discovery disabled by user\n', 'utf8');
  return true;
}

/**
 * Enable feature discovery globally
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {boolean} True if enabled successfully
 */
function enableDiscovery(resumeDir = DEFAULT_RESUME_DIR) {
  const markerPath = path.join(resumeDir, DISCOVERY_MARKER);
  
  if (fs.existsSync(markerPath)) {
    fs.unlinkSync(markerPath);
  }
  
  return true;
}

/**
 * Get feature discovery status
 * @param {string} resumeDir - Resumption prompts directory
 * @returns {Object} Discovery status
 */
function getDiscoveryStatus(resumeDir = DEFAULT_RESUME_DIR) {
  const enabled = isDiscoveryEnabled(resumeDir);
  const markerPath = path.join(resumeDir, DISCOVERY_MARKER);
  
  return {
    enabled,
    markerPath: enabled ? null : markerPath,
    markerExists: fs.existsSync(markerPath)
  };
}

/**
 * Format discovery status for display
 * @param {Object} status - Discovery status object
 * @returns {string} Formatted status text
 */
function formatDiscoveryStatus(status) {
  const lines = [];
  
  lines.push('Feature Discovery Status: ' + (status.enabled ? '✅ Enabled' : '⏸️  Disabled'));
  lines.push('');
  lines.push('Discovery prompts: ' + (status.enabled ? 'ON' : 'OFF'));
  
  if (!status.enabled) {
    lines.push('- No creation offers after resets');
    lines.push('- No capacity warning reminders');
    lines.push('');
    lines.push(`Marker file: ${status.markerPath}`);
  } else {
    lines.push('- Creation offers after resets: ✅');
    lines.push('- Capacity warning reminders: ✅');
  }
  
  lines.push('');
  lines.push('Restoration features: ON');
  lines.push('- Auto-loading: ✅ Works normally');
  lines.push('- Manual trigger: ✅ Works normally');
  lines.push('- CLI commands: ✅ All available');
  
  return lines.join('\n');
}

module.exports = {
  DEFAULT_RESUME_DIR,
  getResumePromptPath,
  getDefaultResumePromptPath,
  hasResumePrompt,
  loadResumePrompt,
  saveResumePrompt,
  deleteResumePrompt,
  listResumePrompts,
  editResumePrompt,
  generateResumePromptTemplate,
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
};
