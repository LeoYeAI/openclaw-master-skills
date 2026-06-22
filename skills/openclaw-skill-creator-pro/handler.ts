/**
 * OpenClaw Skill Creator - Local Skill
 * 
 * This is a LOCAL skill that runs entirely in your OpenClaw agent.
 * No external API calls, no API key required. Complete privacy.
 * 
 * Helps non-technical users create custom skills for their OpenClaw agents.
 */

// ─── Types ───────────────────────────────────────────────────

type Action = 'create' | 'get-api-key-help' | 'test-skill' | 'improve';

interface SkillTemplate {
  name: string;
  description: string;
  code: string;
  installation: string[];
  testing: string[];
  apiKeyHelp?: {
    provider: string;
    steps: string[];
    url: string;
  };
}

interface CreateInput {
  action?: string;
  what_you_want?: string;
  intent?: string;
  why_you_need_it?: string;
  what_you_have?: string;
}

interface ApiKeyHelpInput {
  action: string;
  provider?: string;
}

interface TestSkillInput {
  action: string;
  skill_name?: string;
  test_prompt?: string;
}

interface ImproveSkillInput {
  action: string;
  skill_name?: string;
  feedback?: string;
  what_to_improve?: string;
}

type Input = CreateInput | ApiKeyHelpInput | TestSkillInput | ImproveSkillInput;

// ─── Skill Templates ─────────────────────────────────────────

const TEMPLATES: Record<string, SkillTemplate> = {
  'google-calendar': {
    name: 'google-calendar-reader',
    description: 'Read events from your Google Calendar. Use when the user asks about their schedule, meetings, or calendar availability.',
    code: `import { google } from 'googleapis';

async function listEvents(timeMin: string, timeMax: string, maxResults: number = 10) {
  const auth = new google.auth.GoogleAuth({
    keyFile: process.env.GOOGLE_CALENDAR_CREDENTIALS,
    scopes: ['https://www.googleapis.com/auth/calendar.readonly'],
  });

  const calendar = google.calendar({ version: 'v3', auth });
  
  const response = await calendar.events.list({
    calendarId: 'primary',
    timeMin,
    timeMax,
    maxResults,
    singleEvents: true,
    orderBy: 'startTime',
  });

  return response.data.items || [];
}

export default listEvents;`,
    installation: [
      'Save this file to: ~/openclaw/skills/google-calendar-reader/SKILL.md',
      'Install dependencies: npm install googleapis',
      'Get your Google Calendar API credentials from: https://console.cloud.google.com',
      'Save credentials as: ~/openclaw/skills/google-calendar-reader/credentials.json',
      'Set environment variable: GOOGLE_CALENDAR_CREDENTIALS=~/openclaw/skills/google-calendar-reader/credentials.json',
      'Restart OpenClaw',
    ],
    testing: [
      'Try: "Show me my meetings for tomorrow"',
      'Try: "What\'s on my calendar this week?"',
      'Try: "When am I free for a 1-hour meeting?"',
    ],
    apiKeyHelp: {
      provider: 'Google Calendar',
      steps: [
        'Go to https://console.cloud.google.com',
        'Create a new project or select an existing one',
        'Enable the Google Calendar API',
        'Go to "Credentials" → "Create Credentials" → "Service Account"',
        'Download the JSON key file',
        'Save it as credentials.json in your skill folder',
      ],
      url: 'https://developers.google.com/calendar/api/quickstart/nodejs',
    },
  },
  'slack-messenger': {
    name: 'slack-messenger',
    description: 'Send messages to Slack channels. Use when the user wants to post updates, notify the team, or share information on Slack.',
    code: `import { WebClient } from '@slack/web-api';

const SLACK_TOKEN = process.env.SLACK_BOT_TOKEN;
const DEFAULT_CHANNEL = process.env.SLACK_DEFAULT_CHANNEL || '#general';

async function sendMessage(text: string, channel?: string) {
  const client = new WebClient(SLACK_TOKEN);
  
  const result = await client.chat.postMessage({
    channel: channel || DEFAULT_CHANNEL,
    text,
  });

  return { ok: result.ok, ts: result.ts };
}

export default sendMessage;`,
    installation: [
      'Save this file to: ~/openclaw/skills/slack-messenger/SKILL.md',
      'Install dependencies: npm install @slack/web-api',
      'Get your Slack Bot Token from: https://api.slack.com/apps',
      'Set environment variables:',
      '  SLACK_BOT_TOKEN=xoxb-your-token-here',
      '  SLACK_DEFAULT_CHANNEL=#team-updates',
      'Restart OpenClaw',
    ],
    testing: [
      'Try: "Post \'Task completed!\' to #team-updates"',
      'Try: "Send a message to Slack saying I finished the report"',
      'Try: "Notify the team that the deployment is done"',
    ],
    apiKeyHelp: {
      provider: 'Slack',
      steps: [
        'Go to https://api.slack.com/apps',
        'Click "Create New App" → "From scratch"',
        'Name it "OpenClaw Bot" and select your workspace',
        'Go to "OAuth & Permissions"',
        'Add these scopes: chat:write, channels:read',
        'Click "Install to Workspace"',
        'Copy the "Bot User OAuth Token" (starts with xoxb-)',
      ],
      url: 'https://api.slack.com/start/quickstart',
    },
  },
  'csv-analyzer': {
    name: 'csv-analyzer',
    description: 'Analyze CSV files and answer questions about the data. Use when the user wants to understand trends, calculate statistics, or query tabular data.',
    code: `import * as fs from 'fs';
import * as csv from 'csv-parser';

async function analyzeCSV(filePath: string, query: string) {
  const rows: any[] = [];
  
  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => rows.push(row))
      .on('end', () => {
        const result = {
          total_rows: rows.length,
          columns: Object.keys(rows[0] || {}),
          sample: rows.slice(0, 5),
          query_result: processQuery(rows, query),
        };
        resolve(result);
      })
      .on('error', reject);
  });
}

function processQuery(rows: any[], query: string): any {
  if (query.includes('total') || query.includes('count')) {
    return { count: rows.length };
  }
  if (query.includes('average') || query.includes('mean')) {
    const numericColumns = Object.keys(rows[0]).filter(k => !isNaN(rows[0][k]));
    return numericColumns.reduce((acc, col) => {
      acc[col] = rows.reduce((sum, row) => sum + parseFloat(row[col] || 0), 0) / rows.length;
      return acc;
    }, {} as any);
  }
  return { message: 'Query not understood. Try: "What is the total count?" or "What is the average?"' };
}

export default analyzeCSV;`,
    installation: [
      'Save this file to: ~/openclaw/skills/csv-analyzer/SKILL.md',
      'Install dependencies: npm install csv-parser',
      'No API key needed — this skill works locally',
      'Restart OpenClaw',
    ],
    testing: [
      'Try: "Analyze sales.csv and tell me the total count"',
      'Try: "What is the average revenue in my CSV file?"',
      'Try: "Show me the first 5 rows of data.csv"',
    ],
  },
};

// ─── Action Handlers ─────────────────────────────────────────

function createSkill(input: CreateInput): any {
  const whatYouWant = input.what_you_want || input.intent || '';
  const whyYouNeedIt = input.why_you_need_it || '';

  if (!whatYouWant) {
    throw new Error('Please tell me what you want your agent to do (what_you_want field)');
  }

  // Match to a template
  let template: SkillTemplate | null = null;
  let templateKey = '';

  if (/google calendar|calendar|schedule|meetings/i.test(whatYouWant)) {
    template = TEMPLATES['google-calendar'];
    templateKey = 'google-calendar';
  } else if (/slack|message|notify|team/i.test(whatYouWant)) {
    template = TEMPLATES['slack-messenger'];
    templateKey = 'slack-messenger';
  } else if (/csv|spreadsheet|data|analyze|excel/i.test(whatYouWant)) {
    template = TEMPLATES['csv-analyzer'];
    templateKey = 'csv-analyzer';
  }

  if (!template) {
    const slug = whatYouWant.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 30);
    return {
      action: 'create',
      skill_name: slug,
      message: `I understand you want to: "${whatYouWant}". I don't have a pre-built template for this yet, but I can help you create a custom skill.`,
      next_steps: [
        'Tell me more details: What inputs does this skill need?',
        'What should the output look like?',
        'Does it need to connect to an external service? If so, which one?',
      ],
      suggestion: 'Try being more specific. For example: "Read my Google Calendar", "Send Slack messages", or "Analyze CSV files"',
    };
  }

  // Generate complete SKILL.md
  const skillMd = `---
name: ${template.name}
description: ${template.description}
---

# ${template.name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}

${whatYouWant}

${whyYouNeedIt ? `## Why You Need This\n\n${whyYouNeedIt}\n\n` : ''}

## How It Works

This skill connects to ${template.apiKeyHelp?.provider || 'the service'} and ${whatYouWant.toLowerCase()}.

## Code

\`\`\`typescript
${template.code}
\`\`\`

## Installation

${template.installation.map((step, i) => `${i + 1}. ${step}`).join('\n')}

## Testing

Once installed, try these prompts with your agent:

${template.testing.map(t => `- ${t}`).join('\n')}

## Troubleshooting

### "API key invalid" or "Authentication failed"
- Check that your API key is correct
- Make sure the environment variable is set
- Restart OpenClaw after setting environment variables

### "Skill not found"
- Verify the skill file is in the correct folder
- Check that the file is named SKILL.md (all caps)
- Restart OpenClaw

### "Permission denied"
- Check that your API key has the required permissions
- For Google Calendar: ensure the Calendar API is enabled
- For Slack: ensure the bot has chat:write scope

## Need Help Getting an API Key?

${template.apiKeyHelp ? `Call this skill again with action "get-api-key-help" and provider "${template.apiKeyHelp.provider}"` : 'No API key needed for this skill!'}
`;

  return {
    action: 'create',
    skill_name: template.name,
    template_used: templateKey,
    skill_file: {
      filename: 'SKILL.md',
      content: skillMd,
      save_to: `~/openclaw/skills/${template.name}/SKILL.md`,
    },
    installation_steps: template.installation,
    testing_prompts: template.testing,
    has_api_key: !!template.apiKeyHelp,
    next_action: template.apiKeyHelp 
      ? `If you don't have a ${template.apiKeyHelp.provider} API key yet, call this skill with action "get-api-key-help"` 
      : 'Follow the installation steps above, then test with your agent!',
  };
}

function getApiKeyHelp(input: ApiKeyHelpInput): any {
  const provider = input.provider || '';

  if (!provider) {
    return {
      action: 'get-api-key-help',
      available_providers: Object.keys(TEMPLATES)
        .filter(k => TEMPLATES[k].apiKeyHelp)
        .map(k => TEMPLATES[k].apiKeyHelp!.provider),
      message: 'Please specify which provider you need help with (provider field)',
    };
  }

  const template = Object.values(TEMPLATES).find(
    t => t.apiKeyHelp && t.apiKeyHelp.provider.toLowerCase() === provider.toLowerCase()
  );

  if (!template || !template.apiKeyHelp) {
    return {
      action: 'get-api-key-help',
      error: `No API key help available for "${provider}"`,
      available_providers: Object.keys(TEMPLATES)
        .filter(k => TEMPLATES[k].apiKeyHelp)
        .map(k => TEMPLATES[k].apiKeyHelp!.provider),
    };
  }

  return {
    action: 'get-api-key-help',
    provider: template.apiKeyHelp.provider,
    steps: template.apiKeyHelp.steps,
    documentation_url: template.apiKeyHelp.url,
    estimated_time: '5-10 minutes',
    tips: [
      'Keep your API key secret — never share it publicly',
      'Store it in environment variables, not in code',
      'Most services offer free tiers for testing',
    ],
  };
}

function testSkill(input: TestSkillInput): any {
  const skillName = input.skill_name || '';
  const testPrompt = input.test_prompt || '';

  if (!skillName) {
    throw new Error('Please specify which skill to test (skill_name field)');
  }

  const template = Object.values(TEMPLATES).find(t => t.name === skillName);

  if (!template) {
    return {
      action: 'test-skill',
      skill_name: skillName,
      status: 'unknown',
      message: `I don't have testing guidance for "${skillName}". Try one of these: ${Object.values(TEMPLATES).map(t => t.name).join(', ')}`,
    };
  }

  return {
    action: 'test-skill',
    skill_name: skillName,
    suggested_prompts: template.testing,
    your_prompt: testPrompt || null,
    checklist: [
      { step: 'Skill file saved in correct location', status: 'pending' },
      { step: 'Dependencies installed', status: 'pending' },
      { step: 'API key configured (if needed)', status: 'pending' },
      { step: 'OpenClaw restarted', status: 'pending' },
      { step: 'Test prompt executed', status: 'pending' },
    ],
    troubleshooting: [
      'If the skill doesn\'t trigger, check the description field in SKILL.md',
      'If you get an error, check the OpenClaw logs',
      'If the API call fails, verify your API key is correct',
    ],
  };
}

function improveSkill(input: ImproveSkillInput): any {
  const skillName = input.skill_name || '';
  const feedback = input.feedback || '';
  const whatToImprove = input.what_to_improve || '';

  if (!skillName) {
    throw new Error('Please specify which skill to improve (skill_name field)');
  }

  if (!feedback && !whatToImprove) {
    throw new Error('Please tell me what you want to improve (feedback or what_to_improve field)');
  }

  return {
    action: 'improve',
    skill_name: skillName,
    feedback_received: feedback || whatToImprove,
    suggestions: [
      'To add new features: Tell me specifically what you want to add',
      'To fix errors: Share the error message you\'re seeing',
      'To change behavior: Describe what it does now vs. what you want',
    ],
    next_steps: [
      'Call this skill again with action "create" and include your improvement request',
      'I\'ll generate an updated version of the skill',
      'Replace the old SKILL.md file with the new one',
      'Restart OpenClaw and test',
    ],
  };
}

// ─── Main Entry Point ────────────────────────────────────────

/**
 * Main function called by OpenClaw agent
 * @param input - Skill creation request
 * @returns Skill file and installation instructions
 */
export async function run(input: Input): Promise<any> {
  const action = (input.action || 'create').toLowerCase() as Action;
  
  const validActions: Action[] = ['create', 'get-api-key-help', 'test-skill', 'improve'];
  if (!validActions.includes(action)) {
    throw new Error(`Invalid action "${action}". Valid: ${validActions.join(', ')}`);
  }

  try {
    let result: any;

    switch (action) {
      case 'create':
        result = createSkill(input as CreateInput);
        break;
      case 'get-api-key-help':
        result = getApiKeyHelp(input as ApiKeyHelpInput);
        break;
      case 'test-skill':
        result = testSkill(input as TestSkillInput);
        break;
      case 'improve':
        result = improveSkill(input as ImproveSkillInput);
        break;
    }

    return {
      ...result,
      _meta: {
        skill: 'openclaw-skill-creator',
        version: '1.0.0',
        mode: 'local',
      },
    };
  } catch (error: any) {
    throw new Error(error.message || 'Processing failed');
  }
}

// Default export for compatibility
export default run;
