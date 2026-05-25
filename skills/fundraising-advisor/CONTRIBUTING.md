# Contributing to FA Advisor

感谢您对FA Advisor项目的兴趣！

## 开发设置

```bash
# Clone仓库
git clone https://github.com/your-org/openclaw-fa-advisor.git
cd openclaw-fa-advisor

# 安装依赖
pnpm install

# 开发模式（自动重新编译）
pnpm dev

# 构建
pnpm build

# 运行测试
pnpm test
```

## 项目结构

```
src/
├── types/              # TypeScript类型定义
│   ├── project.ts     # 项目数据结构
│   ├── investor.ts    # 投资机构数据结构
│   └── models.ts      # 估值模型
├── modules/           # 核心功能模块
│   ├── assessment/    # 项目评估
│   ├── pitchdeck/     # BP生成
│   ├── valuation/     # 估值建模
│   ├── matching/      # 投资人匹配
│   └── analysis/      # 投资分析
├── data/              # 数据文件
│   ├── investors/     # 投资机构数据库
│   ├── templates/     # 文档模板
│   └── market/        # 市场数据
└── index.ts           # 主入口

examples/              # 使用示例
```

## 贡献指南

### 添加新功能

1. 在相应的模块目录下创建新文件
2. 导出功能到 `src/index.ts`
3. 添加TypeScript类型定义
4. 编写单元测试
5. 更新文档

### 改进估值算法

估值引擎在 `src/modules/valuation/valuationEngine.ts`。

添加新的估值方法：
1. 在 `ValuationMethod` enum中添加新方法
2. 实现计算逻辑
3. 在 `comprehensiveValuation` 中集成
4. 调整加权系数

### 扩展投资机构数据

投资机构数据格式见 `src/types/investor.ts` 的 `InvestorSchema`。

添加新的投资机构：
1. 创建JSON文件在 `src/data/investors/`
2. 遵循schema定义
3. 包含完整的投资策略信息

### 代码风格

- 使用TypeScript严格模式
- 遵循ESLint规则
- 使用有意义的变量名
- 添加JSDoc注释
- 保持函数简洁（< 50行）

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
# 运行所有测试
pnpm test

# 运行特定测试
pnpm test -- valuation

# 生成覆盖率报告
pnpm test:coverage
```

## 需要帮助的领域

- [ ] DCF估值模型实现
- [ ] 更多行业的基准数据
- [ ] 投资机构数据库扩充
- [ ] 多语言支持（英文、中文）
- [ ] Canvas可视化集成
- [ ] 真实数据源API集成（Crunchbase, PitchBook）
- [ ] 更复杂的匹配算法（机器学习）

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
