# Field Mapping Reference

## Feishu Bitable Fields (17 Required Fields)

### Field Types
- `Text` = type 1
- `Number` = type 2
- `DateTime` = type 5
- `URL` = type 15

## Complete Field List

| # | Field Name (Chinese) | Field Name (English) | Type | Required | Notes |
|---|---------------------|---------------------|------|----------|-------|
| 1 | 胃神经内分泌肿瘤文献库（陈博士版） | Literature Database Name | Text | Yes | **Primary field** - Use Chinese title |
| 2 | 文献题目（英文） | English Title | Text | Yes | From PubMed ArticleTitle |
| 3 | 文献题目（中文） | Chinese Title | Text | Yes | **Must translate** from English |
| 4 | 发表年月 | Publication Date | DateTime | Yes | **Timestamp in milliseconds** |
| 5 | 第一作者 | First Author | Text | Yes | Format: "LastName F" |
| 6 | 第一作者单位 | First Author Affiliation | Text | Yes | From first AffiliationInfo/Affiliation |
| 7 | 通讯作者 | Corresponding Author | Text | Yes | Usually last author or from affiliation |
| 8 | 期刊名称 | Journal Name | Text | Yes | Full journal title |
| 9 | 摘要（英文） | English Abstract | Text | Yes | Structured with all sections |
| 10 | 摘要（中文） | Chinese Abstract | Text | Yes | **Must translate** with structured format |
| 11 | PMID | PubMed ID | Text | Yes | From PMID element |
| 12 | DOI | Digital Object Identifier | Text | Yes | From ArticleId with IdType="doi" |
| 13 | 免费全文链接 | Free Full Text Link | URL | Yes | **JSON format required** |
| 14 | SCI分区 | SCI Partition | Text | Yes | JCR Q1/Q2/Q3/Q4 or "中文核心期刊" |
| 15 | 中科院分区 | CAS Partition | Text | Yes | 医学1区/2区/3区/4区 or "中文核心期刊" |
| 16 | 影响因子 | Impact Factor | Number | Yes | **MUST be numeric, not string!** |
| 17 | 国标参考文献格式 | GB/T 7714-2015 Reference | Text | Yes | Follow GB/T 7714-2015 standard |

## Field Value Formats

### DateTime (发表年月)
- **Format**: Milliseconds since Unix epoch (1970-01-01 00:00:00 UTC)
- **Example**: 1767196800000 (represents 2026-01-01)
- **Conversion**:
  ```python
  import calendar
  from datetime import datetime
  
  # From year and month to timestamp
  dt = datetime(2026, 3, 1)  # March 2026
  timestamp_ms = int(calendar.timegm(dt.timetuple()) * 1000)
  ```

### URL (免费全文链接)
- **Format**: JSON object with "link" and "text" keys
- **PMC Example**: `{"link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/", "text": "PMC免费全文"}`
- **DOI Example**: `{"link": "https://doi.org/10.1234/example", "text": "DOI链接"}`

### Number (影响因子)
- **Format**: Numeric value, NOT string
- **Correct**: `15.3`
- **Wrong**: `"15.3"`
- **Zero for Chinese journals**: `0`

### Text (摘要)
- **English**: Structured with labels (BACKGROUND:, METHODS:, RESULTS:, CONCLUSION:)
- **Chinese**: Structured with labels (【背景】... 【目的】... 【方法】... 【结果】... 【结论】...)

## Common Mistakes to Avoid

1. ❌ **String impact factor**: `"影响因子": "15.3"`
   ✅ **Correct**: `"影响因子": 15.3`

2. ❌ **Plain URL**: `"免费全文链接": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/"`
   ✅ **Correct**: `"免费全文链接": {"link": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/", "text": "PMC免费全文"}`

3. ❌ **DateTime as string**: `"发表年月": "2026-03-01"`
   ✅ **Correct**: `"发表年月": 1767196800000`

4. ❌ **Missing Chinese translation**
   ✅ **Correct**: Always translate title and abstract

5. ❌ **Incomplete abstract** (missing sections)
   ✅ **Correct**: Include all sections (BACKGROUND, METHODS, RESULTS, CONCLUSION)

## Field Creation Example

```python
# Create field using feishu_bitable_create_field
feishu_bitable_create_field(
    app_token="app_token",
    table_id="table_id",
    field_name="文献题目（英文）",
    field_type=1  # Text type
)

# DateTime field
feishu_bitable_create_field(
    app_token="app_token",
    table_id="table_id",
    field_name="发表年月",
    field_type=5  # DateTime type
)

# Number field
feishu_bitable_create_field(
    app_token="app_token",
    table_id="table_id",
    field_name="影响因子",
    field_type=2  # Number type
)

# URL field
feishu_bitable_create_field(
    app_token="app_token",
    table_id="table_id",
    field_name="免费全文链接",
    field_type=15  # URL type
)
```
