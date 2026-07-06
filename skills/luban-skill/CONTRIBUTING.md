# 贡献指南

感谢你对 **luban_skill** 的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果你发现了 bug，请通过 GitHub Issues 报告，并包含以下信息：

- 问题的清晰描述
- 复现步骤
- 期望的行为
- 实际的行为
- 环境信息（Python 版本、操作系统等）

### 提出新功能

如果你有新功能的想法，请先创建一个 Issue 进行讨论，描述：

- 功能的用途
- 预期的使用方式
- 可能的实现方案

### 提交代码

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 代码风格

- Python 代码遵循 PEP 8 规范
- 使用有意义的变量名和函数名
- 添加必要的注释和文档字符串
- 保持代码简洁清晰

### 提交信息规范

提交信息应该清晰描述修改内容：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档修改
- `style:` 代码格式修改（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: add type validation for container types

- Add support for nested container types like list<map<int,string>>
- Improve error messages for invalid type strings
```

### 测试

在提交 PR 之前，请确保：

1. 你的代码可以正常运行
2. 没有引入新的问题
3. 相关的功能都测试通过

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/luban-tools/luban_skill.git
cd luban_skill

# 安装依赖
pip install openpyxl

# 测试运行
python scripts/luban_helper.py --help
```

## 联系方式

如有问题，可以通过以下方式联系：

- GitHub Issues: [创建 Issue](https://github.com/luban-tools/luban_skill/issues)
- 邮件: [你的邮箱]

再次感谢你的贡献！
