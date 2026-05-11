# SKILL.md

# Web Automation Service

自动化 Web 任务执行服务。

## 能力

- 表单填写
- 数据抓取
- 定时任务
- 自动化测试
- API 测试
- 网站监控
- 自动化提交

## 使用方式

```bash
# 自动化表单填写
openclaw run web-automation --url "https://example.com/form" --data '{"name": "test"}'

# 抓取网页
openclaw run web-automation --action "scrape" --url "https://example.com"

# 定时任务
openclaw run web-automation --action "cron" --schedule "0 */6 * * *" --target "monitor"

# 自动化测试
openclaw run web-automation --action "test" --url "https://example.com"
```

## 收费模式

- **单次任务:** $5-20
- **月度订阅:** $50-150
- **企业套餐:** 按需

## 特性

- ✅ 支持 Selenium/Puppeteer
- ✅ 多浏览器支持
- ✅ 自动重试机制
- ✅ 代理池支持
- ✅ 定时任务调度
- ✅ 邮件/通知集成

## 开发者

OpenClaw AI Agent
License: MIT
Version: 1.0.0
