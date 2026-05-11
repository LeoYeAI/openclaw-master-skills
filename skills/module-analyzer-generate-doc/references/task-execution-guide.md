# 任务执行指南

> 详细的多子代理并行执行流程、上下文压缩策略、重试机制说明

---

## 子代理分片策略

### 分片规则

| 模块文件总数 | 子代理数量 | 每片文件数 | 超时时间 | 重试次数 |
|--------------|------------|------------|----------|----------|
| <20 | 1 | 全部 | 300 秒 | 3 |
| 20-40 | 3 | 10-14 | 600 秒 | 3 |
| 40-60 | 4 | 12-16 | 750 秒 | 3 |
| 60-80 | 5 | 12-18 | 900 秒 | 3 |
| 80-100 | 6 | 14-18 | 900 秒 | 3 |
| >100 | 7-8 | 12-16 | 900 秒 | 3 |

### 分片原则

1. **Controller 集中原则**: 尽量将同一目录的 Controller 分到同一片
2. **Service 集中原则**: Service 和对应的 ServiceImpl 尽量在同一片
3. **Config 集中原则**: 配置类通常较小，可以合并到同一片
4. **大小均衡原则**: 每片文件数相近，避免某片过大导致超时

---

## 上下文压缩策略

### 压缩触发条件

| 上下文使用率 | 动作 |
|--------------|------|
| <30% | 正常处理，保留完整上下文 |
| 30-40% | 预警，准备压缩 |
| 40-50% | **开始压缩**：每处理 2 个文件压缩一次 |
| 50-60% | **强制压缩**：每处理 1 个文件压缩一次 |
| >60% | **紧急压缩**：停止处理，报告进度，拆分任务 |

### 压缩操作

**保留内容**（占用上下文少）:
```
- 文件路径列表：["File1.java", "File2.java", ...]
- 每文件 1 行摘要：{"file": "File1.java", "summary": "一句话业务摘要"}
- 当前任务描述：任务目标、输出路径
- 进度统计：已处理 X 个，剩余 Y 个
- 跳过文件列表及原因
```

**丢弃内容**（占用上下文多）:
```
- 已生成文档的完整内容
- 中间思考过程
- 详细方法分析
- 完整代码示例
- 冗长的依赖关系说明
```

### 压缩示例

**压缩前** (占用大量上下文):
```markdown
已处理 File1.java:
# File1 - 业务逻辑详解
## 基本信息
- 文件路径：com/example/File1.java
- 行数：150
- 类型：Controller
## 业务职责
File1 是一个用户管理控制器，提供用户 CRUD 操作...（200 字）
## 核心业务逻辑
### 创建用户
1. 接收请求参数
2. 验证参数合法性
3. 检查用户名是否重复
4. 密码加密
5. 插入数据库
6. 返回结果
...（500 字详细流程）

已处理 File2.java:
# File2 - 业务逻辑详解
...（同样详细的内容）
```

**压缩后** (节省上下文):
```json
{
  "processed": [
    {"file": "File1.java", "lines": 150, "type": "Controller", "summary": "用户管理控制器，提供用户 CRUD、密码管理、头像上传等功能的 RESTful 接口"},
    {"file": "File2.java", "lines": 280, "type": "ServiceImpl", "summary": "用户服务实现类，实现用户认证、权限检查、数据验证等核心业务逻辑"}
  ],
  "progress": {"total": 16, "completed": 2, "remaining": 14}
}
```

---

## 重试机制

### 可重试错误

| 错误类型 | 原因 | 重试策略 |
|----------|------|----------|
| timeout | 子代理处理超时 | 增加超时时间，拆分更小分片 |
| context_overflow | 上下文超出限制 | 减小分片大小，增加压缩频率 |
| file_access_error | 文件读取失败 | 记录失败文件，请求用户确认权限 |
| subagent_crash | 子代理意外退出 | 重新 spawn，传递已完成进度 |

### 不可重试错误

| 错误类型 | 原因 | 处理方式 |
|----------|------|----------|
| invalid_project_path | 项目路径不存在 | 请求用户确认路径 |
| permission_denied | 无权限访问 | 请求用户授权 |
| disk_full | 磁盘空间不足 | 清理空间或停止任务 |

### 重试流程

```
第 1 次失败
  ↓
等待 30 秒（初始延迟）
  ↓
重新 spawn 子代理（相同任务）
  ↓
第 2 次失败
  ↓
等待 60 秒（30 × 2）
  ↓
重新 spawn 子代理（减小分片）
  ↓
第 3 次失败
  ↓
等待 120 秒（60 × 2）
  ↓
重新 spawn 子代理（最小分片）
  ↓
第 4 次失败
  ↓
标记为"需要手动干预"
记录失败文件到状态文件
继续处理其他分片
```

---

## 进度汇报

### 汇报时机

1. **定时汇报**: 每 20 分钟自动汇报
2. **分片完成**: 每完成一个分片汇报
3. **阶段完成**: L3 完成、L2 完成时汇报
4. **异常汇报**: 遇到失败/重试时立即汇报

### 汇报内容模板

```markdown
## 📊 文档生成进度报告

**模块**: {模块名}
**开始时间**: {开始时间}
**当前时间**: {当前时间}
**已用时间**: {已用时间}

### 总体进度：{百分比}%

### 当前阶段：{L3/L2}

| 分片 | 状态 | 已处理 | 已跳过 | 失败 |
|------|------|--------|--------|------|
| chunk1 | ✅ | 16 | 0 | 0 |
| chunk2 | ✅ | 6 | 10 | 0 |
| chunk3 | 🔄 | 12/16 | 0 | 0 |
| chunk4 | ⏳ | 0 | 0 | 0 |
| chunk5 | ⏳ | 0 | 0 | 0 |

### 统计
- 已处理文件：{X}
- 已跳过文件：{Y}（纯定义类）
- 失败文件：{Z}
- 活跃子代理：{N}/{总}

### 预计完成时间
- 当前阶段：约 {X} 分钟（剩余 {Y}%）
- 总计：约 {Z} 分钟
```

---

## 状态文件管理

### 保存时机

1. **任务启动时**: 初始化状态文件
2. **分片完成时**: 更新分片状态
3. **定时保存**: 每 5 分钟自动保存
4. **子代理启动/结束时**: 更新子代理状态
5. **遇到错误时**: 记录错误信息

### 状态文件结构

```json
{
  "version": "1.0.0",
  "projectPath": "E:\\projects\\mgmt-api-cp",
  "targetModule": "admin-api",
  "startTime": "2026-03-07T10:17:00+08:00",
  "currentPhase": "L3",
  "overallProgress": 76.5,
  "phases": {
    "L3": {
      "status": "in_progress",
      "totalFiles": 81,
      "processedFiles": 62,
      "skippedFiles": 19,
      "failedFiles": 0,
      "chunks": {
        "total": 5,
        "completed": 4,
        "inProgress": 1,
        "pending": 0,
        "failed": 0
      }
    },
    "L2": {
      "status": "pending",
      "totalModules": 1,
      "completedModules": 0
    }
  },
  "subagents": [
    {
      "label": "L3-chunk1",
      "status": "completed",
      "files": 16,
      "startTime": "2026-03-07T10:17:00+08:00",
      "endTime": "2026-03-07T10:25:00+08:00"
    }
  ],
  "lastCheckpoint": "2026-03-07T10:40:00+08:00",
  "canResume": true
}
```

### 断点续传

**恢复流程**:
1. 检测状态文件是否存在
2. 解析状态文件，获取已完成进度
3. 询问用户是否恢复进度
4. 如果确认恢复：
   - 跳过已完成的分片
   - 重新启动失败的子代理
   - 继续处理剩余文件

---

## 二次扫描查漏

### 扫描流程

```powershell
# 1. 获取所有 Java 文件
$javaFiles = Get-ChildItem "<模块路径>/src/main/java" -Include *.java -Recurse

# 2. 获取所有已生成文档
$docFiles = Get-ChildItem "<项目根目录>/.ai-doc/<模块名>" -Include *.md -Recurse

# 3. 构建文档路径映射
$docMap = @{}
foreach ($doc in $docFiles) {
    $relative = $doc.FullName.Replace("<项目根目录>/.ai-doc/<模块名>/", "").Replace(".md", "")
    $docMap[$relative] = $doc.FullName
}

# 4. 对比找出缺失
$missing = @()
foreach ($java in $javaFiles) {
    $relative = $java.FullName.Replace("<模块路径>/src/main/java/", "")
    $expectedDoc = "<项目根目录>/.ai-doc/<模块名>/$relative.md"
    
    if (!(Test-Path $expectedDoc)) {
        # 检查是否应该跳过
        $content = Get-Content $java.FullName -Raw
        $lineCount = (Get-Content $java.FullName).Count
        
        if (ShouldSkip -Content $content -LineCount $lineCount) {
            Write-Host "✓ 跳过 (简单类): $relative"
        } else {
            Write-Host "✗ 缺失文档：$relative"
            $missing += $relative
        }
    }
}

# 5. 处理缺失文件
if ($missing.Count -gt 0) {
    Write-Host "发现 $($missing.Count) 个文件缺失文档，spawn 补充任务..."
    Spawn subagent to process missing files
} else {
    Write-Host "✓ 所有业务类都有文档可依！"
}
```

### 跳过判断逻辑（伪代码示例）

```
// 以下仅为逻辑说明，实际使用 PowerShell 或原生工具实现

判断跳过条件:
1. 文件行数 < 50 行 且 只包含字段定义 → 跳过
2. 包含 "enum" 且 无复杂方法 → 跳过
3. 包含 "public interface" 且 无方法实现 → 跳过
4. 纯数据类（只有字段和 getter/setter）→ 跳过
5. 测试类（包含 @Test 或类名含 Test）→ 跳过
```

---

## 文件读取技巧

### PowerShell 读取

```powershell
# 基础读取
$content = Get-Content $filePath -Raw -Encoding UTF8

# 读取行数
$lines = (Get-Content $filePath).Count

# 读取前 N 行
$firstN = Get-Content $filePath -First 50

# 读取后 N 行
$lastN = Get-Content $filePath -Tail 50
```

### 安全限制处理

如果文件被安全软件限制访问：

1. **记录失败文件**: 在日志中标注无法访问的文件
2. **请求用户协助**: 请求用户确认文件访问权限
3. **跳过该文件**: 继续处理其他文件
4. **最终报告**: 在完成任务后统一报告无法访问的文件

**⚠️ 禁止事项**:
- 禁止尝试使用外部工具或替代读取方式
- 禁止尝试提权或绕过安全限制
- 禁止修改安全软件配置

---

## 最佳实践

### 1. 分片大小调整

- 初次执行使用标准分片（10-16 文件/片）
- 如果频繁超时，减小分片到 5-8 文件/片
- 如果执行顺利，可以适当增大分片到 18-20 文件/片

### 2. 上下文管理

- 每处理 2-3 个文件立即压缩
- 不要保留已生成文档的完整内容
- 只保留路径 +1 行摘要
- 接近 50% 阈值时提前压缩

### 3. 错误预防

-  spawn 子代理前检查文件路径
- 确保输出目录存在
- 设置合理的超时时间
- 记录详细的错误日志

### 4. 质量保证

- 二次扫描查漏（推荐执行）
- 检查生成文档的内容质量
- 确保无代码片段
- 确保业务描述详细

---

*Module Analyzer Generate Doc Skill • Task Execution Guide*
