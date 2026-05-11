# 学术数据库访问指南

本指南介绍如何通过浏览器自动化访问各大学术数据库。

## 支持的数据库

| 数据库 | 访问方式 | 是否需要登录 |
|--------|----------|-------------|
| CNKI | 浏览器访问 | 否（检索免费） |
| Web of Science | 浏览器访问 | 部分需要机构访问 |
| ScienceDirect | 浏览器访问 | 否（检索免费） |
| PubMed | 浏览器访问 | 否 |
| Google Scholar | 网页搜索 | 否 |

## CNKI 中国知网

### 访问地址
- 高级检索：`https://kns.cnki.net/kns8/AdvSearch`

### 检索字段代码
| 代码 | 含义 | 示例 |
|------|------|------|
| SU | 主题 | SU='深度学习' |
| TI | 篇名 | TI='图像识别' |
| KY | 关键词 | KY='神经网络' |
| TKA | 篇关摘 | TKA='医学图像' |
| AU | 作者 | AU='张三' |
| JN | 期刊 | JN='计算机学报' |

### 布尔逻辑
- `*` = AND（并且）
- `+` = OR（或者）
- `-` = NOT（排除）

### 示例检索式
```
SU=('深度学习'+'神经网络')*('医学图像'+'医学影像')*('诊断'+'检测')
```

### 来源筛选
- `CSSCI`: 中文社会科学引文索引
- `hx`: 北大核心期刊
- `CSCD`: 中国科学引文数据库

## Web of Science

### 访问地址
- 高级检索：`https://www.webofscience.com/wos/woscc/advanced-search`

### 常用字段
| 字段 | 说明 | 示例 |
|------|------|------|
| TS | Topic（主题） | TS=("deep learning") |
| TI | Title（标题） | TI=("medical imaging") |
| AB | Abstract（摘要） | AB=(diagnosis) |
| AU | Author（作者） | AU=(Smith J) |
| SO | Source（期刊） | SO=(Nature) |

### 示例检索式
```
TS=(("deep learning" OR "neural network") AND ("medical imaging" OR "radiology") AND ("diagnosis" OR "detection"))
```

## ScienceDirect

### 访问地址
- 检索页面：`https://www.sciencedirect.com/search`

### 检索语法
- 支持自然语言和布尔逻辑
- 使用 AND, OR, NOT 连接词
- 使用引号进行精确匹配

### 示例
```
deep learning AND medical imaging AND diagnosis
"convolutional neural network" AND "computed tomography"
```

## PubMed

### 访问地址
- 高级检索：`https://pubmed.ncbi.nlm.nih.gov/advanced/`

### 常用字段
| 字段标签 | 含义 | 示例 |
|---------|------|------|
| [Title/Abstract] | 标题/摘要 | ("deep learning"[Title/Abstract]) |
| [MeSH Terms] | MeSH主题词 | ("Diagnosis"[MeSH]) |
| [Author] | 作者 | (Smith J[Author]) |
| [Journal] | 期刊 | (Nature[Journal]) |
| [Year] | 年份 | (2023:2024[Year]) |

### 示例检索式
```
("deep learning"[Title/Abstract] OR "neural network"[Title/Abstract]) AND ("medical imaging"[Title/Abstract] OR "radiology"[MeSH Terms]) AND ("diagnosis"[Title/Abstract] OR "diagnostic imaging"[MeSH Terms])
```

## 检索策略建议

### 1. 分步骤构建
1. 先搜索核心概念
2. 逐步添加限定条件
3. 根据结果调整检索式

### 2. 中英文并行
- 中文数据库使用中文关键词
- 英文数据库使用英文关键词
- 注意同义词和近义词扩展

### 3. 结果筛选
- 时间范围：近5-10年优先
- 文献类型：期刊论文、会议论文
- 来源质量：核心期刊优先
