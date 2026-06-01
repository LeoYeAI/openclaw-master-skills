/**
 * @fileoverview GitHub 仓库分析工具 - 将 GitHub 仓库转换为 AI 友好的格式
 * @description 分析 GitHub 仓库结构、生成架构图、转换为 Markdown 文档
 * @author AI Assistant
 * @version 1.0.0
 */

const GITHUB_API = "https://api.github.com";
const GITHUB_RAW = "https://raw.githubusercontent.com";

// 文本可读的文件扩展名
const TEXT_EXTENSIONS = new Set([
  ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb", ".java", ".kt",
  ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".php", ".lua", ".r", ".jl",
  ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
  ".md", ".txt", ".rst", ".adoc", ".org",
  ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env.example",
  ".xml", ".html", ".css", ".scss", ".less", ".svg",
  ".sql", ".graphql", ".proto", ".tf", ".hcl",
  ".dockerfile", ".gitignore", ".editorconfig",
  ".makefile", ".cmake",
]);

// 重要文件（无论扩展名都包含）
const IMPORTANT_FILES = new Set([
  "README.md", "readme.md", "README", "LICENSE", "LICENSE.md",
  "Makefile", "CMakeLists.txt", "Dockerfile", "docker-compose.yml",
  "package.json", "Cargo.toml", "go.mod", "pyproject.toml", "setup.py",
  "requirements.txt", "Gemfile", "pom.xml", "build.gradle",
  ".gitignore", ".env.example",
]);

// 跳过的目录
const SKIP_DIRS = new Set([
  "node_modules", "vendor", "dist", "build", "__pycache__", ".git",
  ".next", ".nuxt", "target", "bin", "obj", ".cache", "coverage",
]);

/**
 * 获取 GitHub API 请求头
 * @param {string} [token] - GitHub token（可选）
 * @returns {Object} 请求头对象
 */
function getHeaders(token) {
  const headers = {
    "Accept": "application/vnd.github.v3+json",
  };
  if (token) {
    headers["Authorization"] = `token ${token}`;
  }
  return headers;
}

/**
 * 解析 GitHub URL 或 owner/repo 字符串
 * @param {string} url - GitHub URL 或 owner/repo 格式
 * @returns {{owner: string, repo: string}} 仓库所有者和名称
 * @throws {Error} 如果 URL 格式无效
 */
function parseGitHubUrl(url) {
  url = url.trim().replace(/\/$/, "");
  const match = url.match(/(?:https?:\/\/github\.com\/)?([^/]+)\/([^/]+?)(?:\.git)?$/);
  if (!match) {
    throw new Error(`Invalid GitHub URL: ${url}`);
  }
  return { owner: match[1], repo: match[2] };
}

/**
 * 获取仓库元数据
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {string} [token] - GitHub token（可选）
 * @returns {Promise<Object>} 仓库信息
 */
async function getRepoInfo(owner, repo, token) {
  const response = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}`,
    { headers: getHeaders(token), signal: AbortSignal.timeout(15000) }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch repo info: ${response.status} ${response.statusText}`);
  }
  return await response.json();
}

/**
 * 获取仓库文件树
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {string} branch - 分支名称
 * @param {number} [depth=2] - 目录深度限制
 * @param {string} [token] - GitHub token（可选）
 * @returns {Promise<Array>} 文件树数组
 */
async function getTree(owner, repo, branch, depth = 2, token) {
  const response = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}/git/trees/${branch}?recursive=1`,
    { headers: getHeaders(token), signal: AbortSignal.timeout(15000) }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch tree: ${response.status} ${response.statusText}`);
  }
  const data = await response.json();
  let tree = data.tree || [];
  if (depth > 0) {
    tree = tree.filter((t) => (t.path.match(/\//g) || []).length < depth);
  }
  return tree;
}

/**
 * 获取 README 内容
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {string} [token] - GitHub token（可选）
 * @returns {Promise<string>} README 内容
 */
async function getReadme(owner, repo, token) {
  const headers = {
    ...getHeaders(token),
    "Accept": "application/vnd.github.raw",
  };
  const response = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}/readme`,
    { headers, signal: AbortSignal.timeout(15000) }
  );
  if (response.ok) {
    return await response.text();
  }
  return "(No README found)";
}

/**
 * 获取语言统计
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {string} [token] - GitHub token（可选）
 * @returns {Promise<Object>} 语言统计对象
 */
async function getLanguages(owner, repo, token) {
  const response = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}/languages`,
    { headers: getHeaders(token), signal: AbortSignal.timeout(15000) }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch languages: ${response.status} ${response.statusText}`);
  }
  return await response.json();
}

/**
 * 获取最近的提交
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {number} [count=10] - 提交数量
 * @param {string} [token] - GitHub token（可选）
 * @returns {Promise<Array>} 提交数组
 */
async function getRecentCommits(owner, repo, count = 10, token) {
  const response = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}/commits?per_page=${count}`,
    { headers: getHeaders(token), signal: AbortSignal.timeout(15000) }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch commits: ${response.status} ${response.statusText}`);
  }
  return await response.json();
}

/**
 * 格式化文件树为可视化树形结构
 * @param {Array} treeItems - 文件树项数组
 * @returns {string} 格式化的树形字符串
 */
function formatTree(treeItems) {
  const lines = [];
  const paths = treeItems.map((t) => t.path).sort();
  
  for (const path of paths) {
    const depth = (path.match(/\//g) || []).length;
    const name = path.split("/").pop();
    const isDir = treeItems.some((t) => t.path === path && t.type === "tree");
    const prefix = "│   ".repeat(depth);
    const connector = "├── ";
    const suffix = isDir ? "/" : "";
    lines.push(`${prefix}${connector}${name}${suffix}`);
  }
  
  return lines.join("\n");
}

/**
 * 格式化语言统计为百分比
 * @param {Object} langs - 语言统计对象
 * @returns {string} 格式化的语言字符串
 */
function formatLanguages(langs) {
  const total = Object.values(langs).reduce((sum, val) => sum + val, 0);
  if (total === 0) {
    return "(No language data)";
  }
  
  const lines = Object.entries(langs)
    .sort((a, b) => b[1] - a[1])
    .map(([lang, bytes]) => {
      const pct = ((bytes / total) * 100).toFixed(1);
      return `- ${lang}: ${pct}%`;
    });
  
  return lines.join("\n");
}

/**
 * 生成 Mermaid 架构图
 * @param {Array} treeItems - 文件树项数组
 * @param {Object} repoInfo - 仓库信息
 * @returns {string} Mermaid 图表代码
 */
function generateMermaid(treeItems, repoInfo) {
  const dirs = new Set();
  for (const t of treeItems) {
    if (t.type === "tree" && (t.path.match(/\//g) || []).length === 0) {
      dirs.add(t.path);
    }
  }
  
  if (dirs.size === 0) {
    return "(Repository too flat for architecture diagram)";
  }
  
  const lines = ["graph TD"];
  const repoName = repoInfo.name || "repo";
  lines.push(`  ROOT["${repoName}"]`);
  
  for (const d of Array.from(dirs).sort()) {
    const safe = d.replace(/-/g, "_").replace(/\./g, "_");
    lines.push(`  ROOT --> ${safe}["${d}/"]`);
    
    // 查找子目录
    const subdirs = treeItems
      .filter((t) => t.type === "tree" && t.path.startsWith(d + "/") && (t.path.match(/\//g) || []).length === 1)
      .map((t) => t.path.split("/")[1]);
    
    for (const sd of Array.from(new Set(subdirs)).sort().slice(0, 8)) {
      const sdSafe = `${safe}_${sd.replace(/-/g, "_").replace(/\./g, "_")}`;
      lines.push(`  ${safe} --> ${sdSafe}["${sd}/"]`);
    }
  }
  
  return lines.join("\n");
}

/**
 * 格式化提交信息
 * @param {Array} commits - 提交数组
 * @returns {string} 格式化的提交字符串
 */
function formatCommits(commits) {
  const lines = [];
  for (const c of commits.slice(0, 10)) {
    const date = (c.commit?.author?.date || "").substring(0, 10);
    const msg = (c.commit?.message || "").split("\n")[0].substring(0, 80);
    const author = c.commit?.author?.name || "unknown";
    lines.push(`- ${date}: ${msg} (${author})`);
  }
  return lines.join("\n");
}

/**
 * 判断文件是否应该包含
 * @param {string} path - 文件路径
 * @returns {boolean} 是否应该包含
 */
function shouldInclude(path) {
  const name = path.split("/").pop();
  const parts = path.split("/");
  
  // 跳过隐藏目录和已知的垃圾目录
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i];
    if (SKIP_DIRS.has(part) || (part.startsWith(".") && part !== ".github")) {
      return false;
    }
  }
  
  // 始终包含重要文件
  if (IMPORTANT_FILES.has(name)) {
    return true;
  }
  
  // 检查扩展名
  const ext = name.substring(name.lastIndexOf(".")).toLowerCase();
  if (TEXT_EXTENSIONS.has(ext)) {
    return true;
  }
  
  // 包含根目录下无扩展名的文件（如 Makefile, Dockerfile）
  if (!path.includes("/") && !ext) {
    return true;
  }
  
  return false;
}

/**
 * 获取文件内容
 * @param {string} owner - 仓库所有者
 * @param {string} repo - 仓库名称
 * @param {string} branch - 分支名称
 * @param {string} path - 文件路径
 * @param {number} maxSize - 最大文件大小（字节）
 * @param {string} [token] - GitHub token（可选）
 * @returns {Promise<string>} 文件内容
 */
async function getFileContent(owner, repo, branch, path, maxSize, token) {
  const url = `${GITHUB_RAW}/${owner}/${repo}/${branch}/${path}`;
  try {
    const headers = token ? { Authorization: `token ${token}` } : {};
    const response = await fetch(url, {
      headers,
      signal: AbortSignal.timeout(10000),
    });
    
    if (!response.ok) {
      return `(Failed to fetch: HTTP ${response.status})`;
    }
    
    const content = await response.text();
    if (content.length > maxSize) {
      return content.substring(0, maxSize) + `\n\n... (truncated, ${content.length} bytes total)`;
    }
    return content;
  } catch (error) {
    return `(Error fetching: ${error.message})`;
  }
}

/**
 * 获取代码块语言标识
 * @param {string} path - 文件路径
 * @returns {string} 语言标识
 */
function getLanguageComment(path) {
  const extMap = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".java": "java",
    ".kt": "kotlin",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".php": "php",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".md": "markdown",
    ".dockerfile": "dockerfile",
    ".tf": "hcl",
    ".graphql": "graphql",
    ".proto": "protobuf",
  };
  
  const ext = path.substring(path.lastIndexOf(".")).toLowerCase();
  return extMap[ext] || "";
}

/**
 * 分析 GitHub 仓库（完整分析）
 * @param {string} url - GitHub URL 或 owner/repo 格式
 * @param {Object} [options] - 选项
 * @param {number} [options.depth=2] - 目录深度
 * @param {string} [options.token] - GitHub token（可选）
 * @returns {Promise<string>} 格式化的分析结果（Markdown）
 */
async function analyzeRepository(url, options = {}) {
  const { depth = 2, token } = options;
  const { owner, repo } = parseGitHubUrl(url);
  
  const [info, readme, langs, commits] = await Promise.all([
    getRepoInfo(owner, repo, token),
    getReadme(owner, repo, token),
    getLanguages(owner, repo, token),
    getRecentCommits(owner, repo, 10, token),
  ]);
  
  const branch = info.default_branch || "main";
  const tree = await getTree(owner, repo, branch, depth, token);
  
  const output = [];
  output.push(`# Repository: ${owner}/${repo}`);
  output.push("");
  output.push(`**${info.description || "No description"}**`);
  output.push(`- ⭐ ${(info.stargazers_count || 0).toLocaleString()} stars | 🍴 ${(info.forks_count || 0).toLocaleString()} forks`);
  output.push(`- License: ${info.license?.spdx_id || "None"}`);
  output.push(`- Default branch: ${branch}`);
  output.push(`- Last push: ${info.pushed_at || "Unknown"}`);
  output.push("");
  
  output.push("## Structure");
  output.push("```");
  output.push(formatTree(tree));
  output.push("```");
  output.push("");
  
  output.push("## README");
  let readmeText = readme;
  if (readmeText.length > 3000) {
    readmeText = readmeText.substring(0, 3000) + "\n\n... (truncated)";
  }
  output.push(readmeText);
  output.push("");
  
  output.push("## Language Breakdown");
  output.push(formatLanguages(langs));
  output.push("");
  
  output.push("## Architecture (Mermaid)");
  output.push("```mermaid");
  output.push(generateMermaid(tree, info));
  output.push("```");
  output.push("");
  
  output.push("## Recent Activity");
  output.push(formatCommits(commits));
  
  return output.join("\n");
}

/**
 * 将仓库转换为单个 Markdown 文档
 * @param {string} url - GitHub URL 或 owner/repo 格式
 * @param {Object} [options] - 选项
 * @param {number} [options.maxFiles=75] - 最大文件数
 * @param {number} [options.maxSize=30000] - 每个文件的最大大小（字节）
 * @param {string} [options.token] - GitHub token（可选）
 * @returns {Promise<string>} Markdown 文档
 */
async function convertToMarkdown(url, options = {}) {
  const { maxFiles = 75, maxSize = 30000, token } = options;
  const { owner, repo } = parseGitHubUrl(url);
  
  // 获取仓库信息
  const info = await getRepoInfo(owner, repo, token);
  const branch = info.default_branch || "main";
  
  // 获取完整文件树
  const treeResponse = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}/git/trees/${branch}?recursive=1`,
    { headers: getHeaders(token), signal: AbortSignal.timeout(15000) }
  );
  if (!treeResponse.ok) {
    throw new Error(`Failed to fetch tree: ${treeResponse.status} ${treeResponse.statusText}`);
  }
  const treeData = await treeResponse.json();
  const allItems = treeData.tree || [];
  
  // 过滤可包含的文件
  let files = allItems
    .filter((t) => t.type === "blob" && shouldInclude(t.path))
    .sort((a, b) => {
      const aName = a.path.split("/").pop();
      const bName = b.path.split("/").pop();
      const aImportant = IMPORTANT_FILES.has(aName);
      const bImportant = IMPORTANT_FILES.has(bName);
      if (aImportant !== bImportant) {
        return aImportant ? -1 : 1;
      }
      return a.path.localeCompare(b.path);
    })
    .slice(0, maxFiles);
  
  const output = [];
  output.push(`# ${owner}/${repo}`);
  output.push(`\n> ${info.description || "No description"}`);
  output.push(`\n⭐ ${(info.stargazers_count || 0).toLocaleString()} stars | License: ${info.license?.spdx_id || "None"}`);
  const totalFiles = allItems.filter((t) => t.type === "blob").length;
  output.push(`\nFiles included: ${files.length} of ${totalFiles}`);
  output.push("\n---\n");
  
  // 文件结构概览
  output.push("## File Structure\n```");
  for (const t of allItems.sort((a, b) => a.path.localeCompare(b.path))) {
    if ((t.path.match(/\//g) || []).length < 2) {
      const prefix = "  ".repeat((t.path.match(/\//g) || []).length);
      const suffix = t.type === "tree" ? "/" : "";
      output.push(`${prefix}${t.path.split("/").pop()}${suffix}`);
    }
  }
  output.push("```\n\n---\n");
  
  // 文件内容
  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    const path = f.path;
    console.error(`[repo2md] (${i + 1}/${files.length}) ${path}`);
    const lang = getLanguageComment(path);
    const content = await getFileContent(owner, repo, branch, path, maxSize, token);
    output.push(`## \`${path}\`\n`);
    output.push(`\`\`\`${lang}`);
    output.push(content);
    output.push("```\n");
  }
  
  return output.join("\n");
}

module.exports = {
  analyzeRepository,
  convertToMarkdown,
  parseGitHubUrl,
  getRepoInfo,
  getTree,
  getReadme,
  getLanguages,
  getRecentCommits,
};
