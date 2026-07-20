# 多层搜索策略详细指南

## 概述

DeepSearch-Kpro 采用**四层搜索策略**，从快速到深度，确保数据收集的完整性和可靠性。

**核心原则**：
- 优先使用快速工具（web_search）
- 逐层深入，避免浪费资源
- 关键数据必须多源验证
- 每层失败后自动切换下一层

---

## 🎯 四层搜索策略流程

```
┌─────────────────────────────────────┐
│ 第1层：Agent 内置 web_search        │
│ • 快速获取基础信息                   │
│ • 预计时间：5-10秒                   │
│ • 成功率：~80%                       │
└─────────────────────────────────────┘
  ↓ 成功 → 数据提取
  ↓ 失败 ↓
┌─────────────────────────────────────┐
│ 第2层：Agent 内置 web_fetch         │
│ • 深度搜索 + 高级操作符              │
│ • 预计时间：10-20秒                  │
│ • 成功率：~85%                       │
└─────────────────────────────────────┘
  ↓ 成功 → 数据提取
  ↓ 失败 ↓
┌─────────────────────────────────────┐
│ 第3层：multi-search-engine 能力     │
│ • 17个搜索引擎（8个国内 + 9个国际） │
│ • 多源并行搜索                       │
│ • 预计时间：15-30秒                  │
│ • 成功率：~90%                       │
└─────────────────────────────────────┘
  ↓ 成功 → 数据提取
  ↓ 失败 ↓
┌─────────────────────────────────────┐
│ 第4层：ddg-web-search 能力          │
│ • DuckDuckGo Lite 搜索              │
│ • 零依赖，最终备选                   │
│ • 预计时间：10-15秒                  │
│ • 成功率：~95%                       │
└─────────────────────────────────────┘
  ↓ 成功 → 数据提取
  ↓ 失败 ↓
┌─────────────────────────────────────┐
│ 数据暂不可得                         │
│ • 标注缺失数据                       │
│ • 说明影响范围                       │
│ • 提供替代建议                       │
└─────────────────────────────────────┘
```

---

## 📊 第1层：web_search

### 适用场景
- ✅ 快速获取基础数据
- ✅ 验证数据是否存在
- ✅ 获取最新新闻报道

### 使用方法
```markdown
web_search(
  query="中国护肤市场规模 2024",
  max_results=5
)
```

### 参数建议
- `max_results`: 3-10（根据数据重要性调整）

### 失败判断
- 返回结果为空
- 结果与查询不相关
- 出现 "missing_brave_api_key" 错误

---

## 📊 第2层：web_fetch

### 适用场景
- ✅ 深度搜索特定网站
- ✅ 使用高级搜索操作符
- ✅ 搜索特定文件类型（PDF）
- ✅ 搜索政府网站数据

### 使用方法
```markdown
# 基础搜索
web_fetch(url="https://www.baidu.com/s?wd=中国护肤市场规模+2024")

# 高级搜索
web_fetch(url="https://www.google.com/search?q=site:iresearch.cn+护肤市场")
web_fetch(url="https://www.google.com/search?q=护肤行业报告+filetype:pdf")
web_fetch(url="https://www.google.com/search?q=AI+news&tbs=qdr:w")
```

### 高级操作符
| 操作符 | 示例 | 说明 |
|--------|------|------|
| `site:` | `site:gov.cn 护肤` | 限定特定网站 |
| `filetype:` | `filetype:pdf 报告` | 搜索特定文件类型 |
| `""` | `"护肤品市场规模"` | 精确匹配 |

### 失败判断
- 返回内容为空
- 返回验证码页面
- 超时错误

---

## 📊 第3层：multi-search-engine 能力

### 说明
本技能已整合 **17个搜索引擎**（8个国内 + 9个国际），无需API密钥，直接使用 `web_fetch` 调用。

**详细的搜索引擎列表和URL模板**：见 `search-engines.md`

### 适用场景
- ✅ 第1、2层搜索失败
- ✅ 需要多源验证数据
- ✅ 中文市场深度研究
- ✅ 国际市场数据收集

### 推荐引擎组合

**中文市场数据**：
```markdown
web_fetch(url="https://www.baidu.com/s?wd=护肤市场规模+2024")
web_fetch(url="https://wx.sogou.com/weixin?type=2&query=护肤消费趋势")
```

**国际市场数据**：
```markdown
web_fetch(url="https://www.google.com/search?q=skincare+market+size+2024")
web_fetch(url="https://duckduckgo.com/html/?q=skincare+trends")
```

**政府统计数据**：
```markdown
web_fetch(url="https://www.baidu.com/s?wd=site:gov.cn+化妆品统计")
```

### 失败判断
- 所有引擎都返回空结果
- 主要引擎（百度、Google）都被屏蔽
- 超过3个引擎超时

---

## 📊 第4层：ddg-web-search 能力

### 说明
本技能已整合 **DuckDuckGo Lite 搜索**，零依赖，作为最终备选方案。

**详细的 DuckDuckGo 使用方法**：见 `search-engines.md` 第139-208行

### 适用场景
- ✅ 所有其他搜索方式失败
- ✅ 需要隐私搜索
- ✅ 作为最终备选方案

### 使用方法
```markdown
web_fetch(
  url="https://lite.duckduckgo.com/lite/?q=skincare+market+size+2024",
  extractMode="text",
  maxChars=8000
)
```

### 参数建议
- `extractMode`: 使用 `"text"`（非 markdown）
- `maxChars`: 8000

### 结果解读
- 前 1-2 条结果可能是广告（标记为 "Sponsored link"），跳过
- 有机搜索结果跟在广告之后

### 失败判断
- 返回内容为空
- 所有结果都是广告
- 连接超时

---

## 🔍 数据提取与验证

### 数据提取流程
```markdown
1. 识别搜索结果中的关键数据
   - 定量数据：数值、单位、时间
   - 定性数据：观点、趋势、案例

2. 提取数据来源信息
   - 标题、URL、发布时间
   - 来源类型（官网、报告、新闻）

3. 组织数据结构
   - 按章节分类
   - 按优先级排序
   - 标注数据类型
```

### 多源验证标准

| 数据优先级 | 验证要求 | 来源类型 | 数据偏差 |
|-----------|---------|---------|---------|
| **P0** | 至少 2 个独立来源 | 官网、政府、行业报告 | < 10% |
| **P1** | 至少 2 个来源 | 可信媒体、专家观点 | < 20% |
| **P2** | 至少 1 个来源 | 新闻报道、博客 | 可接受 |

### 数据可信度标注

| 等级 | 标准 | 标注 |
|------|------|------|
| **high** | 2个以上官方来源验证 | ✅ 高可信度 |
| **medium** | 2个以上非官方来源验证 | ⚠️ 中等可信度 |
| **low** | 单一来源或数据冲突 | ❌ 低可信度 |

---

## 🎯 场景化搜索建议

### 场景1：中国市场数据
**推荐组合**：web_search → 百度 → 微信
```markdown
web_search(query="中国护肤市场规模 2024", max_results=5)
web_fetch(url="https://www.baidu.com/s?wd=中国护肤市场规模+2024")
web_fetch(url="https://wx.sogou.com/weixin?type=2&query=护肤市场报告")
```

### 场景2：国际市场数据
**推荐组合**：web_search → Google → DuckDuckGo
```markdown
web_search(query="global skincare market size 2024", max_results=5)
web_fetch(url="https://www.google.com/search?q=skincare+market+size+2024&tbs=qdr:w")
web_fetch(url="https://duckduckgo.com/html/?q=skincare+market+trends+2024")
```

### 场景3：政府统计数据
**推荐组合**：web_search → site:gov.cn → 百度
```markdown
web_search(query="化妆品行业统计 2024", max_results=5)
web_fetch(url="https://www.baidu.com/s?wd=site:gov.cn+化妆品行业统计")
```

### 场景4：行业报告
**推荐组合**：web_search → filetype:pdf → DuckDuckGo Lite
```markdown
web_search(query="护肤行业报告 2024 filetype:pdf", max_results=5)
web_fetch(url="https://www.google.com/search?q=护肤行业报告+filetype:pdf")
web_fetch(url="https://lite.duckduckgo.com/lite/?q=skincare+industry+report+pdf", extractMode="text")
```

---

## ⚠️ 常见问题

### Q1：第1层搜索失败怎么办？
**A**：立即切换到第2层，使用 web_fetch + 特定搜索引擎。

### Q2：如何判断搜索结果是否可靠？
**A**：
1. 检查来源类型（官网 > 行业报告 > 新闻媒体）
2. 多源验证（至少2个独立来源）
3. 数据时效性（优先近期数据）
4. 数据一致性（检查不同来源是否冲突）

### Q3：所有搜索层都失败怎么办？
**A**：
1. 标注"数据暂不可得"
2. 说明数据缺失原因
3. 评估对分析结论的影响
4. 提供替代数据或建议

### Q4：如何优化 Token 消耗？
**A**：
1. 优先使用第1层（web_search）
2. 设置合理的 maxChars（8000）
3. 使用时间过滤减少不相关结果
4. 避免重复搜索相同关键词

---

## 📊 搜索性能对比

| 层级 | 响应时间 | Token 消耗 | 成功率 | 适用场景 |
|------|---------|-----------|--------|----------|
| 第1层 | 5-10秒 | 低 | ~80% | 快速获取 |
| 第2层 | 10-20秒 | 中 | ~85% | 深度搜索 |
| 第3层 | 15-30秒 | 高 | ~90% | 多源验证 |
| 第4层 | 10-15秒 | 低 | ~95% | 最终备选 |

---

## 🎓 最佳实践

1. **优先级原则**：从第1层开始，逐层深入
2. **效率优先**：第1层成功即停止，不浪费资源
3. **多源验证**：关键数据必须从多个来源验证
4. **质量保证**：标注数据可信度，避免误导
5. **成本控制**：合理设置参数，优化 Token 消耗

---

## 📝 搜索完成检查清单

- [ ] 已尝试至少2层搜索
- [ ] P0 数据至少从2个来源验证
- [ ] 数据来源已记录（URL、标题、日期）
- [ ] 数据可信度已标注
- [ ] 缺失数据已明确标注
