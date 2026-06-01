---
name: aieo-diagnosis
description: 为品牌/企业进行完整的GEO/AEO/AIEO诊断分析。当用户提到"GEO诊断"、"AEO诊断"、"AIEO诊断"、"AI可见性分析"、"生成引擎优化"或需要分析品牌在AI搜索引擎中的可见性时，自动调用此Skill。诊断报告自动保存至 01_diagnosis/ 目录，文件名格式：{品牌名}_GEO诊断报告_{YYYY-MM-DD}.md
allowed-tools: Read, Write, Bash, Grep, Glob, WebFetch, WebSearch, mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot, mcp__playwright__browser_click, mcp__playwright__browser_type, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_wait_for, mcp__playwright__browser_close, mcp__playwright__browser_tabs, mcp__playwright__browser_press_key
---

> **AIEO 服务流程**: 诊断(生成问题库初稿) → 定位(修正迭代问题库) → 内容(使用问题库) → 监控(使用问题库)

# GEO/AEO/AIEO 诊断 Skill

专业的 AI Engine Optimization 诊断工具，帮助品牌/企业分析和优化其在 AI 搜索引擎（ChatGPT、文心一言、豆包、通义千问、Perplexity 等）中的可见性。

## 术语说明

| 术语 | 全称 | 说明 |
|------|------|------|
| **GEO** | Generative Engine Optimization | 生成引擎优化，针对AI生成内容的优化 |
| **AEO** | Answer Engine Optimization | 答案引擎优化，让品牌成为AI的"答案" |
| **AIEO** | AI Engine Optimization | AI引擎优化，综合性AI可见性优化 |

> 三个术语可互换使用，本Skill统一提供诊断服务。

---

## 输出规范

### 文件保存位置
```
{客户工作目录}/01_diagnosis/
```
> 工作目录由管理员在部署时指定（默认：`~/.openclaw/work-<agent-id>/`）

### 输出文件清单

诊断阶段完成后，**必须**输出以下两个文件：

| 文件类型 | 命名格式 | 用途 | 下游使用 |
|----------|----------|------|----------|
| **诊断报告** | `{品牌名}_GEO诊断报告_{YYYY-MM-DD}.md` | 诊断分析结果 | 定位阶段参考 |
| **问题库初稿** | `{品牌名}_问题库_{YYYY-MM-DD}.md` | AI测试问题集 | 定位→内容→监控 |

**示例**：
- `百威中国_GEO诊断报告_2025-12-12.md`
- `百威中国_问题库_2025-12-12.md`

### 文件创建命令
```bash
# 获取当前日期
DATE=$(date +%Y-%m-%d)

# 创建诊断报告
touch "{客户工作目录}/01_diagnosis/{品牌名}_GEO诊断报告_${DATE}.md"

# 创建问题库初稿
touch "{客户工作目录}/01_diagnosis/{品牌名}_问题库_${DATE}.md"
```

---

## 诊断框架

### 一、网站技术审计（AEO Technical Audit）

#### 1.1 必检项目清单

| 检查项 | 严重程度 | 检查方法 |
|--------|----------|----------|
| **Meta Description** | 🔴 严重 | 查看 `<meta name="description">` 是否存在且有意义 |
| **Schema标记** | 🔴 严重 | 检查 `<script type="application/ld+json">` |
| **Open Graph标签** | 🟠 中等 | 检查 `og:title`, `og:description`, `og:image` |
| **Canonical标签** | 🟠 中等 | 检查 `<link rel="canonical">` |
| **HTML lang属性** | 🟠 中等 | 检查 `<html lang="zh-CN">` |
| **FAQ页面** | 🔴 严重 | 是否有独立FAQ专区 |
| **图片Alt属性** | 🟠 中等 | 图片缺失Alt比例 |
| **H1标签结构** | 🟠 中等 | 每页应仅有1个H1 |
| **SSL证书** | 🟠 中等 | HTTPS是否正常 |
| **页面加载速度** | 🟠 中等 | 是否<3秒 |
| **Answer-First结构** | 🔴 严重 | 内容是否以直接答案开头 |

#### 1.2 技术审计命令

```bash
# 获取网站头部信息
curl -sI https://example.com

# 获取HTML内容分析Meta标签
curl -s https://example.com | grep -E '<meta|<title|<link rel="canonical"|<html'

# 检查Schema标记
curl -s https://example.com | grep -o '<script type="application/ld+json">.*</script>'

# 检查Open Graph
curl -s https://example.com | grep 'og:'

# 检查H1标签
curl -s https://example.com | grep -i '<h1'
```

#### 1.3 审计报告模板

```markdown
### 网站技术审计结果

| 检查项 | 现状 | 严重程度 | 影响 |
|--------|------|----------|------|
| **Meta Description** | ❌/✅ 状态 | 🔴/🟠/✅ | 影响说明 |
| **Schema标记** | ❌/✅ 状态 | 🔴/🟠/✅ | 影响说明 |
| ... | ... | ... | ... |
```

---

### 二、AI平台可见性测试（AI Visibility Test）

#### 2.1 测试平台矩阵

| 平台 | 类型 | 优先级 | URL | 特点 |
|------|------|--------|-----|------|
| **豆包** | 国内AI | 高 | https://www.doubao.com/chat/ | 字节生态，用户基数大 |
| **Kimi** | 国内AI | 高 | https://kimi.moonshot.cn/ | 长文本能力强，免登录 |
| **DeepSeek** | 国内AI | 高 | https://chat.deepseek.com/ | 技术圈影响力 |
| **通义千问** | 国内AI | 中 | https://tongyi.aliyun.com/qianwen/ | 阿里生态 |
| **文心一言** | 国内AI | 中 | https://yiyan.baidu.com/ | 百度生态 |
| **360纳米AI** | AI搜索 | 中 | https://www.n.cn/ | 实时网页检索 |
| **Perplexity** | AI搜索 | 中 | https://www.perplexity.ai/ | 国际AI搜索引擎 |
| **ChatGPT** | 国际AI | 低 | https://chat.openai.com/ | 国际市场参考 |
| **Claude** | 国际AI | 低 | https://claude.ai/ | 国际市场参考 |

#### 2.2 Playwright MCP 自动化测试流程

**核心原则**: AI平台测试必须使用Playwright MCP执行真实测试，不得用预估数据替代。

**执行前检查**:
- Playwright MCP工具可用（`mcp__playwright__browser_navigate`等工具已启用）→ 执行真实测试
- Playwright MCP工具不可用 → 在报告顶部添加免责声明，所有平台数据标注`(预估)`，建议客户手动验证

**免责声明模板（Playwright不可用时）**:
```
⚠️ 数据说明：本报告中的AI平台测试结果为专业预估，非实际Playwright测试数据。
建议管理员配置Playwright MCP后重新执行真实测试以获取准确数据。
```

##### 测试步骤（以豆包为例）

```
1. 导航到平台
   mcp__playwright__browser_navigate → https://www.doubao.com/chat/

2. 获取页面快照，定位输入框
   mcp__playwright__browser_snapshot

3. 输入测试问题
   mcp__playwright__browser_type → 在输入框输入问题

4. 发送问题（点击发送或按Enter）
   mcp__playwright__browser_click 或 mcp__playwright__browser_press_key → Enter

5. 等待AI响应
   mcp__playwright__browser_wait_for → 等待回答出现

6. 获取回答内容
   mcp__playwright__browser_snapshot → 获取AI回答

7. 截图保存证据
   mcp__playwright__browser_take_screenshot → 保存到 01_diagnosis/screenshots/
```

##### 各平台测试配置

| 平台 | 输入框定位 | 发送方式 | 等待标识 | 需要登录 |
|------|-----------|----------|----------|----------|
| **豆包** | textarea | Enter键 | 回答区域 | 否（有限制） |
| **Kimi** | textarea | 点击发送 | 回答完成 | 否 |
| **DeepSeek** | textarea | Enter键 | 回答区域 | 是 |
| **Perplexity** | textarea | Enter键 | Answer区 | 否 |
| **360纳米AI** | input | Enter键 | 回答区域 | 否 |

##### Playwright 测试代码示例

```javascript
// 使用 mcp__playwright__browser_run_code 执行
async (page) => {
  // 1. 导航到豆包
  await page.goto('https://www.doubao.com/chat/');

  // 2. 等待输入框出现
  await page.waitForSelector('textarea');

  // 3. 输入问题
  await page.fill('textarea', '百威啤酒怎么样？');

  // 4. 按Enter发送
  await page.press('textarea', 'Enter');

  // 5. 等待回答
  await page.waitForTimeout(10000);

  // 6. 获取回答文本
  const answer = await page.textContent('.answer-container');
  return answer;
}
```

#### 2.3 测试问题设计

> **重要**: 完整问题库请参考 `shared/question_library.md`，包含通用问题模板和行业专属问题。

**Tier 1 核心问题（必测 15 题）**:

| 类型 | 问题模板 |
|------|---------|
| 品牌认知 | "[品牌名]怎么样？" |
| 品牌认知 | "[品牌名]好不好？" |
| 品牌认知 | "[品牌名]是什么档次？" |
| 品类推荐 | "[品类]推荐哪个品牌？" |
| 品类推荐 | "[品类]哪个牌子好？" |
| 品类推荐 | "[品类]排名/排行榜" |
| 对比决策 | "[品牌]和[竞品1]哪个好？" |
| 对比决策 | "[品牌]和[竞品2]哪个好？" |
| 对比决策 | "[品牌]和[竞品3]哪个好？" |
| 场景推荐 | "[场景1]用什么[品类]好？" |
| 场景推荐 | "[场景2]推荐什么[品类]？" |
| 产品详情 | "[品牌]有哪些产品？" |
| 产品详情 | "[品牌]最好的产品是什么？" |
| 历史故事 | "[品牌]有多少年历史？" |
| 服务售后 | "[品牌]在哪里买？" |

**Tier 2 扩展问题**: 参见 `shared/question_library.md` 第五章

**Tier 3 长尾问题**: 参见 `shared/question_library.md` 第五章及行业专属模板

#### 2.4 测试结果记录模板

```markdown
### AI可见性实测结果

**实测日期**: YYYY-MM-DD
**测试方法**: Playwright MCP 自动化测试
**测试问题**: "具体问题"

| AI平台 | 类型 | 品牌被提及 | 情感倾向 | 推荐的竞品 | 截图 |
|--------|------|------------|----------|-----------|------|
| **豆包** | 国内 | ❌/✅ | 正面/负面/中性 | 竞品1、竞品2... | [链接] |
| **Kimi** | 国内 | ❌/✅ | 正面/负面/中性 | 竞品1、竞品2... | [链接] |
| **DeepSeek** | 国内 | ❌/✅ | 正面/负面/中性 | 竞品1、竞品2... | [链接] |
| **Perplexity** | AI搜索 | ❌/✅ | 正面/负面/中性 | 竞品1、竞品2... | [链接] |
| ... | ... | ... | ... | ... | ... |

**AI可见性得分**: X/9 平台 = XX%
```

#### 2.5 截图保存规范

```
01_diagnosis/screenshots/
├── {品牌名}_{平台名}_{问题编号}_{日期}.png
├── 百威中国_豆包_Q1_2025-12-12.png
├── 百威中国_Kimi_Q1_2025-12-12.png
└── ...
```

---

### 三、竞品分析（Competitor Analysis）

#### 3.1 竞品识别

1. 从AI测试结果中提取被推荐的竞品
2. 统计各竞品被AI推荐的频次
3. 识别高频被推荐的竞品（出现3次以上）

#### 3.2 竞品分析维度

| 维度 | 分析内容 |
|------|----------|
| **市场定位** | 高端/中端/性价比 |
| **核心卖点** | 差异化价值主张 |
| **AI可见性** | 被推荐频次 |
| **官网技术** | Schema/FAQ等 |
| **内容布局** | 知乎/小红书等 |

#### 3.3 竞品对比表模板

```markdown
| 竞品 | 平台1 | 平台2 | ... | 出现次数 |
|------|-------|-------|-----|----------|
| **品牌A** | ✅ | ✅ | ... | X/9 |
| **品牌B** | ✅ | - | ... | X/9 |
```

---

### 四、Schema标记建议

#### 4.1 必需Schema类型

**Organization Schema（首页必加）**:
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "品牌名称",
  "alternateName": "品牌别名",
  "url": "https://www.example.com",
  "logo": "https://www.example.com/logo.png",
  "description": "品牌描述",
  "foundingDate": "成立年份",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "城市",
    "addressCountry": "CN"
  },
  "knowsAbout": ["关键词1", "关键词2"]
}
```

**FAQPage Schema（FAQ页面必加）**:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题1？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "答案1..."
      }
    }
  ]
}
```

**Product Schema（产品页）**:
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名称",
  "description": "产品描述",
  "brand": {
    "@type": "Brand",
    "name": "品牌名"
  }
}
```

**Course Schema（教育/培训类）**:
```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "课程名称",
  "description": "课程描述",
  "provider": {
    "@type": "Organization",
    "name": "机构名称"
  }
}
```

---

### 五、FAQ内容策略

#### 5.1 FAQ问题分类

| 分类 | 问题类型 | 示例 |
|------|----------|------|
| **品牌认知** | XX是什么？XX怎么样？ | "[品牌名]怎么样？" |
| **产品对比** | XX和YY哪个好？ | "[品牌]和[竞品]对比" |
| **价格咨询** | XX多少钱？ | "[产品]价格/费用" |
| **使用指南** | XX怎么用？ | "如何使用[产品]" |
| **常见问题** | XX问题怎么解决？ | "[产品]常见问题" |

#### 5.2 Answer-First写作原则

```
❌ 错误示例:
Q: 百威啤酒怎么样？
A: 百威啤酒源自1876年的美国...（先讲历史）

✅ 正确示例:
Q: 百威啤酒怎么样？
A: 百威是全球销量领先的高端啤酒品牌，以"皇者风范"著称。
   【直接给结论】然后再展开：源自1876年，采用榉木酿造工艺...
```

---

### 六、90天GEO实施计划模板

```
Month 1: 基础建设（Week 1-4）
├── Week 1: 紧急修复
│   ├── 修复Meta Description
│   ├── 修复语言设置
│   └── 部署Organization Schema
├── Week 2-3: Schema全面部署
│   ├── Product/Course Schema
│   ├── FAQ Schema
│   └── BreadcrumbList Schema
└── Week 4: FAQ页面上线
    ├── 基础架构搭建
    └── 首批30个问答

Month 2: 内容布局（Week 5-8）
├── FAQ内容扩展至50-100+
├── 产品/服务对比页面
├── 知乎高质量回答（15-20个）
├── 行业白皮书/指南
└── 案例故事化改造

Month 3: 生态扩展（Week 9-12）
├── 行业媒体PR
├── KOL/专家背书内容
├── 效果监测与优化
└── 第二阶段规划
```

---

### 七、诊断报告输出格式

完整的GEO诊断报告应包含以下章节：

```markdown
# {品牌名} GEO诊断报告

**客户名称**: XXX
**诊断日期**: YYYY-MM-DD
**文档版本**: v1.0

---

## 〇、核心发现摘要（Executive Summary）
- 网站技术审计结果表格
- AI可见性实测结果
- 优先行动建议

## 一、客户概况分析
- 公司基本信息
- 核心产品与服务
- 核心价值主张
- 竞争优势分析

## 二、网站技术审计详情
- 严重问题清单
- 中等问题清单
- 技术亮点

## 三、AI平台实测结果
- 测试方法
- 各平台测试结果
- 竞品分析总结

## 四、GEO策略框架
- 行业GEO特殊性
- 90天快速验证计划
- 重点优化方向

## 五、合作方案与投入产出
- 服务方案建议
- 预期效果
- ROI模型

## 六、Q&A准备
- 预判常见问题及回答

## 七、附录
- Schema标记代码模板
- Meta标签修复建议
```

---

## 使用方式

### 触发条件
当用户提到以下关键词时，自动调用此Skill：
- "GEO诊断" / "GEO分析"
- "AEO诊断" / "AEO分析"
- "AIEO诊断" / "AIEO分析"
- "AI可见性分析"
- "生成引擎优化"
- "品牌AI可见性"

### 诊断流程

1. **确认品牌信息**: 品牌名称、官网URL、行业
2. **技术审计**: 使用 curl/WebFetch 检查网站的GEO技术配置
3. **AI平台实测**: 使用 Playwright MCP 自动化测试各AI平台
   - 导航到AI平台 → 输入测试问题 → 获取回答 → 截图保存
   - 优先测试: 豆包、Kimi、DeepSeek、Perplexity
4. **竞品分析**: 从AI回答中提取竞品信息
5. **生成报告**: 自动保存至 `01_diagnosis/` 目录

### Playwright MCP 测试执行顺序

```
Step 1: 创建截图目录
        mkdir -p 01_diagnosis/screenshots/

Step 2: 依次测试各平台（推荐顺序）
        1. Kimi (免登录，成功率高)
        2. 豆包 (免登录，有使用限制)
        3. Perplexity (免登录，英文为主)
        4. DeepSeek (需登录)
        5. 360纳米AI (免登录)

Step 3: 每个平台执行
        navigate → snapshot → type → press Enter → wait → snapshot → screenshot

Step 4: 汇总结果，计算可见性得分
```

### 报告保存示例

```bash
# 诊断完成后，报告自动保存为：
/Users/kadenliu/AIRetail/Z_GEO/01_diagnosis/百威中国_GEO诊断报告_2025-12-12.md
```

---

## 参考案例

- [OurSchool_AEO启动会准备材料.md](../../OurSchool_AEO启动会准备材料.md) - 数字校园平台案例
- [一堂创业课_AEO启动会准备材料.md](../../一堂创业课_AEO启动会准备材料.md) - 创业培训案例
- [飞鹤奶粉_AEO启动会准备材料.md](../../飞鹤奶粉_AEO启动会准备材料.md) - 消费品牌案例

---

## AI可见性评分标准

| 得分 | 评级 | 说明 |
|------|------|------|
| 0/9 | ❌ 零可见性 | 紧急需要GEO优化 |
| 1-3/9 | 🟠 低可见性 | 需要系统性优化 |
| 4-6/9 | 🟡 中等可见性 | 有基础，需强化 |
| 7-9/9 | 🟢 高可见性 | 保持并持续优化 |

---

## 八、问题库初稿生成

### 8.1 生成时机

在诊断阶段收集完品牌基本信息后，自动生成问题库初稿。

### 8.2 需要收集的信息

| 信息类型 | 说明 | 示例 |
|----------|------|------|
| **品牌名称** | 中文名 + 英文名（如有） | 百威、Budweiser |
| **所属品类** | 一级品类 + 二级品类 | 啤酒、高端啤酒 |
| **主要竞品** | 3-5个直接竞品 | 青岛、雪花、喜力、科罗娜 |
| **核心产品** | 主打产品线 | 百威经典、百威金尊 |
| **目标场景** | 3-5个使用场景 | 朋友聚会、商务宴请、看球赛 |
| **目标人群** | 核心目标客群 | 年轻白领、运动爱好者 |
| **行业类型** | 用于匹配行业专属问题 | FMCG-WINE |

### 8.3 问题库生成逻辑

```
通用问题模板（shared/question_library.md）
    ↓
+ 品牌基本信息（诊断收集）
    ↓
= 品牌专属问题库初稿
```

**实例化示例**：

| 模板 | 实例化问题 |
|------|-----------|
| `[品牌名]怎么样？` | `百威怎么样？` |
| `[品类]哪个牌子好？` | `啤酒哪个牌子好？` |
| `[品牌]和[竞品]哪个好？` | `百威和青岛啤酒哪个好？` |
| `[场景]喝什么[品类]？` | `朋友聚会喝什么啤酒？` |

### 8.4 问题库初稿结构

```markdown
# {品牌名} 问题库

**生成日期**: YYYY-MM-DD
**版本**: v1.0（初稿）
**状态**: 待定位阶段验证

---

## 品牌基本信息

| 项目 | 内容 |
|------|------|
| 品牌名称 | |
| 所属品类 | |
| 主要竞品 | |
| 核心产品 | |
| 目标场景 | |
| 目标人群 | |

---

## Tier 1 核心问题（15题）

### 品牌认知类 (BR)
1. [实例化问题]
2. ...

### 品类推荐类 (CR)
1. [实例化问题]
2. ...

### 对比决策类 (CP)
1. [实例化问题]
2. ...

---

## Tier 2 扩展问题（20题）

### 场景推荐类 (SC)
1. [实例化问题]
2. ...

### 产品详情类 (PD)
1. [实例化问题]
2. ...

---

## Tier 3 行业专属问题（10-15题）

[根据行业类型从 shared/question_library.md 选取]

---

## 下一步

此问题库为初稿，将在定位阶段：
1. 根据竞品分析结果补充对比问题
2. 根据场景分析补充场景问题
3. 根据定位策略调整问题侧重点

---

**问题库模板参考**: shared/question_library.md
```

### 8.5 问题库输出位置

```
/Users/kadenliu/AIRetail/Z_GEO/01_diagnosis/{品牌名}_问题库_{YYYY-MM-DD}.md
```

### 8.6 问题库流转说明

```
诊断阶段                    定位阶段                     内容阶段                    监控阶段
    │                          │                           │                          │
    ▼                          ▼                           ▼                          ▼
生成问题库初稿 ──────→ 修正/扩展问题库 ──────→ 基于问题库生成FAQ ──────→ 使用问题库监控
(v1.0 初稿)              (v2.0 定稿)              (内容输出)                (追踪变化)
    │                          │                           │                          │
    └──────────────────────────┴───────────────────────────┴──────────────────────────┘
                                     问题库贯穿全流程
```
