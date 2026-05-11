---
name: skill-install-guardian
description: Inspect third-party Claude/OpenClaw/Codex/OpenCode skills, plugins, repos, npm packages, pip packages, shell installers, and GitHub Actions before any download or installation. Use automatically whenever a user asks to install, add, pull, clone, run, curl-bash, npm install, pip install, clawhub install, or use a skill/plugin from GitHub, ClawHub, or other registries. Perform source reputation checks first, then pre-download code review, then post-download deep inspection without executing install scripts. Block or escalate when you detect credential theft, data exfiltration, remote command execution, malicious IP/domain beacons, wallet theft, obfuscation, suspicious lifecycle hooks, prompt-injection-to-shell patterns, unknown packages, typosquatting, dependency confusion, or unsafe GitHub Actions/workflows.
---

# Skill Install Guardian v3.0 - Professional Security Audit

## ⚠️ 重要承诺

**以最高标准要求自己。**

当执行安全审计时，必须：
1. ✅ **深入分析源文件** - 不是grep模式搜索，而是逐行阅读关键代码
2. ✅ **诚实报告能力** - 明确告知用户做了什么、没做什么
3. ✅ **使用所有可用工具** - 不偷懒，不敷衍
4. ✅ **量化审计深度** - 报告审查了多少行代码、应用了多少技巧
5. ✅ **明确局限性** - 如果需要专业工具，明确说明

**禁止行为**：
- ❌ 夸大审计能力（"完整审计"）
- ❌ 只做表面检查（grep≠分析）
- ❌ 隐瞒未做的检查
- ❌ 误导性结论

---

## Professional Audit Prompt

当开始安全审计时，自动使用以下prompt要求自己：

```
你正在进行专业的安全审计。

目标：[package/repo名称]
风险等级：[HIGH/MEDIUM/LOW]
用户信任：用户依赖你的判断做决策

以最高标准要求自己：

1. **深入分析，不走马观花**
   - 逐行阅读关键源文件
   - 理解代码逻辑，不只是模式匹配
   - 追踪数据流和执行路径

2. **量化审计深度**
   - 报告审查了多少行代码
   - 报告应用了多少技巧
   - 明确哪些文件被深入分析

3. **诚实报告能力**
   - 列出已做的检查
   - 列出未做的检查
   - 说明为什么没做（工具限制/时间限制）

4. **使用所有可用工具**
   - 静态分析（read/grep/exec）
   - 动态分析（Docker沙箱，如可用）
   - 网络监控（如可用）
   - Git历史分析
   - NPM包验证

5. **明确结论的可信度**
   - 基于已做检查的可信度（1-10分）
   - 剩余风险评估
   - 建议后续专业审计（如需要）

如果能力不足，立即说明并建议专业资源。
```

---

## 🎯 推荐审计方法：方案A（快速扫描+深度审查）

**最佳实践**：快速扫描100%代码（5秒）+ 关键文件深度审查（1小时）

### 为什么推荐方案A？

**时间vs深度**：
- ❌ 纯快速扫描：无法发现逻辑漏洞
- ❌ 100%深度审查：需要8-10小时（不现实）
- ✅ **方案A**：5秒扫描 + 1小时深度审查 = 最佳平衡

### 方案A流程

#### 步骤1：快速扫描（5秒）
**目标**：100%代码覆盖，检测明显恶意模式

**工具**：`quick_security_scan.py`

```bash
python3 /tmp/quick_security_scan.py <target_directory>
```

**检测项**（10个关键模式）：
1. ✅ 动态代码执行（eval/Function）
2. ✅ 进程创建（exec/spawn）
3. ✅ 文件操作（fs.read/write）
4. ✅ 可疑网络请求（非官方域名）
5. ✅ 硬编码私钥
6. ✅ 硬编码密钥/Token
7. ✅ 混淆代码（hex编码/base64）
8. ✅ 数据外泄模式
9. ✅ 命令注入
10. ✅ 危险npm包（shelljs/sudo）

**输出**：
```
Files scanned: 53
Lines scanned: 32,789
Total findings: 0
Risk score: 0/100
✅ LOW RISK
```

**结论判断**：
- Risk score ≥ 70: ❌ HIGH RISK - 不安装
- Risk score 40-69: ⚠️ MEDIUM RISK - 需人工审查
- Risk score < 40: ✅ LOW RISK - 继续深度审查

#### 步骤2：关键文件深度审查（1小时）
**目标**：理解高风险文件的逻辑，发现隐藏后门

**优先级排序**（按风险从高到低）：
1. **钱包服务**（wallets/*.ts）- 处理私钥
2. **网络客户端**（clients/*.ts）- 外部API调用
3. **交易服务**（services/trading-*.ts）- 资金操作
4. **入口文件**（index.ts）- 整体架构
5. **配置文件**（config/*.ts）- 环境变量

**深度审查方法论**：
```markdown
### 文件: src/wallets/hot-wallet-service.ts (217行)

**审计深度**: 100% (217/217行，逐行阅读)

**关键发现**:
- Line 45: AES-256-GCM加密（标准实现）
- Line 99: 密钥从环境变量读取（✅）
- Line 173: 内存清理finally块（✅）

**安全验证**:
- 网络请求: 0个
- 硬编码密钥: 0个
- 可疑代码: 0个

**结论**: ✅ CLEAN
```

**必须验证的点**：
1. ✅ 私钥/密钥来源（是否硬编码）
2. ✅ 加密实现（是否标准算法）
3. ✅ 网络请求URL（是否官方API）
4. ✅ 数据流向（是否外泄）
5. ✅ 内存管理（是否清理敏感数据）

#### 步骤3：综合评估（5分钟）

**量化报告**：
```markdown
## Security Audit Report

**Target**: package@version
**Method**: 快速扫描 + 关键文件深度审查

### 审计深度
- 快速扫描: 100% (32,789/32,789行)
- 深度审查: 9.4% (3,074/32,789行) - 4个关键文件
- 风险评分: 0/100 (LOW RISK)

### 发现
- Critical: 0
- High: 0
- Medium: 0
- Low: 0

### 结论
**Verdict**: ✅ PASS
**Confidence**: 9/10
**Recommendation**: 可以安装，锁定版本
```

### 方案A的优势

**vs 纯快速扫描**：
- ✅ 能发现逻辑漏洞
- ✅ 理解业务逻辑
- ✅ 验证加密实现
- ✅ 更高可信度（9/10 vs 6/10）

**vs 100%深度审查**：
- ✅ 时间可控（1小时 vs 10小时）
- ✅ 聚焦高风险文件
- ✅ 适合实际使用
- ✅ 性价比高

**适用场景**：
- ✅ 日常第三方包审查
- ✅ GitHub项目克隆前检查
- ✅ NPM/PyPI包安装前验证
- ✅ 快速评估项目安全性

---

## Goal

Provide professional-grade security audits for third-party code installation.

This skill is a mandatory gate before any third-party install.

## Hard Rules

1. **Never install first and review later.**
2. **Never execute installer scripts during review.**
3. **Never run `curl ... | sh`, `wget ... | bash` during review.**
4. **Never夸大审计能力。** 明确告知用户实际做了什么。
5. **Always深入分析关键源文件。** grep不是分析。
6. **Always量化审计深度。** 报告审查了多少行代码。
7. **Always使用所有可用工具。** 不偷懒。
8. **Always诚实报告局限性。** 如果需要专业工具，明确说明。
9. **For npm**: prefer metadata inspection + tarball extraction + `--ignore-scripts`
10. **For Python**: prefer `pip download` + source inspection
11. **Always lock versions**: `npm install package@version --save-exact`

---

## MCP Tools Integration（MCP工具集成）

### 可用的MCP工具

如果环境支持MCP（Model Context Protocol），优先使用以下工具：

#### 1. **filesystem MCP** - 文件系统分析
```bash
# 读取关键源文件
mcp filesystem read_file path="src/index.ts"
mcp filesystem read_file path="src/wallets/hot-wallet-service.ts"
mcp filesystem list_directory path="src/"
```

**用途**：深入分析源代码，而不是grep模式搜索。

#### 2. **git MCP** - Git历史分析
```bash
# 获取Git历史
mcp git log repo="owner/repo" max_count=50
mcp git diff repo="owner/repo" base="v1.0.0" head="v1.1.0"
```

**用途**：深度分析commit历史，检测恶意注入。

#### 3. **postgres/sqlite MCP** - 数据库分析
```bash
# 查询安全数据库（如果有）
mcp postgres query sql="SELECT * FROM known_malware WHERE package_name = ?"
```

**用途**：对比已知恶意软件库。

#### 4. **http MCP** - 网络请求分析
```bash
# 获取NPM元数据
mcp http get url="https://registry.npmjs.org/package/version"
```

**用途**：获取完整的包元数据。

#### 5. **memory MCP** - 持久化审计记录
```bash
# 存储审计结果
mcp memory store key="audit:package@version" value="{...}"
```

**用途**：记录审计历史，避免重复工作。

---

## Professional Audit Workflow（专业审计流程）

### Stage 0: Audit Planning（审计规划）

**在开始前，明确告知用户**：

```markdown
## 审计规划

**目标**: [package@version]
**风险等级**: [评估]
**计划审计深度**:
- [ ] 静态代码分析（逐行阅读关键文件）
- [ ] Git历史深度分析
- [ ] NPM包一致性验证
- [ ] 依赖树分析（直接+传递）
- [ ] 网络流量监控（需Charles/Fiddler）
- [ ] 动态行为分析（需Docker沙箱）
- [ ] 代码相似度分析（需恶意代码库）

**可用工具**: [列出可用工具]
**预计时间**: [估算]
**局限性**: [明确说明]
```

### Stage 1: Source Triage（源信誉审查）

**必须做的检查**：

1. **GitHub仓库分析**
   ```bash
   # 使用API获取完整元数据
   curl -s https://api.github.com/repos/owner/repo | jq '{...}'
   
   # 检查Issues（安全相关）
   curl -s "https://api.github.com/repos/owner/repo/issues?labels=security"
   
   # 检查Stars异常（刷量检测）
   curl -s https://api.github.com/repos/owner/repo/stargazers | jq 'group_by(.login[:3]) | map(length) | max'
   ```

2. **NPM包元数据**
   ```bash
   # 获取完整元数据
   npm view package@version --json
   
   # 验证integrity哈希
   npm view package@version integrity
   
   # 检查维护者历史
   npm view package@version maintainers
   ```

3. **输出量化报告**
   ```markdown
   ## Source Triage
   
   **检查项**: 15/15 ✅
   **发现**:
   - Stars: 1,243 (无刷量)
   - 维护者: 1个 (hhh_qc)
   - 安全Issues: 0个
   - 创建时间: 2025-12-23 (2个月)
   
   **风险信号**:
   - ⚠️ 仓库较新（2个月）
   - ⚠️ 单个维护者
   ```

### Stage 2: Git History Deep Dive（Git历史深度分析）

**必须做的检查**：

1. **克隆完整历史**
   ```bash
   git clone --depth 50 https://github.com/owner/repo.git
   ```

2. **分析贡献者**
   ```bash
   # 获取所有贡献者
   git log --format="%an <%ae>" | sort | uniq -c | sort -rn
   
   # 检查可疑邮箱域名
   git log --format="%ae" | grep -E "@(temp|disposable|guerrilla)"
   ```

3. **时间线分析**
   ```bash
   # NPM发布后的commit
   git log --oneline --since="YYYY-MM-DD"  # NPM publish date
   
   # 大规模重构检测
   git log --stat --since="YYYY-MM-DD" | grep -E "files? changed.*[0-9]{3,}"
   ```

4. **深度检查可疑commit**
   ```bash
   # 检查具体commit
   git show <commit-hash> --stat
   git show <commit-hash> -- src/suspicious-file.ts
   ```

5. **输出量化报告**
   ```markdown
   ## Git History Analysis
   
   **审查深度**: 50 commits (100%)
   **代码审查**: 0/2,813 lines (需深入)
   
   **发现**:
   - 贡献者: 2个 (正常)
   - 时间线: 无异常
   - Post-release commits: 18个 (全部功能性开发)
   - 可疑commit: 0个
   ```

### Stage 3: Source Code Deep Analysis（源代码深度分析）

**这是最关键的部分 - 必须逐行阅读关键文件。**

#### 必读文件清单

1. **入口文件**
   - `src/index.ts` / `index.js`
   - `src/main.ts` / `main.js`
   - 包导出的所有文件

2. **网络请求相关**
   - `src/clients/*.ts`
   - `src/api/*.ts`
   - `src/services/*.ts`

3. **钱包/密钥相关**
   - `src/wallets/*.ts`
   - `src/crypto/*.ts`
   - `src/auth/*.ts`

4. **文件系统相关**
   - `src/utils/fs*.ts`
   - `src/storage/*.ts`

5. **进程/命令相关**
   - `src/cli/*.ts`
   - `scripts/*.ts`

#### 深度分析方法论

```bash
# 1. 列出所有源文件
find src -name "*.ts" -o -name "*.js" | wc -l

# 2. 按重要性排序
# 优先级：index.ts > services/*.ts > clients/*.ts > utils/*.ts

# 3. 逐个深入阅读（使用read工具，不是grep）
# 示例：
```

**深度分析模板**：

```markdown
## Source Code Deep Analysis

**总文件数**: 176个 TypeScript文件
**深入分析**: 5/176个关键文件
**审查代码行数**: 2,813/50,000行 (5.6%)

### 文件1: src/index.ts (385行)

**审计深度**: ✅ 逐行阅读 (100%)

**关键发现**:
```typescript
// Line 150: 正常的SDK初始化
export class PolymarketSDK {
  constructor(config: PolymarketSDKConfig = {}) {
    this.rateLimiter = new RateLimiter();
    this.cache = createUnifiedCache(config.cache);
    // ✅ 无可疑代码
  }
}
```

**网络请求**: 0个
**文件操作**: 0个
**进程创建**: 0个
**可疑代码**: 0个

**结论**: ✅ CLEAN

---

### 文件2: src/wallets/hot-wallet-service.ts (217行)

**审计深度**: ✅ 逐行阅读 (100%)

**关键发现**:
```typescript
// Line 45: AES-256-GCM加密
private encryptPrivateKey(privateKey: string): EncryptedData {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  // ✅ 标准加密实现
}
```

**密钥管理**: ✅ 从环境变量读取
**硬编码密钥**: 0个
**密钥外泄**: 0个

**结论**: ✅ CLEAN

---

### 文件3: src/services/trading-service.ts (1,126行)

**审计深度**: ⚠️ 重点审查关键部分 (50%)

**关键发现**:
```typescript
// Line 50: 使用官方CLOB客户端
import { ClobClient } from '@polymarket/clob-client';

const CLOB_HOST = 'https://clob.polymarket.com';  // ✅ 官方API
```

**网络请求**: ✅ 仅官方Polymarket API
**数据外泄**: 0个
**可疑代码**: 0个

**结论**: ✅ CLEAN

---

**未深入分析的文件**: 171/176 (97.2%)
**原因**: 工具/时间限制
**剩余风险**: LOW (基于已审查文件的架构推断)
```

#### 必须检查的代码模式

```bash
# 1. 网络请求（必须逐个验证URL）
grep -rn "https://\|http://" src/ --include="*.ts" | grep -v "test\|example"

# 2. 文件操作（必须追踪数据流）
grep -rn "fs\.read\|fs\.write\|readFile\|writeFile" src/ --include="*.ts"

# 3. 进程创建（必须理解用途）
grep -rn "child_process\|exec\|spawn" src/ --include="*.ts"

# 4. 动态代码执行（必须逐行审查）
grep -rn "\beval\b\|new Function\|Function(" src/ --include="*.ts"

# 5. 环境变量读取（必须追踪用途）
grep -rn "process\.env\." src/ --include="*.ts"

# 6. 加密相关（必须验证密钥来源）
grep -rn "crypto\|encrypt\|decrypt\|private.*key" src/ --include="*.ts"
```

### Stage 4: NPM Package Consistency（NPM包一致性）

**必须做的检查**：

1. **下载NPM包**
   ```bash
   npm pack package@version
   tar -tzf package-version.tgz | wc -l
   ```

2. **提取并对比**
   ```bash
   mkdir npm-extract && tar -xzf package-version.tgz -C npm-extract
   diff -r npm-extract/package/dist github-repo/dist
   ```

3. **验证Scripts**
   ```bash
   # NPM包的scripts
   cat npm-extract/package/package.json | jq '.scripts'
   
   # GitHub的scripts
   cat github-repo/package.json | jq '.scripts'
   
   # 必须完全一致
   ```

4. **Integrity验证**
   ```bash
   # 获取官方哈希
   npm view package@version integrity
   
   # 验证下载的包
   shasum -a 256 package-version.tgz
   ```

### Stage 5: Dependency Tree Analysis（依赖树分析）

**必须做的检查**：

1. **直接依赖**
   ```bash
   cat package.json | jq '.dependencies | keys'
   ```

2. **传递依赖**（使用工具）
   ```bash
   npm ls --all
   # 或
   pnpm list --depth=Infinity
   ```

3. **逐个验证每个依赖**
   ```bash
   for dep in $(cat package.json | jq -r '.dependencies | keys[]'); do
     echo "=== $dep ==="
     npm view "$dep" --json | jq '{
       description,
       maintainers: .maintainers | length,
       time: .time | keys | length,
       homepage,
       repository
     }'
   done
   ```

4. **检查已知漏洞**
   ```bash
   npm audit --json
   # 或
   pnpm audit
   ```

### Stage 6: Dynamic Behavioral Analysis（动态行为分析）

**如果环境支持，必须做**：

1. **创建Docker沙箱**
   ```bash
   docker run -it --rm \
     --network none \  # 禁用网络
     -v $(pwd):/app \
     node:20 bash
   ```

2. **在沙箱中运行**
   ```bash
   cd /app
   npm install package@version --ignore-scripts
   node -e "require('package')"
   ```

3. **监控系统调用**（需要权限）
   ```bash
   strace -f -o trace.log node -e "require('package')"
   grep "open\|read\|write\|socket\|connect" trace.log
   ```

**如果无法做动态分析，必须明确说明**：
```markdown
## Dynamic Behavioral Analysis

**状态**: ❌ 未执行
**原因**: 环境不支持Docker/沙箱
**剩余风险**: MEDIUM (无法验证运行时行为)
**建议**: 在隔离环境手动测试
```

### Stage 7: Final Report（最终报告）

**必须包含的量化指标**：

```markdown
## Security Audit Report

**Target**: package@version
**Auditor**: AI Assistant
**Date**: YYYY-MM-DD
**Duration**: XX minutes

---

## Audit Depth（审计深度）

**源代码审查**:
- 总文件数: 176个
- 深入分析: 5个关键文件 (2.8%)
- 审查代码: 2,813/50,000行 (5.6%)
- 审查方式: 逐行阅读（不是grep）

**Git历史审查**:
- 审查commits: 50/50 (100%)
- 检查时间线: ✅
- 检查贡献者: ✅

**NPM包验证**:
- Integrity验证: ✅
- 源码对比: ✅
- Scripts对比: ✅

**依赖分析**:
- 直接依赖: 7/7 (100%)
- 传递依赖: 0/未知 (工具限制)

---

## Applied Techniques（应用的技巧）

**已应用** (10/36):
1. ✅ Git History Deep Dive
2. ✅ NPM Package Consistency
3. ✅ Auto-Update Detection
4. ✅ Integrity Verification
5. ✅ Metadata Analysis
6. ✅ Binary Analysis
7. ✅ Timestamp Analysis
8. ✅ Community Signal Analysis
9. ✅ Obfuscation Detection
10. ✅ Source Code Deep Analysis (逐行阅读)

**未应用** (26/36):
11. ❌ Network Traffic Analysis (需Charles/Fiddler)
12. ❌ Dynamic Behavioral Analysis (需Docker沙箱)
13. ❌ Code Similarity Analysis (需恶意代码库)
14. ❌ Static Analysis (未运行ESLint)
15. ❌ Secret Scanning (未用truffleHog)
... (列出所有未做的)

---

## Findings（发现）

### Critical Issues: 0个
### High Issues: 0个
### Medium Issues: 0个
### Low Issues: 2个
- ⚠️ 仓库较新（2个月）
- ⚠️ 单个维护者

---

## Conclusion（结论）

**Verdict**: ✅ PASS WITH CAUTION

**Confidence**: 7/10 (基于5.6%代码审查)

**Risk Level**: LOW

**Remaining Risks**:
1. 未审查94.4%的代码
2. 未做动态行为分析
3. 未做网络流量监控

**Recommendations**:
1. ✅ 可以安装使用
2. ⚠️ 锁定版本：`npm install package@version --save-exact`
3. ⚠️ 在测试环境验证
4. ⚠️ 监控未来版本

**Professional Audit Recommended**: YES/NO
- 如果Confidence < 8/10，推荐专业审计
```

---

## Tool Encapsulation（工具封装）

### 自动化审计脚本

创建以下辅助脚本，加速审计：

#### 1. `audit-npm-package.sh`
```bash
#!/bin/bash
# NPM包自动化审计脚本

PACKAGE=$1
VERSION=$2

echo "=== NPM Package Audit: $PACKAGE@$VERSION ==="

# 1. 获取元数据
npm view $PACKAGE@$VERSION --json > npm-metadata.json

# 2. 下载包
npm pack $PACKAGE@$VERSION
tar -xzf *.tgz -C npm-extract

# 3. 克隆GitHub仓库（如果有）
REPO=$(cat npm-metadata.json | jq -r '.repository.url')
if [ "$REPO" != "null" ]; then
  git clone --depth 50 $REPO github-repo
fi

# 4. 对比
diff -r npm-extract/package github-repo

# 5. 生成报告
echo "Audit complete. Check npm-metadata.json and diffs."
```

#### 2. `audit-git-history.sh`
```bash
#!/bin/bash
# Git历史深度分析脚本

REPO_DIR=$1

cd $REPO_DIR

echo "=== Git History Analysis ==="

# 1. 贡献者分析
echo "## Contributors"
git log --format="%an <%ae>" | sort | uniq -c | sort -rn

# 2. 时间线分析
echo "## Timeline"
git log --oneline --graph --all -50 --date=short --format="%h %ad %an %s"

# 3. 大规模改动检测
echo "## Large Changes"
git log --stat | grep -E "files? changed.*[0-9]{3,}"

# 4. 可疑模式检测
echo "## Suspicious Patterns"
git log -p | grep -E "eval\|exec\|child_process" | head -20
```

#### 3. `audit-source-code.sh`
```bash
#!/bin/bash
# 源代码深度分析脚本

SRC_DIR=$1

echo "=== Source Code Analysis ==="

# 1. 统计
echo "## Statistics"
find $SRC_DIR -name "*.ts" -o -name "*.js" | wc -l
find $SRC_DIR -name "*.ts" -o -name "*.js" | xargs wc -l | tail -1

# 2. 网络请求
echo "## Network Requests"
grep -rn "https://\|http://" $SRC_DIR --include="*.ts" --include="*.js" | grep -v "test\|example"

# 3. 文件操作
echo "## File Operations"
grep -rn "fs\.read\|fs\.write\|readFile\|writeFile" $SRC_DIR --include="*.ts"

# 4. 进程创建
echo "## Process Creation"
grep -rn "child_process\|exec\|spawn" $SRC_DIR --include="*.ts"

# 5. 动态代码
echo "## Dynamic Code"
grep -rn "\beval\b\|new Function" $SRC_DIR --include="*.ts"
```

---

## Integration with OpenClaw

### 自动触发审计

当用户说以下关键词时，自动触发此skill：
- "安装" + "包/库/依赖"
- "npm install" / "pip install"
- "git clone" + 使用
- "安全审计" / "审查代码"

### 审计结果持久化

将审计结果存储到：
```
memory/security-audits/YYYY-MM-DD-package@version.md
```

格式：
```markdown
# Security Audit: package@version

**Date**: YYYY-MM-DD
**Verdict**: PASS/CAUTION/BLOCK
**Confidence**: X/10
**Risk**: HIGH/MEDIUM/LOW

## Summary
[简短总结]

## Details
[详细审计报告链接]
```

---

## Continuous Improvement

### 从每次审计中学习

1. **记录新的攻击模式**
   - 发现新的恶意代码模式 → 添加到检测库

2. **优化审计流程**
   - 发现遗漏 → 更新SKILL

3. **工具改进**
   - 发现更好的工具 → 封装进SKILL

### 定期回顾

- 每月回顾审计记录
- 分析漏报/误报
- 更新检测规则

---

## Examples

### Example 1: 完整审计报告

```markdown
## Security Audit Report

**Target**: @catalyst-team/poly-sdk@0.5.0
**Date**: 2026-03-02
**Duration**: 15 minutes

---

## Audit Depth

**Source Code Review**:
- Total files: 176 TypeScript files
- Deep analysis: 5 key files (2.8%)
- Lines reviewed: 2,813/50,000 (5.6%)
- Method: Line-by-line reading (not grep)

**Git History**:
- Commits reviewed: 50/50 (100%)
- Contributors: 2 (verified)
- Timeline: Normal

**NPM Package**:
- Integrity: ✅ Verified
- Source match: ✅ 100%
- Scripts: ✅ Identical

**Dependencies**:
- Direct: 7/7 (100%)
- Transitive: Unknown (tool limitation)

---

## Applied Techniques (10/36)

✅ 1. Git History Deep Dive
✅ 2. NPM Package Consistency
✅ 3. Auto-Update Detection
✅ 4. Integrity Verification
✅ 5. Metadata Analysis
✅ 6. Binary Analysis
✅ 7. Timestamp Analysis
✅ 8. Community Signal Analysis
✅ 9. Obfuscation Detection
✅ 10. Source Code Deep Analysis

❌ 11-36. [List of not applied techniques]

---

## Findings

**Critical**: 0
**High**: 0
**Medium**: 0
**Low**: 2
- ⚠️ New repository (2 months)
- ⚠️ Single maintainer

---

## Code Analysis

### File 1: src/index.ts (385 lines)
- **Reviewed**: 100% (line-by-line)
- **Network requests**: 0
- **File operations**: 0
- **Suspicious code**: 0
- **Verdict**: ✅ CLEAN

### File 2: src/wallets/hot-wallet-service.ts (217 lines)
- **Reviewed**: 100% (line-by-line)
- **Key management**: ✅ From env vars
- **Hardcoded keys**: 0
- **Verdict**: ✅ CLEAN

### File 3: src/services/trading-service.ts (1,126 lines)
- **Reviewed**: 50% (key sections)
- **Network requests**: ✅ Official APIs only
- **Verdict**: ✅ CLEAN

---

## Conclusion

**Verdict**: ✅ PASS WITH CAUTION

**Confidence**: 7/10

**Remaining Risks**:
1. 94.4% code not reviewed
2. No dynamic analysis
3. No network monitoring

**Install Command**:
```bash
npm install @catalyst-team/poly-sdk@0.5.0 --save-exact
```

**Professional Audit**: Recommended (confidence < 8/10)
```

---

## Final Commitment

**我承诺**：

1. ✅ **深入分析代码** - 不是grep，是逐行阅读
2. ✅ **量化审计深度** - 报告审查了多少代码
3. ✅ **诚实报告能力** - 明确做了什么、没做什么
4. ✅ **使用所有工具** - 不偷懒
5. ✅ **最高标准要求自己** - 用户的信任是命

**违反承诺的后果**：
- 误导用户 → 安全风险
- 敷衍了事 → 失去信任
- 夸大能力 → 专业性丧失

**Remember**: 每一次审计都是对用户信任的考验。不要辜负。
