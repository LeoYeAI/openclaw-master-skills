---
name: amemo-find-data
description: 当用户说「查看/查找我的步数/睡眠/血氧/血压/心率/消耗数据」或「XXX数据怎么样」时调用，返回该类型的历史数据列表。
---

# amemo-find-data — 查询数据

---

## 接口信息

| 属性 | 值 |
|:-----|:---|
| **路由** | `POST https://skill.amemo.cn/find-data` |
| **Bean** | `DataBean` |
| **Content-Type** | `application/json` |

---

## 请求参数

> ⚠️ 服务端要求所有字段必须存在。`userToken` 和 `dataType` 必填且有值，不可传 `null`。

| 参数 | 类型 | 必填 | 说明 |
|:-----|:----:|:----:|:-----|
| `userToken` | str | ✅ | 用户登录凭证 |
| `dataType` | str | ✅ | 数据类型（步数/睡眠/血氧/血压/心率/消耗，不能为空） |

---

## 请求示例

```bash
# 按类型查询
curl -X POST https://skill.amemo.cn/find-data \
  -H "Content-Type: application/json" \
  -d '{"userToken": "<token>", "dataType": "步数"}'
```

---

## 响应示例

```json
{
  "code": 200,
  "desc": "success",
  "data": [...]
}
```

---

## 执行流程（由主模块调度）

### 数据类型映射（6大类）

| 关键词 | dataType 参数值 |
|:-------|:---------------|
| 步数 | `步数` |
| 睡眠 | `睡眠` |
| 血氧 | `血氧` |
| 血压 | `血压` |
| 心率 | `心率` |
| 消耗 | `消耗` |

---

### 关键词提取与匹配规则

**提取示例：**

| 用户输入 | 匹配结果 |
|:---------|:---------|
| "查看我的步数数据" | 步数 |
| "查找我的睡眠记录" | 睡眠 |
| "心率数据怎么样" | 心率 |
| "消耗卡路里" | 消耗 |

**未匹配示例：**

| 用户输入 | 匹配结果 |
|:---------|:--------|
| "查看我的体重数据" | ❌ 不匹配6大类 |
| "查找我的血糖数据" | ❌ 不匹配6大类 |

---

### 执行步骤

```
1. 识别触发词（查看/查找/搜索 + 我的 + XXX + 数据）
    ↓
2. 检查 userToken 是否存在
    ├── 无 token → 引导登录流程
    ↓
3. 提取数据类型关键词
    ├── 去除：查看、查找、搜索、我的、数据、怎么样
    ├── 匹配6大类型
    ↓
4. 匹配判断
    ├── 不匹配 → 告知用户暂无可用数据类型
    ↓
5. 调用 POST /find-data 接口
    ↓
6. 数据总结输出（按对应模板格式化）
```

---

## 数据总结模板

### 📊 步数 (steps)

```markdown
**📊 步数数据**

> 今日: {latest_steps} 步 · 目标: {percentage}%
> 趋势: {trend} 比昨日 {diff} 步

| 日期 | 步数 | 进度 |
|:-----|:----:|:-----|
| {date1} | {steps1} | {bar1} |
| {date2} | {steps2} | {bar2} |
```

### 😴 睡眠 (sleep)

```markdown
**😴 睡眠数据**

> 昨晚: {duration} · 质量: {quality_star}
> 入睡: {bedtime} · 起床: {wakeup}

| 日期 | 时长 | 入睡 | 起床 |
|:-----|:----:|:----:|:----:|
| {date1} | {dur1} | {bt1} | {wu1} |
| {date2} | {dur2} | {bt2} | {wu2} |
```

### 🩸 血氧 (oxygen)

```markdown
**🩸 血氧数据**

> 最近: {latest_oxygen}% · 状况: {status}
> 平均: {avg_oxygen}%

| 日期 | 血氧 | 状况 |
|:-----|:----:|:-----|
| {date1} | {oxy1}% | {stat1} |
| {date2} | {oxy2}% | {stat2} |
```

### ❤️ 血压 (blood_pressure)

```markdown
**❤️ 血压数据**

> 最近: {latest} mmHg · 状况: {status}
> 平均: {avg} mmHg

| 日期 | 高压 | 低压 | 状况 |
|:-----|:----:|:----:|:-----|
| {date1} | {sys1} | {dia1} | {stat1} |
| {date2} | {sys2} | {dia2} | {stat2} |
```

### 💓 心率 (heart_rate)

```markdown
**💓 心率数据**

> 最近: {latest_hr} bpm · 范围: {range}
> 平均: {avg_hr} bpm

| 日期 | 心率 | 状况 |
|:-----|:----:|:-----|
| {date1} | {hr1} | {stat1} |
| {date2} | {hr2} | {stat2} |
```

### 🔥 卡路里消耗 (calorie)

```markdown
**🔥 卡路里消耗**

> 今日: {latest_cal} kcal · 目标: {percentage}%
> 平均: {avg_cal} kcal

| 日期 | 消耗 | 进度 |
|:-----|:----:|:-----|
| {date1} | {cal1} | {bar1} |
| {date2} | {cal2} | {bar2} |
```

---

## 无数据时回复

```markdown
> 📭 暂无「{关键词}」数据
>
> 支持查询：
> 步数 · 睡眠 · 血氧 · 血压 · 心率 · 消耗
```
