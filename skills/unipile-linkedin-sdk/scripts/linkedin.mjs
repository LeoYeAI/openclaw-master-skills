#!/usr/bin/env node
/**
 * Unipile LinkedIn SDK CLI
 * Usage: node linkedin.mjs <command> [options]
 * 
 * Environment:
 *   UNIPILE_DSN           - API endpoint (required)
 *   UNIPILE_ACCESS_TOKEN  - Access token (required)
 *   UNIPILE_PERMISSIONS   - Comma-separated: "read" and/or "write" (default: "read,write")
 * 
 * Examples:
 *   UNIPILE_PERMISSIONS=read node linkedin.mjs posts <account> andrewyng
 *   UNIPILE_PERMISSIONS=read,write node linkedin.mjs create-post <account> "Hello"
 */

import { UnipileClient, UnsuccessfulRequestError } from 'unipile-node-sdk';

const DSN = process.env.UNIPILE_DSN;
const TOKEN = process.env.UNIPILE_ACCESS_TOKEN;
const PERMISSIONS = (process.env.UNIPILE_PERMISSIONS || 'read,write').split(',').map(p => p.trim().toLowerCase());

if (!DSN || !TOKEN) {
  console.error('Error: UNIPILE_DSN and UNIPILE_ACCESS_TOKEN must be set');
  console.error('Get credentials from https://dashboard.unipile.com');
  process.exit(1);
}

const hasRead = PERMISSIONS.includes('read');
const hasWrite = PERMISSIONS.includes('write');

// Commands that require write permission
const WRITE_COMMANDS = [
  'send', 'start-chat', 'invite', 'cancel-invite', 
  'create-post', 'comment', 'react'
];

// Commands that are read-only
const READ_COMMANDS = [
  'accounts', 'account', 'chats', 'chat', 'messages',
  'profile', 'my-profile', 'company', 'relations',
  'posts', 'post', 'invitations', 'attendees'
];

const client = new UnipileClient(DSN, TOKEN);

function parseArgs(args) {
  const result = { _: [] };
  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [key, value] = arg.slice(2).split('=');
      result[key] = value ?? true;
    } else {
      result._.push(arg);
    }
  }
  return result;
}

function json(obj) {
  console.log(JSON.stringify(obj, null, 2));
}

function checkPermission(cmd) {
  if (WRITE_COMMANDS.includes(cmd) && !hasWrite) {
    console.error(`Error: Command '${cmd}' requires write permission.`);
    console.error(`Current permissions: ${PERMISSIONS.join(', ')}`);
    console.error(`Set UNIPILE_PERMISSIONS=write or UNIPILE_PERMISSIONS=read,write to enable.`);
    process.exit(3);
  }
  
  if (READ_COMMANDS.includes(cmd) && !hasRead) {
    console.error(`Error: Command '${cmd}' requires read permission.`);
    console.error(`Current permissions: ${PERMISSIONS.join(', ')}`);
    console.error(`Set UNIPILE_PERMISSIONS=read to enable.`);
    process.exit(3);
  }
}

function showHelp() {
  console.log(`Unipile LinkedIn SDK CLI

Environment:
  UNIPILE_DSN           API endpoint (required)
  UNIPILE_ACCESS_TOKEN  Access token (required)
  UNIPILE_PERMISSIONS   Permissions: "read", "write", or "read,write" (default: read,write)

Read Commands (require read permission):
  accounts                             List LinkedIn accounts
  account <id>                         Get account details
  chats [--account_id=X] [--limit=N]   List chats
  chat <id>                            Get chat details
  messages <chat_id> [--limit=N]       List messages
  profile <account_id> <identifier> [--sections=X] [--notify]
  my-profile <account_id>              Get own profile
  company <account_id> <identifier>    Get company profile
  relations <account_id> [--limit=N]   Get connections
  posts <account_id> <identifier> [--limit=N]
  post <account_id> <post_id>
  invitations <account_id>             List pending invitations
  attendees [--account_id=X]           List chat contacts

Write Commands (require write permission):
  send <chat_id> "<text>"              Send message
  start-chat <account_id> "<text>" --to=<id>[,id] [--inmail]
  invite <account_id> <provider_id> ["message"]
  cancel-invite <account_id> <id>      Cancel invitation
  create-post <account_id> "<text>"
  comment <account_id> <post_id> "<text>"
  react <account_id> <post_id> [--type=like|celebrate|love|...]

Examples:
  # Read-only mode (safe for viewing data)
  UNIPILE_PERMISSIONS=read node linkedin.mjs posts <account> andrewyng

  # Full access (required for sending messages, creating posts)
  UNIPILE_PERMISSIONS=read,write node linkedin.mjs send <chat_id> "Hello!"

  # Default is full access
  node linkedin.mjs accounts
`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [cmd, ...params] = args._;

  if (!cmd || cmd === 'help') {
    showHelp();
    return;
  }

  checkPermission(cmd);

  try {
    switch (cmd) {
      // Account
      case 'accounts':
        const allAccounts = await client.account.getAll();
        json(allAccounts.items?.filter(a => a.type === 'LINKEDIN') || allAccounts);
        break;
        
      case 'account':
        json(await client.account.get(params[0]));
        break;

      // Chats
      case 'chats':
        json(await client.messaging.getAllChats({
          account_type: 'LINKEDIN',
          account_id: args.account_id,
          limit: args.limit ? parseInt(args.limit) : undefined,
          after: args.after,
        }));
        break;

      case 'chat':
        json(await client.messaging.getChat(params[0]));
        break;

      case 'messages':
        json(await client.messaging.getAllMessagesFromChat({
          chat_id: params[0],
          limit: args.limit ? parseInt(args.limit) : undefined,
        }));
        break;

      case 'send':
        await client.messaging.sendMessage({
          chat_id: params[0],
          text: params[1],
        });
        console.log('Message sent');
        break;

      case 'start-chat':
        await client.messaging.startNewChat({
          account_id: params[0],
          attendees_ids: args.to?.split(',') || [],
          text: params[1],
          options: args.inmail ? { linkedin: { inmail: true } } : undefined,
        });
        console.log('Chat started');
        break;

      // Profiles
      case 'profile':
        const profileOpts = {
          account_id: params[0],
          identifier: params[1],
        };
        if (args.sections) profileOpts.linkedin_sections = args.sections.split(',');
        if (args.notify) profileOpts.notify = true;
        json(await client.users.getProfile(profileOpts));
        break;

      case 'my-profile':
        json(await client.users.getOwnProfile(params[0]));
        break;

      case 'company':
        json(await client.users.getCompanyProfile({
          account_id: params[0],
          identifier: params[1],
        }));
        break;

      case 'relations':
        json(await client.users.getAllRelations({
          account_id: params[0],
          limit: args.limit ? parseInt(args.limit) : undefined,
        }));
        break;

      // Invitations
      case 'invite':
        await client.users.sendInvitation({
          account_id: params[0],
          provider_id: params[1],
          message: params[2] || '',
        });
        console.log('Invitation sent');
        break;

      case 'invitations':
        json(await client.users.getAllInvitationsSent({
          account_id: params[0],
        }));
        break;

      case 'cancel-invite':
        await client.users.cancelInvitationSent({
          account_id: params[0],
          invitation_id: params[1],
        });
        console.log('Invitation cancelled');
        break;

      // Posts
      case 'posts':
        json(await client.users.getAllPosts({
          account_id: params[0],
          identifier: params[1],
          limit: args.limit ? parseInt(args.limit) : undefined,
        }));
        break;

      case 'post':
        json(await client.users.getPost({
          account_id: params[0],
          post_id: params[1],
        }));
        break;

      case 'create-post':
        await client.users.createPost({
          account_id: params[0],
          text: params[1],
        });
        console.log('Post created');
        break;

      case 'comment':
        await client.users.sendPostComment({
          account_id: params[0],
          post_id: params[1],
          text: params[2],
        });
        console.log('Comment added');
        break;

      case 'react':
        await client.users.sendPostReaction({
          account_id: params[0],
          post_id: params[1],
          reaction_type: args.type || 'like',
        });
        console.log('Reaction added');
        break;

      // Attendees
      case 'attendees':
        json(await client.messaging.getAllAttendees({
          account_id: args.account_id,
          limit: args.limit ? parseInt(args.limit) : undefined,
        }));
        break;

      default:
        console.error(`Unknown command: ${cmd}`);
        console.error('Run with "help" for usage information.');
        process.exit(1);
    }
  } catch (err) {
    if (err instanceof UnsuccessfulRequestError) {
      console.error(`API Error (${err.body?.status}): ${err.message}`);
      console.error('Type:', err.body?.type);
      if (err.body?.detail) console.error('Detail:', err.body.detail);
    } else {
      console.error('Error:', err.message);
    }
    process.exit(1);
  }
}

main();
