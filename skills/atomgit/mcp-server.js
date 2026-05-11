#!/usr/bin/env node

/**
 * AtomGit (GitCode) MCP Server
 * 
 * 提供 GitCode API v5 的 MCP 工具封装
 * 
 * 环境变量:
 * - ATOMGIT_TOKEN: GitCode 个人访问令牌
 */

const https = require('https');
const http = require('http');

const BASE_URL = 'https://api.gitcode.com/api/v5';

// 从环境变量获取 token
const TOKEN = process.env.ATOMGIT_TOKEN;

if (!TOKEN) {
  console.error('ERROR: ATOMGIT_TOKEN environment variable is not set');
  console.error('Please set your GitCode personal access token');
  process.exit(1);
}

/**
 * 发起 HTTP 请求
 */
function request(method, path, body = null) {
  return new Promise((resolve, reject) => {
    // 移除路径前导斜杠，确保相对路径正确拼接到 BASE_URL
    const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
    const url = new URL(normalizedPath, BASE_URL + '/');
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json',
        'User-Agent': 'OpenClaw-AtomGit-Skill/1.0'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = res.statusCode === 204 ? null : JSON.parse(data);
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: result
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data
          });
        }
      });
    });

    req.on('error', reject);
    
    if (body) {
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

/**
 * MCP 工具实现
 */
const tools = {
  /**
   * 获取当前认证用户信息
   */
  getCurrentUser: async () => {
    const res = await request('GET', '/user');
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to get user: ${res.status}`, data: res.data };
  },

  /**
   * 获取指定用户详情
   */
  getUser: async ({ username }) => {
    if (!username) {
      return { success: false, error: 'username is required' };
    }
    const res = await request('GET', `/users/${encodeURIComponent(username)}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to get user: ${res.status}`, data: res.data };
  },

  /**
   * 列出用户或组织的仓库
   */
  listRepos: async ({ username, type = 'owner', sort = 'updated', direction = 'desc', page = 1, perPage = 20 }) => {
    const params = new URLSearchParams({
      type,
      sort,
      direction,
      page: String(page),
      per_page: String(perPage)
    });
    
    const path = username 
      ? `/users/${encodeURIComponent(username)}/repos?${params}`
      : `/user/repos?${params}`;
    
    const res = await request('GET', path);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to list repos: ${res.status}`, data: res.data };
  },

  /**
   * 获取仓库详情
   */
  getRepo: async ({ owner, repo }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to get repo: ${res.status}`, data: res.data };
  },

  /**
   * 创建新仓库
   */
  createRepo: async ({ name, description = '', private = false, autoInit = false, license = '', readme = '' }) => {
    if (!name) {
      return { success: false, error: 'name is required' };
    }
    const body = {
      name,
      description,
      private,
      auto_init: autoInit,
      license_template: license,
      readme_template: readme
    };
    const res = await request('POST', '/user/repos', body);
    if (res.status === 201) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to create repo: ${res.status}`, data: res.data };
  },

  /**
   * 更新仓库信息
   */
  updateRepo: async ({ owner, repo, name, description, private, hasIssues, hasWiki, defaultBranch }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const body = {};
    if (name !== undefined) body.name = name;
    if (description !== undefined) body.description = description;
    if (private !== undefined) body.private = private;
    if (hasIssues !== undefined) body.has_issues = hasIssues;
    if (hasWiki !== undefined) body.has_wiki = hasWiki;
    if (defaultBranch !== undefined) body.default_branch = defaultBranch;
    
    const res = await request('PATCH', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`, body);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to update repo: ${res.status}`, data: res.data };
  },

  /**
   * 删除仓库
   */
  deleteRepo: async ({ owner, repo }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const res = await request('DELETE', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`);
    if (res.status === 204) {
      return { success: true, message: 'Repository deleted successfully' };
    }
    return { success: false, error: `Failed to delete repo: ${res.status}`, data: res.data };
  },

  /**
   * 列出仓库 Issue
   */
  listIssues: async ({ owner, repo, state = 'all', labels = '', sort = 'created', direction = 'desc', page = 1, perPage = 20 }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const params = new URLSearchParams({
      state,
      labels,
      sort,
      direction,
      page: String(page),
      per_page: String(perPage)
    });
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/issues?${params}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to list issues: ${res.status}`, data: res.data };
  },

  /**
   * 获取 Issue 详情
   */
  getIssue: async ({ owner, repo, number }) => {
    if (!owner || !repo || !number) {
      return { success: false, error: 'owner, repo, and number are required' };
    }
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/issues/${number}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to get issue: ${res.status}`, data: res.data };
  },

  /**
   * 创建新 Issue
   */
  createIssue: async ({ owner, repo, title, body = '', assignee = '', labels = '' }) => {
    if (!owner || !repo || !title) {
      return { success: false, error: 'owner, repo, and title are required' };
    }
    const bodyData = { title };
    if (body) bodyData.body = body;
    if (assignee) bodyData.assignee = assignee;
    if (labels) bodyData.labels = labels.split(',').map(l => l.trim());
    
    const res = await request('POST', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/issues`, bodyData);
    if (res.status === 201) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to create issue: ${res.status}`, data: res.data };
  },

  /**
   * 更新 Issue
   */
  updateIssue: async ({ owner, repo, number, title, body, state, assignee, labels }) => {
    if (!owner || !repo || !number) {
      return { success: false, error: 'owner, repo, and number are required' };
    }
    const bodyData = {};
    if (title !== undefined) bodyData.title = title;
    if (body !== undefined) bodyData.body = body;
    if (state !== undefined) bodyData.state = state;
    if (assignee !== undefined) bodyData.assignee = assignee;
    if (labels !== undefined) bodyData.labels = labels;
    
    const res = await request('PATCH', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/issues/${number}`, bodyData);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to update issue: ${res.status}`, data: res.data };
  },

  /**
   * 列出 Pull Requests
   */
  listPullRequests: async ({ owner, repo, state = 'open', sort = 'created', direction = 'desc', page = 1, perPage = 20 }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const params = new URLSearchParams({
      state,
      sort,
      direction,
      page: String(page),
      per_page: String(perPage)
    });
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/pulls?${params}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to list pull requests: ${res.status}`, data: res.data };
  },

  /**
   * 获取 PR 详情
   */
  getPullRequest: async ({ owner, repo, number }) => {
    if (!owner || !repo || !number) {
      return { success: false, error: 'owner, repo, and number are required' };
    }
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/pulls/${number}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to get pull request: ${res.status}`, data: res.data };
  },

  /**
   * 创建 Pull Request
   */
  createPullRequest: async ({ owner, repo, title, body = '', head, base, maintainerCanModify = true }) => {
    if (!owner || !repo || !title || !head || !base) {
      return { success: false, error: 'owner, repo, title, head, and base are required' };
    }
    const bodyData = {
      title,
      head,
      base,
      maintainer_can_modify: maintainerCanModify
    };
    if (body) bodyData.body = body;
    
    const res = await request('POST', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/pulls`, bodyData);
    if (res.status === 201) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to create pull request: ${res.status}`, data: res.data };
  },

  /**
   * 合并 Pull Request
   */
  mergePullRequest: async ({ owner, repo, number, commitTitle = '', commitMessage = '', mergeMethod = 'merge' }) => {
    if (!owner || !repo || !number) {
      return { success: false, error: 'owner, repo, and number are required' };
    }
    const bodyData = {
      merge_method: mergeMethod
    };
    if (commitTitle) bodyData.commit_title = commitTitle;
    if (commitMessage) bodyData.commit_message = commitMessage;
    
    const res = await request('PUT', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/pulls/${number}/merge`, bodyData);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to merge pull request: ${res.status}`, data: res.data };
  },

  /**
   * 获取仓库文件内容
   */
  getRepoFile: async ({ owner, repo, path, ref = 'main' }) => {
    if (!owner || !repo || !path) {
      return { success: false, error: 'owner, repo, and path are required' };
    }
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/${encodeURIComponent(path)}?ref=${encodeURIComponent(ref)}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to get file: ${res.status}`, data: res.data };
  },

  /**
   * 创建/更新文件
   */
  createFile: async ({ owner, repo, path, content, message, branch = 'main', sha = null }) => {
    if (!owner || !repo || !path || !content || !message) {
      return { success: false, error: 'owner, repo, path, content, and message are required' };
    }
    const bodyData = {
      message,
      content: Buffer.from(content).toString('base64'),
      branch
    };
    if (sha) bodyData.sha = sha;
    
    const res = await request('PUT', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/${encodeURIComponent(path)}`, bodyData);
    if (res.status === 201 || res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to create/update file: ${res.status}`, data: res.data };
  },

  /**
   * 列出分支
   */
  listBranches: async ({ owner, repo, page = 1, perPage = 20 }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const params = new URLSearchParams({
      page: String(page),
      per_page: String(perPage)
    });
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/branches?${params}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to list branches: ${res.status}`, data: res.data };
  },

  /**
   * 创建分支
   */
  createBranch: async ({ owner, repo, branch, ref = 'main' }) => {
    if (!owner || !repo || !branch) {
      return { success: false, error: 'owner, repo, and branch are required' };
    }
    const bodyData = {
      ref: `refs/heads/${branch}`,
      sha: null,
      base_ref: ref
    };
    const res = await request('POST', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/branches`, bodyData);
    if (res.status === 201) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to create branch: ${res.status}`, data: res.data };
  },

  /**
   * 删除分支
   */
  deleteBranch: async ({ owner, repo, branch }) => {
    if (!owner || !repo || !branch) {
      return { success: false, error: 'owner, repo, and branch are required' };
    }
    const res = await request('DELETE', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/branches/${encodeURIComponent(branch)}`);
    if (res.status === 204) {
      return { success: true, message: 'Branch deleted successfully' };
    }
    return { success: false, error: `Failed to delete branch: ${res.status}`, data: res.data };
  },

  /**
   * Fork 一个仓库
   */
  forkRepo: async ({ owner, repo, organization = '' }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const body = {};
    if (organization) body.organization = organization;
    
    const res = await request('POST', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/forks`, body);
    if (res.status === 200 || res.status === 201) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to fork repo: ${res.status}`, data: res.data };
  },

  /**
   * 列出仓库的 Forks
   */
  listForks: async ({ owner, repo, sort = 'newest', page = 1, perPage = 20 }) => {
    if (!owner || !repo) {
      return { success: false, error: 'owner and repo are required' };
    }
    const params = new URLSearchParams({
      sort,
      page: String(page),
      per_page: String(perPage)
    });
    const res = await request('GET', `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/forks?${params}`);
    if (res.status === 200) {
      return { success: true, data: res.data };
    }
    return { success: false, error: `Failed to list forks: ${res.status}`, data: res.data };
  }
};

/**
 * MCP 协议处理
 */
async function handleRequest(request) {
  const { method, params } = request;
  
  if (method === 'tools/list') {
    return {
      tools: Object.keys(tools).map(name => ({
        name,
        description: tools[name].toString().split('\n')[1]?.trim() || 'MCP tool',
        inputSchema: {
          type: 'object',
          properties: {},
          required: []
        }
      }))
    };
  }
  
  if (method === 'tools/call') {
    const { name, arguments: args = {} } = params;
    if (!tools[name]) {
      return { error: `Unknown tool: ${name}` };
    }
    try {
      const result = await tools[name](args);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ success: false, error: error.message })
        }]
      };
    }
  }
  
  return { error: `Unknown method: ${method}` };
}

// 主循环 - 处理 stdin 输入
const readline = require('readline');
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let buffer = '';

process.stdin.on('data', (chunk) => {
  buffer += chunk.toString();
  
  // MCP 使用 JSON-RPC，每条消息以换行分隔
  const lines = buffer.split('\n');
  buffer = lines.pop() || '';
  
  for (const line of lines) {
    if (!line.trim()) continue;
    
    try {
      const request = JSON.parse(line);
      handleRequest(request).then(response => {
        const jsonResponse = JSON.stringify(response);
        process.stdout.write(jsonResponse + '\n');
      }).catch(error => {
        const errorResponse = JSON.stringify({
          error: {
            code: -32603,
            message: error.message
          }
        });
        process.stdout.write(errorResponse + '\n');
      });
    } catch (e) {
      console.error('Failed to parse request:', e.message);
    }
  }
});

// 启动日志
console.error('AtomGit MCP Server started');
console.error('Waiting for requests...');
