# 付费墙难度矩阵

## 难度等级

| 难度 | 说明 | 建议 |
|------|------|------|
| ⭐ | 完全免费，无付费墙 | 直接 web_fetch |
| ⭐⭐ | 软付费墙，易绕过 | smry.ai / 12ft.io |
| ⭐⭐⭐ | 有付费墙，需技巧 | smry + 禁用JS + UA切换 |
| ⭐⭐⭐⭐ | 硬付费墙，部分方法有效 | BPC扩展 + 找替代 |
| ⭐⭐⭐⭐⭐ | 极难，几乎无法绕过 | **必须找替代信源** |

---

## 国际媒体

### ⭐ 完全免费

| 媒体 | 类型 | RSS | 网站 |
|------|------|-----|------|
| BBC News | 国际 | ✅ | bbc.com |
| Reuters | 通讯社 | ✅ | reuters.com |
| AP News | 通讯社 | ✅ | apnews.com |
| AFP | 通讯社 | ✅ | afp.com |
| Al Jazeera | 中东 | ✅ | aljazeera.com |
| Deutsche Welle | 德国 | ✅ | dw.com |
| NHK World | 日本 | ✅ | www3.nhk.or.jp |
| France 24 | 法国 | ✅ | france24.com |

### ⭐⭐ 容易绕过

| 媒体 | 类型 | 推荐方法 |
|------|------|---------|
| Medium | 博客 | 12ft.io / smry.ai / r.jina.ai |
| Substack | 博客 | 12ft.io |
| LinkedIn Articles | 社交 | 12ft.io |
| Quora | 问答 | 12ft.io |
| BuzzFeed News | 新闻 | smry.ai |

### ⭐⭐⭐ 中等难度

| 媒体 | 类型 | 推荐方法 | 效果 |
|------|------|---------|------|
| New York Times | 国际 | smry.ai | ⭐⭐⭐⭐ |
| Washington Post | 美国 | smry.ai / BPC | ⭐⭐⭐⭐ |
| The Guardian | 英国 | 12ft.io | ⭐⭐⭐⭐ |
| Los Angeles Times | 美国 | BPC / 禁用JS | ⭐⭐⭐ |
| Boston Globe | 美国 | BPC | ⭐⭐⭐ |
| The Atlantic | 杂志 | smry.ai | ⭐⭐⭐ |
| New Yorker | 杂志 | smry.ai | ⭐⭐⭐ |

### ⭐⭐⭐⭐ 较难

| 媒体 | 类型 | 推荐方法 | 效果 |
|------|------|---------|------|
| Bloomberg | 财经 | smry.ai / 找替代 | ⭐⭐ |
| Economist | 财经 | smry.ai / BPC | ⭐⭐ |
| Financial Times | 英国 | BPC / 找替代 | ⭐⭐ |
| Foreign Affairs | 国际 | BPC / smry.ai | ⭐⭐ |
| Wired | 科技 | smry.ai / 禁用JS | ⭐⭐⭐ |
| MIT Technology Review | 科技 | BPC | ⭐⭐ |
| The Information | 科技 | **找替代** | ⭐ |

### ⭐⭐⭐⭐⭐ 极难

| 媒体 | 类型 | 建议 |
|------|------|------|
| Wall Street Journal | 财经 | **必须找替代信源** |
| Stratfor | 情报 | **必须找替代信源** |
| The Information Pro | 科技 | **必须找替代信源** |
| Politico Pro | 政治 | **必须找替代信源** |

---

## 中文媒体

### ⭐ 免费/部分免费

| 媒体 | 难度 | RSS | 备注 |
|------|------|-----|------|
| BBC 中文 | ⭐ | ✅ | 完全免费 |
| 德国之声中文 | ⭐ | ✅ | 完全免费 |
| 美国之音 | ⭐ | ✅ | 完全免费 |
| 自由亚洲 | ⭐ | ✅ | 完全免费 |
| 香港01 | ⭐⭐ | ❌ | 部分免费 |

### ⭐⭐⭐ 中等

| 媒体 | 难度 | 推荐方法 |
|------|------|---------|
| 端传媒 | ⭐⭐⭐ | smry.ai（有时有效）|
| 南方周末 | ⭐⭐⭐ | 12ft.io |
| 三联生活周刊 | ⭐⭐⭐ | smry.ai |
| 新周刊 | ⭐⭐⭐ | 12ft.io |

### ⭐⭐⭐⭐ 较难

| 媒体 | 难度 | 推荐方法 |
|------|------|---------|
| 财新网 | ⭐⭐⭐⭐ | smry.ai / BPC |
| 经济观察报 | ⭐⭐⭐⭐ | 找替代 |

---

## 学术/专业

### ⭐⭐ 免费获取

| 媒体 | 类型 | 工具 |
|------|------|------|
| arXiv | 学术 | 完全免费 |
| PubMed | 医学 | 完全免费 |
| PLOS ONE | 学术 | 完全免费 |
| SSRN | 学术 | 部分免费 |

### ⭐⭐⭐ 可绕过

| 媒体 | 类型 | 工具 |
|------|------|------|
| JSTOR | 学术 | Unpaywall / 学校访问 |
| ResearchGate | 学术 | 注册后免费 |
| Academia.edu | 学术 | 注册后部分免费 |

---

## 特殊问题

### Archive.today 人机验证循环

**问题:** 访问 archive.is/archive.ph 出现无限人机验证

**原因:**
- Cloudflare DNS (1.1.1.1) 冲突
- iCloud Private Relay 冲突
- VPN 影响

**解决方案:**
1. 换 DNS 为 Google (8.8.8.8) 或 Cloudflare (1.1.1.1)
2. 系统 → iCloud → Private Relay → 关闭
3. 使用无痕模式
4. 换网络（手机热点）

### 动态付费墙

**问题:** 某些网站限制月度阅读篇数

**解决方案:**
1. 清除该网站 cookies
2. 使用无痕模式
3. 换浏览器/设备

---

_最后更新: 2026-03-05_
