---
name: clean-content-fetch
description: 获取干净、可读的网页正文内容，适合现代网页、博客、新闻、公告和微信公众号文章抓取；支持网页正文提取、内容清洗、去噪、Markdown 输出，适用于普通 fetch 效果不佳、页面噪音较多或动态渲染干扰的场景。Clean content fetch for modern web pages, article extraction, WeChat article capture, content cleanup, noise reduction, and markdown output when ordinary fetch is not clean enough.
---

# Scrapling Web Fetch

当用户要获取网页内容、正文提取、把网页转成 markdown/text、抓取文章主体时，优先使用此技能。

## 默认流程
1. 使用 `python3 scripts/scrapling_fetch.py <url> <max_chars>`
2. 默认正文选择器优先级：
   - `article`
   - `main`
   - `.post-content`
   - `[class*="body"]`
3. 命中正文后，使用 `html2text` 转 Markdown
4. 若都未命中，回退到 `body`
5. 最终按 `max_chars` 截断输出

## 用法
```bash
python3 /Users/zzd/.openclaw/workspace/skills/scrapling-web-fetch/scripts/scrapling_fetch.py <url> 30000
```

## 依赖
优先检查：
- `scrapling`
- `html2text`
- `curl_cffi`
- `playwright`
- `browserforge`

推荐使用独立虚拟环境，避免系统 Python 的 PEP 668 限制：
```bash
python3 -m venv /Users/zzd/.openclaw/workspace/.venvs/clean-content-fetch
/Users/zzd/.openclaw/workspace/.venvs/clean-content-fetch/bin/pip install scrapling html2text curl_cffi playwright browserforge
/Users/zzd/.openclaw/workspace/.venvs/clean-content-fetch/bin/python -m playwright install chromium
```

如直接运行脚本，优先使用该虚拟环境中的 Python：
```bash
/Users/zzd/.openclaw/workspace/.venvs/clean-content-fetch/bin/python /Users/zzd/.openclaw/workspace/skills/scrapling-web-fetch/scripts/scrapling_fetch.py <url> 30000
```

## 输出约定
脚本默认输出 Markdown 正文内容。
如需结构化输出，可追加 `--json`。
如需调试提取命中了哪个 selector，可查看 stderr 输出。

## 附加资源
- 用法参考：`/Users/zzd/.openclaw/workspace/skills/scrapling-web-fetch/references/usage.md`
- 选择器策略：`/Users/zzd/.openclaw/workspace/skills/scrapling-web-fetch/references/selectors.md`
- 统一入口：`/Users/zzd/.openclaw/workspace/skills/scrapling-web-fetch/scripts/fetch-web-content`

## 何时用这个技能
- 获取文章正文
- 抓博客/新闻/公告正文
- 将网页转成 Markdown 供后续总结
- 常规 fetch 效果差，希望提升现代网页抓取稳定性
- 抓小红书分享短链或笔记落地页正文

## 小红书抓取方法
对于 `xhslink.com` 短链或小红书笔记页，推荐直接使用虚拟环境中的脚本运行：
```bash
/Users/zzd/.openclaw/workspace/.venvs/clean-content-fetch/bin/python /Users/zzd/.openclaw/workspace/skills/scrapling-web-fetch/scripts/scrapling_fetch.py 'http://xhslink.com/o/9745hugimlD' 30000
```

说明：
- 脚本会先解析短链并抓取落地页正文
- 适合提取小红书笔记文案、标题和主体内容
- 若页面需要更复杂交互，再切到浏览器自动化

## 何时不用
- 需要完整浏览器交互、点击、登录、翻页时：改用浏览器自动化
- 只是简单获取 API JSON：直接请求 API 更合适
