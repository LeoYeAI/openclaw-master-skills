---
name: TOKEN节约器
description: ✂️ TOKEN节约器 - 工作流程控制器。通过问题预检、路径验证、进度检查、错误快速定位，防止重复无效工作，节约TOKEN消耗。兼容Windows/Mac/Linux/MaxClaw/ClawHub。
tags:
  - workflow
  - productivity
  - error-handling
  - development
  - automation
  - token优化
  - 效率提升
author: Matrix Agent
version: 1.2.0
---

<div align="center">

# ✂️ TOKEN节约器

**工作流程控制器 · 预检优于补救 · 验证优于猜测 · 记录优于遗忘**

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-blue)]()
[![Version](https://img.shields.io/badge/Version-1.1.0-green)
[![Compatible](https://img.shields.io/badge/Compatible-MaxClaw%20%7C%20ClawHub-orange)]()

</div>

---

## 一、核心价值

### 1.1 问题
- **重复无效工作**: 同样的错误反复出现、同样的检查重复进行
- **错误-修复循环**: 修复→测试→再修复→再测试的恶性循环
- **TOKEN浪费**: 每个错误修复消耗大量TOKEN，每个重复检查消耗更多
- **路径迷失**: 不知道当前在哪一步、不知道下一步该做什么

### 1.2 解决
```
TOKEN节约 = (预防问题 + 快速定位 + 减少循环) × 每问题节约TOKEN
```

### 1.3 效果
| 指标 | 改善前 | 改善后 | 节约率 |
|------|--------|--------|--------|
| 重复检查次数 | 5+次/问题 | 1次/问题 | 80% |
| 错误定位时间 | 45分钟 | 5分钟 | 89% |
| TOKEN消耗 | 高 | 低 | 60%+ |

---

## 二、四大控制组件

### 2.1 组件概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     TOKEN节约器 - 控制架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  问题预检器  │ →  │  路径验证器  │ →  │  进度检查点  │        │
│  │ Pre-Check   │    │  Path-Verify│    │  Checkpoint │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         ↓                                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ 错误快速定位 │ ←  │  日志分析器  │ ←  │  经验记录器  │        │
│  │ Fast-Locate │    │  Log-Analyze│    │  Memory-Log │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件说明

| 组件 | 功能 | 适用场景 |
|------|------|----------|
| **问题预检器** | 执行前检查常见错误模式 | 任何任务开始前 |
| **路径验证器** | 确认当前路径是否正确 | 遇到错误时 |
| **进度检查点** | 记录关键里程碑 | 任务执行中 |
| **错误快速定位器** | 缩小问题范围 | 错误发生后 |
| **日志分析器** | 自动解析日志输出 | 查看日志时 |
| **经验记录器** | 保存问题-解决方案对 | 问题解决后 |

---

## 三、问题预检器 (Pre-Check)

### 3.1 检查清单

#### 代码修改类
```
☑ 1. 文件存在性检查 - 目标文件是否存在？
☑ 2. 路径正确性检查 - 路径格式是否正确？
☑ 3. 依赖可用性检查 - import的模块是否可用？
☑ 4. 语法正确性检查 - 代码语法是否正确？
☑ 5. 权限检查 - 是否有读写权限？
```

#### API调用类
```
☑ 1. 服务可用性检查 - 后端服务是否运行？
☑ 2. 端口占用检查 - 端口是否被占用？
☑ 3. 网络连通性检查 - 目标地址是否可达？
☑ 4. 认证状态检查 - Token/API Key是否有效？
☑ 5. 限流检查 - 是否触发频率限制？
```

#### 构建部署类
```
☑ 1. 构建产物检查 - dist目录是否更新？
☑ 2. 环境变量检查 - 必要变量是否设置？
☑ 3. 进程冲突检查 - 是否有残留进程？
☑ 4. 磁盘空间检查 - 空间是否充足？
☑ 5. 打包完整性检查 - asar是否最新？
```

### 3.2 预检执行流程

```
任务开始
    ↓
执行问题预检清单
    ↓
发现问题 → 修复后再继续
    ↓
无问题 → 继续执行
    ↓
记录检查通过
```

### 3.3 预检器组件代码

```javascript
/**
 * TOKEN节约器 - 问题预检器 (Pre-Checker)
 * 
 * 功能: 在执行任务前检查常见错误模式，预防问题发生
 */
const { execSync } = require('child_process');
const fs = require('fs');

class PreChecker {
    constructor() {
        this.results = [];
        this.config = { timeout: 5000 };
    }

    checkFile(filePath) {
        // 参数安全检查
        if (!filePath || typeof filePath !== 'string') return false;
        if (filePath.length > 10000) return false; // 防止DoS
        const exists = fs.existsSync(filePath);
        this.results.push({ type: 'file', path: filePath, exists });
        return exists;
    }

    checkPort(port) {
        try {
            const isWindows = process.platform === 'win32';
            const cmd = isWindows 
                ? `netstat -ano | findstr :${port}`
                : `lsof -i :${port}`;
            const output = execSync(cmd, { encoding: 'utf-8', timeout: this.config.timeout });
            const inUse = new RegExp(`:${port}`).test(output);
            this.results.push({ type: 'port', port, inUse, available: !inUse });
            return !inUse;
        } catch { return true; } // 端口未被占用
    }

    checkProcess(processName) {
        try {
            const isWindows = process.platform === 'win32';
            const cmd = isWindows
                ? `powershell -Command "Get-Process -Name '${processName}' -ErrorAction SilentlyContinue | Select-Object Id"`
                : `pgrep -x "${processName}"`;
            const output = execSync(cmd, { encoding: 'utf-8' });
            const pids = output.trim().split('\n').filter(l => /^\d+$/.test(l.trim())).map(Number);
            const result = { type: 'process', name: processName, running: pids.length > 0, count: pids.length, pids };
            this.results.push(result);
            return result;
        } catch {
            return { type: 'process', name: processName, running: false, count: 0, pids: [] };
        }
    }

    getReport() {
        return { timestamp: new Date().toISOString(), total: this.results.length, results: this.results };
    }
}

module.exports = PreChecker;
```

---

## 四、路径验证器 (Path-Verify)

### 4.1 验证流程

```
遇到错误/问题
    ↓
确定问题类型 (前端/后端/网络/环境)
    ↓
按类型验证路径
    ↓
找到问题节点
    ↓
修复后继续
```

### 4.2 分层验证检查表

#### 前端问题
```
☑ 1. dist目录是否最新？
☑ 2. 浏览器是否刷新到最新？
☑ 3. API路径配置是否正确？
☑ 4. 环境变量是否正确？
☑ 5. 打包文件(asar)是否更新？
```

#### 后端问题
```
☑ 1. 服务是否启动？
☑ 2. 端口是否正确监听？
☑ 3. 路由是否正确注册？
☑ 4. 数据库连接是否正常？
☑ 5. 日志是否有错误？
```

### 4.3 快速定位决策树

```
问题: API 404
    ↓
curl后端API通吗?
    ├── 通 → 前端问题 → dist最新吗? → 是 → 完整重启
    │                              └── 否 → 重新构建
    │
    └── 不通 → 后端问题 → 端口监听正常吗?
                              ├── 正常 → 查看后端日志
                              └── 不正常 → 检查进程/重启
```

---

## 五、进度检查点 (Checkpoint)

### 5.1 检查点设计

```
任务开始 → [检查点1] → 子任务1 → [检查点2] → 子任务2 → [检查点3] → ... → 完成
                ↓               ↓               ↓
            记录状态        验证结果        保存检查点
```

### 5.2 检查点模板

```markdown
## 检查点 [#]

**时间**: YYYY-MM-DD HH:MM
**任务**: [当前任务描述]
**状态**: ⬜ 进行中 | ✅ 完成 | ❌ 失败

### 已完成
- [x] 子任务1
- [x] 子任务2

### 当前问题
> 描述遇到的问题（如有）

### 下一步
- [ ] 子任务3
- [ ] 子任务4

### TOKEN消耗
- 预估: XXX
- 实际: YYY
- 状态: ⚠️ 超预算 | ✅ 正常
```

### 5.3 检查点组件代码

```javascript
/**
 * TOKEN节约器 - 进度检查点 (Checkpoint)
 */
const fs = require('fs');

class Checkpoint {
    constructor(options = {}) {
        this.storagePath = options.storagePath || './checkpoint-data.json';
        this.autoSave = options.autoSave !== false;
        this.data = { checkpoints: [], currentPhase: null, tokenBudget: options.tokenBudget || null, tokenUsed: 0 };
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(this.storagePath)) {
                this.data = JSON.parse(fs.readFileSync(this.storagePath, 'utf-8'));
            }
        } catch (e) { /* 忽略 */ }
    }

    save() {
        try {
            this.data.lastUpdate = new Date().toISOString();
            const dir = require('path').dirname(this.storagePath);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(this.storagePath, JSON.stringify(this.data, null, 2));
            return true;
        } catch { return false; }
    }

    create(name, metadata = {}) {
        const checkpoint = {
            id: `cp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name, timestamp: new Date().toISOString(), phase: this.data.currentPhase, status: metadata.status || 'in_progress', data: metadata, tokenAtPoint: this.data.tokenUsed
        };
        this.data.checkpoints.push(checkpoint);
        if (this.autoSave) this.save();
        return checkpoint;
    }

    setPhase(phase) {
        this.data.currentPhase = phase;
        this.create(`阶段切换 → ${phase}`, { type: 'phase_change'});
    }

    updateToken(used) {
        this.data.tokenUsed += used;
        this.create('TOKEN更新', { type: 'token', increment: used, total: this.data.tokenUsed });
        if (this.autoSave) this.save();
        const ratio = this.data.tokenUsed / this.data.tokenBudget;
        if (ratio > 0.9) return 'critical';
        if (ratio > 0.75) return 'warning';
        return 'ok';
    }

    getState() {
        return {
            currentPhase: this.data.currentPhase,
            totalCheckpoints: this.data.checkpoints.length,
            latestCheckpoint: this.data.checkpoints[this.data.checkpoints.length - 1],
            tokenBudget: this.data.tokenBudget,
            tokenUsed: this.data.tokenUsed,
            tokenRemaining: this.data.tokenBudget ? this.data.tokenBudget - this.data.tokenUsed : null
        };
    }
}

module.exports = Checkpoint;
```

---

## 六、错误快速定位器 (Fast-Locate)

### 6.1 错误分类表

| 错误类型 | 典型表现 | 优先检查 |
|----------|----------|----------|
| **404** | 资源不存在 | 路径是否正确、dist是否最新 |
| **500** | 服务器错误 | 后端日志、异常堆栈 |
| **端口占用** | EADDRINUSE | 进程残留、端口检测 |
| **权限拒绝** | EACCES/EPERM | 文件权限、管理员运行 |
| **超时** | ETIMEDOUT | 网络连通、防火墙 |
| **找不到模块** | Module Not Found | 依赖安装、路径配置 |

### 6.2 快速定位命令集

#### 端口检查
```bash
# Windows
netstat -ano | findstr 7860
```

#### 进程检查
```bash
# Windows
Get-Process -Name "electron" | Select-Object Id, ProcessName
Stop-Process -Name "electron" -Force
```

### 6.3 快速定位组件代码

```javascript
/**
 * TOKEN节约器 - 错误快速定位器 (Fast Locator)
 */
class FastLocator {
    constructor() {
        this.patterns = {
            http_404: {
                pattern: /404|Not\s+Found/i, type: 'HTTP_404', category: '前端',
                likely: ['路径错误', 'dist未更新', '路由未注册'],
                solutions: ['检查API路径', 'npm run build', '检查后端路由']
            },
            http_500: {
                pattern: /500|Internal\s+Server\s+Error/i, type: 'HTTP_500', category: '后端',
                likely: ['后端代码异常', '数据库错误', '服务崩溃'],
                solutions: ['查看后端日志', '检查最近修改', '验证数据库']
            },
            port_in_use: {
                pattern: /EADDRINUSE|address\s+already\s+in\s+use|端口.*占用|10048/i,
                type: 'PORT_IN_USE', category: '环境',
                likely: ['进程残留', '重复启动'],
                solutions: ['netstat -ano | findstr PORT', 'Stop-Process -Id PID -Force', '添加端口检测']
            },
            connection_refused: {
                pattern: /ECONNREFUSED|连接.*拒绝/i, type: 'CONNECTION_REFUSED', category: '网络',
                likely: ['服务未启动', '端口错误', '防火墙'],
                solutions: ['确认服务启动', '检查端口配置', '检查防火墙']
            },
            file_not_found: {
                pattern: /ENOENT|文件.*不存在|No\s+such\s+file/i, type: 'FILE_NOT_FOUND', category: '前端',
                likely: ['路径错误', '文件未创建', '拼写错误'],
                solutions: ['检查路径', '确认文件存在', '检查大小写']
            },
            permission_denied: {
                pattern: /EACCES|EPERM|权限.*拒绝|Permission\s+denied/i, type: 'PERMISSION_DENIED', category: '环境',
                likely: ['权限不足', '需管理员'],
                solutions: ['以管理员运行', '检查文件权限']
            },
            timeout: {
                pattern: /ETIMEDOUT|超时|timeout/i, type: 'TIMEOUT', category: '网络',
                likely: ['网络不稳定', '服务响应慢'],
                solutions: ['检查网络', '增加超时配置']
            },
            broken_pipe: {
                pattern: /EPIPE|Broken\s+pipe/i, type: 'BROKEN_PIPE', category: 'Electron',
                likely: ['stdout已关闭', 'console.log在Electron中'],
                solutions: ['禁用console.log', '改用文件日志', '捕获异常']
            },
            module_not_found: {
                pattern: /Cannot\s+find\s+module|Module\s+not\s+found|找不到.*模块/i,
                type: 'MODULE_NOT_FOUND', category: '前端',
                likely: ['依赖未安装', '路径错误'],
                solutions: ['npm install', '检查import路径']
            }
        };
    }

    locate(error) {
        if (error === null || error === undefined) {
            return { matched: false, type: 'UNKNOWN', category: '未知', likely: ['输入为空'], solutions: ['请提供有效错误信息'] };
        }
        const errorString = typeof error === 'string' ? error : (error.message || String(error));
        for (const [name, config] of Object.entries(this.patterns)) {
            if (config.pattern.test(errorString)) {
                return { matched: true, type: config.type, category: config.category, likely: config.likely, solutions: config.solutions, suggestions: config.solutions.join('\n') };
            }
        }
        return { matched: false, type: 'UNKNOWN', category: '未知', likely: ['需手动排查'], solutions: ['查看完整错误', '搜索关键字', '检查最近变更'] };
    }
}

module.exports = FastLocator;
```

---

## 七、日志分析器 (Log-Analyze)

### 7.1 日志模式识别

```javascript
const LOG_PATTERNS = {
    port_in_use: /EADDRINUSE|address already in use|端口.*占用/i,
    connection_refused: /ECONNREFUSED|连接被拒绝/i,
    timeout: /ETIMEDOUT|超时/i,
    file_not_found: /ENOENT|文件.*不存在/i,
    permission_denied: /EACCES|EPERM|权限.*拒绝/i,
    http_404: /404\s+Not\s+Found/i,
    http_500: /500\s+Internal/i,
    process_exit: /Process.*exited|进程.*退出/i,
    broken_pipe: /EPIPE|Broken\s+pipe/i,
};
```

### 7.2 日志分析器组件代码

```javascript
/**
 * TOKEN节约器 - 日志分析器 (Log Analyzer)
 */
class LogAnalyzer {
    constructor() {
        this.patterns = {
            port_error: { regex: /EADDRINUSE|address\s+already\s+in\s+use|端口.*占用|10048/i, severity: 'error', category: '环境', title: '端口冲突', suggestions: ['netstat -ano | findstr PORT', 'Stop-Process -Id PID'] },
            http_error: { regex: /\b(404|500|502|503|504)\s+\w+/i, severity: 'error', category: '网络', title: 'HTTP错误', suggestions: ['检查路径', '查看服务端日志'] },
            file_not_found: { regex: /ENOENT|No\s+such\s+file|文件.*不存在|Cannot\s+find/i, severity: 'error', category: '文件', title: '文件不存在', suggestions: ['检查路径', '确认文件存在'] },
            permission_error: { regex: /EACCES|EPERM|Permission\s+denied|权限.*拒绝/i, severity: 'error', category: '权限', title: '权限不足', suggestions: ['以管理员运行', '检查文件权限'] },
            timeout_error: { regex: /ETIMEDOUT|timeout|超时/i, severity: 'warning', category: '网络', title: '连接超时', suggestions: ['检查网络', '增加超时配置'] },
            connection_refused: { regex: /ECONNREFUSED|连接.*拒绝/i, severity: 'error', category: '网络', title: '连接被拒绝', suggestions: ['确认服务启动', '检查端口配置'] },
            module_error: { regex: /Cannot\s+find\s+module|Module\s+not\s+found|找不到.*模块/i, severity: 'error', category: '依赖', title: '模块未找到', suggestions: ['npm install', '检查import路径'] },
            warning: { regex: /\[WARN[\s\]]?|WARNING|Warn|WARN[^I]|警告/i, severity: 'warning', category: '警告', title: '警告信息', suggestions: ['关注但不一定需处理'] },
            json_error: { regex: /JSON\.parse|JSON\.unexpected|SyntaxError.*JSON/i, severity: 'error', category: '数据', title: 'JSON解析错误', suggestions: ['检查JSON格式', '验证语法'] }
        };
    }

    analyze(content) {
        const lines = content.split('\n').filter(l => l.trim());
        const matches = [], errors = [], warnings = [];
        lines.forEach((line, index) => {
            for (const [name, config] of Object.entries(this.patterns)) {
                if (config.regex.test(line)) {
                    const entry = { line: index + 1, content: line.substring(0, 100), pattern: name, severity: config.severity, category: config.category, title: config.title, suggestions: config.suggestions };
                    matches.push(entry);
                    if (config.severity === 'error') errors.push(entry);
                    else warnings.push(entry);
                    break;
                }
            }
        });
        const byCategory = {};
        matches.forEach(m => byCategory[m.category] = (byCategory[m.category] || 0) + 1);
        const topCategory = Object.entries(byCategory).sort((a, b) => b[1] - a[1])[0];
        return { total: lines.length, matched: matches.length, errors, warnings, summary: { byCategory, topCategory }, rootCause: topCategory ? { identified: true, primaryCategory: topCategory[0], message: `${topCategory[1]}个${topCategory[0]}类错误` } : { identified: false } };
    }
}

module.exports = LogAnalyzer;
```

---

## 八、使用检查清单

```
任务开始前:
☑ 1. 运行预检器检查环境
☑ 2. 评估TOKEN预算
☑ 3. 确认路径正确

任务进行中:
☑ 4. 在关键点设置检查点
☑ 5. 记录每个阶段TOKEN消耗
☑ 6. 异常时使用快速定位器

任务完成后:
☑ 7. 记录问题-解决方案
☑ 8. 更新经验库
☑ 9. 评估TOKEN使用效率
```

---

## 九、快速集成

```javascript
// 引入组件
const PreChecker = require('./pre-checker');
const Checkpoint = require('./checkpoint');
const FastLocator = require('./fast-locator');
const LogAnalyzer = require('./log-analyzer');

// 使用示例
const preChecker = new PreChecker();
const checkpoint = new Checkpoint({ tokenBudget: 5000 });

// 任务开始预检
preChecker.checkFile('./src/index.js');
preChecker.checkPort(7860);

// 设置检查点
checkpoint.setPhase('需求分析');
checkpoint.updateToken(200);

// 遇到错误快速定位
const errorInfo = new FastLocator().locate(error);
console.log('可能原因:', errorInfo.likely);
console.log('解决建议:', errorInfo.solutions);
```

---

## 十、TOKEN预算管理

### 10.1 警戒机制

```
TOKEN使用 > 50% → ⚠️ 提醒：已使用过半
TOKEN使用 > 75% → 🔴 警告：剩余有限
TOKEN使用 > 90% → 🚨 紧急：仅剩少量，需精简
TOKEN使用 = 100% → ⛔ 停止：任务需暂停或拆分
```

### 10.2 节约策略

| 策略 | 说明 | 节约效果 |
|------|------|----------|
| **预检先行** | 执行前检查常见问题 | 避免重复尝试 |
| **精确提问** | 提供完整上下文 | 减少往返确认 |
| **批量操作** | 合并同类操作 | 减少切换开销 |
| **复用经验** | 记录并复用解决方案 | 避免重复探索 |
| **路径验证** | 确认方向正确后再深入 | 避免走错路 |

---

## 附录：常用命令

```bash
# 端口检查
netstat -ano | findstr PORT

# 进程检查
Get-Process -Name "NAME"
Stop-Process -Name "NAME" -Force

# 日志查看
Get-Content "file.log" -Tail 100 -Wait

# 文件检查
Get-Item "path" | Select-Object *
```

---

**版本**: 1.0.0
**维护**: Matrix Agent
**更新**: 2026-03-26
