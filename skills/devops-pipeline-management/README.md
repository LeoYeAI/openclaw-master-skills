# Pipeline Management Skill 使用指南

本文档介绍如何在 Claude 会话中使用 Pipeline Management Skill。

## 环境准备

在使用 Skill 之前，需要先设置环境变量：

```bash
export DEVOPS_DOMAIN_ACCOUNT="user@company.com"
export DEVOPS_BFF_URL="https://one-dev.iflytek.com/devops"
```

## 功能列表

| 功能 | 命令 | 说明 |
|-----|------|------|
| 流水线列表查询 | list | 分页查询流水线 |
| 流水线详情查询 | detail | 获取流水线详细信息 |
| 流水线创建 | create | 创建新流水线 |
| 流水线执行 | run | 手动触发流水线执行 |
| 流水线取消 | cancel | 取消正在执行的流水线 |
| 流水线删除 | delete | 删除指定流水线 |
| 流水线执行详情 | run-detail | 获取执行记录详情 |

## 触发关键词

| 用户意图 | 触发的命令 | 说明 |
|---------|----------|------|
| "查看流水线列表" | list | 查询流水线列表 |
| "我的流水线有哪些" | list | 查询流水线列表 |
| "查看流水线详情" | detail | 获取流水线详情 |
| "创建流水线" | create | 创建新流水线 |
| "执行流水线123" | run 123 | 运行指定流水线 |
| "运行这个流水线" | run | 运行流水线 |
| "取消流水线执行" | cancel | 停止正在执行的流水线 |
| "停止流水线" | cancel | 停止正在执行的流水线 |
| "删除流水线" | delete | 删除指定流水线 |
| "移除这个流水线" | delete | 删除指定流水线 |
| "查看执行详情" | run-detail | 获取执行详情 |

## 使用示例

### 示例1：查看流水线列表

```
你: 查看一下我的流水线列表

Claude: (自动触发 list 命令)
```

### 示例2：查看流水线详情

```
你: 查看流水线12345的详情

Claude: (自动触发 detail 12345 命令)
```

### 示例3：创建流水线

```
你: 创建一个名为my-pipeline的流水线

Claude: (自动触发 create my-pipeline 命令)
```

### 示例4：执行流水线

```
你: 执行ID为12345的流水线

Claude: (自动触发 run 12345 命令)
```

### 示例5：取消流水线执行

```
你: 取消流水线12345的执行

Claude: (自动触发 cancel 12345 命令)
```

### 示例6：删除流水线

```
你: 删除ID为67890的流水线

Claude: (自动触发 delete 67890 命令)
```

### 示例7：查看执行详情

```
你: 查看流水线12345的执行详情run-67890

Claude: (自动触发 run-detail 12345 run-67890 命令)
```

## 命令行直接调用

你也可以直接在命令行中调用这些脚本：

```bash
# 查看所有命令
python pipeline-management/scripts/main.py

# 流水线列表
python pipeline-management/scripts/main.py list

# 流水线详情
python pipeline-management/scripts/main.py detail <pipeline_id>

# 创建流水线
python pipeline-management/scripts/main.py create <name> [space_id>

# 执行流水线
python pipeline-management/scripts/main.py run <pipeline_id> [branch]

# 取消流水线
python pipeline-management/scripts/main.py cancel <pipeline_id>

# 删除流水线
python pipeline-management/scripts/main.py delete <pipeline_id>

# 执行详情
python pipeline-management/scripts/main.py run-detail <pipeline_id> <run_id>
```

## 注意事项

1. **domain_account 为必填参数**：用于权限校验和操作审计
2. **删除操作不可恢复**：请谨慎使用 delete 命令
3. **取消操作有限制**：只能取消正在执行的流水线
4. **创建需要权限**：需要有创建流水线的权限

## 参考文档

详见 `references/` 目录下的子功能文档：

- [pipeline-list.md](references/pipeline-list.md) - 流水线列表查询
- [pipeline-detail.md](references/pipeline-detail.md) - 流水线详情查询
- [pipeline-create.md](references/pipeline-create.md) - 流水线创建
- [pipeline-run.md](references/pipeline-run.md) - 流水线执行
- [pipeline-cancel.md](references/pipeline-cancel.md) - 流水线取消
- [pipeline-delete.md](references/pipeline-delete.md) - 流水线删除
- [pipeline-run-detail.md](references/pipeline-run-detail.md) - 流水线执行详情
