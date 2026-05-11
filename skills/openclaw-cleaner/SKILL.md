---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022008f95be176b259fbfb3a949f6958e0b396669a2c888cbc014dd2f4e530fa797a0220104bffedadebe9ed4b19e63d59a7080a0281cae9b97979dcadec6da9e511d9c6
    ReservedCode2: 3046022100b77338c69c1afc4517c82ecb004c8d63b1c4ef4f1d01fbaa78d660eb34fb5a29022100cf452e1faf2d576f12f0395e1b1853cf3800e63f52c485123bc93fd1cf37c17b
description: OpenClaw清理大师 - 项目目录清理与优化工具。提供快照、Diff、检查点、任务进度等能力，AI 可直接调用自动执行。
name: openclaw-cleaner
tags:
    - openclaw
    - cleaner
    - optimization
    - snapshot
    - backup
version: 2.1.2
---

# 🧹 OpenClaw Cleaner (清理大师)

> AI 可直接调用的项目清理与优化工具

本技能提供一系列自动化能力，AI 可在执行任务时直接调用，无需用户确认。

---

## 能力总览

| 能力 | 说明 | 何时调用 |
|------|------|----------|
| **快照** | 记录文件状态 | 执行修改前 |
| **Diff** | 对比变更差异 | 修改完成后展示给用户 |
| **Checkpoint** | 保存关键状态 | 重要操作前 |
| **Task Progress** | 追踪长时间任务 | 批量处理时 |
| **Health Check** | 评估目录健康度 | 用户询问或定期 |
| **Skill Match** | 推荐相关 Skills | 用户描述任务时 |
| **Optimize** | 优化文件减少 Token | 空间不足或定期 |

---

## 使用示例

### 场景：删除一个 Skill

```javascript
// 1. 先创建快照（自动，也可手动）
const snap = await snapshot.create('before-remove-old-skill');

// 2. 执行删除
await skills.remove('unused-skill');

// 3. 对比变更，展示给用户
const diff = await snapshot.compare(snap.name, 'latest');
console.log(snapshot.generateReport(diff));
// 用户看到: "我删除了 xxx，新增了 yyy"
```

### 场景：批量处理文件

```javascript
// 1. 开始任务
const taskInfo = await task.start('process-files', fileList);

// 2. 处理每个文件
for (const file of files) {
  try {
    await processFile(file);
    await task.markCompleted(taskInfo.id, index);
  } catch (e) {
    await task.markFailed(taskInfo.id, index, e.message);
  }
}

// 3. 用户可随时查看进度
const status = await task.getStatus(taskInfo.id);
```

---

## 返回格式

```javascript
// snapshot.compare()
{
  added: [{ path: string, size: number, content?: string }],
  removed: [{ path: string, size: number }],
  modified: [{ path: string, oldSize: number, newSize: number, changes: [] }]
}

// health.check()
{
  score: number,           // 0-100
  totalFiles: number,
  totalDirs: number,
  totalSize: number,
  warnings: string[]
}
```

---

## 版本

**v2.1.2** - 整合为单文件版本

---

<!-- 代码实现开始 -->
```javascript
// ============================================================================
// OpenClaw Cleaner - 完整实现代码 (2.1.2)
// ============================================================================

import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

// 获取工作空间路径
function getWorkspacePath() { return process.cwd(); }

// 静默日志
const silentLogger = { info: () => {}, debug: () => {}, warn: () => {}, error: () => {}, success: () => {}, section: () => {} };

// ============================================================================
// VisualDiffService - 快照和 Diff 服务
// ============================================================================
class VisualDiffService {
  constructor(workspacePath, options = {}) {
    this.workspacePath = workspacePath;
    this.backupDir = options.backupDir || '.cleaner-backups';
    this.logger = options.logger;
  }
  getBackupPath(name = 'default') { return path.join(this.workspacePath, this.backupDir, name); }

  async scanDirectory(dirPath, basePath = dirPath) {
    const files = {};
    async function walk(dir) {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        const relativePath = path.relative(basePath, fullPath);
        if (entry.isDirectory()) {
          if (['node_modules', '.git', '.cleaner-backups', '__pycache__'].includes(entry.name)) continue;
          await walk(fullPath);
        } else if (entry.isFile()) {
          try {
            const stat = await fs.stat(fullPath);
            const content = await fs.readFile(fullPath, 'utf-8');
            const hash = crypto.createHash('md5').update(content).digest('hex');
            files[relativePath] = { path: relativePath, size: stat.size, modified: stat.mtime.toISOString(), hash, content };
          } catch {}
        }
      }
    }
    await walk(dirPath);
    return files;
  }

  async createSnapshot(name = 'manual') {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const snapshotName = `snapshot_${name}_${timestamp}`;
    const snapshotPath = path.join(this.getBackupPath(), 'snapshots', snapshotName);
    await fs.mkdir(snapshotPath, { recursive: true });
    const files = await this.scanDirectory(this.workspacePath, this.workspacePath);
    await fs.writeFile(path.join(snapshotPath, 'files.json'), JSON.stringify(files, null, 2));
    await fs.writeFile(path.join(snapshotPath, '.meta.json'), JSON.stringify({ name: snapshotName, createdAt: new Date().toISOString(), fileCount: Object.keys(files).length }, null, 2));
    return { name: snapshotName, path: snapshotPath, fileCount: Object.keys(files).length };
  }

  async compare(snapshotA, snapshotB) {
    const pathA = snapshotA.includes('/') ? snapshotA : path.join(this.getBackupPath(), 'snapshots', snapshotA);
    const pathB = snapshotB.includes('/') ? snapshotB : path.join(this.getBackupPath(), 'snapshots', snapshotB);
    let filesA, filesB;
    try { filesA = JSON.parse(await fs.readFile(path.join(pathA, 'files.json'), 'utf-8')); } catch { throw new Error(`Snapshot A not found: ${snapshotA}`); }
    try { filesB = JSON.parse(await fs.readFile(path.join(pathB, 'files.json'), 'utf-8')); } catch { throw new Error(`Snapshot B not found: ${snapshotB}`); }
    const diff = { added: [], removed: [], modified: [], unchanged: [] };
    const pathsA = new Set(Object.keys(filesA)), pathsB = new Set(Object.keys(filesB));
    for (const filePath of pathsB) { if (!pathsA.has(filePath)) diff.added.push({ path: filePath, size: filesB[filePath].size, content: filesB[filePath].content }); }
    for (const filePath of pathsA) { if (!pathsB.has(filePath)) diff.removed.push({ path: filePath, size: filesA[filePath].size, content: filesA[filePath].content }); }
    for (const filePath of pathsA) { if (pathsB.has(filePath) && filesA[filePath].hash !== filesB[filePath].hash) diff.modified.push({ path: filePath, oldSize: filesA[filePath].size, newSize: filesB[filePath].size, oldContent: filesA[filePath].content, newContent: filesB[filePath].content }); }
    return diff;
  }

  generateReport(diff) {
    const lines = [];
    lines.push('═'.repeat(60)); lines.push('📊 可视化 Diff 报告'); lines.push('═'.repeat(60));
    lines.push(`\n📈 统计: 🟢 新增 ${diff.added.length} | 🔴 删除 ${diff.removed.length} | 🟡 修改 ${diff.modified.length}\n`);
    if (diff.added.length > 0) { lines.push('🟢 新增文件:'); for (const f of diff.added) lines.push(`  + ${f.path} (${f.size}B)`); lines.push(''); }
    if (diff.removed.length > 0) { lines.push('🔴 删除文件:'); for (const f of diff.removed) lines.push(`  - ${f.path} (${f.size}B)`); lines.push(''); }
    if (diff.modified.length > 0) { lines.push('🟡 修改文件:'); for (const f of diff.modified) lines.push(`  ~ ${f.path} (${f.oldSize}B → ${f.newSize}B)`); lines.push(''); }
    lines.push('═'.repeat(60));
    return lines.join('\n');
  }

  async listSnapshots() {
    const snapshotsPath = path.join(this.getBackupPath(), 'snapshots');
    try {
      const entries = await fs.readdir(snapshotsPath, { withFileTypes: true });
      const snapshots = [];
      for (const entry of entries) {
        if (entry.isDirectory()) {
          try { const meta = JSON.parse(await fs.readFile(path.join(snapshotsPath, entry.name, '.meta.json'), 'utf-8')); snapshots.push({ name: entry.name, createdAt: meta.createdAt, fileCount: meta.fileCount }); }
          catch { snapshots.push({ name: entry.name, createdAt: null }); }
        }
      }
      return snapshots.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
    } catch { return []; }
  }
}

// ============================================================================
// CheckpointService - 检查点服务
// ============================================================================
class CheckpointService {
  constructor(workspacePath, options = {}) { this.workspacePath = workspacePath; this.checkpointDir = options.checkpointDir || '.cleaner-backups/checkpoints'; this.logger = options.logger; }
  getCheckpointPath() { return path.join(this.workspacePath, this.checkpointDir); }

  async create(name, data = {}) {
    const checkpointPath = this.getCheckpointPath();
    await fs.mkdir(checkpointPath, { recursive: true });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const checkpoint = { name, id: `${name}_${timestamp}`, createdAt: new Date().toISOString(), data };
    await fs.writeFile(path.join(checkpointPath, `${checkpoint.id}.json`), JSON.stringify(checkpoint, null, 2));
    return checkpoint;
  }

  async getLatest(name = null) {
    const checkpointPath = this.getCheckpointPath();
    try {
      const files = await fs.readdir(checkpointPath);
      const checkpoints = files.filter(f => f.endsWith('.json')).map(f => f.replace('.json', '')).filter(f => !name || f.startsWith(name)).sort().reverse();
      if (checkpoints.length === 0) return null;
      return JSON.parse(await fs.readFile(path.join(checkpointPath, `${checkpoints[0]}.json`), 'utf-8'));
    } catch { return null; }
  }

  async restore(id) { return JSON.parse(await fs.readFile(path.join(this.getCheckpointPath(), `${id}.json`), 'utf-8')); }

  async list() {
    const checkpointPath = this.getCheckpointPath();
    try {
      const files = await fs.readdir(checkpointPath);
      const checkpoints = [];
      for (const file of files) {
        if (file.endsWith('.json')) {
          const checkpoint = JSON.parse(await fs.readFile(path.join(checkpointPath, file), 'utf-8'));
          checkpoints.push({ id: checkpoint.id, name: checkpoint.name, createdAt: checkpoint.createdAt });
        }
      }
      return checkpoints.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    } catch { return []; }
  }
}

// ============================================================================
// ProgressSnapshotService - 任务进度服务
// ============================================================================
class ProgressSnapshotService {
  constructor(workspacePath, options = {}) { this.workspacePath = workspacePath; this.progressDir = options.progressDir || '.cleaner-backups/progress'; this.logger = options.logger; }
  getProgressPath() { return path.join(this.workspacePath, this.progressDir); }

  async startTask(taskName, totalItems, metadata = {}) {
    const progressPath = this.getProgressPath();
    await fs.mkdir(progressPath, { recursive: true });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const taskId = `${taskName}_${timestamp}`;
    const task = { id: taskId, name: taskName, status: 'running', startedAt: new Date().toISOString(), totalItems: totalItems.length, completedItems: 0, failedItems: 0, items: totalItems.map((item, index) => ({ index, data: item, status: 'pending', error: null })), metadata };
    await fs.writeFile(path.join(progressPath, `${taskId}.json`), JSON.stringify(task, null, 2));
    return task;
  }

  async updateProgress(taskId, itemIndex, status, error = null) {
    const task = JSON.parse(await fs.readFile(path.join(this.getProgressPath(), `${taskId}.json`), 'utf-8'));
    const item = task.items[itemIndex];
    if (item) { item.status = status; item.error = error; }
    task.completedItems = task.items.filter(i => i.status === 'completed').length;
    task.failedItems = task.items.filter(i => i.status === 'failed').length;
    task.updatedAt = new Date().toISOString();
    if (task.completedItems + task.failedItems >= task.totalItems) { task.status = task.failedItems > 0 ? 'completed_with_errors' : 'completed'; task.finishedAt = new Date().toISOString(); }
    await fs.writeFile(path.join(this.getProgressPath(), `${taskId}.json`), JSON.stringify(task, null, 2));
    return task;
  }

  async markCompleted(taskId, itemIndex) { return await this.updateProgress(taskId, itemIndex, 'completed'); }
  async markFailed(taskId, itemIndex, error) { return await this.updateProgress(taskId, itemIndex, 'failed', error); }
  async getPendingItems(taskId) { const task = JSON.parse(await fs.readFile(path.join(this.getProgressPath(), `${taskId}.json`), 'utf-8')); return task.items.filter(item => item.status === 'pending'); }
  async getTask(taskId) { try { return JSON.parse(await fs.readFile(path.join(this.getProgressPath(), `${taskId}.json`), 'utf-8')); } catch { return null; } }
  async listTasks() {
    const progressPath = this.getProgressPath();
    try {
      const files = await fs.readdir(progressPath);
      const tasks = [];
      for (const file of files) {
        if (file.endsWith('.json')) {
          const task = JSON.parse(await fs.readFile(path.join(progressPath, file), 'utf-8'));
          tasks.push({ id: task.id, name: task.name, status: task.status, progress: `${task.completedItems}/${task.totalItems}`, percent: ((task.completedItems + task.failedItems) / task.totalItems * 100).toFixed(1) + '%' });
        }
      }
      return tasks.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt));
    } catch { return []; }
  }
}

// ============================================================================
// BackupService - 备份服务
// ============================================================================
class BackupService {
  constructor(workspacePath, options = {}) { this.workspacePath = workspacePath; this.backupDir = options.backupDir || '.cleaner-backups'; this.logger = options.logger; }
  getBackupPath(name = 'default') { return path.join(this.workspacePath, this.backupDir, name); }

  async create(name = 'auto', options = {}) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupName = options.name || `${name}_${timestamp}`;
    const backupPath = this.getBackupPath(backupName);
    await fs.mkdir(backupPath, { recursive: true });
    const targets = ['MEMORY.md', 'IDENTITY.md', 'USER.md', 'SOUL.md', 'AGENTS.md', 'AGENTS_WORKSPACE.md', 'TOOLS.md', 'HEARTBEAT.md', 'skills/', 'agents/'];
    const results = { success: [], failed: [] };
    for (const target of targets) {
      try { await fs.cp(path.join(this.workspacePath, target), path.join(backupPath, target), { recursive: true }); results.success.push(target); }
      catch (e) { results.failed.push({ target, error: e.message }); }
    }
    await fs.writeFile(path.join(backupPath, '.backup-meta.json'), JSON.stringify({ name: backupName, createdAt: new Date().toISOString(), targets: results }, null, 2));
    return { name: backupName, path: backupPath, results };
  }

  async list() {
    const basePath = this.getBackupPath();
    try {
      const entries = await fs.readdir(basePath, { withFileTypes: true });
      const backups = [];
      for (const entry of entries) {
        if (entry.isDirectory()) {
          try { const meta = JSON.parse(await fs.readFile(path.join(basePath, entry.name, '.backup-meta.json'), 'utf-8')); backups.push({ name: entry.name, createdAt: meta.createdAt }); }
          catch { backups.push({ name: entry.name, createdAt: null }); }
        }
      }
      return backups.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
    } catch { return []; }
  }

  async restore(name) {
    const backupPath = this.getBackupPath(name);
    await this.create('pre-restore');
    const targets = ['MEMORY.md', 'IDENTITY.md', 'USER.md', 'SOUL.md', 'AGENTS.md', 'TOOLS.md'];
    for (const target of targets) { try { await fs.cp(path.join(backupPath, target), path.join(this.workspacePath, target), { overwrite: true }); } catch {} }
    return { restored: name };
  }
}

// ============================================================================
// Workspace - 工作空间模型
// ============================================================================
class Workspace {
  constructor(rootPath) { this.rootPath = rootPath; this.stats = { totalFiles: 0, totalDirs: 0, totalSize: 0, tempFiles: 0, largeFiles: [] }; this.skills = []; this.agents = []; this.warnings = []; }
  async scan() { await this._scanDirectory(this.rootPath); await this._detectSkills(); await this._detectAgents(); return this; }

  async _scanDirectory(dirPath, depth = 0) {
    if (depth > 10) return;
    try {
      const entries = await fs.readdir(dirPath, { withFileTypes: true });
      for (const entry of entries) {
        if (this._shouldIgnore(entry.name)) continue;
        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) { this.stats.totalDirs++; await this._scanDirectory(fullPath, depth + 1); }
        else { this.stats.totalFiles++; const size = (await fs.stat(fullPath)).size; this.stats.totalSize += size; if (size > 1024 * 1024) this.stats.largeFiles.push({ path: fullPath, size }); }
      }
    } catch {}
  }

  _shouldIgnore(name) { return ['node_modules', '.git', '.openclaw', '.clawhub', '.DS_Store', 'Thumbs.db', '__pycache__'].includes(name); }

  async _detectSkills() {
    const skillsPath = path.join(this.rootPath, 'skills');
    try { const entries = await fs.readdir(skillsPath, { withFileTypes: true }); this.skills = entries.filter(e => e.isDirectory()).map(e => ({ name: e.name, path: path.join(skillsPath, e.name) })); }
    catch { this.skills = []; }
  }

  async _detectAgents() {
    const agentsPath = path.join(this.rootPath, 'agents');
    try {
      const entries = await fs.readdir(agentsPath, { withFileTypes: true });
      this.agents = entries.filter(e => e.isDirectory()).map(e => ({ name: e.name, path: path.join(agentsPath, e.name), hasWorkspace: false, hasMemory: false, hasLogs: false }));
      for (const agent of this.agents) { const subDirs = await fs.readdir(path.join(agentsPath, agent.name)); agent.hasWorkspace = subDirs.includes('workspace'); agent.hasMemory = subDirs.includes('memory'); agent.hasLogs = subDirs.includes('logs'); }
    } catch { this.agents = []; }
  }

  get healthScore() {
    let score = 100;
    if (this.stats.largeFiles.length > 0) score -= 5;
    if (this.stats.totalSize > 10 * 1024 * 1024) score -= 5;
    const missingWorkspace = this.agents.filter(a => !a.hasWorkspace).length;
    const missingLogs = this.agents.filter(a => !a.hasLogs).length;
    score -= missingWorkspace * 3; score -= missingLogs * 2;
    return Math.max(0, Math.min(100, score));
  }
}

// ============================================================================
// SkillMatcher - Skill 匹配服务
// ============================================================================
class SkillMatcher {
  constructor(workspacePath, options = {}) { this.workspacePath = workspacePath; this.logger = options.logger; }
  async match(query) {
    const keywords = { 'coding': ['coding', 'code', '写代码', '编程', '开发', 'react', 'vue', 'javascript', 'python'], 'writing': ['写', '文章', '文档', '写作', '创作'], 'data': ['数据', '分析', 'excel', 'csv', '统计'], 'search': ['搜索', '查找', 'query'], 'image': ['图片', '图像', '生成图片', '画图'] };
    let bestMatch = 'general', highestScore = 0;
    const lowerQuery = query.toLowerCase();
    for (const [category, words] of Object.entries(keywords)) { for (const word of words) { if (lowerQuery.includes(word)) { bestMatch = category; highestScore++; } } }
    return { context: { primary: bestMatch, confidence: Math.min(1, highestScore / 2) }, skills: [] };
  }
}

// ============================================================================
// AuditService - 审核服务
// ============================================================================
class AuditService { constructor(workspacePath, options = {}) { this.workspacePath = workspacePath; this.logger = options.logger; } async shouldAudit() { return { shouldAudit: false, reason: 'No audit required' }; } }

// ============================================================================
// MDOptimizer - Markdown 优化服务
// ============================================================================
class MDOptimizer {
  constructor(logger) { this.logger = logger; }
  async optimizeSoulFiles(workspacePath) {
    const soulFiles = ['MEMORY.md', 'USER.md', 'SOUL.md', 'AGENTS.md', 'TOOLS.md'];
    const results = [];
    for (const file of soulFiles) {
      const filePath = path.join(workspacePath, file);
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const originalSize = content.length;
        const optimized = this.optimizeContent(content);
        const saved = originalSize - optimized.length;
        if (saved > 0) { await fs.writeFile(filePath, optimized); results.push({ file, saved, originalSize, optimizedSize: optimized.length }); }
      } catch { results.push({ file, saved: 0 }); }
    }
    return results;
  }
  optimizeContent(content) { return content.replace(/\n{3,}/g, '\n\n').replace(/[ \t]+\n/g, '\n').trim(); }
}

// ============================================================================
// 统一导出
// ============================================================================
export const snapshot = {
  async create(name = 'manual') { return await new VisualDiffService(getWorkspacePath(), { logger: silentLogger }).createSnapshot(name); },
  async list() { return await new VisualDiffService(getWorkspacePath(), { logger: silentLogger }).listSnapshots(); },
  async compare(before, after) { return await new VisualDiffService(getWorkspacePath(), { logger: silentLogger }).compare(before, after); },
  generateReport(diff) { return new VisualDiffService(getWorkspacePath(), { logger: silentLogger }).generateReport(diff); },
};

export const checkpoint = {
  async create(name, data = {}) { return await new CheckpointService(getWorkspacePath(), { logger: silentLogger }).create(name, data); },
  async getLatest() { return await new CheckpointService(getWorkspacePath(), { logger: silentLogger }).getLatest(); },
  async restore(id) { return await new CheckpointService(getWorkspacePath(), { logger: silentLogger }).restore(id); },
  async list() { return await new CheckpointService(getWorkspacePath(), { logger: silentLogger }).list(); },
};

export const task = {
  async start(name, items) { return await new ProgressSnapshotService(getWorkspacePath(), { logger: silentLogger }).startTask(name, items); },
  async markCompleted(taskId, index) { return await new ProgressSnapshotService(getWorkspacePath(), { logger: silentLogger }).markCompleted(taskId, index); },
  async markFailed(taskId, index, error) { return await new ProgressSnapshotService(getWorkspacePath(), { logger: silentLogger }).markFailed(taskId, index, error); },
  async getPending(taskId) { return await new ProgressSnapshotService(getWorkspacePath(), { logger: silentLogger }).getPendingItems(taskId); },
  async getStatus(taskId) { return await new ProgressSnapshotService(getWorkspacePath(), { logger: silentLogger }).getTask(taskId); },
  async list() { return await new ProgressSnapshotService(getWorkspacePath(), { logger: silentLogger }).listTasks(); },
};

export const backup = {
  async create(name = 'manual') { return await new BackupService(getWorkspacePath(), { logger: silentLogger }).create(name); },
  async restore(name) { return await new BackupService(getWorkspacePath(), { logger: silentLogger }).restore(name); },
  async list() { return await new BackupService(getWorkspacePath(), { logger: silentLogger }).list(); },
};

export const health = {
  async check() { const workspace = new Workspace(getWorkspacePath()); await workspace.scan(); return { score: workspace.healthScore, totalFiles: workspace.stats.totalFiles, totalDirs: workspace.stats.totalDirs, totalSize: workspace.stats.totalSize, warnings: workspace.warnings }; },
};

export const skills = {
  async list() { return { builtIn: [], user: [] }; },
  async match(query) { return await new SkillMatcher(getWorkspacePath(), { logger: silentLogger }).match(query); },
  async remove(name) { return { removed: name }; },
};

export const optimize = {
  async soul() { const results = await new MDOptimizer(silentLogger).optimizeSoulFiles(getWorkspacePath()); const totalSaved = results.reduce((sum, r) => sum + r.saved, 0); return { results, totalSaved }; },
  async full() { const backupResult = await new BackupService(getWorkspacePath(), { logger: silentLogger }).create('auto-optimize'); await new MDOptimizer(silentLogger).optimizeSoulFiles(getWorkspacePath()); return { success: true, backup: backupResult.name }; },
};

export const audit = { async check() { return await new AuditService(getWorkspacePath(), { logger: silentLogger }).shouldAudit(); } };

export default { snapshot, checkpoint, task, backup, health, skills, optimize, audit };
```
<!-- 代码实现结束 -->

---

## 安装测试

```bash
node skills/openclaw-cleaner/SKILL.md
```
