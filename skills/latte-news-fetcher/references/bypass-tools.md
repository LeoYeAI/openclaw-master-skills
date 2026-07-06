# 绕过工具对比

## 工具列表

### 1. smry.ai

**URL 格式:** `https://smry.ai/{原文链接}`

**优点:**
- 自动总结 + 全文
- 对 NYT、Medium 效果好
- 速度快（~10秒）

**缺点:**
- 对 WSJ 无效
- 有时会失败

**效果评分:**
| 媒体 | 效果 |
|------|------|
| NYT | ⭐⭐⭐⭐⭐ |
| Medium | ⭐⭐⭐⭐⭐ |
| Bloomberg | ⭐⭐⭐ |
| WSJ | ⭐ |
| Economist | ⭐⭐ |

---

### 2. 12ft.io

**URL 格式:** `https://12ft.io/{原文链接}`

**优点:**
- 简单直接
- 对博客类效果好
- 支持多种媒体

**缺点:**
- 不支持所有网站
- 有时被屏蔽

**效果评分:**
| 媒体 | 效果 |
|------|------|
| Medium | ⭐⭐⭐⭐⭐ |
| WaPo | ⭐⭐⭐⭐ |
| Guardian | ⭐⭐⭐⭐ |
| WSJ | ⭐⭐ |
| Bloomberg | ⭐⭐ |

---

### 3. removepaywalls.com

**URL 格式:** `https://removepaywalls.com/{原文链接}`

**优点:**
- 搜索多个归档源
- 对某些小众媒体有效

**缺点:**
- 搜索时间长（~15秒）
- 不总是成功
- 对大媒体效果一般

**效果评分:**
| 媒体 | 效果 |
|------|------|
| NYT | ⭐⭐⭐ |
| 小众媒体 | ⭐⭐⭐⭐ |
| WSJ | ⭐ |
| Bloomberg | ⭐⭐ |

---

### 4. Archive.today / archive.is

**URL 格式:** 
- `https://archive.today/{原文链接}`
- `https://archive.is/{原文链接}`

**优点:**
- 历史归档
- 有时有意外收获

**缺点:**
- **人机验证问题严重**
- Cloudflare DNS 冲突
- 需要换 DNS 才能正常使用

**解决方案:**
1. 关闭 1.1.1.1 DNS
2. 关闭 iCloud Private Relay
3. 用无痕模式
4. 用手机热点

---

### 5. browser 工具（内置）

**方法:** 使用内置 browser 打开页面

**优点:**
- 真实浏览器
- 可能拿到部分内容

**缺点:**
- 硬付费墙依然挡着
- 只能看到开头
- 资源消耗大

**建议:** 仅作为最后手段

---

## 组合策略

### 推荐顺序

```
1. smry.ai
2. 12ft.io
3. removepaywalls.com
4. archive.today（需换 DNS）
5. browser 工具
6. 搜索替代信源
```

### 按媒体选择

**NYT:**
- smry.ai（首选）
- 12ft.io（备选）

**WSJ:**
- **直接找替代信源**（推荐）
- smry.ai（可能只拿到开头）

**Bloomberg:**
- smry.ai（试试）
- 找替代信源

**Medium:**
- 12ft.io
- smry.ai

---

## 命令速查

```bash
# smry.ai
TAVILY_API_KEY=xxx node /path/to/tavily-search/scripts/extract.mjs "https://smry.ai/{url}"

# 直接提取
web_fetch url="https://smry.ai/{url}"

# 搜索
TAVILY_API_KEY=xxx node /path/to/tavily-search/scripts/search.mjs "关键词" -n 10
```

---

_最后更新: 2026-03-05_
