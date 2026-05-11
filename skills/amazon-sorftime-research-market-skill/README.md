# Product Research Skill

基于 **Sorftime MCP + LLM Agent** 的 Amazon 选品深度调研技能。

## 核心特点

- **LLM 驱动**：分析、洞察、决策全部由 LLM 完成
- **交互式执行**：逐步推进，用户可中途干预
- **轻量脚本**：仅用于 API 调用和 Dashboard 渲染
- **简化数据**：不用复杂的 unified payload 结构

## 使用方法

```
/product-research [产品关键词] [站点]
```

示例：
- `/product-research "bluetooth speaker" US`
- `/product-research laptop backpack GB`

## 执行流程

```
Step 0: 信息收集（确认站点、场景、约束）
   ↓
Step 1: 数据采集（Top100、关键词、趋势、竞品）
   ↓
Step 2: 属性标注（LLM 从标题提取维度）
   ↓
Step 3: 交叉分析（LLM 发现供需缺口）
   ↓
Step 4: 竞品与 VOC（LLM 选择竞品、归类差评）
   ↓
Step 5: 评估决策（壁垒评估 + 选品决策评分）
   ↓
Step 6: 报告输出（Markdown + Dashboard）
```

## 输出

- `report.md` - Markdown 完整报告（LLM 直接撰写）
- `data.json` - 结构化数据（供 Dashboard 使用）
- `dashboard.html` - 可视化看板（脚本渲染）

## 与其他 Skills 的关系

```
category-selection (品类筛选五维评分)
        ↓
product-research (深度选品调研) ← 本技能
        ↓
amazon-analyse (竞品 Listing 深挖)
        ↓
review-analysis (评论深度分析)
```

## 脚本架构（极简）

```
scripts/
├── api_client.py          # Sorftime API 调用 + SSE 解析
└── render_dashboard.py    # Dashboard 可视化渲染
```

**设计原则**：
- 脚本不做分析判断（由 LLM 完成）
- 脚本不做复杂计算（让 LLM 从数据中发现）
- 脚本仅做数据搬运（API → 结构化数据）

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-03-19 | LLM Agent 驱动，简化脚本架构 |
| v1.0 | 2026-03-19 | 初始版本 |

## 许可证

MIT License
