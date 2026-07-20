---
name: amemo-find-task
description: 当用户说「查看清单/查询清单/我的待办/查看任务/列出任务」时调用，返回按今日/明日/近期/未来分组的完整待办清单。
---

# amemo-find-task — 查询任务

---

## 接口信息

| 属性 | 值 |
|:-----|:---|
| **路由** | `POST https://skill.amemo.cn/find-task` |
| **Bean** | `TaskBean` |
| **Content-Type** | `application/json` |

---

## 请求参数

> ⚠️ 服务端要求所有字段必须存在。`userToken` 必填且有值，其他字段可选但字段必须存在。

| 参数 | 类型 | 必填 | 说明 |
|:-----|:----:|:----:|:-----|
| `userToken` | str | ✅ | 用户登录凭证 |
| `taskId` | str | — | 按 ID 精确查询，不传则传 `null` |
| `taskTitle` | str | — | 按标题模糊查询，不传则传 `null` |
| `taskTime` | str | — | 按时间筛选，不传则传 `null` |
| `taskEmail` | list[str] | — | 按邮箱筛选，不传则传 `null` |

---

## 请求示例

```bash
# 查询所有任务（所有可选字段传 null）
curl -X POST https://skill.amemo.cn/find-task \
  -H "Content-Type: application/json" \
  -d '{
    "userToken": "<token>",
    "taskId": null,
    "taskTitle": null,
    "taskTime": null,
    "taskEmail": null
  }'

# 按标题查询
curl -X POST https://skill.amemo.cn/find-task \
  -H "Content-Type: application/json" \
  -d '{
    "userToken": "<token>",
    "taskId": null,
    "taskTitle": "报告",
    "taskTime": null,
    "taskEmail": null
  }'
```

---

## 响应数据结构

```json
{
  "code": 200,
  "desc": "success",
  "data": {
    "recommend": [],
    "myFollow": [],
    "todayList": [],
    "tomorrowList": [],
    "recentList": [],
    "finishList": [],
    "futureList": []
  }
}
```

### TaskInfo 任务信息

| 字段 | 类型 | 说明 |
|:-----|:----:|:-----|
| `taskId` | str | 任务唯一标识 |
| `taskTitle` | str | 任务标题 |
| `recentRemindTime` | int | 最近的提醒时间 |

---

## 待办清单展示模板

### 无数据时回复

```markdown
**📋 暂无待办清单**

> 创建新任务 →
> • 「今天 3 点开会」
> • 「提醒我明天交报告」
```

---

### 任务清单展示模板

```markdown
**✅ 待办清单** · 共 {total} 项

---

### 📅 今日待办

- ⏳ {task1}
- ⏳ {task2}
- ⏳ {task3}

---

### 📆 明日待办 ({count})

- ⏳ {task1}

---

### 📋 近期待办 ({count})

- ⏳ {task1}

---

### 🔮 未来待办 ({count})

- ⏳ {task1}

---

### ⭐ 收藏 ({count})

- ★ {task1}

---

### ✔ 已完成 ({count})

- ✓ {task1}
```

---

### 单个任务项格式化

| 任务类型 | 格式 |
|:---------|:-----|
| 待做任务 | `{index}. {taskTitle}` |
| 收藏任务 | `{index}. ⭐ {taskTitle}` |
| 已完成任务 | `{index}. ✔ {taskTitle}` |

---

### 任务状态图标

| 状态 | 图标 | 说明 |
|:-----|:----:|:-----|
| pending | ⏳ | 待完成 |
| completed | ✔ | 已完成 |
| expired | ❌ | 已过期 |
| follow | ⭐ | 已收藏 |

---

### 分组展示优先级

| 优先级 | 分类 | 说明 |
|:------:|:-----|:-----|
| 1 | 今日待办 | 今日必须完成的任务，优先展示 |
| 2 | 明日待办 | 明日计划的任务 |
| 3 | 近期待办 | 未来15天内的任务 |
| 4 | 未来待办 | 15天之后的任务 |
| 5 | 我的收藏 | 用户收藏的重要任务 |
| 6 | 已完成 | 已完成的任务 |

---

### 分类计数统计

```markdown
| 分类 | 数量 |
|:-----|:----:|
| 今日待办 | {count} |
| 明日待办 | {count} |
| 近期待办 | {count} |
| 未来待办 | {count} |
| 我的收藏 | {count} |
| 已完成 | {count} |
| **总计** | **{count}** |
```

---

### 任务为空时处理

如果某分类为空：

| 分类 | 空状态提示 |
|:-----|:----------|
| 今日/明日/近期 | `暂无15天内待办` |
| 未来 | `暂无未来待办` |
| 收藏 | `暂无收藏任务` |
| 已完成 | `暂无已完成任务` |

---


## 输出示例

```markdown
**✅ 待办清单** · 共 17 项

---

### 📅 今日待办

- ⏳ 完成项目报告
- ⏳ 提交代码审查
- ⏳ 准备会议材料

---

### 📆 明日待办 (2)

- ⏳ 产品需求评审
- ⏳ 团队周会

---

### 📋 近期待办 (4)

- ⏳ 客户方案调整
- ⏳ 技术文档更新
- ⏳ 测试报告评审
- ⏳ 版本发布准备

---

### 🔮 未来待办 (2)

- ⏳ 季度 OKR 制定
- ⏳ 年度总结规划

---

### ⭐ 收藏 (1)

- ★ 年度总结

---

### ✔ 已完成 (5)

- ✓ 登录功能开发
- ✓ 数据库优化
- ✓ API 接口调试
- ✓ 前端页面联调
- ✓ 部署文档编写
```

---

## 调用示例

### 示例一：查看待办清单

**用户输入：**
```
查看我的待办清单
```

**系统处理：**
1. 检查 `userToken`
2. 调用 `POST /find-task`
3. 解析返回数据，按分类组织展示

### 示例二：查找清单

**用户输入：**
```
查找我的清单
```

**系统处理：**
1. 检查 `userToken`
2. 调用 `POST /find-task`
3. 格式化输出给用户

---

## 执行流程（由主模块调度）

### 执行步骤

```
1. 识别触发词（查看/查询/列出 + 清单/任务/待办）
    ↓
2. 检查 userToken 是否存在
    ├── 无 token → 引导登录流程
    ↓
3. 调用 POST /find-task 接口
    ↓
4. 解析返回数据
    ├── todayList: 今日列表
    ├── tomorrowList: 明日列表
    ├── recentList: 近期列表（15天内）
    ├── futureList: 未来列表
    ├── finishList: 已完成列表
    └── myFollow: 我的收藏
    ↓
5. 按分类组织并格式化输出
```

---

## 回复模板

### 无数据时

```markdown
**📋 暂无待办清单**

> 创建新任务 →
> • 「今天 3 点开会」
> • 「提醒我明天交报告」
```
