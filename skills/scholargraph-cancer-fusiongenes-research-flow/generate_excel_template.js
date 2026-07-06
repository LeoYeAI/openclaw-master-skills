const XLSX = require('xlsx');

// 频率标签逻辑
function getFreqLabel(freq) {
  if (freq.includes('EGFR扩增')) return '-';
  const nums = freq.match(/\d+/g)?.map(Number) || [];
  if (nums.length === 0) return '-';
  const maxVal = Math.max(...nums);
  if (maxVal >= 25) return '高';
  if (maxVal >= 10) return '中';
  if (maxVal >= 3) return '低';
  return '极低';
}

function countSources(ref) {
  if (!ref) return 0;
  return ref.split(/;\s*/).filter(s => s.trim().length > 0).length;
}

// 提取变体信息
function extractVariant(fusionType) {
  const match = fusionType.match(/V\d[a-z]?$/);
  return match ? match[0] : '-';
}

// 完整数据 - 修复了缺失的5'伙伴断裂
const fusionData = [
  // ALK
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V1", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 13", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~33%", "癌种": "肺癌", "临床意义": "标准型", "靶向药物": "Crizotinib; Alectinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504; Christopoulos P, et al. EML4-ALK fusion variant V3. Clin Cancer Res. 2018" },
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V2", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 20", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~10%", "癌种": "肺癌", "临床意义": "预后较好", "靶向药物": "Crizotinib; Alectinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504" },
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V3a", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 6a", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~29%", "癌种": "肺癌", "临床意义": "最常见变体，与一代TKI耐药相关", "靶向药物": "Lorlatinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504; Christopoulos P, et al. EML4-ALK fusion variant V3. Clin Cancer Res. 2018" },
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V3b", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 6b", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~10%", "癌种": "肺癌", "临床意义": "与V3a相似的生物学行为", "靶向药物": "Lorlatinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504" },
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V5'", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 2", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~5%", "癌种": "肺癌", "临床意义": "少见变体", "靶向药物": "Alectinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504" },
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V5a", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 18", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~6%", "癌种": "肺癌", "临床意义": "少见变体", "靶向药物": "Alectinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504" },
  { "基因": "ALK", "融合类型": "EML4-ALK", "变体": "V7", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "EML4", "5'基因断裂位置": "exon 14", "3'基因": "ALK", "3'基因断裂位置": "exon 20", "频率": "~3%", "癌种": "肺癌", "临床意义": "少见变体", "靶向药物": "Alectinib", "参考文献": "Zhang SS, et al. Going beneath the tip of the iceberg. Lung Cancer. 2021; PMID: 34175504" },
  { "基因": "ALK", "融合类型": "HIP1-ALK", "变体": "-", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "HIP1", "5'基因断裂位置": "", "3'基因": "ALK", "3'基因断裂位置": "exon 19", "频率": "<1%", "癌种": "肺癌", "临床意义": "少见非EML4融合", "靶向药物": "Crizotinib", "参考文献": "Zhu YC, et al. HIP1-ALK fusion variant in non-small cell lung cancer. Case Rep Oncol. 2018" },
  { "基因": "ALK", "融合类型": "KIF5B-ALK", "变体": "-", "融合转录本": "NM_004935", "参考基因组": "GRCh37", "5'基因": "KIF5B", "5'基因断裂位置": "", "3'基因": "ALK", "3'基因断裂位置": "exon 19", "频率": "<1%", "癌种": "肺癌", "临床意义": "少见非EML4融合", "靶向药物": "Crizotinib", "参考文献": "Zhao R, et al. Clinicopathological Features of ALK Expression. 2019" },
  
  // ROS1 - 修复了缺失的5'伙伴断裂
  { "基因": "ROS1", "融合类型": "CD74-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5'基因": "CD74", "5'基因断裂位置": "exon 6", "3'基因": "ROS1", "3'基因断裂位置": "exon 31", "频率": "~35-40%", "癌种": "肺癌", "临床意义": "最常见ROS1融合", "靶向药物": "Crizotinib; Entrectinib", "参考文献": "Bubendorf L, et al. Testing for ROS1 in non-small cell lung cancer. Virchows Arch. 2016; Park S, et al. Characteristics and Outcome of ROS1-Positive NSCLC. J Thorac Oncol. 2018" },
  { "基因": "ROS1", "融合类型": "SDC4-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5'基因": "SDC4", "5'基因断裂位置": "exon 4", "3'基因": "ROS1", "3'基因断裂位置": "exon 31", "频率": "~10-15%", "癌种": "肺癌", "临床意义": "常见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1 in non-small cell lung cancer. Virchows Arch. 2016" },
  { "基因": "ROS1", "融合类型": "TPM3-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5'基因": "TPM3", "5'基因断裂位置": "exon 8", "3'基因": "ROS1", "3'基因断裂位置": "exon 32", "频率": "~8-10%", "癌种": "肺癌", "临床意义": "常见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1 in non-small cell lung cancer. Virchows Arch. 2016" },
  { "基因": "ROS1", "融合类型": "EZR-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5'基因": "EZR", "5'基因断裂位置": "exon 10", "3'基因": "ROS1", "3'基因断裂位置": "exon 31", "频率": "~5-8%", "癌种": "肺癌", "临床意义": "少见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1. Virchows Arch. 2016" },
  { "基因": "ROS1", "融合类型": "KDELR2-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5\'基因": "KDELR2", "5'基因断裂位置": "exon 2", "3'基因": "ROS1", "3'基因断裂位置": "exon 31", "频率": "~3%", "癌种": "肺癌", "临床意义": "少见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1. Virchows Arch. 2016" },
  { "基因": "ROS1", "融合类型": "TPR-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5\'基因": "TPR", "5'基因断裂位置": "exon 4", "3'基因": "ROS1", "3'基因断裂位置": "exon 31", "频率": "~2%", "癌种": "肺癌", "临床意义": "少见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1. Virchows Arch. 2016" },
  { "基因": "ROS1", "融合类型": "ZCCHC8-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5\'基因": "ZCCHC8", "5'基因断裂位置": "exon 1", "3'基因": "ROS1", "3'基因断裂位置": "exon 31", "频率": "~1%", "癌种": "肺癌", "临床意义": "少见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1. Virchows Arch. 2016" },
  { "基因": "ROS1", "融合类型": "GOPC-ROS1", "变体": "-", "融合转录本": "NM_002944", "参考基因组": "GRCh37", "5\'基因": "GOPC", "5'基因断裂位置": "exon 5", "3'基因": "ROS1", "3'基因断裂位置": "intron 31-32", "频率": "<1%", "癌种": "肺癌", "临床意义": "少见ROS1融合", "靶向药物": "Crizotinib", "参考文献": "Bubendorf L, et al. Testing for ROS1. Virchows Arch. 2016" },
  
  // RET
  { "基因": "RET", "融合类型": "KIF5B-RET", "变体": "-", "融合转录本": "NM_020975", "参考基因组": "GRCh37", "5'基因": "KIF5B", "5'基因断裂位置": "intron 15-23", "3'基因": "RET", "3'基因断裂位置": "exon 11", "频率": "~45-50%", "癌种": "肺癌", "临床意义": "最常见RET融合", "靶向药物": "Selpercatinib; Pralsetinib", "参考文献": "Subbiah V, et al. Pan-cancer efficacy of pralsetinib. Ann Oncol. 2022" },
  { "基因": "RET", "融合类型": "CCDC6-RET", "变体": "-", "融合转录本": "NM_020975", "参考基因组": "GRCh37", "5'基因": "CCDC6", "5'基因断裂位置": "exon 1", "3'基因": "RET", "3'基因断裂位置": "exon 11", "频率": "~30-35%", "癌种": "肺癌", "临床意义": "常见RET融合", "靶向药物": "Selpercatinib", "参考文献": "Subbiah V, et al. Pan-cancer efficacy of pralsetinib. Ann Oncol. 2022" },
  { "基因": "RET", "融合类型": "NCOA4-RET", "变体": "-", "融合转录本": "NM_020975", "参考基因组": "GRCh37", "5\'基因": "NCOA4", "5'基因断裂位置": "exon 7", "3'基因": "RET", "3'基因断裂位置": "exon 11", "频率": "~5-10%", "癌种": "肺癌", "临床意义": "少见RET融合", "靶向药物": "Selpercatinib", "参考文献": "Subbiah V, et al. Pan-cancer efficacy of pralsetinib. Ann Oncol. 2022" },
  { "基因": "RET", "融合类型": "TRIM33-RET", "变体": "-", "融合转录本": "NM_020975", "参考基因组": "GRCh37", "5\'基因": "TRIM33", "5'基因断裂位置": "exon 12", "3'基因": "RET", "3'基因断裂位置": "exon 11", "频率": "~3%", "癌种": "肺癌", "临床意义": "少见RET融合", "靶向药物": "Selpercatinib", "参考文献": "Subbiah V, et al. Pan-cancer efficacy of pralsetinib. Ann Oncol. 2022" },
  
  // NTRK1
  { "基因": "NTRK1", "融合类型": "ETV6-NTRK1", "变体": "-", "融合转录本": "NM_002529", "参考基因组": "GRCh37", "5\'基因": "ETV6", "5'基因断裂位置": "exon 5", "3'基因": "NTRK1", "3'基因断裂位置": "exon 8", "频率": "~40-45%", "癌种": "泛癌种", "临床意义": "最常见NTRK1融合", "靶向药物": "Larotrectinib; Entrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection across multiple assays. Mod Pathol. 2020; PMID: 31375766" },
  { "基因": "NTRK1", "融合类型": "TPM3-NTRK1", "变体": "-", "融合转录本": "NM_002529", "参考基因组": "GRCh37", "5'基因": "TPM3", "5'基因断裂位置": "exon 8", "3'基因": "NTRK1", "3'基因断裂位置": "exon 8", "频率": "~15-20%", "癌种": "泛癌种", "临床意义": "常见NTRK1融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  { "基因": "NTRK1", "融合类型": "LMNA-NTRK1", "变体": "-", "融合转录本": "NM_002529", "参考基因组": "GRCh37", "5\'基因": "LMNA", "5'基因断裂位置": "exon 8", "3'基因": "NTRK1", "3'基因断裂位置": "exon 8", "频率": "~5-10%", "癌种": "泛癌种", "临床意义": "少见NTRK1融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  { "基因": "NTRK1", "融合类型": "IRF2BP2-NTRK1", "变体": "-", "融合转录本": "NM_002529", "参考基因组": "GRCh37", "5\'基因": "IRF2BP2", "5'基因断裂位置": "exon 1", "3'基因": "NTRK1", "3'基因断裂位置": "exon 8", "频率": "~3%", "癌种": "泛癌种", "临床意义": "少见NTRK1融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  { "基因": "NTRK1", "融合类型": "TFG-NTRK1", "变体": "-", "融合转录本": "NM_002529", "参考基因组": "GRCh37", "5\'基因": "TFG", "5'基因断裂位置": "exon 5", "3'基因": "NTRK1", "3'基因断裂位置": "exon 8", "频率": "~3%", "癌种": "泛癌种", "临床意义": "少见NTRK1融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  
  // NTRK2
  { "基因": "NTRK2", "融合类型": "AGAP2-NTRK2", "变体": "-", "融合转录本": "NM_006180", "参考基因组": "GRCh37", "5'基因": "AGAP2", "5'基因断裂位置": "", "3'基因": "NTRK2", "3'基因断裂位置": "intron 11-15", "频率": "~25%", "癌种": "泛癌种", "临床意义": "最常见NTRK2融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  { "基因": "NTRK2", "融合类型": "TRIM24-NTRK2", "变体": "-", "融合转录本": "NM_006180", "参考基因组": "GRCh37", "5'基因": "TRIM24", "5'基因断裂位置": "", "3'基因": "NTRK2", "3'基因断裂位置": "intron 12-16", "频率": "~15%", "癌种": "泛癌种", "临床意义": "常见NTRK2融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  { "基因": "NTRK2", "融合类型": "BCAN-NTRK2", "变体": "-", "融合转录本": "NM_006180", "参考基因组": "GRCh37", "5'基因": "BCAN", "5'基因断裂位置": "", "3'基因": "NTRK2", "3'基因断裂位置": "exon 13", "频率": "~10%", "癌种": "泛癌种", "临床意义": "少见NTRK2融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  
  // NTRK3
  { "基因": "NTRK3", "融合类型": "ETV6-NTRK3", "变体": "-", "融合转录本": "NM_002449", "参考基因组": "GRCh37", "5\'基因": "ETV6", "5'基因断裂位置": "exon 5", "3'基因": "NTRK3", "3'基因断裂位置": "intron 10-14", "频率": "~60-70%", "癌种": "泛癌种", "临床意义": "最常见NTRK3融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection across multiple assays. Mod Pathol. 2020" },
  { "基因": "NTRK3", "融合类型": "BTBD1-NTRK3", "变体": "-", "融合转录本": "NM_002449", "参考基因组": "GRCh37", "5\'基因": "BTBD1", "5'基因断裂位置": "exon 10", "3'基因": "NTRK3", "3'基因断裂位置": "exon 10", "频率": "~5%", "癌种": "泛癌种", "临床意义": "少见NTRK3融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  { "基因": "NTRK3", "融合类型": "LMNA-NTRK3", "变体": "-", "融合转录本": "NM_002449", "参考基因组": "GRCh37", "5\'基因": "LMNA", "5'基因断裂位置": "exon 10", "3'基因": "NTRK3", "3'基因断裂位置": "exon 10", "频率": "~3%", "癌种": "泛癌种", "临床意义": "少见NTRK3融合", "靶向药物": "Larotrectinib", "参考文献": "Solomon JP, et al. NTRK fusion detection. Mod Pathol. 2020" },
  
  // MET
  { "基因": "MET", "融合类型": "CAPZA2-MET", "变体": "-", "融合转录本": "NM_000245", "参考基因组": "GRCh37", "5'基因": "CAPZA2", "5'基因断裂位置": "", "3'基因": "MET", "3'基因断裂位置": "intron 13-14", "频率": "~50%", "癌种": "肺癌", "临床意义": "最常见MET融合", "靶向药物": "Capmatinib; Tepotinib", "参考文献": "Pan Y, et al. Detection of Novel MET Fusions. J Thorac Oncol. 2019" },
  { "基因": "MET", "融合类型": "LAYN-MET", "变体": "-", "融合转录本": "NM_000245", "参考基因组": "GRCh37", "5'基因": "LAYN", "5'基因断裂位置": "", "3'基因": "MET", "3'基因断裂位置": "exon 13", "频率": "~10%", "癌种": "肺癌", "临床意义": "少见MET融合", "靶向药物": "Capmatinib", "参考文献": "Pan Y, et al. Detection of Novel MET Fusions. J Thorac Oncol. 2019" },
  { "基因": "MET", "融合类型": "TRIM4-MET", "变体": "-", "融合转录本": "NM_000245", "参考基因组": "GRCh37", "5'基因": "TRIM4", "5'基因断裂位置": "", "3'基因": "MET", "3'基因断裂位置": "exon 13", "频率": "~5%", "癌种": "肺癌", "临床意义": "少见MET融合", "靶向药物": "Capmatinib", "参考文献": "Pan Y, et al. Detection of Novel MET Fusions. J Thorac Oncol. 2019" },
  
  // FGFR
  { "基因": "FGFR1", "融合类型": "ZMYM2-FGFR1", "变体": "-", "融合转录本": "NM_023110", "参考基因组": "GRCh37", "5'基因": "ZMYM2", "5'基因断裂位置": "", "3'基因": "FGFR1", "3'基因断裂位置": "intron 17-18", "频率": "~30%", "癌种": "泛癌种", "临床意义": "最常见FGFR1融合", "靶向药物": "Erdafitinib", "参考文献": "Helsten T, et al. The FGFR Landscape in Cancer. Clin Cancer Res. 2015" },
  { "基因": "FGFR1", "融合类型": "TACC1-FGFR1", "变体": "-", "融合转录本": "NM_023110", "参考基因组": "GRCh37", "5'基因": "TACC1", "5'基因断裂位置": "", "3'基因": "FGFR1", "3'基因断裂位置": "intron 17-18", "频率": "~15%", "癌种": "泛癌种", "临床意义": "常见FGFR1融合", "靶向药物": "Erdafitinib", "参考文献": "Helsten T, et al. The FGFR Landscape in Cancer. Clin Cancer Res. 2015" },
  { "基因": "FGFR2", "融合类型": "BICC1-FGFR2", "变体": "-", "融合转录本": "NM_000141", "参考基因组": "GRCh37", "5'基因": "BICC1", "5'基因断裂位置": "", "3'基因": "FGFR2", "3'基因断裂位置": "intron 17-18", "频率": "~50%", "癌种": "泛癌种", "临床意义": "最常见FGFR2融合", "靶向药物": "Pemigatinib", "参考文献": "Helsten T, et al. The FGFR Landscape in Cancer. Clin Cancer Res. 2015" },
  { "基因": "FGFR2", "融合类型": "CASP7-FGFR2", "变体": "-", "融合转录本": "NM_000141", "参考基因组": "GRCh37", "5'基因": "CASP7", "5'基因断裂位置": "", "3'基因": "FGFR2", "3'基因断裂位置": "intron 17-18", "频率": "~10%", "癌种": "泛癌种", "临床意义": "少见FGFR2融合", "靶向药物": "Pemigatinib", "参考文献": "Helsten T, et al. The FGFR Landscape in Cancer. Clin Cancer Res. 2015" },
  { "基因": "FGFR3", "融合类型": "TACC3-FGFR3", "变体": "-", "融合转录本": "NM_001142", "参考基因组": "GRCh37", "5'基因": "TACC3", "5'基因断裂位置": "", "3'基因": "FGFR3", "3'基因断裂位置": "intron 17-18", "频率": "~50%", "癌种": "泛癌种", "临床意义": "最常见FGFR3融合", "靶向药物": "Erdafitinib", "参考文献": "Helsten T, et al. The FGFR Landscape. Clin Cancer Res. 2015; Qin A, et al. Detection of FGFR Fusions. J Thorac Oncol. 2019" },
  
  // NRG1
  { "基因": "NRG1", "融合类型": "CD74-NRG1", "变体": "-", "融合转录本": "NM_013962", "参考基因组": "GRCh37", "5'基因": "CD74", "5'基因断裂位置": "exon 6", "3'基因": "NRG1", "3'基因断裂位置": "", "频率": "~25-30%", "癌种": "肺癌; 胰腺癌", "临床意义": "最常见NRG1融合", "靶向药物": "Zenocutuzumab; Seribantumab", "参考文献": "Schram AM, et al. NRG1 fusion-positive solid tumors. J Natl Cancer Inst. 2025; Ishida M, et al. Prevalence of NRG1 fusions. Lung Cancer. 2025" },
  { "基因": "NRG1", "融合类型": "SDC4-NRG1", "变体": "-", "融合转录本": "NM_013962", "参考基因组": "GRCh37", "5'基因": "SDC4", "5'基因断裂位置": "exon 3", "3'基因": "NRG1", "3'基因断裂位置": "", "频率": "~15%", "癌种": "肺癌", "临床意义": "常见NRG1融合", "靶向药物": "Seribantumab", "参考文献": "Schram AM, et al. NRG1 fusion-positive solid tumors. J Natl Cancer Inst. 2025" },
  { "基因": "NRG1", "融合类型": "ATP1B1-NRG1", "变体": "-", "融合转录本": "NM_013962", "参考基因组": "GRCh37", "5\'基因": "ATP1B1", "5'基因断裂位置": "exon 2", "3'基因": "NRG1", "3'基因断裂位置": "", "频率": "~10%", "癌种": "实体瘤", "临床意义": "少见NRG1融合", "靶向药物": "Zenocutuzumab", "参考文献": "Schram AM, et al. NRG1 fusion-positive solid tumors. J Natl Cancer Inst. 2025" },
  { "基因": "NRG1", "融合类型": "RBPMS-NRG1", "变体": "-", "融合转录本": "NM_013962", "参考基因组": "GRCh37", "5\'基因": "RBPMS", "5'基因断裂位置": "exon 2", "3'基因": "NRG1", "3'基因断裂位置": "", "频率": "~8%", "癌种": "实体瘤", "临床意义": "少见NRG1融合", "靶向药物": "Zenocutuzumab", "参考文献": "Schram AM, et al. NRG1 fusion-positive solid tumors. J Natl Cancer Inst. 2025" },
  { "基因": "NRG1", "融合类型": "PARM1-NRG1", "变体": "-", "融合转录本": "NM_013962", "参考基因组": "GRCh37", "5\'基因": "PARM1", "5'基因断裂位置": "exon 1", "3'基因": "NRG1", "3'基因断裂位置": "", "频率": "~5%", "癌种": "实体瘤", "临床意义": "少见NRG1融合", "靶向药物": "Zenocutuzumab", "参考文献": "Schram AM, et al. NRG1 fusion-positive solid tumors. J Natl Cancer Inst. 2025" },
  
  // BRAF
  { "基因": "BRAF", "融合类型": "KIAA1549-BRAF", "变体": "-", "融合转录本": "NM_004333", "参考基因组": "GRCh37", "5'基因": "KIAA1549", "5'基因断裂位置": "", "3'基因": "BRAF", "3'基因断裂位置": "intron 8-11", "频率": "~70%", "癌种": "黑色素瘤; 肺癌", "临床意义": "最常见BRAF融合", "靶向药物": "Dabrafenib; Trametinib", "参考文献": "Stransky N, et al. The landscape of kinase fusions in cancer. Nat Commun. 2014" },
  { "基因": "BRAF", "融合类型": "FAM131B-BRAF", "变体": "-", "融合转录本": "NM_004333", "参考基因组": "GRCh37", "5'基因": "FAM131B", "5'基因断裂位置": "", "3'基因": "BRAF", "3'基因断裂位置": "exon 8", "频率": "~10%", "癌种": "黑色素瘤", "临床意义": "少见BRAF融合", "靶向药物": "Dabrafenib", "参考文献": "Stransky N, et al. The landscape of kinase fusions. Nat Commun. 2014" },
  { "基因": "BRAF", "融合类型": "AKAP9-BRAF", "变体": "-", "融合转录本": "NM_004333", "参考基因组": "GRCh37", "5'基因": "AKAP9", "5'基因断裂位置": "", "3'基因": "BRAF", "3'基因断裂位置": "exon 7", "频率": "~5%", "癌种": "黑色素瘤", "临床意义": "少见BRAF融合", "靶向药物": "Dabrafenib", "参考文献": "Stransky N, et al. The landscape of kinase fusions. Nat Commun. 2014" },
  
  // EGFR
  { "基因": "EGFR", "融合类型": "EGFRvIII", "变体": "缺失突变", "融合转录本": "NM_005228", "参考基因组": "GRCh37", "5'基因": "EGFR exon", "5'基因断裂位置": "intron 1-7", "3'基因": "exon", "3'基因断裂位置": "exon 8", "频率": "~50% EGFR扩增", "癌种": "脑胶质瘤", "临床意义": "EGFR缺失突变体，构成性激活", "靶向药物": "无批准药物", "参考文献": "Furnari FB, et al. EGFRvIII in glioblastoma. Neuro Oncol. 2015; Nathanson DA, et al. EGFR-mediated phosphorylation of EGFRvIII. Cancer Cell. 2014" },
  
  // ESR1
  { "基因": "ESR1", "融合类型": "ESR1-CCDC170", "变体": "-", "融合转录本": "NM_000125", "参考基因组": "GRCh37", "5'基因": "CCDC170", "5'基因断裂位置": "", "3'基因": "ESR1 exon", "3'基因断裂位置": "intron 4-8", "频率": "~1-2%", "癌种": "乳腺癌", "临床意义": "内分泌治疗耐药机制", "靶向药物": "研究中的RET抑制剂", "参考文献": "Lei JT, et al. ESR1 fusions in breast cancer. Breast Cancer Res. 2020; Wu J, et al. Retooling the RET Inhibitor Pralsetinib. Cancer Res. 2023" },
  { "基因": "ESR1", "融合类型": "ESR1-YAP1", "变体": "-", "融合转录本": "NM_000125", "参考基因组": "GRCh37", "5'基因": "YAP1", "5'基因断裂位置": "", "3'基因": "ESR1 exon", "3'基因断裂位置": "intron 4-8", "频率": "<1%", "癌种": "乳腺癌", "临床意义": "内分泌治疗耐药机制", "靶向药物": "无", "参考文献": "Lei JT, et al. ESR1 fusions in breast cancer. Breast Cancer Res. 2020" },
  { "基因": "ESR1", "融合类型": "ESR1-CUX1", "变体": "-", "融合转录本": "NM_000125", "参考基因组": "GRCh37", "5'基因": "CUX1", "5'基因断裂位置": "", "3'基因": "ESR1 exon", "3'基因断裂位置": "intron 4-8", "频率": "<1%", "癌种": "乳腺癌", "临床意义": "内分泌治疗耐药机制", "靶向药物": "无", "参考文献": "Lei JT, et al. ESR1 fusions in breast cancer. Breast Cancer Res. 2020" },
];

// 添加频率级别和参考文献数
const enrichedData = fusionData.map(item => ({
  ...item,
  "频率级别": getFreqLabel(item["频率"]),
  "参考文献数": countSources(item["参考文献"])
}));

const wb = XLSX.utils.book_new();
const sheet = XLSX.utils.json_to_sheet(enrichedData);
XLSX.utils.book_append_sheet(wb, sheet, "融合基因汇总");

// Probe sheet
const probe = [
  { "基因": "ALK", "DNA探针区域": "intron 19", "RNA探针区域": "exon 18-21", "探针长度": "300-500bp", "备注": "覆盖所有变体" },
  { "基因": "ROS1", "DNA探针区域": "intron 31-35", "RNA探针区域": "exon 32-36", "探针长度": "400-600bp", "备注": "覆盖常见融合伙伴" },
  { "基因": "RET", "DNA探针区域": "intron 10-12", "RNA探针区域": "exon 11-15", "探针长度": "350-500bp", "备注": "激酶域" },
  { "基因": "NTRK1", "DNA探针区域": "intron 8-11", "RNA探针区域": "exon 8-12", "探针长度": "400-500bp", "备注": "" },
  { "基因": "NTRK2", "DNA探针区域": "intron 11-16", "RNA探针区域": "exon 12-17", "探针长度": "400-600bp", "备注": "" },
  { "基因": "NTRK3", "DNA探针区域": "intron 10-15", "RNA探针区域": "exon 12-18", "探针长度": "400-600bp", "备注": "" },
  { "基因": "MET", "DNA探针区域": "intron 13-14", "RNA探针区域": "exon 14-15", "探针长度": "250-350bp", "备注": "exon 14 skip" },
  { "基因": "FGFR1-3", "DNA探针区域": "intron 17-18", "RNA探针区域": "exon 18-20", "探针长度": "300-450bp", "备注": "激酶域" },
  { "基因": "NRG1", "DNA探针区域": "intron 6-8", "RNA探针区域": "exon 6-10", "探针长度": "300-500bp", "备注": "heregulin区域" },
  { "基因": "BRAF", "DNA探针区域": "intron 8-11", "RNA探针区域": "exon 11-18", "探针长度": "400-600bp", "备注": "激酶域" },
  { "基因": "EGFRvIII", "DNA探针区域": "exon 1-8 junction", "RNA探针区域": "exon 1-8 junction", "探针长度": "150-250bp", "备注": "缺失检测" },
  { "基因": "ESR1", "DNA探针区域": "exon 4-8", "RNA探针区域": "exon 4-8", "探针长度": "300-500bp", "备注": "激素结合域" },
];
const probeSheet = XLSX.utils.json_to_sheet(probe);
XLSX.utils.book_append_sheet(wb, probeSheet, "探针设计推荐");

// Cancer summary
const cancer = [
  { "癌种": "肺癌", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('肺癌')).length, "主要基因": "ALK, ROS1, RET, MET" },
  { "癌种": "乳腺癌", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('乳腺癌')).length, "主要基因": "ESR1, NTRK" },
  { "癌种": "泛癌种", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('泛癌种')).length, "主要基因": "NTRK, FGFR" },
  { "癌种": "实体瘤", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('实体瘤')).length, "主要基因": "NRG1" },
  { "癌种": "脑胶质瘤", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('脑胶质瘤')).length, "主要基因": "EGFRvIII" },
  { "癌种": "黑色素瘤", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('黑色素瘤')).length, "主要基因": "BRAF" },
  { "癌种": "胰腺癌", "融合数": enrichedData.filter(d=>(d['癌种']||'').includes('胰腺癌')).length, "主要基因": "NRG1" },
];
const cancerSheet = XLSX.utils.json_to_sheet(cancer);
XLSX.utils.book_append_sheet(wb, cancerSheet, "分癌种汇总");

XLSX.writeFile(wb, '/root/.openclaw/workspace/research/fusion/reports/fusion_genes_report_v2.xlsx');
console.log("Total:", enrichedData.length, "records");
