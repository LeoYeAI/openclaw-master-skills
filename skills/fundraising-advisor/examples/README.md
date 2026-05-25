# FA Advisor Examples

这个目录包含了FA Advisor skill的使用示例。

## 运行示例

```bash
# 安装依赖
pnpm install

# 构建项目
pnpm build

# 运行基础示例
node dist/examples/basic-usage.js
```

## 示例说明

### basic-usage.ts

演示了FA Advisor的所有核心功能：

1. **完整创业服务包** - 为融资公司生成全套材料
   - 项目评估
   - Pitch Deck生成
   - 估值分析
   - 投资人匹配

2. **快速评估** - 快速检查项目投资准备度

3. **投资人分析包** - 从投资方角度分析项目
   - 投资备忘录
   - 尽职调查清单
   - 估值分析

4. **单独功能调用** - 独立使用各个模块

## 自定义使用

你可以基于这些示例创建自己的FA workflow：

```typescript
import FAAdvisor from '@openclaw/skill-fa-advisor';
import type { Project } from '@openclaw/skill-fa-advisor';

// 1. 创建advisor实例
const advisor = new FAAdvisor(yourInvestorDatabase);

// 2. 准备项目信息
const project: Project = {
  // ... 你的项目信息
};

// 3. 使用任何功能
const assessment = await advisor.quickAssessment(project);
const pitchDeck = await advisor.generatePitchDeck(project);
const matches = await advisor.matchInvestors(project);
```

## OpenClaw集成

在OpenClaw中使用此skill：

```bash
# 添加到你的workspace
openclaw skill add fa-advisor

# 通过对话使用
"帮我评估一下我的项目"
"生成一份pitch deck"
"推荐一些合适的投资机构"
```

## 数据源

示例使用了模拟的投资机构数据（`src/data/investors/sample-investors.json`）。

在生产环境中，你应该：
- 接入真实的投资机构数据库（如Crunchbase, PitchBook）
- 实时更新市场数据和估值倍数
- 集成外部API获取公司信息

## 下一步

- 查看 [API文档](../README.md) 了解完整功能
- 自定义估值模型参数
- 扩展投资机构数据库
- 集成到你的工作流中
