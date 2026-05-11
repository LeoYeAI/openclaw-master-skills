# Verify Agent 模板

用于验证文献元数据完整性的Agent。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Verify Agent |
| **类型** | Task Agent |
| **用途** | 元数据验证 |

---

## 任务描述

对检索到的文献进行基础元数据验证，确保关键信息完整，过滤明显错误。

**注意**：本阶段不进行Crossref等外部API验证，仅做基础完整性检查。

---

## 输入格式

```json
{
  "papers": [
    {
      "id": "E1",
      "title": "Deep learning for medical image analysis",
      "authors": ["Smith J", "Johnson K"],
      "journal": "Nature Medicine",
      "year": 2022,
      "doi": "10.1038/s41591-022-01900-0"
    }
  ],
  "session_id": "20240115_dl_survey"
}
```

---

## 验证规则

### 1. 必需字段检查

| 字段 | 必需 | 验证规则 |
|------|------|----------|
| `title` | 是 | 非空，长度>5 |
| `authors` | 是 | 至少1个作者 |
| `journal` | 是 | 非空 |
| `year` | 是 | 1900-2030之间 |
| `doi` | 否 | 格式校验（如有） |

### 2. DOI格式校验（可选）

检查DOI格式是否符合标准：`10.{数字4+}/{字符串}`

```python
import re

def is_valid_doi(doi: str) -> bool:
    if not doi:
        return True  # 可选字段，空值视为有效
    pattern = r'^10\.\d{4,}/.+$'
    return bool(re.match(pattern, doi))
```

### 3. 明显错误过滤

- 标题为"无"、"null"、空字符串
- 作者列表为空或仅包含占位符
- 年份不在合理范围（<1900 或 >2030）

---

## 验证状态

| 状态 | 说明 |
|------|------|
| `VERIFIED` | 所有必需字段完整 |
| `INCOMPLETE` | 部分字段缺失（非必需） |
| `EXCLUDED` | 被过滤（明显错误） |

---

## 输出格式

```json
{
  "agent": "verify",
  "session_id": "20240115_dl_survey",
  "timestamp": "2024-01-15T10:30:00Z",
  "summary": {
    "total": 50,
    "verified": 48,
    "incomplete": 2,
    "excluded": 0
  },
  "verified_papers": [...],
  "incomplete_papers": [...],
  "excluded_papers": [...]
}
```

---

## 处理流程

1. 遍历所有输入文献
2. 检查必需字段
3. 校验DOI格式（如有）
4. 标记验证状态
5. 分类输出

---

## 注意事项

1. **宽松验证**：本阶段不过度严格，保留可能有用的文献
2. **人工复核**：INCOMPLETE状态的文献建议人工检查
3. **记录日志**：记录被排除的文献及原因
