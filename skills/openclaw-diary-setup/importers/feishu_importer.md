# 飞书用户档案导入器实现指南

## 概述

从飞书云文档导入用户档案信息。使用 OpenClaw 的飞书 MCP 工具实现。

## 导入目的

**不是导入日记数据**，而是导入描述用户身份的文档：
- 个人简介
- 年度总结
- 关于我
- 工作总结
- 任何描述用户是谁、在做什么的文档

**目的**：建立用户档案，让 AI 更了解用户。

## 前置条件

- 用户已提供飞书应用授权（App ID 和 App Secret）
- 环境变量已设置：`FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
- 用户在飞书中有日记文档

## 实现步骤

### 步骤 1：搜索或指定文档

**方式 A：让用户指定文档名**

询问用户："你的个人档案文档叫什么名字？比如：关于我、个人简介、年度总结"

使用 `mcp__feishu__docx_builtin_search` 搜索文档。

**调用参数**：
```json
{
  "data": {
    "search_key": "关于我",  // 用户提供的文档名
    "docs_types": ["docx"],
    "count": 10
  },
  "useUAT": true
}
```

**方式 B：让用户提供文档链接**

如果用户直接提供飞书文档链接，从链接中提取 `document_id`。

**链接格式**：
```
https://example.feishu.cn/docx/doxcnXXXXXXXXXXXXXXXXXXXXXXX
```

提取 `doxcnXXXXXXXXXXXXXXXXXXXXXXX` 作为 `document_id`。

### 步骤 2：读取文档内容

使用 `mcp__feishu__docx_v1_document_rawContent` 读取文档内容。

**调用参数**：
```json
{
  "path": {
    "document_id": "doxcnXXXXXXXXXXXXXXXXXXXXXXX"
  },
  "params": {
    "lang": 0
  },
  "useUAT": true
}
```

**返回结果示例**：
```json
{
  "data": {
    "content": "# 关于我\n\n我是一名软件工程师，专注于 Web 开发和 AI 应用。\n\n## 专业背景\n\n- 5年 Web 开发经验\n- 熟悉 React、Node.js\n- 目前在探索 AI 应用开发\n\n## 目标\n\n- 成为全栈工程师\n- 构建有影响力的产品\n\n## 兴趣爱好\n\n- 阅读技术博客\n- 开源贡献\n- 跑步"
  }
}
```

### 步骤 3：AI 提取和结构化

使用 AI 能力从文档内容中提取关键信息。

**提取的关键信息**：
- **角色和职业** - "软件工程师"
- **工作领域** - "Web 开发和 AI 应用"
- **专业背景** - "5年 Web 开发经验，熟悉 React、Node.js"
- **技能和专长** - ["React", "Node.js", "AI 应用开发"]
- **目标和追求** - "成为全栈工程师，构建有影响力的产品"
- **兴趣爱好** - ["阅读技术博客", "开源贡献", "跑步"]

**AI 提示词示例**：
```
从以下文档中提取用户的关键信息：

{文档内容}

请提取：
1. 角色和职业
2. 工作领域和专业背景
3. 技能和专长（列表）
4. 目标和追求
5. 价值观和思维方式
6. 兴趣爱好（列表）
7. 重要经历

以结构化的方式输出。
```

### 步骤 4：创建用户身份文件

**确定输出路径**：
- 基础路径：`~/write_me/01studio/me/`
- 文件名：`identity.md`
- 完整路径：`~/write_me/01studio/me/identity.md`

**写入逻辑**：
1. 展开 `~` 为完整路径
2. 创建目录（如果不存在）：
   ```bash
   mkdir -p ~/write_me/01studio/me
   ```
3. 使用 Write 工具写入文件

**文件内容格式**：
```markdown
---
created: 2026-03-14
updated: 2026-03-14
source: feishu
source_url: https://example.feishu.cn/docx/xxx
---

# 用户身份

## 基本信息

**角色**：软件工程师
**工作领域**：Web 开发和 AI 应用

## 专业背景

5年 Web 开发经验，熟悉 React、Node.js，目前在探索 AI 应用开发。

## 技能和专长

- React
- Node.js
- AI 应用开发

## 目标和追求

成为全栈工程师，构建有影响力的产品。

## 兴趣爱好

- 阅读技术博客
- 开源贡献
- 跑步

---

## 原始内容

<details>
<summary>点击查看从飞书导入的原始内容</summary>

# 关于我

我是一名软件工程师，专注于 Web 开发和 AI 应用。

## 专业背景

- 5年 Web 开发经验
- 熟悉 React、Node.js
- 目前在探索 AI 应用开发

## 目标

- 成为全栈工程师
- 构建有影响力的产品

## 兴趣爱好

- 阅读技术博客
- 开源贡献
- 跑步

</details>
```

### 步骤 5：确认和调整

向用户展示提取的信息：

```
我从你的飞书文档中提取了以下信息：

【展示结构化的用户身份】

这些信息准确吗？需要补充或修改什么吗？
```

允许用户：
- 确认无误
- 补充信息
- 修改不准确的部分

## 错误处理

### 授权失败

**错误信息**：
```json
{
  "code": 99991663,
  "msg": "app access token invalid"
}
```

**处理方式**：
```
❌ 飞书授权失败

可能的原因：
1. App ID 或 App Secret 不正确
2. 应用权限不足
3. 环境变量未设置

请检查：
- FEISHU_APP_ID 是否正确
- FEISHU_APP_SECRET 是否正确
- 应用是否有"读取云文档"权限

获取授权信息：https://open.feishu.cn/app
```

### 搜索无结果

**处理方式**：
```
未找到飞书日记文档。

可能的原因：
1. 飞书中没有包含"日记"关键词的文档
2. 文档权限不足，无法访问

建议：
- 检查飞书中是否有日记文档
- 确认文档标题包含"日记"关键词
- 确认应用有权限访问这些文档
```

### 读取文档失败

**错误信息**：
```json
{
  "code": 1254044,
  "msg": "document not found"
}
```

**处理方式**：
```
❌ 无法读取文档：{文档标题}

可能的原因：
1. 文档已被删除
2. 文档权限不足
3. 文档 ID 无效

跳过此文档，继续导入其他文档...
```

### 文件写入失败

**处理方式**：
```
❌ 无法写入文件：{文件路径}

可能的原因：
1. 目录不存在或无权限
2. 磁盘空间不足
3. 文件被占用

建议：
- 检查目录权限：ls -la ~/write_me/00inbox/journal/
- 检查磁盘空间：df -h
- 尝试手动创建目录：mkdir -p ~/write_me/00inbox/journal/imported
```

## 实现示例

### 完整流程伪代码

```python
def import_from_feishu(auth_info, output_dir):
    """从飞书导入日记"""

    # 步骤 1：搜索文档
    print("正在搜索飞书日记文档...")
    search_result = mcp__feishu__docx_builtin_search({
        "data": {
            "search_key": "日记",
            "docs_types": ["docx"],
            "count": 50
        },
        "useUAT": True
    })

    docs = search_result["data"]["docs"]
    print(f"✓ 找到 {len(docs)} 个日记文档")

    # 过滤日记文档
    diary_docs = [doc for doc in docs if "日记" in doc["title"]]

    # 步骤 2-3：读取和解析
    imported_count = 0
    for doc in diary_docs:
        print(f"正在读取：{doc['title']}")

        # 读取文档内容
        content_result = mcp__feishu__docx_v1_document_rawContent({
            "path": {"document_id": doc["document_id"]},
            "params": {"lang": 0},
            "useUAT": True
        })

        content = content_result["data"]["content"]

        # 添加导入标记
        import_info = f"""
> **导入信息**：从飞书文档导入
> **原始文档**：{doc['title']}
> **导入时间**：{current_time}
> **文档链接**：{doc['url']}

---

{content}
"""

        # 步骤 4：写入本地
        month = extract_month_from_title(doc['title'])  # 如 "2026-03"
        file_path = f"{output_dir}/imported/{month}.md"

        write_file(file_path, import_info)
        print(f"✓ {doc['title']} ({count_entries(content)} 条记录)")
        imported_count += count_entries(content)

    # 步骤 5：显示结果
    print(f"\n✓ 飞书导入完成！")
    print(f"- 文档数量：{len(diary_docs)} 个")
    print(f"- 记录总数：{imported_count} 条")
    print(f"- 保存位置：{output_dir}/imported/")

    return {
        "success": True,
        "count": imported_count,
        "docs": len(diary_docs)
    }
```

## 测试

### 测试场景

1. **正常导入**：
   - 飞书中有 3 个日记文档
   - 每个文档包含多条记录
   - 预期：成功导入所有文档

2. **无文档**：
   - 飞书中没有日记文档
   - 预期：提示未找到文档

3. **授权失败**：
   - App ID 或 App Secret 错误
   - 预期：提示授权失败，提供解决方案

4. **部分失败**：
   - 3 个文档中有 1 个无法读取
   - 预期：跳过失败的文档，继续导入其他文档

### 测试数据

创建测试用的飞书文档：
- 标题：`日记 2026-03`
- 内容：包含多条日记记录
- 格式：符合 diary skill 的标准格式

## 优化建议

### 1. 批量读取

如果文档数量很多，可以并行读取：
- 使用多个 MCP 调用同时读取
- 提高导入速度

### 2. 增量导入

记录已导入的文档：
- 保存导入历史
- 下次只导入新文档
- 避免重复导入

### 3. 内容验证

验证导入的内容：
- 检查格式是否正确
- 统计条目数量
- 提供预览功能

### 4. 冲突处理

如果本地已有同名文件：
- 提供选项：覆盖 / 合并 / 跳过
- 智能合并：去重，按时间排序

---

最后更新：2026-03-14
