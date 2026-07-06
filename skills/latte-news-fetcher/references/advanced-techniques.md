# 进阶技巧与工具

## 浏览器扩展

### Bypass Paywalls Clean (BPC)

**最佳选择** - 开源扩展，支持数百个主流新闻网站

**状态 (2026):**
- 已从 Chrome/Firefox 官方商店下架（法律压力）
- 需要手动下载 .zip/.xpi 安装

**安装方式:**
1. 从 GitHub 下载最新版本
2. Chrome: 开发者模式 → 加载已解压的扩展程序
3. Firefox: about:addons → 从文件安装附加组件

**效果:**
| 媒体 | 效果 |
|------|------|
| NYT | ⭐⭐⭐⭐⭐ |
| WSJ | ⭐⭐⭐⭐ |
| Bloomberg | ⭐⭐⭐⭐ |
| WaPo | ⭐⭐⭐⭐⭐ |

### uBlock Origin + Firefox

**组合使用：**
1. 安装 Firefox
2. 安装 uBlock Origin
3. 配置特定过滤规则

**优点:** 免费、开源、维护活跃

### 其他扩展

| 扩展 | 效果 | 备注 |
|------|------|------|
| SPayWall | ⭐⭐⭐ | Chrome Web Store |
| Paywall Remover.io | ⭐⭐⭐ | 在线服务 |
| Unpaywall | ⭐⭐⭐⭐ | 学术文章专用 |

---

## 高级技术

### 1. 禁用 JavaScript

**原理:** 许多付费墙依赖 JavaScript 运行，禁用可绕过

**操作步骤:**
1. Chrome: `chrome://settings/content/cookies` → JavaScript → 关闭
2. Firefox: `about:config` → `javascript.enabled` → `false`
3. Safari: 开发菜单 → 停用 JavaScript

**快捷键:** 
- Chrome: F12 → Settings → Disable JavaScript
- 使用扩展 "Quick JavaScript Switcher"

**适用:** 软付费墙（内容已加载但被遮盖）

### 2. User-Agent 切换

**原理:** 网站允许搜索引擎爬虫（Googlebot/Bingbot）访问完整内容

**User-Agent 字符串:**
```
Googlebot: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
Bingbot: Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
```

**操作:**
1. F12 → Network conditions → User agent
2. 选择 "Googlebot" 或自定义输入

**浏览器扩展:** User-Agent Switcher

### 3. Referer Spoofing

**原理:** 某些网站允许从特定来源（如 Twitter、Facebook）访问

**伪造来源:**
```
Referer: https://t.co/  (Twitter)
Referer: https://www.facebook.com/
Referer: https://news.google.com/
```

**扩展:** Referer Control

### 4. 无痕模式 + 清除 Cookies

**组合策略:**
1. 无痕模式打开链接
2. 如果失败，清除该网站 cookies 后重试
3. 某些网站限制月度阅读篇数，清除 cookies 重置计数

**Chrome 快捷键:** `Ctrl + Shift + Delete`

---

## 文本提取工具

### Textise.net

**URL 格式:** `https://r.jina.ai/http://{原文链接}`

**或使用:** `https://r.jina.ai/{原文链接}`

**功能:**
- 将网页转为纯文本
- 移除广告、图片、脚本
- 适合打印和阅读

**命令行:**
```bash
curl "https://r.jina.ai/http://example.com/article"
```

### Reader Mode

**浏览器内置:**
- Safari: 视图 → 显示阅读器
- Chrome: 侧边栏 → 阅读模式
- Firefox: 地址栏右侧阅读器图标

**强制开启:**
某些网站可以设置为始终使用阅读模式打开

### Outline.com

**使用方式:** `https://outline.com/{原文链接}`

**状态:** 不稳定，有时无法访问

---

## 归档工具

### Wayback Machine

**URL:** `https://web.archive.org/`

**使用:**
1. 访问网站
2. 粘贴 URL
3. 查看历史快照

**API:**
```
https://archive.org/wayback/available?url={encoded_url}
```

**浏览器扩展:** Wayback Machine (official)

### Google Cache

**方法 1:** 搜索 `cache:{原文链接}`

**方法 2:** 
```
https://webcache.googleusercontent.com/search?q=cache:{原文链接}
```

**注意:** 并非所有页面都有缓存

### Archive.today

**别名:** archive.is / archive.ph

**使用:** `https://archive.today/{原文链接}`

**已知问题:**
- 人机验证无限循环
- 与 Cloudflare DNS (1.1.1.1) 冲突
- 与 iCloud Private Relay 冲突

**解决方案:**
1. 换 DNS 为 8.8.8.8
2. 关闭 iCloud Private Relay
3. 使用无痕模式

---

## 组合技巧

### 快速复制法

**原理:** 在付费墙加载前复制内容

**操作:**
1. 打开 Word 文档
2. 点击文章链接
3. 快速 `Ctrl+A` → `Ctrl+C` → 粘贴到 Word
4. 必须在付费墙脚本加载前完成

### 查看页面源代码

**操作:**
1. 右键 → 查看网页源代码
2. 搜索文章关键词
3. 某些网站内容在源代码中可见

---

## 免费 API 资源

### 新闻 API

| API | 免费额度 | 特点 |
|-----|---------|------|
| NewsAPI.org | 100 请求/天 | 全球新闻源 |
| Guardian Open Platform | 免费 | 卫报内容 |
| Newsdata.io | 200 请求/天 | 多语言 |
| GNews | 100 请求/天 | 实时新闻 |

### 学术资源

**Unpaywall:** 自动查找学术论文免费版本

**Google Scholar:** 搜索 `[PDF]` 标签

---

_最后更新: 2026-03-05_
