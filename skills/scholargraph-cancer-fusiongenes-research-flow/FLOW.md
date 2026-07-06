# ScholarGraph-FusionGenes 工作流程说明

## 流程概述

全流程使用 **ScholarGraph v1.4 及以上版本 skill** 进行：

```
第一轮搜索: 各癌种融合基因 review
        ↓
深度分析: 提取融合基因、伙伴、断点、频率
        ↓
获取 PDF 文献 (Europe PMC)
        ↓
第二轮补充搜索: 发现遗漏基因
        ↓
多轮搜索结果合并去重
        ↓
生成结构化 Excel 表格 (每行独立完整)
```

---

## 详细步骤

### Step 1: 第一轮文献搜索
- 使用 ScholarGraph 搜索各癌种融合基因 review
- 按癌种分类：肺癌、乳腺癌、结直肠癌、实体瘤
- 筛选 Review 类型文献
- 保存结果到 `round1.json`

### Step 2: 深度分析
- 搜索特定基因融合详细信息
- 提取: 基因、融合伙伴、断裂点、频率、靶向药物
- 提取参考文献 (作者、标题、期刊、年份、PMID)

### Step 3: 获取 PDF 文献
- 使用 Europe PMC 下载免费文献
- 创建 `research/fusion/review/` 目录存储

### Step 4: 第二轮补充搜索
- 搜索可能遗漏的融合基因
- 搜索非 EML4 的 ALK 融合、ESR1、BRAF、MET 等
- 保存结果到 `round2.json`

### Step 5: 多轮搜索结果合并去重

```javascript
// merge_fusion_data.js
function mergeAndDeduplicate(round1, round2) {
  const seen = new Map();
  const merged = [];
  
  for (const item of [...round1, ...round2]) {
    // 根据基因+融合伙伴作为唯一标识
    const key = `${item.gene}-${item.fusion}`;
    if (!seen.has(key)) {
      seen.set(key, true);
      merged.push(item);
    }
  }
  return merged;
}
```

### Step 6: 生成 Excel 表格

⚠️ **关键规范**: 每行参考文献必须独立完整

Excel 自动生成两列新数据:
- **频率级别**: 基于频率自动计算 (高/中/低/极低)
- **参考文献数**: 统计每行参考文献数量

✅ 正确:
```javascript
{ 
  "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg... Lung Cancer. 2021; PMID: 34175504; Christopoulos P, et al. EML4-ALK fusion variant V3... Clin Cancer Res. 2018"
}
```

❌ 错误:
```javascript
{ "参考文献": "同上" }
{ "参考文献": "同V3a" }
```

---

## 频率级别标签逻辑

| 频率级别 | 阈值 |
|---------|------|
| 高 | ≥25% |
| 中 | 10-24% |
| 低 | 3-9% |
| 极低 | <3% |
| - | 特殊(EGFR扩增) |

---

## 输出文件结构

```
/workspace/research/fusion/
├── review/                    # PDF 文献
│   ├── 01_xxx.pdf
│   └── ...
├── reports/                   # 分析报告
│   ├── fusion_genes_report.xlsx   # 主输出
│   └── ...
├── round1.json                # 第一轮搜索结果
├── round2.json                # 第二轮搜索结果
├── merged_results.json        # 合并去重后结果
└── generate_excel.js          # Excel 生成脚本
```

---

## Excel 表格内容

### Sheet 1: 融合基因汇总 (16列)
| 字段 | 说明 |
|------|------|
| 基因 | ALK, ROS1, RET, NTRK1/2/3, MET, FGFR, NRG1, BRAF, EGFR, ESR1 |
| 融合类型 | 完整融合名称 (如EML4-ALK) |
| 变体 | V1/V2/V3a/缺失突变/- |
| 融合转录本 | NM_004935 (ALK), NM_002944 (ROS1) 等 |
| 参考基因组 | GRCh37 |
| 5'基因 | 5'伙伴基因 |
| 5'基因断裂位置 | exon/intron + 编号 |
| 3'基因 | 3'端基因 |
| 3'基因断裂位置 | exon/intron + 编号 |
| 频率 | 发生频率 |
| 频率级别 | 高/中/低/极低 (自动计算) |
| 癌种 | 关联癌种 |
| 临床意义 | 临床意义描述 |
| 靶向药物 | 靶向药物 (分号分隔) |
| 参考文献 | 完整引用 (分号分隔多来源) |
| 参考文献数 | 自动统计 |

### Sheet 2: 探针设计推荐
- DNA探针区域、RNA探针区域、探针长度、备注

### Sheet 3: 分癌种汇总
- 癌种、融合数、主要基因

---

## 核心命令

```bash
# 搜索
bun run cli.ts search "关键词" --limit 10

# 下载
bun run cli.ts download "关键词" --limit 5 --output ./downloads

# 合并去重
node merge_fusion_data.js

# 生成 Excel
node generate_excel.js
```

---

## 更新日志

- 2026-03-06 v2: 增加多轮搜索合并去重逻辑，明确 Excel 参考文献格式规范
- 2026-03-06 v3: 增加频率级别标签逻辑 (高/中/低/极低)，增加参考文献数统计
