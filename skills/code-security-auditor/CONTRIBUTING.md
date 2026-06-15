# 🤝 贡献指南

**欢迎为 Code Security Auditor 贡献！**

---

## 📖 目录

1. [行为准则](#行为准则)
2. [快速开始](#快速开始)
3. [开发环境](#开发环境)
4. [提交代码](#提交代码)
5. [报告问题](#报告问题)
6. [请求功能](#请求功能)
7. [添加规则](#添加规则)
8. [成为维护者](#成为维护者)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- ✅ 使用友好和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

### 不可接受的行为

- 🚫 使用性化的语言或图像
- 🚫 人身攻击或侮辱性评论
- 🚫 公开或私下骚扰
- 🚫 未经许可发布他人信息
- 🚫 其他不道德或不专业的行为

---

## 快速开始

### 1. Fork 项目

```bash
# GitHub
https://github.com/your-username/code-security-auditor

# Gitee
https://gitee.com/your-username/code-security-auditor
```

### 2. 克隆仓库

```bash
git clone https://github.com/your-username/code-security-auditor.git
cd code-security-auditor
```

### 3. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"
```

### 4. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_sql_injection.py

# 代码覆盖率
pytest --cov=auditor tests/
```

---

## 开发环境

### 必需工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 主要语言 |
| pip | 21.0+ | 包管理 |
| pytest | 7.0+ | 测试框架 |
| black | 23.0+ | 代码格式化 |
| flake8 | 6.0+ | 代码检查 |
| mypy | 1.0+ | 类型检查 |

### 可选工具

| 工具 | 用途 |
|------|------|
| pre-commit | Git 钩子管理 |
| coverage.py | 覆盖率报告 |
| sphinx | 文档生成 |
| docker | 容器化测试 |

### 安装 pre-commit

```bash
pip install pre-commit
pre-commit install
```

---

## 提交代码

### 1. 创建分支

```bash
# 功能开发
git checkout -b feature/add-new-rule

# Bug 修复
git checkout -b fix/sql-injection-false-positive

# 文档改进
git checkout -b docs/update-readme
```

### 2. 编写代码

遵循以下规范：

- ✅ 使用有意义的变量名
- ✅ 添加文档字符串
- ✅ 编写单元测试
- ✅ 保持代码简洁
- ✅ 避免硬编码

### 3. 运行检查

```bash
# 代码格式化
black auditor/ tests/

# 代码检查
flake8 auditor/ tests/

# 类型检查
mypy auditor/

# 运行测试
pytest tests/ -v
```

### 4. 提交更改

```bash
# 添加文件
git add auditor/rules/new_rule.py
git add tests/test_new_rule.py

# 提交 (遵循约定式提交)
git commit -m "feat: add SQL injection detection rule"
```

### 5. 推送代码

```bash
git push origin feature/add-new-rule
```

### 6. 创建 Pull Request

在 GitHub/Gitee 上创建 PR，包含：

- 📝 清晰的标题
- 📋 详细的描述
- ✅ 关联的 Issue
- 🧪 测试覆盖证明
- 📸 截图 (如适用)

---

## 报告问题

### Bug 报告

使用 [Issue 模板](https://github.com/code-security-auditor/issues/new?template=bug_report.md)

**必需信息**:

- 🐛 **问题描述**: 清晰描述问题
- 🔄 **复现步骤**: 如何复现问题
- ✅ **预期行为**: 应该发生什么
- ❌ **实际行为**: 实际发生了什么
- 💻 **环境信息**: Python 版本、操作系统等
- 📄 **日志/截图**: 错误日志、截图

**示例**:

```markdown
### 问题描述
SQL 注入检测在某些情况下会产生误报

### 复现步骤
1. 运行 `auditor.py audit myproject/`
2. 查看报告第 45 行
3. 代码实际使用了参数化查询

### 预期行为
不应报告 SQL 注入漏洞

### 实际行为
报告了 CRITICAL 级别的 SQL 注入

### 环境信息
- Python: 3.11.0
- OS: Ubuntu 22.04
- Auditor: v1.1.0

### 代码示例
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
```

### 安全漏洞报告

**请勿公开报告安全漏洞！**

发送电子邮件至：security@code-security-auditor.org

我们会在 48 小时内回复，并在修复后公开致谢。

---

## 请求功能

### 功能请求

使用 [功能请求模板](https://github.com/code-security-auditor/issues/new?template=feature_request.md)

**必需信息**:

- 💡 **功能描述**: 想要什么功能
- 🎯 **使用场景**: 为什么需要这个功能
- 📚 **类似实现**: 其他工具的参考
- 🚀 **优先级**: 对你有多重要

**示例**:

```markdown
### 功能描述
希望能检测 Log4j 漏洞 (CVE-2021-44228)

### 使用场景
公司项目使用了 Log4j，需要快速扫描风险

### 类似实现
- Snyk: 有 Log4j 检测
- Dependabot: 会提示升级

### 优先级
高 - 影响生产安全
```

---

## 添加规则

### 规则模板

```python
"""
规则 ID: A03-XXX
规则名称: [简短描述]
严重程度: CRITICAL/HIGH/MEDIUM/LOW
OWASP 分类: A03:2021 注入
"""

import re
from typing import List, Dict, Any

class NewSecurityRule:
    """新安全规则"""
    
    rule_id = "A03-XXX"
    name = "规则名称"
    severity = "CRITICAL"
    category = "injection"
    description = "详细描述"
    references = [
        "https://owasp.org/...",
        "https://cwe.mitre.org/..."
    ]
    
    # 检测模式
    patterns = [
        r'pattern1',
        r'pattern2'
    ]
    
    # 修复建议
    remediation = {
        'description': '修复说明',
        'code': '''
# 修复前
vulnerable_code()

# 修复后
secure_code()
'''
    }
    
    def detect(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """检测漏洞"""
        findings = []
        
        for i, line in enumerate(code.splitlines(), 1):
            for pattern in self.patterns:
                if re.search(pattern, line):
                    findings.append({
                        'rule_id': self.rule_id,
                        'type': self.category,
                        'severity': self.severity,
                        'location': {'file': file_path, 'line': i},
                        'description': self.description,
                        'evidence': line.strip()[:100],
                        'remediation': self.remediation
                    })
        
        return findings
    
    def test_cases(self) -> List[Dict[str, Any]]:
        """测试用例"""
        return [
            {
                'name': '应检测到漏洞',
                'code': 'vulnerable_code()',
                'expected_findings': 1
            },
            {
                'name': '不应误报',
                'code': 'secure_code()',
                'expected_findings': 0
            }
        ]
```

### 规则提交流程

1. **创建规则文件**: `auditor/rules/A03-XXX_new_rule.py`
2. **编写测试**: `tests/rules/test_A03_XXX.py`
3. **更新文档**: `rules/extended-rules.md`
4. **运行测试**: `pytest tests/rules/test_A03_XXX.py -v`
5. **提交 PR**: 包含规则 + 测试 + 文档

### 规则审核标准

| 标准 | 要求 |
|------|------|
| **准确性** | 误报率 < 5% |
| **覆盖率** | 检出率 > 90% |
| **性能** | 单文件扫描 < 100ms |
| **文档** | 完整的描述和示例 |
| **测试** | 至少 2 个测试用例 |

---

## 成为维护者

### 维护者职责

- ✅ 审核 Pull Request
- ✅ 回复 Issue
- ✅ 发布新版本
- ✅ 维护文档
- ✅ 社区管理

### 成为维护者的条件

- 📅 持续贡献 3 个月+
- 🔢 提交 10+ 个有效 PR
- 💬 积极参与社区讨论
- 📚 熟悉项目代码和架构

### 申请流程

1. 联系现有维护者
2. 提交申请邮件
3. 维护团队审核
4. 公开宣布

---

## 🏆 贡献者名单

感谢所有贡献者！

```
┌─────────────────────────────────────────┐
│  🥇 核心贡献者 (10+ PR)                 │
│  - @username1 (45 PR)                   │
│  - @username2 (32 PR)                   │
│                                         │
│  🥈 活跃贡献者 (5-9 PR)                 │
│  - @username3 (8 PR)                    │
│  - @username4 (6 PR)                    │
│                                         │
│  🥉 新贡献者 (1-4 PR)                   │
│  - @username5 (3 PR)                    │
│  - @username6 (1 PR)                    │
└─────────────────────────────────────────┘
```

**想成为贡献者吗？** 从第一个 PR 开始！

---

## 📞 联系方式

- 📧 Email: contributors@code-security-auditor.org
- 💬 Discord: https://discord.gg/code-security-auditor
- 🐦 Twitter: @CodeSecAuditor
- 📱 微信群: 扫码加入 (见 README)

---

## 📜 许可证

本项目采用 [MIT 许可证](LICENSE)

贡献即表示你同意将贡献内容在 MIT 许可证下发布。

---

*最后更新：2026-03-07*  
*版本：v1.0*

**开始贡献吧！** 🚀
