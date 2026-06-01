# GEO/AEO/AIEO 诊断快速检查清单

> **术语说明**: GEO（生成引擎优化）、AEO（答案引擎优化）、AIEO（AI引擎优化）可互换使用

---

## 报告输出规范

### 命名格式
```
{品牌名}_GEO诊断报告_{YYYY-MM-DD}.md
```

### 创建命令
```bash
DATE=$(date +%Y-%m-%d)
# 保存到客户工作目录 (由管理员指定)
touch "{客户工作目录}/{品牌名}_GEO诊断报告_${DATE}.md"
```

---

## 网站技术审计 Checklist

### 🔴 严重问题（必须修复）

- [ ] **Meta Description** - 是否存在且有意义？
  - 检查: `<meta name="description" content="...">`
  - 常见问题: 为空、显示模板默认文字、过长/过短

- [ ] **Schema标记** - 是否部署结构化数据？
  - 检查: `<script type="application/ld+json">`
  - 必需类型: Organization, FAQPage, Product/Course

- [ ] **FAQ页面** - 是否有独立FAQ专区？
  - 至少30+问答对
  - 覆盖品牌对比、产品选择、使用指南等

- [ ] **Answer-First结构** - 内容是否以直接答案开头？
  - 核心页面应直接回答用户问题
  - 避免"品牌故事式"开头

### 🟠 中等问题（建议修复）

- [ ] **Open Graph标签** - 社交分享是否优化？
  - 检查: `og:title`, `og:description`, `og:image`
  - 影响微信/社交媒体分享效果

- [ ] **Canonical标签** - 是否避免重复内容？
  - 检查: `<link rel="canonical" href="...">`

- [ ] **HTML lang属性** - 语言设置是否正确？
  - 中文网站应为: `<html lang="zh-CN">`

- [ ] **图片Alt属性** - 图片是否可索引？
  - 缺失率应<30%

- [ ] **H1标签** - 每页是否仅有1个H1？
  - 多个H1会稀释页面主题

- [ ] **SSL证书** - HTTPS是否正常？

- [ ] **页面加载速度** - 是否<3秒？

---

## AI平台测试 Checklist

### 必测平台（国内）

- [ ] **文心一言** - https://yiyan.baidu.com
- [ ] **豆包** - https://www.doubao.com
- [ ] **通义千问** - https://tongyi.aliyun.com
- [ ] **DeepSeek** - https://chat.deepseek.com
- [ ] **Kimi** - https://kimi.moonshot.cn

### 必测平台（AI搜索）

- [ ] **360纳米AI** - https://n.cn
- [ ] **Perplexity** - https://www.perplexity.ai

### 可选平台（国际）

- [ ] **ChatGPT** - https://chat.openai.com
- [ ] **Claude** - https://claude.ai
- [ ] **Gemini** - https://gemini.google.com

### 测试问题模板

**Tier 1 核心问题**:
1. "[行业]哪个品牌/平台最好？"
2. "[品牌名]怎么样？"
3. "[品牌名]和[竞品]哪个好？"

**Tier 2 对比问题**:
1. "[品牌A]和[品牌B]对比"
2. "[产品类型]选购指南"

**Tier 3 长尾问题**:
1. 使用场景相关
2. 常见问题/疑虑

---

## 竞品分析 Checklist

- [ ] 从AI测试结果提取被推荐竞品
- [ ] 统计各竞品被推荐频次
- [ ] 识别高频竞品（≥3次）
- [ ] 分析竞品官网技术配置
- [ ] 分析竞品内容布局（知乎/小红书等）

---

## 报告输出 Checklist

- [ ] **Executive Summary** - 核心发现摘要
- [ ] **客户概况** - 公司信息、产品、价值主张
- [ ] **技术审计** - 问题清单、严重程度
- [ ] **AI测试结果** - 各平台测试截图/记录
- [ ] **竞品分析** - 竞品对比表
- [ ] **策略框架** - 90天计划
- [ ] **Schema代码** - 可直接使用的代码模板
- [ ] **Meta标签** - 修复建议
- [ ] **保存报告** - 保存至 `diagnosis/` 目录

---

## 常用curl命令

```bash
# 检查HTTP头
curl -sI https://example.com

# 检查Meta标签
curl -s https://example.com | grep -E '<meta|<title'

# 检查Schema
curl -s https://example.com | grep 'application/ld+json'

# 检查Open Graph
curl -s https://example.com | grep 'og:'

# 检查lang属性
curl -s https://example.com | grep '<html'

# 检查H1标签
curl -s https://example.com | grep -i '<h1'
```

---

## AI可见性评分标准

| 得分 | 评级 | 说明 |
|------|------|------|
| 0/9 | ❌ 零可见性 | 紧急需要GEO优化 |
| 1-3/9 | 🟠 低可见性 | 需要系统性优化 |
| 4-6/9 | 🟡 中等可见性 | 有基础，需强化 |
| 7-9/9 | 🟢 高可见性 | 保持并持续优化 |

