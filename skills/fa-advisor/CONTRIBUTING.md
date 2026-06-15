# Contributing to FA Advisor

感谢您对FA Advisor项目的兴趣！

## 开发设置

```bash
# Clone仓库
git clone https://github.com/your-org/openclaw-financial-analyst.git
cd openclaw-financial-analyst

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
pip install -r requirements-dev.txt

# 安装系统依赖（用于PDF处理）
# macOS
brew install tesseract ghostscript poppler

# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils ghostscript

# 运行测试
python3 -m pytest
# 或
python3 test_complete.py
```

## 项目结构

```
fa_advisor/
├── types/              # Pydantic类型定义
│   ├── project.py     # 项目数据结构
│   ├── investor.py    # 投资机构数据结构
│   └── models.py      # 估值模型和结果类型
├── modules/           # 核心功能模块
│   ├── assessment/    # 项目评估
│   ├── pitchdeck/     # Pitch Deck和BP生成
│   ├── valuation/     # 估值建模
│   ├── matching/      # 投资人匹配
│   └── analysis/      # 投资分析
├── pdf/               # PDF处理（Python优势）
│   ├── parser.py      # PDF解析
│   ├── financial_parser.py  # 财务数据提取
│   ├── ocr.py        # OCR识别
│   └── generator.py   # PDF报告生成
├── data/              # 数据文件
│   ├── investors/     # 投资机构数据库
│   ├── templates/     # 文档模板
│   └── market/        # 市场数据
└── advisor.py         # FAAdvisor主类

examples/              # 使用示例
tests/                 # 测试用例
```

## 贡献指南

### 添加新功能

1. 在相应的模块目录下创建新Python文件
2. 在 `fa_advisor/__init__.py` 中导出功能
3. 添加Pydantic类型定义
4. 编写单元测试
5. 更新文档和类型注解

### 改进估值算法

估值引擎在 `fa_advisor/modules/valuation/valuationEngine.py`。

添加新的估值方法：
1. 在 `ValuationEngine` 类中添加新方法
2. 实现计算逻辑（使用async def）
3. 在 `comprehensive_valuation` 中集成
4. 调整加权系数

### 扩展投资机构数据

投资机构数据格式见 `fa_advisor/types/investor.py` 的 `Investor` Pydantic模型。

添加新的投资机构：
1. 创建JSON文件在 `fa_advisor/data/investors/`
2. 遵循Pydantic schema定义
3. 包含完整的投资策略信息

### 代码风格

- 使用Python 3.10+ 类型注解
- 遵循PEP 8规范
- 使用有意义的变量名
- 添加docstring（Google风格）
- 保持函数简洁（< 50行）
- 使用Pydantic进行数据验证
- 使用async/await处理异步操作

### 提交规范

使用约定式提交（Conventional Commits）：

- `feat:` 新功能
- `fix:` bug修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: add DCF valuation method
fix: correct investor matching score calculation
docs: update API documentation
```

### Pull Request流程

1. Fork项目
2. 创建feature分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

### 测试

```bash
# 运行完整测试
python3 test_complete.py

# 运行示例
python3 example_python.py

# 使用pytest运行测试
python3 -m pytest

# 运行特定测试
python3 -m pytest tests/test_valuation.py

# 生成覆盖率报告
python3 -m pytest --cov=fa_advisor --cov-report=html
```

## 需要帮助的领域

- [ ] DCF估值模型实现
- [ ] 更多行业的基准数据
- [ ] 投资机构数据库扩充
- [ ] 多语言支持（英文、中文）
- [ ] PDF报告样式优化
- [ ] 真实数据源API集成（Crunchbase, PitchBook）
- [ ] 使用机器学习改进匹配算法
- [ ] 财务报表自动分析
- [ ] NLP技术用于文本分析
- [ ] 单元测试覆盖率提升

## 行为准则

- 尊重所有贡献者
- 欢迎建设性反馈
- 专注于代码质量
- 保持专业和友好

## 问题反馈

遇到问题？请：
1. 检查已有的issues
2. 提供详细的复现步骤
3. 包含错误信息和环境信息
4. 附上相关代码片段

## 许可

贡献的代码将遵循项目的MIT许可证。

## 联系方式

- GitHub Issues: 用于bug报告和功能请求
- Discussions: 用于问题讨论和想法交流

感谢您的贡献！🙏
