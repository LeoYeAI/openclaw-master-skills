---
name: paper-summarize-pdf-to-feishu
version: 1.0.1
author: yy-fan
license: MIT
homepage: https://github.com/openclaw/openclaw
description: |
  总结论文 PDF 为飞书文档（含图表）。当用户发送 PDF 文件并要求总结、阅读、提取内容，
  或要求将 PDF 内容写入飞书文档时激活。支持学术论文、技术报告、一般 PDF 文档。
  自动检测扫描版 PDF 并回退 OCR，支持提取并上传论文图片到飞书文档。
  含多模型自审核机制：生成 → 配图 → 审核 → 人工确认 → 完善。
  **支持去重系统**：自动识别重复 PDF、同文章不同版本、补充材料，智能合并处理。
  触发场景：发送 PDF 附件、"总结这个 PDF"、"帮我读一下这个论文"、"把 PDF 写成飞书文档"、
  "论文总结"、"PDF 摘要"、"阅读 PDF 并输出到飞书"。
metadata:
  openclaw:
    requires:
      bins:
        - pdftotext
        - pdfinfo
        - pdfimages
        - pdftoppm
        - tesseract
        - jq
      env:
        - OPENCLAW_WORKSPACE
      config:
        - ~/.openclaw/openclaw.json
    primaryEnv: OPENCLAW_WORKSPACE
---

# paper-summarize-pdf-to-feishu

将 PDF 文件完整阅读后生成结构化总结，写入飞书文档，并将论文 Figure 精确插入对应章节。
**含多模型审核 + 配置确认 + 人工确认机制**，确保最终输出质量。

## 前置依赖

### 系统工具
| 工具 | 用途 | 版本要求 |
|------|------|----------|
| `pdftotext` | PDF 文本提取 | poppler-utils ≥ 0.86 |
| `pdfinfo` | PDF 元信息查看 | poppler-utils ≥ 0.86 |
| `pdfimages` | PDF 图片提取 | poppler-utils ≥ 0.86 |
| `pdftoppm` | PDF 转图片（截图/OCR） | poppler-utils ≥ 0.86 |
| `tesseract` | OCR 识别 | ≥ 4.1 |
| `jq` | JSON 处理 | ≥ 1.6 |

### OpenClaw 插件
| 插件 | 用途 | 版本 |
|------|------|------|
| `feishu` | 飞书文档操作 | 2026.3.13¹ |
| `feishu_doc` | 文档读写/图片上传 | 内置 |

> ¹ OpenClaw 官方插件与主程序同步发布，版本号一致

检查依赖：
```bash
# 检查系统工具
which pdftotext pdfinfo pdfimages pdftoppm tesseract jq || \
  sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim jq

# 检查版本
pdftotext -v  # 应显示 poppler-utils 版本
tesseract --version  # 应显示 tesseract 版本
jq --version
```

## 完整工作流程（六阶段）

### 阶段零：去重检查

**目标**：避免重复处理，智能识别补充材料并合并

#### 0.1 提取元数据

```bash
scripts/extract_metadata.sh <input.pdf> "$TEMP_DIR/metadata.json"
```

提取内容：
- DOI（优先，用于唯一标识）
- 标题、作者、发表年份
- PDF 文件哈希（用于精确去重）
- 生成 `paper_id`：`<DOI>` 或 `hash_<指纹>`

#### 0.2 检查是否已处理

```bash
scripts/check_duplicate.sh "$TEMP_DIR/metadata.json" "$PAPERS_DIR"
```

**判断逻辑**：
```
收到 PDF → 计算 paper_id → 查询 papers/ 目录
  ├─ 不存在 → 新论文，创建文件夹，进入阶段一
  ├─ 存在 + PDF 哈希相同 → 完全重复，跳过并告知用户
  ├─ 存在 + DOI 相同但哈希不同 → 同文章不同版本，询问是否更新
  └─ 存在 + 判断为补充材料 → 合并到 supplements/，追加到飞书文档
```

#### 0.3 补充材料识别规则

文件名包含以下关键词视为补充材料：
- `supplement`, `suppl`, `_si_`, `supporting`, `appendix`

DOI 包含 `.supp` 或 `supplementary` 也视为补充材料。

#### 0.4 文件夹结构

```
papers/
├── 10.xxxx-xxxxxx/                      # DOI 作为 ID（优先）
│   ├── metadata.json                    # 元数据（DOI、标题、作者等）
│   ├── paper.pdf                        # 主文章
│   ├── paper.txt                        # 提取的全文文本
│   ├── feishu_doc_token.txt             # 飞书文档 token
│   ├── summary.md                       # 总结文档
│   ├── versions.json                    # 版本历史（如有更新）
│   ├── images/                          # 提取的 Figure/Table
│   └── supplements/                     # 补充材料
│       ├── 20260326_120000_suppl1.pdf
│       ├── 20260326_120000_suppl1_meta.json
│       └── 20260326_120000_suppl1.txt
│
└── hash_xxxxxxxxxxxx/                   # 无 DOI 时用指纹哈希
    └── ...
```

---

### 阶段一：生成

#### 1. 创建论文专属文件夹

```bash
PAPER_DIR=<OpenClaw 工作目录>/papers/<paper_id>
mkdir -p "$PAPER_DIR"/{images,supplements}
cp <input.pdf> "$PAPER_DIR/paper.pdf"
cp "$TEMP_DIR/metadata.json" "$PAPER_DIR/metadata.json"
```

#### 2. 智能提取 PDF 文本

```bash
scripts/extract_pdf_text.sh "$PAPER_DIR/paper.pdf" "$PAPER_DIR/paper.txt"
```

策略：pdftotext → 检测字符密度（≥50 字符/页正常，<50 走 OCR 回退）

#### 3. 分段完整阅读

用 `read` 工具每次 500 行，直到读完全文。

**关键要求：必须读完全文再总结，不要只读摘要或部分内容。**

#### 4. 生成结构化总结

**学术论文**结构：

```markdown
# 总结：<论文标题>

> 原文标题 / 发表日期 / 机构

---

## 📊 论文统计
- 总字数 / 总页数
- Figure（正文）：X 张
- Figure（附录）：X 张
- Table（正文）：X 张
- Table（附录）：X 张

---

## 一、研究背景与动机
## 二、研究设计
## 三、方法/系统架构
## 四、核心结果
### 4.1 结果 A
### 4.2 结果 B
## 五、讨论与局限性
## 六、结论
## 七、关键数据速览
```

#### 5. 创建飞书文档并写入

```json
{
  "action": "create",
  "title": "总结：<文档标题>",
  "owner_open_id": "<用户的 open_id>"
}
```

```json
{
  "action": "write",
  "doc_token": "<doc_token>",
  "content": "<Markdown 格式总结>"
}
```

保存 `feishu_doc_token.txt` 以便后续补充材料合并时使用。

---

### 阶段一（补充）：补充材料合并

**如果阶段零判断为补充材料**，执行以下流程：

```bash
# 读取已有的飞书文档 token
DOC_TOKEN=$(cat "$PAPER_DIR/feishu_doc_token.txt")

# 步骤 1：合并补充材料（文件层面）
scripts/merge_supplement.sh "$PAPER_DIR" "<supplement.pdf>" "$DOC_TOKEN"

# 步骤 2：追加到飞书文档（调用 feishu_doc 工具）
feishu_doc action=append doc_token="$DOC_TOKEN" content="
## 📎 补充材料：$(basename $SUPPLEMENT_PDF)
- 添加时间：$(date +%Y-%m-%d %H:%M)
- 摘要：$(cat $SUPP_TXT | head -20)
"
```

**合并逻辑**：
1. `merge_supplement.sh` 负责文件层面操作：
   - 复制补充材料到 `supplements/` 目录（带时间戳命名）
   - 提取补充材料的元数据（`_meta.json`）
   - 提取简要摘要（`.txt`）
2. **Agent 调用 `feishu_doc` 工具**追加内容到飞书文档
3. 更新 `versions.json` 记录（待实现）

**注意**：`merge_supplement.sh` 不直接操作飞书文档，仅准备文件和数据。飞书文档更新由上层 Agent 调用 `feishu_doc` 工具完成。

---

### 阶段二：配图（Figure/Table 提取与验证）

#### 6. 定位 Figure/Table 页码

```bash
scripts/locate_figures.sh "$PAPER_DIR/paper.pdf" "$PAPER_DIR/paper.txt" "$PAPER_DIR/images"
```

脚本会：
1. 用 `grep` 找到所有 Figure/Table 标题行
2. 根据行号估算页码
3. 对估算页码 ±2 页范围截图（候选页面）

**⚠️ 注意：行号→页码是粗略估算，必须经过审核验证！**

#### 7. 验证截图（关键步骤）

对每个 Figure 的候选截图逐张审核：

```
for each Figure:
  1. read 候选截图
  2. 判断：图中是否包含目标 Figure？
     - ✅ 包含 → 记录正确页码，复制为 Figure_XX_full.png
     - ❌ 不包含 → 检查相邻页面
  3. 如果所有候选页面都不对 → 扩大搜索范围
```

**验证标准**：
- ✅ 截图中必须可见 "Figure X" 或 "Table X" 标题文字
- ✅ 截图中必须包含图表内容（非纯文字页面）
- ✅ 复合图（多子图拼合）应作为完整页面保留

**如果截图是纯文字**：
1. ❌ 不要使用该截图
2. 检查相邻页面（±3 页范围）
3. 检查文本提取是否有误（Figure 标题可能在图片中无法提取）
4. 手动浏览 PDF 定位：`pdftoppm -f X -l X paper.pdf output`

#### 8. 插入图片到对应章节

**精确定位**：

```json
{
  "action": "upload_image",
  "doc_token": "<doc_token>",
  "file_path": "<图片路径>",
  "parent_block_id": "<doc_token>",
  "index": <目标索引>
}
```

**技巧**：从文档末尾往前插（倒序），避免索引偏移。

---

### 阶段三：审核（多模型审核）

**核心思想**：直接使用 fallback 模型审核 → 告知用户 → 主模型审查 → 人工确认

#### 9. 读取模型配置并启动审核

```bash
# 读取 OpenClaw 配置文件
CONFIG_FILE=<OpenClaw 配置文件路径>

# 提取 fallback 模型列表（取第一个作为审核模型）
FALLBACK_MODEL=$(jq -r '.agents.defaults.model.fallbacks[0]' "$CONFIG_FILE")

# 确认配置并启动审核
if [ -z "$FALLBACK_MODEL" ] || [ "$FALLBACK_MODEL" = "null" ]; then
  echo "⚠️ 未配置 fallback 模型，将使用主模型自审"
  # 降级方案：使用主模型重新阅读 PDF + 文档进行自审
  sessions_spawn task="请审核这份飞书文档与原始 PDF 的一致性..."
else
  echo "✅ 使用 fallback 模型进行审核：$FALLBACK_MODEL"
  # 告知用户审核模型
  echo "📋 已启动审核流程，使用模型：$FALLBACK_MODEL"
  sessions_spawn task="请审核这份飞书文档与原始 PDF 的一致性..." \
    model="$FALLBACK_MODEL"
fi
```

**注意**：
- 优先使用配置中的 fallback 模型
- **不需要用户确认**，直接启动审核
- 审核前告知用户使用的模型即可

**审核内容**：
1. 文档章节完整性
2. Figure 是否正确显示（非纯文字）
3. 关键数据准确性（百分比、p 值、置信区间）
4. 格式和错别字检查

#### 10. 生成审核报告

审核报告包含：
- 字数对比（原始 PDF vs 飞书文档）
- 章节完整性检查
- Figure/Table 清单核对
- 关键数据提取（百分比、p 值、样本量等）
- **修改建议清单**（逐条列出）

#### 11. 主模型审查审核意见

**主模型审查流程**：
```
1. 阅读审核报告
2. 逐条审查修改建议：
   - ✅ 合理建议 → 标记为"采纳"
   - ❌ 错误建议 → 标记为"拒绝"并说明原因
   - ⚠️ 需确认 → 标记为"待用户确认"
3. 生成最终修改方案
```

**注意**：
- 不照单全收审核意见
- 主模型对最终质量负责
- 有争议的建议提交用户确认

---

### 阶段四：人工确认

#### 12. 提交用户确认

向用户发送：
- 飞书文档链接（初版）
- 审核报告摘要
- 修改建议清单（标注采纳/拒绝/待确认）
- **确认提示**：

```
📋 文档已完成初稿和审核

✅ 已完成的修改：X 处
⚠️ 待您确认的修改：Y 处
❌ 拒绝的修改：Z 处（原因：...）

请查看文档后回复：
- "确认" → 应用所有修改，输出最终版
- "修改 XXX" → 指定需要调整的内容
- "跳过" → 直接输出当前版本
```

#### 13. 等待用户确认

**用户回复处理**：
- ✅ **"确认" / "没问题" / "可以"** → 进入阶段五（完善）
- ✏️ **"修改 XXX"** → 根据用户要求修改后重新提交确认
- ⚠️ **"跳过" / "直接输出"** → 跳过修改，进入阶段五

---

### 阶段五：完善

#### 14. 应用最终修改

根据用户确认的修改方案：
- 补充遗漏的章节
- 修正错误的数据
- 添加缺失的 Figure/Table
- 优化格式和表述

**格式标准化检查清单**（必须逐项核对）：
- [ ] 文档开头：引用块包含标题、期刊、DOI、作者、接受日期
- [ ] 论文统计：使用表格格式，包含所有必填指标
- [ ] 章节标题：使用统一的标题层级（H1 → H2 → H3）
- [ ] 关键数据：加粗重要数值，补充置信区间
- [ ] 表格：所有数据表格使用统一样式
- [ ] 图片：Figure 插入到对应章节后
- [ ] 相关链接：包含原文、补充材料、数据平台、预注册链接
- [ ] **署名信息**：文档末尾必须包含撰写人和审核人（见步骤 17）

#### 15. 最终检查

- 通读飞书文档，检查格式、错别字
- 确认所有链接可点击
- 确认图片显示正常
- **核对格式检查清单**（见步骤 15）

#### 16. 添加署名信息（强制）

**在文档末尾添加署名块**（必须包含）：

```markdown
---

## 📝 文档信息

| 项目 | 信息 |
|------|------|
| 撰写人 | <Agent 名字>（<主模型名称>） |
| 审核模型 | <审核模型名称> |
| 审核状态 | ✅ 已通过 |
| 生成时间 | YYYY-MM-DD HH:MM |
| 文档版本 | v1.0 |

---

*本总结由 AI 助手自动生成，如有问题请指出。*
```

**示例**：
```
撰写人：Lux（qwen3.5-plus）
审核模型：kimi-k2.5
审核状态：✅ 已通过
生成时间：2026-03-26 17:13
文档版本：v1.0
```

**注意**：
- 撰写人 = 当前 Agent 的名字（从 IDENTITY.md 或会话上下文获取）
- 主模型 = 生成文档使用的模型（如 `qwencode/qwen3.5-plus`）
- 审核模型 = fallback 模型（如 `qwencode/kimi-k2.5`）
- 如果跳过审核，标注"审核状态：⏭️ 已跳过"

#### 17. 返回最终文档

向用户发送：
- 飞书文档链接（最终版）
- 修改摘要（可选）
- 使用说明："如有问题请随时指出，我可以进一步修改"

---

## 脚本说明

### 去重系统

| 脚本 | 功能 | 输出 |
|------|------|------|
| `extract_metadata.sh` | 提取 PDF 元数据（DOI、标题、作者、页数），生成 paper_id | JSON：`paper_id`, `doi`, `title`, `pdf_hash` |
| `check_duplicate.sh` | 检查是否已处理，判断重复/版本更新/补充材料 | JSON：`action`, `file_type`, `message` |
| `merge_supplement.sh` | 复制补充材料到 `supplements/`，提取元数据和摘要 | JSON：文件路径 + 摘要，**不操作飞书文档** |

### 原有脚本

| 脚本 | 功能 |
|------|------|
| `extract_pdf_text.sh` | 智能文本提取（pdftotext + OCR 回退） |
| `extract_pdf_images.sh` | 提取嵌入图片 + 生成清单 |
| `locate_figures.sh` | 定位 Figure/Table 页码 + 截取候选页面 |
| `review_document.sh` | 生成审核报告（对比 PDF 与飞书文档） |

## 注意事项

### 去重系统
- **DOI 优先**：有 DOI 的论文用 DOI 作为唯一标识（`/` 替换为 `_`），无 DOI 时用指纹哈希
- **版本管理**：同 DOI 不同版本会提示用户确认是否更新，不会自动覆盖
- **补充材料识别**：文件名含 `supplement/suppl/_si_/supporting/appendix/moesm/_esm` 自动识别
  - 支持 Nature 系列期刊标准命名（MOESM = Materials Online Electronic Supplementary Material）
- **精确去重**：PDF 哈希完全相同则跳过，避免重复处理
- **文件夹命名**：`papers/<paper_id>/`，其中 `paper_id` 为 DOI（`/`→`_`）或 `hash_<指纹>`

### 补充材料合并
- **文件层面**：`merge_supplement.sh` 复制到 `supplements/` + 提取元数据和摘要
- **飞书文档**：Agent 调用 `feishu_doc action=append` 追加"补充材料"章节
- **命名规则**：`YYYYMMDD_HHMMSS_<原文件名>`（带时间戳避免冲突）

### 配图验证
- **页码估算不可靠**：每张截图都要 `read` 验证
- **优先页面截图**：`pdftoppm` 整页截图 > `pdfimages` 嵌入图片

### 多模型审核
- **配置确认**：执行前读取 OpenClaw 配置文件中的 `agents.defaults.model.fallbacks` 配置
- **Fallback 模型审核**：使用配置中的第一个 fallback 模型进行审核（避免自己审核自己）
- **降级方案**：如未配置 fallback 模型，使用主模型重新阅读 PDF + 文档进行自审
- **主模型审查**：逐条审查审核建议，不照单全收
- **人工确认**：有争议的建议提交用户确认

### 流程自动化
- **六阶段流程**：去重检查 → 生成 → 配图 → 审核 → 人工确认 → 完善
- **补充材料自动合并**：识别后追加到主文档的"补充材料"章节
- **审核告知**：审核前告知用户使用的 fallback 模型（无需确认）
- **人工确认环节**：审核完成后需用户确认再输出最终版
- **格式标准化**：使用检查清单确保每次输出格式一致
- **强制署名**：文档末尾必须包含撰写人、审核模型、生成时间

### 输出格式稳定性

**为确保每次生成的文档格式一致，必须遵守**：

1. **文档结构模板化**：
   - 严格按照"一、二、三..."章节编号
   - 每个章节使用 H2 标题（`##`）
   - 子章节使用 H3 标题（`###`）

2. **表格样式统一**：
   - 所有统计数据使用 Markdown 表格
   - 表格第一行为表头
   - 重要数据加粗（如 `**55.0%**`）

3. **强制署名**：
   - 文档末尾必须包含署名块（见步骤 17）
   - 使用表格格式展示撰写人、审核模型等信息
   - 不得省略或修改署名格式

4. **质量检查**：
   - 使用格式检查清单（步骤 15）逐项核对

### 已知限制（待实现）
- [ ] `.index.json` 索引文件维护
- [ ] `versions.json` 版本历史记录
- [ ] 同 DOI 不同版本的用户确认交互

### 飞书文档图片插入方法

**正确用法**（已验证）：
```bash
# 方法 1：上传到文档根目录，用 index 指定位置（0-based）
feishu_doc action=upload_image \
  doc_token="<doc_token>" \
  file_path="<image_path>" \
  parent_block_id="<文档根 block ID>" \
  index=20

# 方法 2：上传到指定章节下（parent_block_id 为章节 block ID）
feishu_doc action=upload_image \
  doc_token="<doc_token>" \
  file_path="<image_path>" \
  parent_block_id="<章节 block ID>"
```

**注意事项**：
- `parent_block_id` 为文档根 ID 时，`index` 表示在 children 数组中的位置
- `parent_block_id` 为章节 ID 时，图片会追加到该章节下
- `insert` + `after_block_id` 方式会报错，不推荐使用

---

## 注意事项

### Token 消耗提醒

请注意 Token 消耗，建议使用包月套餐。

### 安全说明

**环境变量**：
- `OPENCLAW_WORKSPACE`：OpenClaw 工作目录（用于存储论文和临时文件）

**配置文件读取**：
- 技能会读取 `~/.openclaw/openclaw.json` 获取 fallback 模型配置（用于多模型审核）
- 如未配置 fallback 模型，将使用主模型自审

**本地存储**：
- 论文文本：`<OPENCLAW_WORKSPACE>/papers/<paper_id>/paper.txt`
- 飞书文档 Token：`<OPENCLAW_WORKSPACE>/papers/<paper_id>/feishu_doc_token.txt`
- 提取的图片：`<OPENCLAW_WORKSPACE>/papers/<paper_id>/images/`

**系统依赖**：
- 脚本可能运行 `sudo apt-get install` 安装 poppler-utils、tesseract-ocr 等工具（用于 PDF 处理和 OCR）
- 需要 root 权限，请确保在受信任的环境中使用

**权限说明**：
- 技能需要访问 OpenClaw 配置文件（读取 fallback 模型）
- 技能会调用 `sessions_spawn` 启动子代理审核（使用 fallback 模型）
- 技能会创建和修改本地文件（论文存储、Token 保存）

---

**版本**: 1.0.0  
**许可证**: MIT  
**作者**: yy-fan  
**最后更新**: 2026-03-26
