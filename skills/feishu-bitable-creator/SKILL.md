---
name: feishu-bitable-creator
description: |
  Create and populate Feishu (Lark) Bitable (multidimensional tables) with automated cleanup.
  Use when the user needs to:
  1. Create a new Bitable from scratch with clean structure (no placeholder rows/columns)
  2. Batch create fields and records in a Bitable
  3. Convert structured data into a Bitable format
  4. Create data tables for research, comparison, or tracking purposes
  
  Automatically handles: empty placeholder row cleanup, default column removal, 
  intelligent primary field naming, and batch record creation.
metadata:
  openclaw:
    requires:
      config: ["channels.feishu.appId", "channels.feishu.appSecret"]
    emoji: 📊
---

# Feishu Bitable Creator

Creates clean, ready-to-use Feishu Bitable tables with automatic cleanup and data population.

## Authentication & Permissions

This skill requires a **pre-configured Feishu (Lark) integration** via OpenClaw's channel system. It does not accept API keys directly from the user.

### How Authentication Works

1. **Feishu Channel Configuration**: Your OpenClaw instance must have the Feishu channel enabled and configured with a valid app ID and app secret in `~/.openclaw/openclaw.json`:
   ```json
   {
     "channels": {
       "feishu": {
         "enabled": true,
         "appId": "cli_xxxxxxxxxxxxxxxx",
         "appSecret": "your-app-secret"
       }
     }
   }
   ```

2. **Token Management**: OpenClaw's Feishu extension automatically handles token acquisition and refresh using the configured app credentials. No manual token management is required.

3. **User Consent**: When creating a table, the tool uses the **agent's own identity** (the Feishu app/bot). The `addBitableAdmin()` function requires the owner's explicit `user_id` obtained from the conversation context, ensuring consent.

### Required Feishu App Permissions

Your Feishu app must have these permissions granted:

| Permission | Purpose |
|------------|---------|
| `bitable:app` | Create and manage Bitable apps |
| `drive:permission:manage` | Add users as admins to documents |
| `drive:drive:read` | Read drive contents |

### Security Notes

- ⚠️ **No User-Supplied Credentials**: This skill does NOT accept API keys, tokens, or secrets from user prompts. All authentication is handled through OpenClaw's secure channel configuration.
- ⚠️ **Scope Limitation**: The skill only performs actions on Bitable tables it creates. It cannot access existing tables without explicit sharing.
- ⚠️ **Admin Addition Requires Explicit User ID**: Adding an admin requires the specific `user_id` from conversation context — the agent cannot arbitrarily add unknown users.

### Setup Instructions

Before using this skill, ensure your OpenClaw host admin has:

1. Created a Feishu app at https://open.feishu.cn/app
2. Enabled the required permissions in the Feishu app console
3. Configured the app ID and secret in `~/.openclaw/openclaw.json`
4. Restarted the OpenClaw gateway to apply changes

For detailed setup, see: https://docs.openclaw.ai/channels/feishu

**Problem with default Bitable creation:**
- Feishu creates 10 empty placeholder rows by default
- Creates 4 default columns (文本, 单选, 日期, 附件) that are often unused
- Primary field is always named "文本" which is not descriptive
- Creator has full control, but human owner has no permissions

**This skill solves these issues:**
- ✅ Automatically deletes empty placeholder rows and default columns
- ✅ Intelligently renames primary field based on table name
- ✅ Adds owner as admin with full permissions
- ✅ Provides clean slate for your actual data

## Quick Start

```typescript
// 1. Create table (auto-cleans placeholder rows & default columns)
const table = await feishu_bitable_create_app({ name: "项目名称清单" });
// Returns: { app_token, url, table_id, primary_field_name, cleaned_placeholder_rows, cleaned_default_fields }

// 2. Add owner as admin (REQUIRED - get user_id from conversation context)
await addBitableAdmin({
  app_token: table.app_token,
  user_id: "ou_xxxxxxxxxxxxxxxx"  // Get from conversation context or Feishu user profile
});

// 3. Create RICH fields with tags/categories (建议根据场景选择)
// 参考 "Designing Rich Fields" 章节，选择适合的维度字段

// 4. Add records with complete tag information
await feishu_bitable_create_record({
  app_token: table.app_token,
  table_id: table.table_id,
  fields: {
    [table.primary_field_name]: "项目A",
    "标签": ["AI", "开源"],           // MultiSelect for filtering
    "分类": "技术",                   // SingleSelect for grouping
    "状态": "进行中",                 // SingleSelect for workflow
    "优先级": "高"                   // SingleSelect for sorting
  }
});

return table.url;
```

## Designing Rich Fields (发挥多维表格价值)

**💡 核心建议**: 为了让多维表格真正发挥作用，建议设计丰富的标签/分类字段，但**根据实际场景灵活选择**。

### 推荐的字段设计思路

根据数据类型，**考虑**添加以下维度字段：

| 数据场景 | 建议字段 | 用途 |
|---------|---------|------|
| **项目管理** | 状态、优先级、负责人、截止日期 | 追踪进展，分配任务 |
| **研究/调研** | 分类、标签、来源、评分 | 归类信息，评估价值 |
| **产品/功能** | 模块、优先级、状态、负责人 | 产品规划，迭代管理 |
| **客户/用户** | 类型、阶段、标签、负责人 | 客户分层，跟进管理 |
| **竞品分析** | 分类、评分、标签、来源 | 对比分析，筛选查看 |

### 字段类型选择指南

| 字段名 | 类型 | 适用场景 |
|--------|------|---------|
| **标签** | MultiSelect | 一个项目可属于多个类别，用于交叉筛选 |
| **分类** | SingleSelect | 一级分类，用于分组统计 |
| **状态** | SingleSelect | 有明确流转阶段，如待办→进行中→完成 |
| **优先级** | SingleSelect | 需要排序或区分重要性 |
| **负责人** | User | 需要分配到人 |
| **日期** | DateTime | 有时间节点要求 |
| **评分** | Number | 需要量化评估 |
| **来源** | SingleSelect | 需要追踪信息出处 |

### 实际设计示例

**示例1：开源大模型研究**
```typescript
const fields = [
  { name: "模型名称", type: 1 },
  { name: "开发团队", type: 1 },
  { name: "参数量", type: 1 },
  // 维度字段（根据数据特点选择）
  { name: "技术标签", type: 4 },      // ["MoE", "多语言", "代码", "轻量级"]
  { name: "地区", type: 3 },          // "美国"/"中国"/"欧洲"
  { name: "模型类型", type: 3 },      // "通用"/"代码"/"推理"
  { name: "适用场景", type: 4 },      // ["企业部署", "端侧运行", "科研"]
  { name: "开源协议", type: 3 },      // "Apache-2.0"/"MIT"
  { name: "发布日期", type: 5 },
  { name: "特点描述", type: 1 }
];
```

**示例2：工作任务清单**
```typescript
const fields = [
  { name: "任务名称", type: 1 },
  { name: "描述", type: 1 },
  // 维度字段
  { name: "分类", type: 3 },          // "技术"/"产品"/"运营"
  { name: "状态", type: 3 },          // "待办"/"进行中"/"已完成"
  { name: "优先级", type: 3 },        // "P0"/"P1"/"P2"
  { name: "负责人", type: 11 },       // @username
  { name: "截止日期", type: 5 },
  { name: "标签", type: 4 }           // ["紧急", "重要", "外部依赖"]
];
```

### 设计原则

1. **先想怎么用**：先思考用户会如何筛选/分组/排序数据
2. **适度原则**：字段不是越多越好，选择真正能区分数据的维度
3. **数据可得**：确保收集数据时能填上这些字段，不要设计无法获取的维度
4. **灵活调整**：如果某个字段使用率很低，后续可以删除或修改

### 检验标准

设计完字段后，问自己：
- ❓ 用户能按哪些维度筛选数据？
- ❓ 能按哪些维度分组查看？
- ❓ 能按哪些维度排序？
- ❓ 数据收集时这些字段是否容易获取？

如果以上问题都有明确答案，说明字段设计合理！

### 实际示例：开源大模型表格

```typescript
// 创建表格
const table = await feishu_bitable_create_app({ name: "全球开源大模型TOP10" });

// 添加管理员
await addBitableAdmin({ app_token: table.app_token, user_id: bossUserId });

// 创建丰富的字段（带标签/分类）
const fields = [
  { name: "排名", type: 2 },                                    // Number
  { name: "模型名称", type: 1 },                                // Text
  { name: "开发团队", type: 1 },                                // Text
  { name: "参数量", type: 1 },                                  // Text
  { name: "标签", type: 4, property: { options: [              // MultiSelect
    { name: "MoE" }, { name: "多语言" }, { name: "代码" }, 
    { name: "轻量级" }, { name: "推理优化" }, { name: "国产" }
  ]}},
  { name: "地区", type: 3, property: { options: [              // SingleSelect
    { name: "美国" }, { name: "中国" }, { name: "欧洲" }, 
    { name: "中东" }, { name: "其他" }
  ]}},
  { name: "类型", type: 3, property: { options: [               // SingleSelect
    { name: "通用模型" }, { name: "代码模型" }, { name: "推理模型" }
  ]}},
  { name: "开源协议", type: 3, property: { options: [           // SingleSelect
    { name: "Apache-2.0" }, { name: "MIT" }, { name: "Llama License" },
    { name: "Qwen License" }
  ]}},
  { name: "GitHub星标", type: 2 },                              // Number
  { name: "发布日期", type: 5 },                                // DateTime
  { name: "特点", type: 1 },                                    // Text
  { name: "适用场景", type: 4, property: { options: [           // MultiSelect
    { name: "企业部署" }, { name: "端侧运行" }, { name: "科学研究" },
    { name: "商业应用" }, { name: "教育学习" }
  ]}}
];

for (const field of fields) {
  await feishu_bitable_create_field({
    app_token: table.app_token,
    table_id: table.table_id,
    field_name: field.name,
    field_type: field.type,
    property: field.property
  });
}

// 添加带完整标签的数据
await feishu_bitable_create_record({
  app_token: table.app_token,
  table_id: table.table_id,
  fields: {
    [table.primary_field_name]: "Llama 3",
    "模型名称": "Llama 3",
    "排名": 1,
    "开发团队": "Meta",
    "参数量": "8B/70B/400B",
    "标签": ["多语言"],
    "地区": "美国",
    "类型": "通用模型",
    "开源协议": "Llama License",
    "GitHub星标": 50000,
    "发布日期": 1713398400000,  // 2024-04-18
    "特点": "开源模型领导者，性能对标GPT-4",
    "适用场景": ["企业部署", "商业应用", "科学研究"]
  }
});
```

## Add Owner as Admin

**IMPORTANT**: Tool creates table but does NOT add permissions. You must add the owner as admin manually.

```typescript
/**
 * Add a user as admin to a Bitable table
 * @param app_token - The Bitable app token
 * @param user_id - The user's open_id (from conversation context)
 */
async function addBitableAdmin({ app_token, user_id }) {
  const token = await getTenantAccessToken();
  
  const response = await fetch(
    `https://open.feishu.cn/open-apis/drive/v1/permissions/${app_token}/members/batch_create?type=bitable`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        members: [{
          member_type: 'openid',
          member_id: user_id,
          perm: 'full_access'
        }]
      })
    }
  );
  
  const result = await response.json();
  if (result.code === 0) {
    console.log('✅ Successfully added owner as admin');
    return result.data;
  } else {
    throw new Error(result.msg);
  }
}
```

### Required Permissions
- `bitable:app` - Manage Bitable apps
- `drive:permission:manage` - Manage document permissions

## Primary Field Naming

| Table name contains | Primary field becomes |
|---------------------|----------------------|
| "项目" | "项目名称" |
| "研究" | "研究名称" |
| "测试" | "测试项" |
| "数据" | "数据项" |
| "任务" | "任务名称" |
| "记录" | "记录项" |
| Other (≤6 chars) | Use table name as-is |
| Other (>6 chars) | First 4 chars + "..." |

## Common Field Types

| Type ID | Name | Use For |
|---------|------|---------|
| 1 | Text | Names, descriptions |
| 2 | Number | Counts, amounts |
| 3 | SingleSelect | Status, priority |
| 4 | MultiSelect | Tags, features |
| 5 | DateTime | Dates, deadlines |
| 7 | Checkbox | Done/Incomplete |
| 11 | User | Assignees |

## Complete Example: Research Data Table with Rich Tags

```typescript
async function createBitableForBoss({ tableName, records, bossUserId }) {
  // 1. Create table
  const table = await feishu_bitable_create_app({ name: tableName });
  
  // 2. Add owner as admin
  await addBitableAdmin({
    app_token: table.app_token,
    user_id: bossUserId
  });
  
  // 3. Create RICH fields with tags/categories (关键！)
  const fields = [
    { name: "排名", type: 2 },
    { name: "名称", type: 1 },
    { name: "标签", type: 4 },           // MultiSelect - 最关键！
    { name: "分类", type: 3 },           // SingleSelect
    { name: "状态", type: 3 },           // SingleSelect
    { name: "优先级", type: 3 },         // SingleSelect
    { name: "负责人", type: 11 },        // User
    { name: "来源", type: 3 },           // SingleSelect
    { name: "评分", type: 2 },           // Number
    { name: "日期", type: 5 },           // DateTime
    { name: "描述", type: 1 }            // Text
  ];
  
  for (const field of fields) {
    await feishu_bitable_create_field({
      app_token: table.app_token,
      table_id: table.table_id,
      field_name: field.name,
      field_type: field.type
    });
  }
  
  // 4. Add records with complete tags
  for (const record of records) {
    await feishu_bitable_create_record({
      app_token: table.app_token,
      table_id: table.table_id,
      fields: {
        [table.primary_field_name]: record.name,
        "名称": record.name,
        "标签": record.tags,              // 必填！
        "分类": record.category,          // 必填！
        "状态": record.status || "待处理",
        "优先级": record.priority || "中",
        "来源": record.source || "搜索",
        "描述": record.description
      }
    });
  }
  
  return {
    url: table.url,
    message: `✅ Table created with rich tags: ${table.url}`
  };
}

// Usage
const result = await createBitableForBoss({
  tableName: "AI开源项目研究",
  records: [
    {
      name: "AutoGPT",
      tags: ["AI代理", "自动化", "热门"],      // MultiSelect
      category: "智能体",                       // SingleSelect
      priority: "高",
      source: "GitHub",
      description: "自主递归任务执行AI代理"
    }
  ],
  bossUserId: "ou_xxxxxxxxxxxxxxxx"  // Replace with actual user's open_id
});
```
    { name: "GitHub星标", type: 2 },
    { name: "使用场景", type: 4 }
  ],
  records: [{
    "AI框架对比": "AutoGPT",
    "框架名称": "AutoGPT",
    "GitHub星标": 157000,
    "使用场景": ["自动化", "研究"]
  }],
  bossUserId: "ou_xxxxxxxxxxxxxxxx"  // Replace with actual user's open_id
});
```

## Tips

1. **设计丰富的标签字段**: 为了让多维表格发挥作用，建议根据数据特点添加标签、分类、状态等维度字段（参考 "Designing Rich Fields" 章节）

2. **根据场景选择字段**: 不同数据类型需要不同的维度字段，如项目管理需要"状态"，研究调研需要"来源"，灵活设计

3. **先想怎么用**: 设计字段前先思考用户会如何筛选/分组/排序数据

4. **Multi-select values**: Pass as array: `["标签A", "标签B"]`

5. **User ID**: Get from conversation context (e.g., `ou_xxxxxxxxxxxxxxxx`)

6. **Cleanup verified**: Tool returns `cleaned_placeholder_rows` and `cleaned_default_fields`

7. **Field order**: Create fields first, then add records

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| FieldNameNotFound | Wrong primary field name | Check `primary_field_name` in result |
| 400 Bad Request | Invalid field type/value | Verify field_type ID |
| Permission Denied | Missing `drive:permission:manage` | Check app permissions |
| User Not Found | Wrong user_id format | Use `openid` type |

## Output Format

```
✅ Table "项目名称" created successfully!

🔗 URL: https://my.feishu.cn/base/xxxxxxxxxxxxx
🧹 Cleanup: 10 placeholder rows, 4 default columns deleted
👤 Owner: Added as admin (full_access)
📊 Records: X records added
📝 Fields: 名称, 标签, 分类, 状态, 优先级, 负责人, 日期, 描述
💡 Tip: 建议添加标签/分类/状态等维度字段，让表格支持多维筛选和分组
```

**设计检查建议**:
- 是否可以根据标签交叉筛选数据？
- 是否可以按分类分组查看？
- 是否可以按状态/优先级排序？
- 数据收集时这些字段是否容易获取？

如果以上问题都有答案，说明字段设计合理！
- ✅ 优先级 (SingleSelect) - for sorting
