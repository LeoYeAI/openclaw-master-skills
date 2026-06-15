# TOOLS.md - 盾卫的工具箱

## 安全扫描工具

### 静态代码分析
- 语言特定：bandit (Python), eslint-security (JS), gosec (Go)
- 通用：semgrep, CodeQL

### 依赖检查
- npm audit / yarn audit
- pip-audit
- Snyk CLI

### 密钥扫描
- git-secrets
- truffleHog
- gitleaks

## 常用检查清单

### Web 应用
- [ ] SQL 注入防护
- [ ] XSS 防护（输入过滤 + 输出编码）
- [ ] CSRF 防护
- [ ] 身份认证强度
- [ ] 权限验证逻辑
- [ ] 敏感数据加密存储
- [ ] HTTPS 强制

### 配置安全
- [ ] 无硬编码密钥/密码
- [ ] 环境变量管理
- [ ] 最小权限原则
- [ ] 日志脱敏

### API 安全
- [ ] 速率限制
- [ ] 认证/授权
- [ ] 输入验证
- [ ] 错误信息不泄露敏感信息
