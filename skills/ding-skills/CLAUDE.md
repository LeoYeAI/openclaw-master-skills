# 项目规范

## 发布流程

用户要求发布代码时，自动执行以下步骤：

1. **重构文档** - 更新 README.md 和 SKILL.md，确保与当前功能一致
2. **更新 package.json** - 递增 version（遵循 semver），更新 description 与功能匹配
3. **提交并发布** - git add/commit/push 到 GitHub，然后 `clawhub publish` 发布到 ClawHub

## ClawHub 发布命令

```bash
clawhub publish /Users/jackery/ding-skills --slug ding-skills --name "DingTalk Skills" --version <新版本号> --changelog "<变更说明>"
```

## 技术栈

- Python 3 + requests
- 直接调用钉钉 REST API（OpenAPI + TOP API）
- 环境变量：DINGTALK_APP_KEY、DINGTALK_APP_SECRET
- 共享客户端模块：scripts/dingtalk_client.py
