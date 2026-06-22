---
name: feishu-literature-manager
description: Automated literature retrieval and Feishu Bitable management. Use when user requests to create a literature database, search PubMed for specific topics, or manage research papers in Feishu tables. Triggers on phrases like "create a literature table", "search papers and add to Feishu", "build a research database", "补充文献", "添加文献到表格", or "检索文献并建立表格". Supports complete workflow from topic definition to populated Feishu table with all required fields including Chinese translations, impact factors, and reference formatting. Also supports supplementing existing databases with new papers.
---

# Feishu Literature Manager

## Overview

This skill automates the complete workflow of creating a literature database in Feishu Bitable, from PubMed search to fully populated table with all required metadata including Chinese translations, impact factors, and formatted references.

**Two Main Workflows:**
1. **Create New Database**: Create a new Feishu Bitable from scratch
2. **Supplement Existing Database**: Add new papers to an existing table (avoiding duplicates)

## Workflow Decision Tree

### Workflow A: Create New Database
```
User provides: topic + number of papers
           ↓
1. Create Feishu Bitable
           ↓
2. Create all 17 required fields
           ↓
3. Search PubMed for papers
           ↓
4. Parse and validate results
           ↓
5. Extract complete metadata
           ↓
6. Translate titles and abstracts
           ↓
7. Add papers to table (PARALLEL CALLS)
           ↓
8. Set table permissions (full_access)
           ↓
9. Report completion
```

### Workflow B: Supplement Existing Database ⭐ NEW
```
User provides: research topic + specific focus + table URL + number of papers
           ↓
1. Parse table URL to get app_token and table_id
           ↓
2. Get existing records to extract current PMIDs
           ↓
3. Search PubMed with focused keywords
           ↓
4. Filter out existing PMIDs (deduplication)
           ↓
5. Score and rank papers by relevance
           ↓
6. Select top N papers
           ↓
7. Fetch XML data for selected papers
           ↓
8. Parse metadata and translate
           ↓
9. Add papers to table (PARALLEL CALLS - 5-10 at a time)
           ↓
10. Report completion with summary
```

## Batch Processing for Large Tasks

**IMPORTANT: When retrieving more than 5 papers, process in batches!**

**Why Batch Processing is Necessary:**
1. **Token limitations** - Large numbers of papers require extensive translation work
2. **Quality assurance** - Each batch ensures complete field information before proceeding
3. **Better user experience** - Users receive regular progress updates
4. **Error recovery** - Easier to resume if interrupted

**Batch Processing Workflow:**

```
User requests: topic + N papers (N > 5)
           ↓
Calculate batches: ceil(N / 5)
           ↓
For each batch (5 papers):
  1. Fetch PMIDs for this batch
  2. Retrieve XML data
  3. Parse metadata
  4. Translate titles and abstracts
  5. Add all 5 papers to table with COMPLETE fields
  6. Report batch completion
           ↓
Continue to next batch
           ↓
All batches complete → Report final status
```

**Example: User requests 10 papers**
```
Batch 1 (Papers 1-5):
  - Fetch PMIDs 1-5
  - Get XML data
  - Parse and translate
  - Add 5 papers with complete fields (including 摘要)
  - Report: "第一批完成，已添加5篇文献"

Batch 2 (Papers 6-10):
  - Fetch PMIDs 6-10
  - Get XML data
  - Parse and translate
  - Add 5 papers with complete fields (including 摘要)
  - Report: "第二批完成，已添加5篇文献"

Final Report: "任务全部完成！共添加10篇文献"
```

**Critical Rules:**
1. **Never start a new batch until current batch is COMPLETE**
   - COMPLETE means ALL 17 fields filled, including 摘要（英文）and 摘要（中文）
   - Report completion before starting next batch

2. **Progress Reporting:**
   - After each batch: "第X批完成，已添加Y篇文献，剩余Z篇"
   - Keep user informed of progress

3. **Token Management:**
   - Monitor token usage
   - If running low, inform user and continue in next conversation
   - Save state (PMIDs retrieved, current batch) for resumption

4. **Quality over Speed:**
   - Better to complete fewer papers with full information
   - Than many papers with incomplete fields

## ⭐ PARALLEL API CALLS - BEST PRACTICE

**CRITICAL: Always use parallel API calls when adding multiple papers!**

### Why Parallel Calls?

Sequential API calls are SLOW. Each call waits for response before next call.
Parallel calls submit multiple requests simultaneously, dramatically improving efficiency.

### How to Make Parallel Calls

In tool calls, submit MULTIPLE `feishu_bitable_create_record` calls in the SAME function_calls block:

```
// CORRECT: Parallel calls (5-10 papers at once)
<function_calls>
<invoke name="feishu_bitable_create_record">
<parameter name="app_token">xxx</parameter>
<parameter name="table_id">xxx</parameter>
<parameter name="fields">{paper 1 data}</parameter>
</invoke>
<invoke name="feishu_bitable_create_record">
<parameter name="app_token">xxx</parameter>
<parameter name="table_id">xxx</parameter>
<parameter name="fields">{paper 2 data}</parameter>
</invoke>
<invoke name="feishu_bitable_create_record">
<parameter name="app_token">xxx</parameter>
<parameter name="table_id">xxx</parameter>
<parameter name="fields">{paper 3 data}</parameter>
</invoke>
... (up to 10 calls at once)
</function_calls>

// WRONG: Sequential calls (SLOW!)
<function_calls>
<invoke name="feishu_bitable_create_record">...</invoke>
</function_calls>
// Wait for response...
<function_calls>
<invoke name="feishu_bitable_create_record">...</invoke>
</function_calls>
// Wait for response...
```

### Recommended Batch Size

- **5-10 papers per parallel call** - Optimal balance of speed and reliability
- **Maximum 10 papers** - Avoid overwhelming the API

### Example: Adding 10 Papers Efficiently

```python
# Step 1: Prepare all paper data
papers_data = [prepare_paper_data(p) for p in papers[:10]]

# Step 2: Make parallel calls (submit all at once)
# All 10 feishu_bitable_create_record calls in same function_calls block
results = parallel_add_papers(papers_data)

# Step 3: Report results
print(f"Successfully added {len(results)} papers in one batch!")
```

## ⭐ SUPPLEMENTING EXISTING DATABASE - Step by Step

### Overview

When user provides:
- **Research topic**: e.g., "胃神经内分泌肿瘤"
- **Specific focus**: e.g., "药物临床研究", "手术治疗", "诊断方法"
- **Table URL**: Feishu Bitable link
- **Number of papers**: How many to add

### Step 1: Parse Table URL and Get Existing PMIDs

```python
# Extract app_token from URL
# URL format: https://xxx.feishu.cn/base/APP_TOKEN?table=TABLE_ID
# Or: https://xxx.feishu.cn/wiki/xxx?table=TABLE_ID

# Get existing records
records = feishu_bitable_list_records(
    app_token=app_token,
    table_id=table_id,
    page_size=500  # Get all records
)

# Extract existing PMIDs
existing_pmids = set()
for record in records['records']:
    pmid = record['fields'].get('PMID')
    if pmid:
        existing_pmids.add(pmid)

print(f"Existing records: {len(records['records'])}, Unique PMIDs: {len(existing_pmids)}")
```

### Step 2: Build Focused Search Query

```python
# Combine research topic with specific focus
# Example: "胃神经内分泌肿瘤" + "药物临床研究"

# Search terms for different focuses:
FOCUS_KEYWORDS = {
    "药物临床研究": [
        "chemotherapy", "targeted therapy", "PRRT", "somatostatin analog",
        "everolimus", "sunitinib", "octreotide", "lanreotide", "immunotherapy",
        "PD-1", "PD-L1", "temozolomide", "capecitabine", "177Lu", "Lutetium",
        "clinical trial", "phase", "randomized", "treatment"
    ],
    "手术治疗": [
        "surgery", "resection", "gastrectomy", "endoscopic resection",
        "lymph node dissection", "surgical outcome"
    ],
    "诊断方法": [
        "diagnosis", "biomarker", "PET/CT", "endoscopy", "pathology",
        "immunohistochemistry", "molecular marker"
    ],
    "预后评估": [
        "prognosis", "survival", "outcome", "risk factor", "nomogram"
    ]
}

# Build search query
search_query = f"({topic}) AND ({' OR '.join(focus_keywords)})"
```

### Step 3: Search PubMed and Filter

```python
# Search PubMed
response = curl(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={search_query}&retmax=50&retmode=json&sort=pub_date")

new_pmids = [pmid for pmid in response['idlist'] if pmid not in existing_pmids]

print(f"Found {len(response['idlist'])} papers, {len(new_pmids)} are new")
```

### Step 4: Score and Rank Papers by Relevance

```python
# Fetch detailed info for new PMIDs
xml_data = curl(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(new_pmids)}&retmode=xml")

# Score each paper
def score_paper(paper, focus):
    score = 0
    title = paper['title'].lower()
    abstract = paper['abstract'].lower()[:500]
    
    # High relevance: keyword in title
    for kw in FOCUS_KEYWORDS.get(focus, []):
        if kw.lower() in title:
            score += 3
        if kw.lower() in abstract:
            score += 1
    
    # Neuroendocrine in title
    if 'neuroendocrine' in title or 'net' in title:
        score += 2
    
    # Clinical trial/phase in title
    if 'trial' in title or 'phase' in title:
        score += 2
    
    return score

# Sort by score
scored_papers = [(score_paper(p, focus), p) for p in papers]
scored_papers.sort(reverse=True, key=lambda x: x[0])

# Select top N
selected_papers = [p for score, p in scored_papers[:number_requested]]
```

### Step 5: Add Papers with Parallel Calls

```python
# Prepare all paper data
papers_data = [prepare_full_paper_data(p) for p in selected_papers]

# Make PARALLEL API calls (5-10 at a time)
# Submit all feishu_bitable_create_record calls in SAME function_calls block
results = parallel_add_papers(papers_data)

# Report results
print(f"✅ Added {len(results)} papers successfully!")
```

## Core Capabilities

### 1. Table Field Structure (17 Required Fields)

**Primary Field:**
- 文献标题（中文） - Text (主字段, use Chinese title as primary field)

**Basic Information:**
- 文献题目（英文） - Text
- 文献题目（中文） - Text
- 发表年月 - DateTime (timestamp in milliseconds)
- 第一作者 - Text
- 第一作者单位 - Text
- 通讯作者 - Text
- 期刊名称 - Text

**Abstracts:**
- 摘要（英文） - Text (structured with BACKGROUND, METHODS, RESULTS, CONCLUSION)
- 摘要（中文） - Text (structured with 【背景】【目的】【方法】【结果】【结论】)

**Identifiers:**
- PMID - Text
- DOI - Text

**Metadata:**
- 免费全文链接 - URL (format: `{"link": "URL", "text": "PMC免费全文"}` or `{"link": "DOI_URL", "text": "DOI链接"}`)
- SCI分区 - Text (e.g., "JCR Q1", "JCR Q2", "中文核心期刊")
- 中科院分区 - Text (e.g., "医学1区", "医学2区", "中文核心期刊")
- 影响因子 - Number (MUST be numeric, not string!)
- 国标参考文献格式 - Text (GB/T 7714-2015 format)

### 2. Step-by-Step Workflow

**Step 1: Create Feishu Bitable**
```python
# Use feishu_bitable_create_app
app = feishu_bitable_create_app(
    name="文献库标题",
    folder_token="optional_folder_token"
)
# Save app_token and default table_id from response
```

**Step 2: Create Fields**
```python
# Use feishu_bitable_create_field for each of the 17 fields
# Field types: Text=1, Number=2, DateTime=5, URL=15
# Example:
feishu_bitable_create_field(
    app_token=app_token,
    table_id=table_id,
    field_name="文献题目（英文）",
    field_type=1  # Text
)
```

**Step 3: Search PubMed**
```bash
# Search PubMed using E-utilities API
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=SEARCH_TERM&retmax=NUMBER&retmode=json&sort=pub_date"

# Extract PMIDs from response
# Fetch detailed information for each PMID
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID1,PMID2,...&retmode=xml"
```

**Step 4: Parse PubMed XML**
```python
# Extract from XML:
# - Title (ArticleTitle)
# - Authors (LastName + ForeName initial)
# - First author affiliation
# - Corresponding author (last author or from affiliation)
# - Journal name
# - Publication date (Year, Month)
# - DOI
# - PMC ID (if available)
# - Volume, Issue, Pages
# - Abstract (all AbstractText elements with labels)
```

**Step 5: Translate to Chinese**
```python
# Translate title to Chinese
# Translate abstract to Chinese with structured format:
# 【背景】... 【目的】... 【方法】... 【结果】... 【结论】...
```

**Step 6: Get Journal Metadata**
```python
# Look up impact factor for journal
# Determine SCI partition (JCR Q1/Q2/Q3/Q4)
# Determine CAS partition (医学1区/2区/3区/4区)
# Use references/impact_factors.md for common journals
```

**Step 7: Format Reference**
```python
# GB/T 7714-2015 format:
# Author1, Author2, Author3, et al. Title[J]. Journal Abbrev, Year, Volume(Issue): Pages. DOI: xxx.

# Example:
# Fazio N, La Salvia A. Immune Checkpoint Inhibitors in High-grade Gastroenteropancreatic Neuroendocrine Neoplasms[J]. Endocr Rev, 2026, 47(2): 178-190. DOI: 10.1210/endrev/bnaf037.
```

**Step 8: Add to Feishu Table**
```python
# Use feishu_bitable_create_record
# IMPORTANT: 影响因子 must be numeric, not string!
# IMPORTANT: 免费全文链接 must be JSON format: {"link": "URL", "text": "text"}

record = feishu_bitable_create_record(
    app_token=app_token,
    table_id=table_id,
    fields={
        "PMID": pmid,
        "文献题目（英文）": english_title,
        "文献题目（中文）": chinese_title,
        "发表年月": timestamp_ms,  # DateTime as milliseconds
        "第一作者": first_author,
        "第一作者单位": first_affiliation,
        "通讯作者": corresponding_author,
        "期刊名称": journal,
        "摘要（英文）": english_abstract,
        "摘要（中文）": chinese_abstract,
        "DOI": doi,
        "免费全文链接": {"link": url, "text": text},
        "SCI分区": sci_partition,
        "中科院分区": cas_partition,
        "影响因子": impact_factor,  # Number, not string!
        "国标参考文献格式": reference,
        "文献标题（中文）": chinese_title  # Primary field (中文标题作为主字段)
    }
)
```

**Step 9: Set Table Permissions**
```python
# Use feishu_perm to set full_access permission for the user
# This allows the user to fully manage the table (view, edit, manage permissions, delete)

feishu_perm(
    action="add",
    token=app_token,  # Use the Bitable's app_token
    type="bitable",
    member_type="openid",  # User's open_id
    member_id=user_open_id,  # User's open_id (e.g., "ou_xxx")
    perm="full_access"  # Full management permission
)

# Permission levels:
# - "view": View only
# - "edit": Can edit
# - "full_access": Full access (can manage permissions)

# Note: feishu_perm tool must be enabled in configuration:
# channels.feishu.tools.perm = true
```

### 3. User Reporting Requirements

**Report after each step:**

1. ✅ **Table Created**: "已创建飞书多维表格，表格名称：[名称]，表格ID：[ID]"
2. ✅ **Fields Created**: "已创建所有必填字段"
3. ✅ **PubMed Search**: "已从PubMed检索到 [N] 篇文献"
4. ✅ **Deduplication**: "去重后剩余 [N] 篇新文献"
5. ✅ **Metadata Extraction**: "正在提取第 [X]/[N] 篇文献的详细信息..."
6. ✅ **Translation**: "正在翻译中文标题和摘要..."
7. ✅ **Adding to Table**: "正在添加第 [X]/[N] 篇文献到表格..."
8. ✅ **Permissions Set**: "已为您设置表格管理权限"
9. ✅ **Completion**: "✅ 任务完成！共添加 [N] 篇文献到表格中，表格现有 [M] 条记录，您拥有完全管理权限"

### 4. Common Pitfalls to Avoid

**❌ WRONG:**
- String impact factor: `"影响因子": "15.3"`
- Plain URL: `"免费全文链接": "https://..."`
- Missing Chinese translation
- Incomplete abstract (missing sections)

**✅ CORRECT:**
- Numeric impact factor: `"影响因子": 15.3`
- JSON URL: `"免费全文链接": {"link": "https://...", "text": "PMC免费全文"}`
- Complete translations
- Structured abstracts with all sections

### 5. Quality Checklist

Before adding each paper, verify:

- [ ] All 17 fields are present
- [ ] 影响因子 is numeric
- [ ] 免费全文链接 is JSON format
- [ ] 发表年月 is timestamp in milliseconds
- [ ] 摘要（中文） has structured format
- [ ] 国标参考文献格式 follows GB/T 7714-2015
- [ ] No duplicate PMIDs in table

### 6. Permission Management

**IMPORTANT**: Always set table permissions for the user after creating the table.

**Configuration Required:**
The `feishu_perm` tool must be enabled in the OpenClaw configuration:

```bash
openclaw config set channels.feishu.tools.perm true
openclaw gateway restart  # Restart gateway to apply changes
```

**Why It's Important:**
- Without proper permissions, users cannot fully manage tables they create
- `full_access` permission allows users to:
  - View and edit table content
  - Manage permissions (add/remove collaborators)
  - Delete the table
  - Export and share the table

**How to Get User's open_id:**
The user's open_id is available in the inbound context metadata:
```json
{
  "sender_id": "ou_xxxxxxxxxxxx",
  "sender": "User Name"
}
```

**Permission Levels:**
- `view`: Read-only access
- `edit`: Can view and edit content
- `full_access`: Full management access (recommended for table owners)

## Resources

### scripts/
- `pubmed_search.py` - PubMed E-utilities API wrapper
- `parse_pubmed_xml.py` - XML parsing utilities

### references/
- `field_mapping.md` - Complete field definitions and types
- `impact_factors.md` - Common journal impact factors and partitions
- `reference_format.md` - GB/T 7714-2015 formatting rules
