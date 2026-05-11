#!/usr/bin/env node

/**
 * Reddit CLI - Browse, search, post, and moderate subreddits
 * 
 * Read-only: Uses public JSON API (no auth)
 * Write/Mod: Requires OAuth - run `login` command first
 */

import { createServer } from 'http';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { exec } from 'child_process';

const BASE_URL = 'https://www.reddit.com';
const OAUTH_URL = 'https://oauth.reddit.com';
const USER_AGENT = 'script:clawdbot-reddit:v1.0.0';
const TOKEN_FILE = join(homedir(), '.reddit-token.json');
const REDIRECT_URI = 'http://localhost:8080/callback';
const SCOPES = 'read submit edit identity mysubreddits modposts modcontributors modmail modconfig modlog modself flair';

let tokenCache = null;

function getClientCreds() {
  const { REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET } = process.env;
  if (!REDDIT_CLIENT_ID || !REDDIT_CLIENT_SECRET) {
    throw new Error('Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET');
  }
  return { clientId: REDDIT_CLIENT_ID, clientSecret: REDDIT_CLIENT_SECRET };
}

function loadToken() {
  if (tokenCache) return tokenCache;
  if (!existsSync(TOKEN_FILE)) return null;
  try {
    tokenCache = JSON.parse(readFileSync(TOKEN_FILE, 'utf-8'));
    return tokenCache;
  } catch {
    return null;
  }
}

function saveToken(token) {
  tokenCache = token;
  writeFileSync(TOKEN_FILE, JSON.stringify(token, null, 2));
}

async function refreshAccessToken() {
  const token = loadToken();
  if (!token?.refresh_token) {
    throw new Error('Not logged in. Run: node reddit.mjs login');
  }
  
  const { clientId, clientSecret } = getClientCreds();
  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
  
  const res = await fetch('https://www.reddit.com/api/v1/access_token', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': USER_AGENT,
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: token.refresh_token,
    }),
  });
  
  if (!res.ok) {
    throw new Error(`Token refresh failed: ${res.status} ${await res.text()}`);
  }
  
  const data = await res.json();
  const newToken = {
    access_token: data.access_token,
    refresh_token: token.refresh_token, // Reddit doesn't always return a new refresh token
    expires_at: Date.now() + (data.expires_in * 1000),
  };
  saveToken(newToken);
  return newToken.access_token;
}

async function getAccessToken() {
  const token = loadToken();
  if (!token) {
    throw new Error('Not logged in. Run: node reddit.mjs login');
  }
  
  // Refresh if expired or expiring soon (5 min buffer)
  if (Date.now() > (token.expires_at - 300000)) {
    return refreshAccessToken();
  }
  
  return token.access_token;
}

async function publicFetch(path) {
  // Insert .json before query string if present
  let url;
  if (path.includes('?')) {
    const [basePath, query] = path.split('?');
    url = `${BASE_URL}${basePath}.json?${query}`;
  } else {
    url = `${BASE_URL}${path}.json`;
  }
  
  const res = await fetch(url, {
    headers: { 
      'User-Agent': USER_AGENT,
      'Accept': 'application/json',
    },
  });
  
  const text = await res.text();
  
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${text.slice(0, 200)}`);
  }
  
  // Check if we got HTML instead of JSON (Reddit sometimes does this)
  if (text.trim().startsWith('<')) {
    throw new Error('Reddit returned HTML instead of JSON. Try again in a moment.');
  }
  
  return JSON.parse(text);
}

async function oauthFetch(path, options = {}) {
  const token = await getAccessToken();
  const url = `${OAUTH_URL}${path}`;
  
  const res = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'User-Agent': USER_AGENT,
      ...options.headers,
    },
  });
  
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed: ${res.status} ${text.slice(0, 500)}`);
  }
  
  return res.json();
}

async function oauthPost(path, data) {
  return oauthFetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(data),
  });
}

// OAuth Login Flow

async function login() {
  const { clientId, clientSecret } = getClientCreds();
  
  const state = Math.random().toString(36).slice(2);
  const authUrl = `https://www.reddit.com/api/v1/authorize?client_id=${clientId}&response_type=code&state=${state}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&duration=permanent&scope=${encodeURIComponent(SCOPES)}`;
  
  console.log('\n🔐 Reddit OAuth Login\n');
  console.log('Open this URL in your browser:\n');
  console.log(authUrl);
  console.log('\nWaiting for authorization...\n');
  
  // Start local server to catch the callback
  return new Promise((resolve, reject) => {
    const server = createServer(async (req, res) => {
      if (!req.url.startsWith('/callback')) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      
      const url = new URL(req.url, 'http://localhost:8080');
      const code = url.searchParams.get('code');
      const returnedState = url.searchParams.get('state');
      const error = url.searchParams.get('error');
      
      if (error) {
        res.writeHead(400);
        res.end(`Authorization failed: ${error}`);
        server.close();
        reject(new Error(`Authorization failed: ${error}`));
        return;
      }
      
      if (returnedState !== state) {
        res.writeHead(400);
        res.end('State mismatch - possible CSRF attack');
        server.close();
        reject(new Error('State mismatch'));
        return;
      }
      
      // Exchange code for token
      const auth = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
      
      try {
        const tokenRes = await fetch('https://www.reddit.com/api/v1/access_token', {
          method: 'POST',
          headers: {
            'Authorization': `Basic ${auth}`,
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': USER_AGENT,
          },
          body: new URLSearchParams({
            grant_type: 'authorization_code',
            code,
            redirect_uri: REDIRECT_URI,
          }),
        });
        
        if (!tokenRes.ok) {
          throw new Error(`Token exchange failed: ${await tokenRes.text()}`);
        }
        
        const tokenData = await tokenRes.json();
        
        const token = {
          access_token: tokenData.access_token,
          refresh_token: tokenData.refresh_token,
          expires_at: Date.now() + (tokenData.expires_in * 1000),
        };
        
        saveToken(token);
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end('<html><body><h1>✅ Logged in!</h1><p>You can close this tab.</p></body></html>');
        
        console.log('✅ Successfully logged in! Token saved to ~/.reddit-token.json\n');
        
        server.close();
        resolve();
      } catch (err) {
        res.writeHead(500);
        res.end(`Error: ${err.message}`);
        server.close();
        reject(err);
      }
    });
    
    server.listen(8080, () => {
      // Try to open browser automatically
      const cmd = process.platform === 'darwin' ? 'open' : process.platform === 'win32' ? 'start' : 'xdg-open';
      exec(`${cmd} "${authUrl}"`);
    });
    
    // Timeout after 5 minutes
    setTimeout(() => {
      server.close();
      reject(new Error('Login timed out'));
    }, 300000);
  });
}

// Commands

async function getPosts(subreddit, { sort = 'hot', time = 'day', limit = 25 }) {
  const timeSuffix = sort === 'top' || sort === 'controversial' ? `?t=${time}&limit=${limit}` : `?limit=${limit}`;
  const data = await publicFetch(`/r/${subreddit}/${sort}${timeSuffix}`);
  
  const posts = data.data.children.map(p => ({
    id: p.data.id,
    title: p.data.title,
    author: p.data.author,
    score: p.data.score,
    comments: p.data.num_comments,
    url: p.data.url,
    permalink: `https://reddit.com${p.data.permalink}`,
    created: new Date(p.data.created_utc * 1000).toISOString(),
    selftext: p.data.selftext?.slice(0, 500) || null,
    flair: p.data.link_flair_text || null,
  }));
  
  console.log(JSON.stringify(posts, null, 2));
}

async function searchPosts(subreddit, query, { sort = 'relevance', time = 'all', limit = 25 }) {
  const path = subreddit === 'all' 
    ? `/search?q=${encodeURIComponent(query)}&sort=${sort}&t=${time}&limit=${limit}`
    : `/r/${subreddit}/search?q=${encodeURIComponent(query)}&restrict_sr=on&sort=${sort}&t=${time}&limit=${limit}`;
  
  const data = await publicFetch(path);
  
  const posts = data.data.children.map(p => ({
    id: p.data.id,
    subreddit: p.data.subreddit,
    title: p.data.title,
    author: p.data.author,
    score: p.data.score,
    comments: p.data.num_comments,
    permalink: `https://reddit.com${p.data.permalink}`,
    created: new Date(p.data.created_utc * 1000).toISOString(),
  }));
  
  console.log(JSON.stringify(posts, null, 2));
}

async function getComments(postId, { limit = 50 }) {
  // Handle full URLs
  if (postId.startsWith('http')) {
    const match = postId.match(/comments\/([a-z0-9]+)/i);
    if (match) postId = match[1];
  }
  
  // Need to find the subreddit - fetch post info first
  const postData = await publicFetch(`/by_id/t3_${postId}`);
  const subreddit = postData.data.children[0]?.data?.subreddit;
  
  if (!subreddit) throw new Error('Could not find post');
  
  const data = await publicFetch(`/r/${subreddit}/comments/${postId}?limit=${limit}`);
  
  function parseComments(children, depth = 0) {
    const results = [];
    for (const c of children) {
      if (c.kind !== 't1') continue;
      results.push({
        id: c.data.id,
        author: c.data.author,
        body: c.data.body?.slice(0, 1000),
        score: c.data.score,
        depth,
        created: new Date(c.data.created_utc * 1000).toISOString(),
      });
      if (c.data.replies?.data?.children) {
        results.push(...parseComments(c.data.replies.data.children, depth + 1));
      }
    }
    return results;
  }
  
  const comments = parseComments(data[1].data.children);
  console.log(JSON.stringify(comments, null, 2));
}

async function submitPost(subreddit, { title, text, url }) {
  const data = {
    sr: subreddit,
    title,
    kind: url ? 'link' : 'self',
    api_type: 'json',
  };
  
  if (url) data.url = url;
  if (text) data.text = text;
  
  const result = await oauthPost('/api/submit', data);
  
  if (result.json?.errors?.length) {
    throw new Error(`Submit failed: ${JSON.stringify(result.json.errors)}`);
  }
  
  console.log(JSON.stringify({
    success: true,
    url: result.json?.data?.url,
    id: result.json?.data?.id,
  }, null, 2));
}

async function reply(thingId, text) {
  // Ensure proper prefix
  if (!thingId.startsWith('t1_') && !thingId.startsWith('t3_')) {
    // Guess based on length - posts are usually shorter IDs
    thingId = `t1_${thingId}`; // Assume comment by default
  }
  
  const result = await oauthPost('/api/comment', {
    thing_id: thingId,
    text,
    api_type: 'json',
  });
  
  if (result.json?.errors?.length) {
    throw new Error(`Reply failed: ${JSON.stringify(result.json.errors)}`);
  }
  
  console.log(JSON.stringify({
    success: true,
    id: result.json?.data?.things?.[0]?.data?.id,
  }, null, 2));
}

async function modAction(action, thingId, subreddit) {
  // Ensure proper prefix for IDs
  if (thingId && !thingId.startsWith('t1_') && !thingId.startsWith('t3_')) {
    thingId = `t3_${thingId}`; // Assume post
  }
  
  switch (action) {
    case 'remove':
      await oauthPost('/api/remove', { id: thingId, spam: false });
      console.log(JSON.stringify({ success: true, action: 'removed', id: thingId }));
      break;
      
    case 'approve':
      await oauthPost('/api/approve', { id: thingId });
      console.log(JSON.stringify({ success: true, action: 'approved', id: thingId }));
      break;
      
    case 'sticky':
      await oauthPost('/api/set_subreddit_sticky', { id: thingId, state: true });
      console.log(JSON.stringify({ success: true, action: 'stickied', id: thingId }));
      break;
      
    case 'unsticky':
      await oauthPost('/api/set_subreddit_sticky', { id: thingId, state: false });
      console.log(JSON.stringify({ success: true, action: 'unstickied', id: thingId }));
      break;
      
    case 'lock':
      await oauthPost('/api/lock', { id: thingId });
      console.log(JSON.stringify({ success: true, action: 'locked', id: thingId }));
      break;
      
    case 'unlock':
      await oauthPost('/api/unlock', { id: thingId });
      console.log(JSON.stringify({ success: true, action: 'unlocked', id: thingId }));
      break;
      
    case 'queue':
      if (!subreddit) throw new Error('Subreddit required for modqueue');
      const data = await oauthFetch(`/r/${subreddit}/about/modqueue?limit=25`);
      const items = data.data.children.map(p => ({
        id: p.data.id,
        type: p.kind === 't1' ? 'comment' : 'post',
        author: p.data.author,
        title: p.data.title || p.data.body?.slice(0, 100),
        reports: p.data.num_reports,
        created: new Date(p.data.created_utc * 1000).toISOString(),
      }));
      console.log(JSON.stringify(items, null, 2));
      break;
      
    default:
      throw new Error(`Unknown mod action: ${action}`);
  }
}

async function whoami() {
  const data = await oauthFetch('/api/v1/me');
  console.log(JSON.stringify({
    username: data.name,
    id: data.id,
    karma: data.total_karma,
    created: new Date(data.created_utc * 1000).toISOString(),
  }, null, 2));
}

// CLI Parser

function parseArgs(args) {
  const result = { _: [] };
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        result[key] = next;
        i++;
      } else {
        result[key] = true;
      }
    } else {
      result._.push(arg);
    }
  }
  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [command, ...rest] = args._;
  
  try {
    switch (command) {
      case 'login': {
        await login();
        break;
      }
      
      case 'whoami': {
        await whoami();
        break;
      }
      
      case 'posts': {
        const [subreddit] = rest;
        if (!subreddit) throw new Error('Usage: posts <subreddit> [--sort hot|new|top] [--time day|week|month|year|all] [--limit N]');
        await getPosts(subreddit, args);
        break;
      }
      
      case 'search': {
        const [subreddit, ...queryParts] = rest;
        const query = queryParts.join(' ');
        if (!subreddit || !query) throw new Error('Usage: search <subreddit|all> <query> [--sort relevance|top|new] [--time all|day|week|month|year] [--limit N]');
        await searchPosts(subreddit, query, args);
        break;
      }
      
      case 'comments': {
        const [postId] = rest;
        if (!postId) throw new Error('Usage: comments <post_id|url> [--limit N]');
        await getComments(postId, args);
        break;
      }
      
      case 'submit': {
        const [subreddit] = rest;
        if (!subreddit || !args.title) throw new Error('Usage: submit <subreddit> --title "Title" [--text "Body"] [--url "URL"]');
        await submitPost(subreddit, args);
        break;
      }
      
      case 'reply': {
        const [thingId, ...textParts] = rest;
        const text = textParts.join(' ');
        if (!thingId || !text) throw new Error('Usage: reply <thing_id> <text>');
        await reply(thingId, text);
        break;
      }
      
      case 'mod': {
        const [action, targetOrSubreddit] = rest;
        if (!action) throw new Error('Usage: mod <remove|approve|sticky|unsticky|lock|unlock|queue> <thing_id|subreddit>');
        await modAction(action, targetOrSubreddit, targetOrSubreddit);
        break;
      }
      
      default:
        console.error(`Commands: login, whoami, posts, search, comments, submit, reply, mod`);
        process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
