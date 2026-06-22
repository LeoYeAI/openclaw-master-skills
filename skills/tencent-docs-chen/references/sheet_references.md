# Sheet 表格操作参考文档

本文件包含腾讯文档 MCP 中 Sheet（在线表格）相关工具的完整 API 说明、详细调用示例、参数说明和返回值说明。

---

## 通用说明

### Sheet 工具概述

Sheet 工具专门用于操作腾讯文档中的在线表格（Excel格式），提供表格信息的查询、范围数据的获取以及批量更新等功能。

### 响应结构

所有 API 返回都包含：
- `error`: 错误信息（成功时为空）
- `trace_id`: 调用链追踪 ID

### 表格范围表示法

Sheet 工具使用 A1 表示法来指定表格范围：
- `A1`: 单个单元格
- `A1:B10`: 矩形区域
- `Sheet1!A1:B10`: 指定工作表名称的范围

---

## 工具调用示例

## 1. GetSheetInfo

### 功能说明
查询工作表的基本信息，包括所有子表的ID、标题、大小和已使用的行列数。

### 调用示例
```json
{
  "file_id": "sheet_1234567890"
}
```

### 参数说明
- `file_id` (string, 必填): 表格文件唯一标识符

### 返回值说明
```json
{
  "sheet_info": {
    "file_id": "sheet_1234567890",
    "title": "销售数据表",
    "sheets": [
      {
        "sheet_id": "sht1234567890",
        "title": "Sheet1",
        "row_count": 100,
        "column_count": 10,
        "used_row_count": 50,
        "used_column_count": 5
      }
    ]
  },
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 2. GetSheetRange

### 功能说明
获取指定范围内的在线表格信息，支持 A1 表示法指定查询范围。

### 调用示例
```json
{
  "file_id": "sheet_1234567890",
  "range": "A1:C10"
}
```

### 参数说明
- `file_id` (string, 必填): 表格文件唯一标识符
- `range` (string, 必填): 查询范围，使用 A1 表示法
- `sheet_id` (string, 可选): 工作表ID，不指定时使用默认工作表

### 返回值说明
```json
{
  "range_data": {
    "range": "A1:C10",
    "values": [
      ["姓名", "年龄", "部门"],
      ["张三", "25", "技术部"],
      ["李四", "30", "产品部"]
    ]
  },
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 3. BatchUpdateSheet

### 功能说明
批量执行对在线表格的更新操作，支持添加工作表、更新单元格内容、删除行列、删除工作表等多种操作。

### 调用示例
```json
{
  "file_id": "sheet_1234567890",
  "requests": [
    {
      "add_sheet": {
        "properties": {
          "title": "新工作表"
        }
      }
    },
    {
      "update_cells": {
        "range": "A1:B2",
        "rows": [
          {"values": ["标题1", "标题2"]},
          {"values": ["数据1", "数据2"]}
        ]
      }
    }
  ]
}
```

### 参数说明
- `file_id` (string, 必填): 表格文件唯一标识符
- `requests` (array, 必填): 批量操作请求列表，单次请求的操作数量不大于5

### 支持的操作类型

#### 添加工作表
```json
{
  "add_sheet": {
    "properties": {
      "title": "工作表标题",
      "index": 0
    }
  }
}
```

#### 更新单元格
```json
{
  "update_cells": {
    "range": "A1:B2",
    "rows": [
      {"values": ["值1", "值2"]},
      {"values": ["值3", "值4"]}
    ]
  }
}
```

#### 删除行列
```json
{
  "delete_dimension": {
    "range": {
      "sheet_id": "sht1234567890",
      "dimension": "ROWS",
      "start_index": 5,
      "end_index": 10
    }
  }
}
```

#### 删除工作表
```json
{
  "delete_sheet": {
    "sheet_id": "sht1234567890"
  }
}
```

### 返回值说明
```json
{
  "replies": [
    {
      "add_sheet": {
        "properties": {
          "sheet_id": "sht1234567890",
          "title": "新工作表",
          "index": 1
        }
      }
    }
  ],
  "error": "",
  "trace_id": "trace_1234567890"
}
```

---

## 典型工作流示例

### 工作流 1：查询表格信息并获取数据

```bash
# 1. 获取表格基本信息
mcporter call "tencent-docs.GetSheetInfo" --args '{"file_id":"sheet_1234567890"}'

# 2. 获取指定范围的数据
mcporter call "tencent-docs.GetSheetRange" --args '{"file_id":"sheet_1234567890","range":"A1:C10"}'
```

# 2. 批量更新表格内容

```bash
# 1. 批量更新单元格内容
mcporter call "tencent-docs.BatchUpdateSheet" --args '{
  "file_id": "sheet_1234567890",
  "requests": [
    {
      "update_cells": {
        "range": "A1:B2",
        "rows": [
          {"values": ["标题1", "标题2"]},
          {"values": ["数据1", "数据2"]}
        ]
      }
    }
  ]
}'
```

### 工作流 3：管理工作表结构

```bash
# 1. 添加新工作表
mcporter call "tencent-docs.BatchUpdateSheet" --args '{
  "file_id": "sheet_1234567890",
  "requests": [
    {
      "add_sheet": {
        "properties": {
          "title": "2024年数据"
        }
      }
    }
  ]
}'

# 2. 删除不需要的工作表
mcporter call "tencent-docs.BatchUpdateSheet" --args '{
  "file_id": "sheet_1234567890",
  "requests": [
    {
      "delete_sheet": {
        "sheet_id": "sht1234567890"
      }
    }
  ]
}'
```

---

## 注意事项

### 范围限制
- `GetSheetRange` 单次查询范围限制：行数≤1000，列数≤200，单元格总数≤10000
- `BatchUpdateSheet` 单次请求的操作数量不大于5

### 数据格式
- 单元格数据使用二维数组表示，第一维是行，第二维是列
- 空单元格使用空字符串表示
- 数值类型的数据会自动转换为字符串

### 性能建议
- 对于大数据量的更新，建议使用 `BatchUpdateSheet` 进行批量操作
- 查询大范围数据时，建议分页获取数据
- 避免频繁的小范围更新操作

### 错误处理
- 如果范围超出表格边界，会返回错误信息
- 如果工作表不存在，会返回相应的错误提示
- 批量操作中某个操作失败时，整个批量操作会回滚