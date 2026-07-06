---
name: scholargraph-fusion-genes
description: 使用 ScholarGraph v1.4 及以上版本 进行癌症融合基因文献调研的全流程技能。包括搜索、多轮合并去重、提取信息、生成报告和 Excel 表格。
metadata:
  {
    "openclaw": {
      "emoji": "🧬",
      "requires": {
        "bins": ["bun", "node"],
        "env": ["AI_PROVIDER", "MINIMAX_API_KEY"]
      }
    }
  }
---

# ScholarGraph-FusionGenes 使用流程

## 概述

本技能提供癌症融合基因文献调研的完整流程，使用 ScholarGraph v1.4 及以上版本 进行系统性搜索、分析和整理。支持多轮搜索、合并去重、生成含完整参考文献的 Excel 表格。

## 适用场景

- 癌症融合基因文献调研
- 融合探针设计区域分析
- 靶向治疗生物标志物研究

---

## 完整工作流程

### 步骤 1: 环境配置

```bash
# 1. 进入 ScholarGraph 目录
cd /root/.openclaw/workspace/skills/ScholarGraph

# 2. 配置 MiniMax API Key (或使用其他 provider)
export AI_PROVIDER=minimax
export MINIMAX_API_KEY="your-api-key"

# 3. 验证配置
~/.bun/bin/bun run cli.ts --help
```

### 步骤 2: 第一轮文献搜索

```bash
# 创建工作目录
mkdir -p /workspace/research/fusion/review
mkdir -p /workspace/research/fusion/reports

# 第一轮: 搜索各癌种融合基因 review
~/.bun/bin/bun run cli.ts search "lung cancer fusion gene review" --limit 10
~/.bun/bin/bun run cli.ts search "breast cancer fusion gene review" --limit 10
~/.bun/bin/bun run cli.ts search "colorectal cancer fusion gene review" --limit 10
~/.bun/bin/bun run cli.ts search "solid tumor fusion gene review" --limit 10
```

### 步骤 3: 深度分析 - 搜索融合基因详细信息

```bash
# 搜索特定基因的融合信息 (并行执行)
~/.bun/bin/bun run cli.ts search "EML4-ALK fusion variant V1 V2 V3 breakpoint" --limit 10
~/.bun/bin/bun run cli.ts search "ROS1 fusion partner CD74 SDC4 TPM3" --limit 10
~/.bun/bin/bun run cli.ts search "RET fusion KIF5B CCDC6 NCOA4 breakpoint" --limit 10
~/.bun/bin/bun run cli.ts search "NTRK1 NTRK2 NTRK3 fusion partner ETV6" --limit 10
~/.bun/bin/bun run cli.ts search "FGFR fusion partner TACC3 BICC1" --limit 10
~/.bun/bin/bun run cli.ts search "NRG1 fusion CD74 SDC4 cancer" --limit 10
```

### 步骤 4: 获取 PDF 文献

```bash
# 使用 Europe PMC 下载免费文献 (推荐)
# 搜索 PMID 后访问: https://europepmc.org/articles/PMC[ID]?pdf=render
curl -L -o "/workspace/research/fusion/review/filename.pdf" "https://europepmc.org/articles/PMC[ID]?pdf=render"

# 或使用 ScholarGraph download (需配置 SERPER_API_KEY)
~/.bun/bin/bun run cli.ts download "RET fusion cancer review" --limit 3 --output /workspace/research/fusion/review
```

### 步骤 5: 第二轮补充搜索 (发现遗漏)

```bash
# 补充搜索可能遗漏的融合基因
~/.bun/bin/bun run cli.ts search "EGFRvIII glioma fusion deletion" --limit 5
~/.bun/bin/bun run cli.ts search "ESR1 fusion breast cancer endocrine resistance" --limit 5
~/.bun/bin/bun run cli.ts search "BRAF fusion KIAA1549 melanoma" --limit 5
~/.bun/bin/bun run cli.ts search "MET fusion CAPZA2 LAYN lung cancer" --limit 5
~/.bun/bin/bun run cli.ts search "ALK fusion HIP1 KIF5B non-EML4" --limit 5
```

### 步骤 6: 多轮搜索结果合并去重

将多轮搜索结果保存到 JSON 文件，然后进行合并去重:

```javascript
// merge_results.js
const fs = require('fs');

// 假设有两轮搜索结果
const round1 = require('./round1.json');
const round2 = require('./round2.json');

// 合并去重函数
function mergeAndDeduplicate(results1, results2) {
  const seen = new Map();
  const merged = [];
  
  for (const item of [...results1, ...results2]) {
    // 根据基因+融合伙伴作为唯一标识
    const key = `${item.gene}-${item.fusion}`;
    if (!seen.has(key)) {
      seen.set(key, true);
      merged.push(item);
    }
  }
  return merged;
}

const merged = mergeAndDeduplicate(round1, round2);
fs.writeFileSync('./merged_results.json', JSON.stringify(merged, null, 2));
console.log(`Merged: ${merged.length} unique records`);
```

### 步骤 7: 生成 Excel 表格 (含完整字段)

```bash
# 安装 xlsx 库
npm install xlsx
```

创建 `generate_excel.js`:

```javascript
const XLSX = require('xlsx');

// ========== 辅助函数 ==========

// 频率级别标签逻辑
function getFreqLabel(freq) {
  // 特殊情况: EGFR扩增等
  if (freq.includes('EGFR扩增')) return '-';
  
  // 提取所有数字
  const nums = freq.match(/\d+/g)?.map(Number) || [];
  if (nums.length === 0) return '-';
  
  // 取最大值进行判断
  const maxVal = Math.max(...nums);
  
  // 频率级别判断
  if (maxVal >= 25) return '高';    // ≥25%: 高频率
  if (maxVal >= 10) return '中';    // 10-24%: 中频率
  if (maxVal >= 3) return '低';     // 3-9%: 低频率
  return '极低';                     // <3%: 极低频率
}

// 参考文献数量统计
function countSources(ref) {
  if (!ref) return 0;
  const sources = ref.split(/;\s*/).filter(s => s.trim().length > 0);
  return sources.length;
}

// 标准转录本映射
const transcriptMap = {
  'ALK': 'NM_004935',
  'ROS1': 'NM_002944',
  'RET': 'NM_020975',
  'NTRK1': 'NM_002529',
  'NTRK2': 'NM_006180',
  'NTRK3': 'NM_002449',
  'MET': 'NM_000245',
  'FGFR1': 'NM_023110',
  'FGFR2': 'NM_000141',
  'FGFR3': 'NM_001142',
  'NRG1': 'NM_013962',
  'BRAF': 'NM_004333',
  'EGFR': 'NM_005228',
  'ESR1': 'NM_000125',
};

// ============================

// 完整数据格式 - 每行独立完整
// 字段: 基因, 融合类型, 变体, 融合转录本, 参考基因组, 5'基因, 5'基因断裂位置, 3'基因, 3'基因断裂位置, 频率, 癌种, 临床意义, 靶向药物, 参考文献
const fusionData = [
  // 示例:
  { 
    "基因": "ALK", 
    "融合类型": "EML4-ALK", 
    "变体": "V1",
    "融合转录本": "NM_004935",
    "参考基因组": "GRCh37",
    "5'基因": "EML4", 
    "5'基因断裂位置": "exon 13", 
    "3'基因": "ALK", 
    "3'基因断裂位置": "exon 20",
    "频率": "~33%", 
    "癌种": "肺癌", 
    "临床意义": "标准型", 
    "靶向药物": "Crizotinib; Alectinib", 
    "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg... Lung Cancer. 2021; PMID: 34175504"
  },
  // ... 更多记录
];

// 添加频率级别和参考文献数
const enrichedData = fusionData.map(item => ({
  ...item,
  "频率级别": getFreqLabel(item["频率"]),
  "参考文献数": countSources(item["参考文献"])
}));

const wb = XLSX.utils.book_new();

// Sheet 1: 融合基因汇总
const mainSheet = XLSX.utils.json_to_sheet(enrichedData);
XLSX.utils.book_append_sheet(wb, mainSheet, "融合基因汇总");

// Sheet 2: 探针设计推荐
const probeData = [
  { "基因": "ALK", "DNA探针区域": "intron 19", "RNA探针区域": "exon 18-21", "探针长度": "300-500bp", "备注": "覆盖所有变体" },
  { "基因": "ROS1", "DNA探针区域": "intron 31-35", "RNA探针区域": "exon 32-36", "探针长度": "400-600bp", "备注": "覆盖常见融合伙伴" },
  // ...
];
const probeSheet = XLSX.utils.json_to_sheet(probeData);
XLSX.utils.book_append_sheet(wb, probeSheet, "探针设计推荐");

// Sheet 3: 分癌种汇总
const cancerSummary = [
  { "癌种": "肺癌", "融合数": 15, "主要基因": "ALK, ROS1, RET, MET" },
  { "癌种": "乳腺癌", "融合数": 3, "主要基因": "ESR1, NTRK" },
  // ...
];
const cancerSheet = XLSX.utils.json_to_sheet(cancerSummary);
XLSX.utils.book_append_sheet(wb, cancerSheet, "分癌种汇总");

// 保存文件
XLSX.writeFile(wb, '/workspace/research/fusion/reports/fusion_genes_report.xlsx');
```

运行生成:
```bash
node generate_excel.js
```

---

## Excel 表格规范

### 频率级别标签逻辑

⚠️ **重要**: 每行必须包含独立完整的频率级别，不依赖其他行

```javascript
// 频率级别判断函数
function getFreqLabel(freq) {
  // 特殊情况: EGFR扩增等
  if (freq.includes('EGFR扩增')) return '-';
  
  // 提取所有数字
  const nums = freq.match(/\d+/g)?.map(Number) || [];
  if (nums.length === 0) return '-';
  
  // 取最大值进行判断
  const maxVal = Math.max(...nums);
  
  // 频率级别判断
  if (maxVal >= 25) return '高';    // ≥25%: 高频率
  if (maxVal >= 10) return '中';    // 10-24%: 中频率
  if (maxVal >= 3) return '低';     // 3-9%: 低频率
  return '极低';                     // <3%: 极低频率
}
```

| 频率级别 | 阈值范围 | 示例 |
|---------|---------|------|
| 高 | ≥25% | ~33%, ~29%, ~50%, ~70% |
| 中 | 10-24% | ~15%, ~10%, ~20% |
| 低 | 3-9% | ~5%, ~8%, ~3% |
| 极低 | <3% | <1%, ~2% |
| - | 特殊 | EGFRvIII (~50% EGFR扩增) |

### 参考文献格式要求

⚠️ **重要**: 每行参考文献必须独立完整，不依赖其他行信息

✅ 正确格式:
```text
参考文献: Zhang SS, et al. Going beneath the tip of the iceberg: Identifying and understanding EML4-ALK variants and TP53 mutations. Lung Cancer. 2021; PMID: 34175504; Christopoulos P, et al. EML4-ALK fusion variant V3 is a high-risk feature. Clin Cancer Res. 2018
```

❌ 错误格式 (依赖其他行):
```text
参考文献: 同上
参考文献: 同V3a
```

### 字段说明 (Sheet 1: 融合基因汇总 - 16列)

| 字段 | 说明 | 示例 |
|------|------|------|
| 基因 | 融合基因名称 | ALK, ROS1, RET |
| 融合类型 | 完整融合名称 | EML4-ALK, CD74-ROS1 |
| 变体 | 变体信息 (如V1/V3) | V1, V3a, - |
| 融合转录本 | 标准转录本ID | NM_004935 |
| 参考基因组 | 基因组版本 | GRCh37 |
| 5'基因 | 5'端伙伴基因 | EML4, CD74 |
| 5'基因断裂位置 | 断裂位置(必须包含exon/intron) | exon 13, intron 6 |
| 3'基因 | 3'端基因 | ALK, ROS1 |
| 3'基因断裂位置 | 断裂位置(必须包含exon/intron) | exon 20, intron 31 |
| 频率 | 发生频率 | ~33%, ~10-15% |
| 频率级别 | 自动计算 | 高/中/低/极低 |
| 癌种 | 关联癌种 | 肺癌, 泛癌种 |
| 临床意义 | 临床意义描述 | 最常见, 耐药 |
| 靶向药物 | 靶向药物 (分号分隔) | Crizotinib; Alectinib |
| 参考文献 | 完整引用 (作者; 作者; 期刊. 年份; PMID) | 见格式规范 |
| 参考文献数 | 自动统计来源数量 | 1, 2 |
| 癌种 | 关联癌种 | 肺癌, 泛癌种 |
| 临床意义 | 临床意义描述 | 最常见, 耐药 |
| 靶向药物 | 靶向药物 | Crizotinib; Alectinib |
| 参考文献 | 完整引用信息 | 见上文格式 |

---

## 关键命令速查

| 功能 | 命令 |
|------|------|
| 搜索文献 | `bun run cli.ts search "关键词" --limit 10` |
| 下载 PDF | `bun run cli.ts download "关键词" --limit 5 --output ./downloads` |
| 学习概念 | `bun run cli.ts learn "概念" --depth intermediate` |
| 分析论文 | `bun run cli.ts analyze "论文URL" --mode deep` |
| 构建知识图谱 | `bun run cli.ts graph 概念1 概念2 --format mermaid` |
| 生成 Excel | `node generate_excel.js` |

---

## 配置说明

### MiniMax API 配置

在 `ScholarGraph/.env` 文件中配置:

```bash
AI_PROVIDER=minimax
MINIMAX_API_KEY=sk-cp-xxx
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.5
```

### 注意事项

1. **API 限制**: Semantic Scholar 有 429 速率限制，建议使用 PubMed/OpenAlex 源
2. **PDF 下载**: 大多数期刊 DOI 需要订阅，可尝试 Europe PMC 获取免费文献
3. **文献审核**: 报告中所有数据应标注参考文献，便于人工核实
4. **Excel 规范**: 每行参考文献必须独立完整，使用分号分隔多来源

---

## 输出文件结构

```
/workspace/research/fusion/
├── review/                    # PDF 文献
│   ├── 01_Drug_resistance_2021.pdf
│   ├── 02_TNBC_molecular_mechanisms_2022.pdf
│   └── ...
├── reports/                  # 分析报告
│   ├── fusion_probe_design_report_v2.md
│   ├── detection_methods_report.md
│   └── fusion_genes_report.xlsx    # 主输出
├── round1.json               # 第一轮搜索结果
├── round2.json                # 第二轮搜索结果
├── merged_results.json       # 合并去重后结果
└── generate_excel.js         # Excel 生成脚本
```

---

## 常见问题

### Q1: ScholarGraph learn/analyze 报错
**A**: 检查 API Key 是否正确配置，或尝试使用其他 provider

### Q2: PDF 下载失败 (403/406)
**A**: 大多数期刊需要订阅，使用 Europe PMC 作为备选

### Q3: Semantic Scholar 429 错误
**A**: 使用 `--source pubmed` 或 `--source openalex` 绕过

### Q4: Excel 参考文献格式问题
**A**: 确保每行独立完整，不使用"同上"或"同V3a"等依赖表述

---

## 更新日志

- 2026-03-06: 初始版本，包含完整流程
- 2026-03-06 v2: 增加多轮搜索合并去重逻辑，更新 Excel 参考文献格式规范
- 2026-03-07 v3: 新增"教授级深度搜索"方法论

---

## 教授级深度搜索方法论

### 核心理念

教授级搜索不仅是找文献，而是**系统性构建知识体系**。核心原则：

1. **按癌种分类** - 不是按基因，而是按临床应用场景组织
2. **证据分级** - 从临床意义角度解读，不只是罗列基因
3. **可追溯** - 每条信息标注 PMID，便于溯源核实
4. **新发现优先** - 关注近1-2年的新融合、新靶点

### 搜索策略

#### Step 1: 确定癌种范围

根据研究目的确定重点癌种:

| 优先级 | 癌种 | 常见融合基因 |
|--------|------|-------------|
| 高 | 肺癌 | EML4-ALK, ROS1融合, RET, MET, NTRK |
| 高 | 结直肠癌 | RSPO融合, NTRK, ALK |
| 高 | 乳腺癌 | ESR1, NTRK, ETV6-NTRK3 |
| 中 | 胆管癌 | FGFR2融合, TFG-MET |
| 中 | 胃肠道间质瘤 | KIT, PDGFRA, NTRK |
| 泛癌 | 实体瘤 | NTRK1/2/3, BRAF, NRG1 |

#### Step 2: 针对性搜索命令

每个癌种执行深度搜索:

```bash
# 肺癌融合基因深度搜索
~/.bun/bin/bun run cli.ts search "lung cancer fusion gene 2024 2025" --limit 20
~/.bun/bin/bun run cli.ts search "ROS1 CD74 fusion lung cancer clinical" --limit 10
~/.bun/bin/bun run cli.ts search "EML4-ALK variant V1 V3 breakpoint" --limit 10

# 结直肠癌融合基因
~/.bun/bin/bun run cli.ts search "colorectal cancer fusion gene RSPO Wnt" --limit 15

# 乳腺癌融合基因
~/.bun/bin/bun run cli.ts search "breast cancer fusion gene NTRK ESR1" --limit 15

# 胆管癌/胆囊癌融合
~/.bun/bin/bun run cli.ts search "biliary cancer FGFR2 fusion MET" --limit 15

# 胃肠道间质瘤
~/.bun/bin/bun run cli.ts search "GIST KIT PDGFRA NTRK fusion" --limit 15

# 泛癌种/罕见实体瘤
~/.bun/bin/bun run cli.ts search "solid tumor NTRK fusion basket trial" --limit 15
~/.bun/bin/bun run cli.ts search "NUT carcinoma fusion gene" --limit 10
```

#### Step 3: 临床意义深度挖掘

针对每个发现的融合，搜索其临床意义:

```bash
# 靶向治疗响应
~/.bun/bin/bun run cli.ts search "[融合名] TKI response targeted therapy" --limit 5

# 耐药机制
~/.bun/bin/bun run cli.ts search "[融合名] resistance crizotinib alectinib" --limit 5

# 诊断价值
~/.bun/bin/bun run cli.ts search "[融合名] diagnostic biomarker" --limit 5

# 预后意义
~/.bun/bin/bun run cli.ts search "[融合名] prognosis survival" --limit 5
```

### 输出格式规范

教授级搜索结果**必须**采用以下格式:

#### 格式要求

```
## [癌种名称] (英文)

| 融合 | 临床意义 | PMID |
| ---- | -------- | ---- |
| [融合名称1] | [具体临床意义描述] | [PMID1] |
| [融合名称2] | [具体临床意义描述] | [PMID2] |
```

#### 示例输出

```
肺癌 (Lung Cancer)

| 融合 | 临床意义 | PMID |
| ----------- | --------------------- | -------- |
| ROS1-CD74 | 新融合伙伴，部分TKI有效 | 36387218 |
| HIPK2::YAP1 | 肺纤维瘤病新实体 | 38714933 |
| BRAF融合变异体 | DNA+RNA测序揭示结构 | 40253487 |
| ETV6::NTRK3 | 非典型类癌，repotrectinib有效 | 38113652 |

结直肠癌 (Colorectal Cancer)

| 融合 | 临床意义 | PMID |
| ------ | ------- | -------- |
| RSPO融合 | Wnt通路激活 | 35715628 |
| 新型结构变异 | 长读测序发现 | 36812239 |
```

### 质量检查清单

在输出最终结果前，检查以下要点:

- [ ] 每条记录包含: 融合名称 + 临床意义 + PMID
- [ ] 临床意义具体明确 (不只是"发现新融合")
- [ ] 包含治疗响应信息 (如TKI药物名称)
- [ ] 标注PMID便于文献追溯
- [ ] 按癌种分类组织，非按基因
- [ ] 新发现优先展示 (近年文献)
- [ ] 表格格式清晰统一

### 与传统搜索的区别

| 维度 | 传统搜索 | 教授级搜索 |
|------|---------|-----------|
| 组织方式 | 按基因 | 按癌种/临床场景 |
| 信息深度 | 基因+频率 | 融合+临床意义+药物 |
| 证据追溯 | 可选 | 必含PMID |
| 时间维度 | 无要求 | 优先新发现 |
| 输出格式 | 自由文本 | 标准化表格 |

### 进阶技巧

1. **长读测序发现**: 搜索 "long-read sequencing fusion" 发现结构变异
2. **RNA-seq验证**: 搜索 "RNA-seq fusion validation" 确认融合转录本
3. **少见癌种**: 使用 "pediatric" + "fusion" 搜索儿童肿瘤
4. **耐药研究**: 重点关注 "resistance" + "fusion" + "TKI"
