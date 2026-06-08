# 飞书文档编辑方法

**最后更新**: 2026-03-26  
**测试文档**: `<测试文档链接>`

---

## 一、插入文本

```javascript
feishu_doc action=insert
  after_block_id=<目标 block_id>
  content="要插入的文本"
  doc_token=<文档 ID>
```

**关键点**：
- 使用 `content` 参数
- `after_block_id` 指定在哪个 block 后面插入
- 插入的内容与目标 block 同级

---

## 二、更新表格单元格内容

```javascript
// 步骤 1：删除单元格内原有的文本 block
feishu_doc action=delete_block
  block_id=<单元格内的文本 block_id>
  doc_token=<文档 ID>

// 步骤 2：向单元格追加新的空 block
feishu_doc action=append
  parent_block_id=<单元格 block_id>
  content=" "
  doc_token=<文档 ID>

// 步骤 3：获取新 block 的 ID
feishu_doc action=get_block
  block_id=<单元格 block_id>
  doc_token=<文档 ID>
// children[0].block_id 即为新文本 block

// 步骤 4：填充实际内容
feishu_doc action=insert
  after_block_id=<新文本 block_id>
  content="实际内容"
  doc_token=<文档 ID>
```

**关键点**：
- `append` 创建空 block，`insert` 填充内容
- `parent_block_id` 是单元格 block_id

---

## 三、删除 Block

```javascript
feishu_doc action=delete_block
  block_id=<要删除的 block_id>
  doc_token=<文档 ID>
```

**关键点**：
- 删除前用 `get_block` 确认内容
- 删除后无法恢复

---

## 四、更改/删除句子

```javascript
// 步骤 1：获取句子所在的 text block
feishu_doc action=get_block
  block_id=<text block_id>
  doc_token=<文档 ID>

// 步骤 2：本地修改文本内容（删除/修改目标句子）

// 步骤 3：覆盖更新整个 block
feishu_doc action=update_block
  block_id=<text block_id>
  content="修改后的完整文本"
  doc_token=<文档 ID>
```

**关键点**：
- 使用 `update_block` + `content` 参数
- 句子是文本的一部分，不是独立 block
- 必须传入完整的修改后文本

---

## 五、文档结构

```
文档根 (doc_token)
  ├─ 章节标题 1 (heading1)
  ├─ 内容 1 (text)
  ├─ 内容 2 (text)
  ├─ 章节标题 2 (heading2)
  ├─ 表格 (table)
  │   └─ 单元格 (table_cell)
  │       └─ 文本 block (text)
  └─ ...
```

**关键理解**：
1. 飞书文档是**扁平结构**，章节标题和内容是同级 block，通过顺序表示从属关系
2. 表格单元格是容器，内容存储在子 text block 中
3. `append` + `parent_block_id`：向容器末尾添加子 block
4. `insert` + `after_block_id`：在指定 block 后面插入同级 block

---

## 六、常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `doc_token` | 文档 ID | `<文档 ID>` |
| `block_id` | Block ID | `doxcnbWCeQebJThOIwB3NXdJj1d` |
| `parent_block_id` | 父容器 block_id | 单元格、文档根等 |
| `after_block_id` | 前置 block_id | 章节标题、段落等 |
| `content` | 文本内容（支持 Markdown） | `"**加粗** 或 [链接](url)"` |

---

## 七、测试结果

| 测试项 | 方法 | 结果 |
|--------|------|------|
| 插入文本 | `insert` + `content` | ✅ 通过 |
| 更新表格单元格 | `delete` → `append` → `insert` | ✅ 通过 |
| 删除 Block | `delete_block` | ✅ 通过 |
| 更改句子 | `update_block` + `content` | ✅ 通过 |

---

**测试状态**: ✅ 全部验证通过
