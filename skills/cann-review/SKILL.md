---
name: cann-review
description: |
  CANN 代码审查技能。用于审查 GitCode 上的 CANN 项目 PR。
  当用户提到"审查 PR"、"代码审查"、"cann review"或提供 GitCode PR 链接时触发。
  自动分析代码变更，检查内存泄漏、安全漏洞和可读性，生成结构化报告并发布评论。
---

# CANN 代码审查技能

你是一位资深的 C/C++/Python 代码工程师，专门负责审查 CANN 项目的 Pull Request。

## 重要：使用 GitCode API

**本技能使用 GitCode API 进行所有操作，无需浏览器自动化，确保稳定性和可靠性。**

### 🔧 首次使用配置

**安装技能后，需要配置 GitCode API Token：**

#### 方法 1：使用配置向导（推荐）

```bash
cd ~/.openclaw/workspace/skills/cann-review
./gitcode-api.sh setup
```

按提示输入你的 GitCode API Token。

#### 方法 2：手动配置

```bash
# 复制配置模板
cd ~/.openclaw/workspace/skills/cann-review
cp config/gitcode.conf.example config/gitcode.conf

# 编辑配置文件
nano config/gitcode.conf
```

设置 `GITCODE_API_TOKEN=your_token_here`

#### 方法 3：环境变量

```bash
export GITCODE_API_TOKEN=your_token_here
```

### 🔑 获取 GitCode API Token

1. 访问 https://gitcode.com/setting/token-classic
2. 点击"生成新令牌"
3. 选择权限：`api`, `write_repository`
4. 复制生成的 Token

### 配置文件位置

- **配置文件**: `~/.openclaw/workspace/skills/cann-review/config/gitcode.conf`
- **权限**: 600（仅当前用户可读写，保护敏感信息）

### 配置优先级

1. 环境变量 `GITCODE_API_TOKEN`（最高优先级）
2. 配置文件 `config/gitcode.conf`
3. 默认值（无）

### API 认证方式

配置完成后，所有 API 请求会自动添加认证头：
```bash
Authorization: Bearer $GITCODE_API_TOKEN
```

## 任务目标

对指定的 PR 进行全面代码审查，重点检查：
1. **内存泄漏** - 动态内存分配是否正确释放
2. **安全漏洞** - 缓冲区溢出、空指针解引用、类型转换问题
3. **代码可读性** - 命名规范、注释完整性、代码结构

## 执行步骤

### 步骤 1: 解析 PR URL 并获取基本信息

从 PR URL 中提取项目信息和 PR 编号：
```
示例 URL: https://gitcode.com/cann/runtime/merge_requests/628
项目路径: cann/runtime
PR 编号: 628
```

使用 API 获取 PR 基本信息：
```bash
curl -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628"
```

返回信息包括：
- PR 标题、描述、状态
- 作者、审查者、测试者
- 标签（lgtm, approved 等）
- 创建时间、更新时间
- 源分支、目标分支

### 步骤 2: 获取代码变更

使用 API 获取所有变更的文件：
```bash
curl -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/files"
```

返回信息包括：
- 文件名、路径
- 新增行数、删除行数
- diff 补丁内容
- blob_url 和 raw_url（可用于获取完整文件内容）

重点关注：
- 新增的 `.c`, `.cc`, `.cpp`, `.h`, `.hpp` 文件
- 内存管理相关代码 (`malloc`, `free`, `new`, `delete`, `memcpy` 等)
- 指针操作和类型转换
- API 接口定义

### 步骤 3: 分析代码

对每个变更文件进行审查：

#### 内存泄漏检查清单
- [ ] `malloc/calloc/realloc` 是否有对应的 `free`
- [ ] `new` 是否有对应的 `delete`
- [ ] 异常路径下是否正确释放资源
- [ ] 使用 RAII 模式管理资源
- [ ] 容器内存管理是否合理

#### 安全检查清单
- [ ] 指针使用前是否进行空检查
- [ ] 数组/缓冲区边界检查
- [ ] `memcpy_s` 等安全函数的使用
- [ ] 整数溢出检查
- [ ] 类型转换安全性

#### 可读性检查清单
- [ ] 变量/函数命名是否清晰
- [ ] 是否有适当的注释
- [ ] 代码结构是否清晰
- [ ] 是否遵循项目代码风格

### 步骤 4: 生成审查报告

**重要**：审查结论必须放在最前面，然后是详细分析。

按以下格式生成报告：

```markdown
## 🤖 CANN 代码审查报告

**PR**: #<pr_number> - <pr_title>
**严重性**: <✅ Low / ⚠️ Medium / ❌ High / 🔴 Critical>
**审查时间**: <YYYY-MM-DD HH:MM>

---

### 📊 审查结论

**<✅ 建议合入 / ⚠️ 建议修改后合入 / ❌ 需要修改>**

- **严重性**: <Low/Medium/High/Critical>
- **代码质量**: <优秀/良好/一般/需改进>
- **内存安全**: <✅ 无风险 / ⚠️ 有风险 / ❌ 存在问题>
- **安全性**: <✅ 无漏洞 / ⚠️ 有隐患 / ❌ 存在漏洞>
- **测试覆盖**: <完整/部分/缺失>
- **文档完整性**: <完整/部分/NA>

<简要评价：一句话总结代码质量和建议>

---

### 📋 修改概述

<描述本次 PR 的主要变更内容>

- **修改文件**: <N>个 (+<X>行, -<Y>行)
- **核心变更**:
  - `<file1>`: <变更描述>
  - `<file2>`: <变更描述>
  - `<file3>`: <变更描述>

---

### 🔍 代码质量检查

#### 1. 内存安全 <✅/⚠️/❌>
- **内存泄漏**: <无风险/有风险/存在问题>
- **指针操作**: <安全/需注意/有问题>
- **动态分配**: <合理/需优化/有问题>
- **资源管理**: <RAII/手动管理/存在问题>

#### 2. 安全性 <✅/⚠️/❌>
- **输入验证**: <完整/部分/缺失>
- **边界检查**: <完整/部分/缺失>
- **潜在漏洞**: <无/有/严重>

#### 3. 可读性 <✅/⚠️/❌>
- **代码清晰度**: <优秀/良好/一般/需改进>
- **命名规范**: <符合/部分符合/不符合>
- **注释完整性**: <完整/部分/缺失>

#### 4. 逻辑正确性 <✅/⚠️/❌>
- **算法逻辑**: <正确/需验证/有问题>
- **边界条件**: <处理完整/部分处理/未处理>
- **影响范围**: <明确/需评估/不明确>

---

### 💡 改进建议

1. **<建议类别1>**: <具体建议>
2. **<建议类别2>**: <具体建议>

---

### ✅ 代码亮点

- <列出代码中做得好的地方>

总体评价：<简要总结>

---

> ⚠️ **声明**: 本审查报告由 AI 自动生成，仅供参考。建议人工复核后再做最终决定。
```

### 步骤 5: 发布审查评论

使用 API 发布审查评论（简单可靠）：

```bash
curl -X POST \
  -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  -H "Content-Type: application/json" \
  -d '{"body":"<审查报告内容>"}' \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/comments"
```

**注意事项**：
- 评论内容需要转义 JSON 字符串（换行符用 `\n`，引号用 `\"`）
- API 会返回评论 ID 和 note_id，表示发布成功
- 如果 PR 已合并，可能无法发布评论（根据项目设置）

**示例**：
```bash
# 使用 heredoc 处理多行文本
COMMENT=$(cat <<'EOF'
## 🤖 CANN 代码审查报告

**PR**: #628 - 示例标题
**严重性**: ✅ Low

### 📊 审查结论
代码质量良好，可以合入
EOF
)

# 发布评论
curl -X POST \
  -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  -H "Content-Type: application/json" \
  -d "{\"body\":\"$(echo "$COMMENT" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"}" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/comments"
```

## 严重程度判定标准

| 等级 | 条件 | 是否可合入 |
|------|------|------------|
| Low | 仅有建议性改进 | ✅ 可以 |
| Medium | 有一般性问题，不影响功能 | ⚠️ 建议 |
| High | 有严重问题，可能导致缺陷 | ❌ 需要 |
| Critical | 有安全漏洞或严重内存问题 | ❌ 需要 |

## C/C++ 常见问题模式

### 内存泄漏模式
```cpp
// 危险: 忘记释放
char* buffer = (char*)malloc(size);
// ... 使用后没有 free(buffer)

// 安全: 使用智能指针
std::unique_ptr<char[]> buffer(new char[size]);
```

### 安全漏洞模式
```cpp
// 危险: 没有边界检查
void process(const char* input) {
    char buffer[256];
    strcpy(buffer, input);  // 潜在缓冲区溢出
}

// 安全: 使用安全函数
void process(const char* input) {
    char buffer[256];
    errno_t err = strcpy_s(buffer, sizeof(buffer), input);
    if (err != 0) {
        // 处理错误
    }
}
```

### 空指针模式
```cpp
// 危险: 没有空检查
void process(Object* obj) {
    obj->method();  // 如果 obj 为空会崩溃
}

// 安全: 添加空检查
void process(Object* obj) {
    if (obj == nullptr) {
        return ERROR_INVALID_PARAM;
    }
    obj->method();
}
```

## 输入参数

- **pr_url**: PR 页面链接 (必需)
- **focus_areas**: 审查重点 (memory/security/readability/all)，默认 all

## 输出

返回审查结果 JSON:
```json
{
  "severity": "low",
  "can_merge": true,
  "issues_count": 2,
  "comment_posted": true,
  "summary": "代码质量良好，可以合入"
}
```

## 自动审查模式

当 skill 被定时任务触发时，执行批量自动审查流程。

### ⚡ 工作方式

**10分钟间隔扫描，逐个审查**：

1. **扫描所有配置的仓库** → 读取 `config/repos.conf`
2. **筛选过去10分钟内提交的 PR** → 根据更新时间过滤
3. **收集所有待审查 PR** → 保存到 `.pending-reviews.json`
4. **逐个审查每个 PR** → 完整的代码审查流程
5. **发布审查评论** → 使用 GitCode API
6. **生成汇总报告** → 展示所有审查结果

**特点**：
- ✅ 每10分钟扫描过去10分钟内新提交的 PR
- ✅ 逐个审查，确保每个 PR 都得到完整审查
- ✅ 无状态设计，不记录历史审查记录
- ✅ 生成汇总报告，一目了然
- ✅ 支持跨小时、跨天的时间区间计算

### 🔧 配置审查仓库

**首次使用需要配置要审查的仓库列表：**

#### 方法 1：使用配置文件（推荐）

```bash
cd ~/.openclaw/workspace/skills/cann-review

# 复制配置模板
cp config/repos.conf.example config/repos.conf

# 编辑配置文件
nano config/repos.conf
```

添加需要审查的仓库（格式: `owner/repo`），示例：
```
cann/runtime
cann/compiler
cann/driver
```

#### 方法 2：使用环境变量

```bash
export CANN_REVIEW_REPOS="cann/runtime,cann/compiler,cann/driver"
```

### 🔧 配置审查仓库

**首次使用需要配置要审查的仓库列表：**

#### 方法 1：使用配置文件（推荐）

```bash
cd ~/.openclaw/workspace/skills/cann-review

# 复制配置模板
cp config/repos.conf.example config/repos.conf

# 编辑配置文件
nano config/repos.conf
```

添加需要审查的仓库（格式: `owner/repo`），示例：
```
cann/runtime
cann/compiler
cann/driver
```

#### 方法 2：使用环境变量

```bash
export CANN_REVIEW_REPOS="cann/runtime,cann/compiler,cann/driver"
```

### 📋 自动审查流程

当定时任务触发时，执行以下流程：

#### 1. 扫描所有仓库

运行扫描脚本：
```bash
bash ~/.openclaw/workspace/skills/cann-review/auto-review-final.sh
```

输出示例：
```
🤖 CANN 自动审查（10分钟间隔扫描模式）
======================================
开始时间: 2026-03-28 16:30:00
扫描范围: 2026-03-28T16:20:00+08:00 ~ 2026-03-28T16:29:59+08:00

📊 配置信息:
  仓库数量: 3

🔍 扫描所有仓库...
  检查: cann/runtime
    ✅ 发现 2 个10分钟内提交的 PR
  检查: cann/oam-tools
    ✅ 发现 1 个10分钟内提交的 PR
  检查: cann/oam-tools-diag
    ℹ️  时间段内无新 PR

======================================
扫描完成
  待审查 PR 总数: 3

📋 待审查 PR 列表:
  1. cann/runtime#1270 - fix memory leak
     作者: zhaozhixuan
     链接: https://gitcode.com/cann/runtime/merge_requests/1270
  ...

💡 接下来将逐个审查这些 PR...
```

#### 2. 解析待审查列表

脚本会输出 JSON 格式的待审查列表（在 `PENDING_REVIEWS_JSON_START` 和 `PENDING_REVIEWS_JSON_END` 之间）：
```json
{
  "pending": [
    {
      "repo": "cann/runtime",
      "pr_number": 666,
      "title": "for msprof block dim",
      "author": "zhaozhixuan",
      "url": "https://gitcode.com/cann/runtime/merge_requests/666"
    },
    ...
  ],
  "scan_time": "2026-03-06T10:34:15+08:00"
}
```

#### 3. 逐个审查 PR

对每个待审查的 PR：
1. 调用 `cann-review` skill 进行审查
2. 使用 API 获取 PR 详情和文件变更
3. 执行代码审查（步骤 3）
4. 生成审查报告（步骤 4）
5. 使用 API 发布评论（步骤 5）
6. 如适用，发布 LGTM（步骤 6）
7. 标记为已审查

#### 4. 生成汇总报告

向用户发送汇总消息：
```markdown
## 自动审查完成

已审查 25 个 MR：

✅ **cann/runtime** (6 个)
- #666: for msprof block dim - Low - 已发布审查报告
- #665: Dump 支持 - Medium - 已发布审查报告
...

✅ **cann/oam-tools** (13 个)
- #81: 支持用户离线编译 - Low - 已发布审查报告
...

✅ **cann/oam-tools-diag** (6 个)
- #24: revert safe link - Low - 已发布审查报告
...

总计: 25 个 PR 已审查
```

## 注意事项
   éré新SKILL.md（使用 API 而浏览器自动化），移除
1. 保持专业和建设性的语气
2. 指问题的同时给出解决方案
3. 认可代码中做得好的部分
4. 遵循项目的代码审查规范
5. 如果无法访问 API，及时报告错误
6. 自动审查时，避免重复审查已处理的 PR
7. 不要在命令行直接传递 Token（会被记录到 history日志）

1. **使用 API 而非浏览器**：所有操作通过 GitCode API 完成，无需浏览器自动化
2. **API 认证**：确保请求头包含正确的 Authorization
3. **JSON 转义**：发布评论时注意转义特殊字符
4. 保持专业和建设性的语气
5. 指出问题的同时给出解决方案
6. 认可代码中做得好的部分
7. 遵循项目的代码审查规范
8. 自动审查时，避免重复审查已处理的 PR

## 常见问题

### 1. 如何配置 GitCode API Token？

**首次使用**：
```bash
cd ~/.openclaw/workspace/skills/cann-review
./gitcode-api.sh setup
```

**重新配置**：
```bash
# 删除旧配置
rm config/gitcode.conf

# 重新运行配置向导
./gitcode-api.sh setup
```

**或使用环境变量**：
```bash
export GITCODE_API_TOKEN=your_token_here
```

### 2. API 返回 401 Unauthorized

**问题**：API 请求返回 401 错误。

**原因**：Token 无效或已过期。

**解决方案**：
- 检查配置文件：`cat config/gitcode.conf`
- 验证 Token 是否正确：`echo $GITCODE_API_TOKEN`
- 重新生成 Token：https://gitcode.com/setting/token-classic
- 更新配置：`./gitcode-api.sh setup`

### 2. 无法在已合并的 PR 上发布评论

**问题**：评论发布失败，提示 "not allowed to be reviewed after being merged"。

**原因**：项目设置禁止在已合并的 PR 上发布评论。

**解决方案**：
- 这是正常行为，跳过已合并的 PR
- 或者联系项目管理员修改设置

### 3. API 请求频率限制

**问题**：API 返回 429 Too Many Requests。

**原因**：GitCode API 有频率限制（默认 50次/分钟，4000次/小时）。

**解决方案**：
- 在自动审查模式下，添加适当延迟
- 分批处理大量 PR
- 避免频繁轮询

### 4. JSON 转义问题

**问题**：发布评论时 JSON 解析失败。

**原因**：评论内容包含未转义的特殊字符。

**解决方案**：
```bash
# 使用 sed 转义引号和换行符
COMMENT_ESCAPED=$(echo "$COMMENT" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

# 或使用 Python 的 json.dumps
COMMENT_ESCAPED=$(python3 -c "import json; print(json.dumps('''$COMMENT'''))")
```

### 5. 获取大量文件变更时响应缓慢

**问题**：PR 包含大量文件，API 响应很慢。

**原因**：GitCode 需要计算和返回所有文件的 diff。

**解决方案**：
- 使用分页参数（如果 API 支持）
- 优先审查高风险文件（.c, .cpp, .h）
- 跳过纯文档或配置文件

## 最佳实践

1. **先浏览再审查**：先看一遍所有文件改动，了解整体情况
2. **重点优先**：优先审查高风险代码（内存操作、指针、类型转换）
3. **建设性反馈**：不仅指出问题，还提供改进建议
4. **平衡语气**：既不过于严厉，也不过于宽松
5. **及时更新**：如果发现之前的判断有误，及时更正

## 版本历史

- **v4.2.1** (2026-03-28 17:35)
  - 🐛 **重要修复**：定时任务不执行扫描脚本的 bug
  - 📝 更新定时任务指令，  - ⚠️ 强制要求每次执行扫描脚本
  - ⚠️ 禁止读取旧的扫描结果文件
  - ✨ 新增标准化执行报告格式
  - 📊 输出格式：任务执行概况 + 扫描结果 + 执行结果
  - 📢 启用自动通知功能(delivery.mode=announce)

- **v4.2.0** (2026-03-28)
  - ⏰ **重大更新**：改为10分钟间隔扫描模式
  - 🔄 从"整点扫描"改为"10分钟间隔扫描"，更及时的审查
  - 🛠️ 修复UTF-8编码问题，使用临时文件传递JSON数据
  - 🌏 修复时区比较问题，添加+08:00时区支持
  - 📝 更新定时任务配置：从 `0 * * * *` 改为 `*/10 * * * *`
  - 🎯 支持跨小时、跨天的时间区间计算

- **v4.1.0** (2026-03-27)
  - 🔧 重构自动审查逻辑：整点扫描模式
  - 🚀 移除 max_reviews 限制，审查整点内所有新提交的 PR
  - 🗑️ 移除状态跟踪（.review-state.json），改为无状态设计
  - ⏰ 按更新时间筛选整点范围内的 PR

- **v4.0.1** (2026-03-27)
  - 📝 审查报告末尾添加 AI 生成声明提示
  - ⚠️ 提醒用户 AI 审查仅供参考，建议人工复核

- **v4.0.0** (2026-03-27)
  - 📝 审查报告末尾添加 AI 生成声明提示
  - ⚠️ 提醒用户 AI 审查仅供参考，建议人工复核

- **v3.1.0** (2026-03-27)
  - 📝 审查报告末尾添加 AI 生成声明提示
  - ⚠️ 提醒用户 AI 审查仅供参考，建议人工复核

- **v3.0.2** (2026-03-27)
  - 📝 审查报告末尾添加 AI 生成声明提示
  - ⚠️ 提醒用户 AI 审查仅供参考，建议人工复核

- **v3.0.1** (2026-03-27)
  - 📝 审查报告末尾添加 AI 生成声明提示
  - ⚠️ 提醒用户 AI 审查仅供参考，建议人工复核

- **v3.0.0** (2026-03-04)
  - 🎉 **重大更新**：全面改用 GitCode API，弃用浏览器自动化
  - ✨ 使用 API 获取 PR 信息和代码变更
  - ✨ 使用 API 发布审查评论
  - 🚀 提高稳定性和可靠性
  - 📝 简化操作流程，无需处理浏览器元素定位
  - 🐛 解决浏览器自动化常见问题（ref 不稳定、元素定位错误等）

- **v2.0.3** (2026-03-03)
  - 🐛 修复 ref 编号不稳定问题
  - 📝 推荐使用 aria refs 和 fill 操作
  - 📝 添加输入后验证步骤
  - 🔧 优化评论输入流程，提高可靠性

- **v2.0.2** (2026-03-03)
  - 🐛 修复评论输入框定位问题
  - 📝 添加常见问题和故障排查指南
  - 📝 优化步骤 5，添加详细说明

- **v2.0.1** (2026-03-03)
  - 🎨 优化报告格式：审查结论前置
  - 🔧 修改标题：去掉 "Runtime"
  - ✨ 更换代码质量检查图标

- **v2.0.0** (2026-03-03)
  - 🎉 新增自动审查模式
  - 🌐 改用 OpenClaw 内置浏览器
  - ⏰ 支持定时任务调度
  - 📊 添加汇总报告功能
  - 📝 完善文档和安装指南

- **v1.0.0** (2026-03-03)
  - 🎉 初始版本发布
  - 🔍 支持内存泄漏检查
  - 🔒 支持安全漏洞检查
  - 📖 支持代码可读性检查
  - 💬 自动发布审查评论

