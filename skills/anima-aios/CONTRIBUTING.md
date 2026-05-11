# Contributing to Anima

感谢你有兴趣为 Anima 贡献代码！🌟

Anima 的目标是让 AI Agent 拥有成长的灵魂，每一个贡献都让这个项目更接近这个愿景。

## 🚀 快速开始

### 1. Fork 仓库

```bash
# 在 GitHub 上点击 Fork 按钮
# 然后克隆你的 fork
git clone https://github.com/YOUR_USERNAME/anima.git
cd anima
```

### 2. 创建分支

```bash
# 基于 main 分支创建新分支
git checkout -b feature/your-feature-name
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

### 3. 开发环境搭建

```bash
# 安装依赖
pip install watchdog

# 运行测试确保环境正常
cd anima-aios && python3 tests/test_integration_v6.py
```

### 4. 提交代码

```bash
# 添加修改
git add .

# 提交（使用清晰的提交信息）
git commit -m "feat: add new feature xxx"

# 推送到远程
git push origin feature/your-feature-name
```

### 5. 发起 Pull Request

在 GitHub 上发起 PR，使用 PR 模板填写相关信息。

## 🏗️ 代码结构

```
anima-aios/
├── core/           # 核心记忆架构（L1-L5）
│   ├── memory_watcher.py     # L1→L2 文件监听
│   ├── fact_store.py         # L2/L3 事实存储
│   ├── distill_engine.py     # L2→L3 LLM 提炼
│   ├── palace_index.py       # L4 记忆宫殿索引
│   ├── pyramid_engine.py     # L4 金字塔知识组织
│   ├── cognitive_profile.py  # L5 认知画像
│   ├── exp_tracker.py        # EXP 追踪
│   ├── native_importer.py    # v6.2 原生记忆导入
│   └── ...
├── health/         # 健康系统（5 个模块）
├── tests/          # 集成测试
├── docs/           # 文档
└── config/         # 配置文件
```

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 函数不超过 50 行
- 命名自解释（变量、函数、类）

### 提交信息规范

```
feat: add new feature xxx
fix: resolve memory leak in palace_classifier
docs: update README installation steps
refactor: simplify exp_tracker logic
test: add integration test for L4 pyramid
```

### 测试要求

- 新功能需要附带测试
- 提交前确保所有测试通过
- 运行测试：`python3 tests/test_integration_v6.py`

### 文档要求

- 新功能需要更新 README 或添加文档
- 代码注释清晰，特别是复杂逻辑
- 使用中文注释和文档

## 🎯 Good First Issues

新手推荐从标记了 [`good first issue`](https://github.com/anima-aios/anima/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 的任务开始，这些任务相对简单，适合熟悉项目。

## 🧪 测试

```bash
# 运行集成测试（37 项检查）
cd anima-aios && python3 tests/test_integration_v6.py
```

## 📄 License

贡献的代码将遵循 [Apache 2.0 许可证](LICENSE)。

---

## ❓ 需要帮助？

- 查看 [README.md](README.md) 了解项目概况
- 查看 [docs/](docs/) 了解详细文档
- 发起 Issue 提问
- 在 OpenClaw 社区寻求支持

---

_Every contribution helps Anima grow — just like the Agents it serves._ ⭐️

**架构只能演进，不能退化。**
**先诚实，再迭代。代码要配得上宣传。**
