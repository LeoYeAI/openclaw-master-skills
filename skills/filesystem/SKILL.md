---
name: filesystem
description: Advanced filesystem operations for listing files, searching content, batch processing, and directory analysis. Supports recursive search, file type filtering, size analysis, and batch operations like copy/move/delete. Use when you need to: list directory contents, search for files by name or content, analyze directory structures, perform batch file operations, or analyze file sizes and distribution.
---

# Filesystem Operations

文件系统操作工具，提供目录列表、内容搜索、批量处理和目录分析功能。

## 快速开始

### 列出目录
```bash
# 列出当前目录
ls -la

# 递归列出目录树
find . -type f -name "*.md" | head -20

# 按类型过滤
find . -type f \( -name "*.md" -o -name "*.txt" \)
```

### 搜索文件
```bash
# 按名称搜索
find . -name "*keyword*"

# 按内容搜索
grep -r "keyword" . --include="*.md"

# 不区分大小写搜索
grep -ri "keyword" . --include="*.md"
```

### 分析目录
```bash
# 统计文件类型
find . -type f -name "*.md" | wc -l

# 查看目录大小
du -sh .

# 找出最大文件
find . -type f -exec ls -lh {} \; | sort -k5 -h | head -10
```

---

## 核心功能

### 1. 目录列表

**基础列表**：
```bash
ls -la                    # 详细列表
ls -lh                    # 人类可读大小
ls -lt                    # 按修改时间排序
ls -R                     # 递归列表
```

**高级列表**：
```bash
# 列出特定类型
find . -type f -name "*.md"

# 按深度列出
find . -maxdepth 2 -type f

# 排除特定目录
find . -type f -not -path "*/node_modules/*"
```

---

### 2. 文件搜索

**按名称搜索**：
```bash
# 精确匹配
find . -name "filename.md"

# 模式匹配
find . -name "*pattern*"

# 大小写不敏感
find . -iname "*pattern*"
```

**按内容搜索**：
```bash
# 基础搜索
grep -r "keyword" .

# 包含行号
grep -rn "keyword" .

# 只搜索特定文件
grep -r "keyword" . --include="*.md"

# 排除目录
grep -r "keyword" . --exclude-dir=node_modules
```

**正则表达式搜索**：
```bash
# 使用正则
grep -r "^## " . --include="*.md"

# 多个关键词
grep -r "key1\|key2" .

# 行首/行尾
grep -r "^关键词" .
grep -r "关键词$" .
```

---

### 3. 批量操作

**批量复制**：
```bash
# 复制特定类型
find . -name "*.md" -exec cp {} backup/ \;

# 复制到多个位置
for file in *.md; do cp "$file" dir1/ && cp "$file" dir2/; done
```

**批量移动**：
```bash
# 移动特定文件
find . -name "*.log" -exec mv {} logs/ \;

# 按条件移动
find . -type f -size +1M -exec mv {} large/ \;
```

**批量删除**：
```bash
# 删除特定类型
find . -name "*.tmp" -delete

# 删除空目录
find . -type d -empty -delete

# 删除旧文件
find . -type f -mtime +30 -delete
```

**批量重命名**：
```bash
# 使用 rename 命令
rename 's/old/new/' *.md

# 添加前缀
for file in *.md; do mv "$file" "prefix_$file"; done
```

---

### 4. 目录分析

**大小分析**：
```bash
# 总大小
du -sh .

# 各目录大小
du -h --max-depth=1 . | sort -hr

# 最大的文件
find . -type f -exec ls -lh {} \; | sort -k5 -hr | head -10
```

**文件类型统计**：
```bash
# 按扩展名统计
find . -type f -name "*.md" | wc -l

# 各类型统计
find . -type f -name "*.*" | sed 's/.*\.//' | sort | uniq -c
```

**目录结构分析**：
```bash
# 目录树
tree -L 2

# 递归深度
find . -type d | wc -l

# 文件分布
find . -type f | cut -d/ -f1-2 | sort | uniq -c
```

---

### 5. 文件信息查询

**文件详情**：
```bash
# 完整信息
stat filename

# 只看大小
ls -lh filename

# 只看时间
ls -lt filename
```

**文件内容预览**：
```bash
# 头部
head -20 filename

# 尾部
tail -20 filename

# 随机行
shuf -n 10 filename

# 字符数
wc -c filename

# 行数
wc -l filename
```

---

## 实用工具

### tree 命令
```bash
# 安装
brew install tree

# 使用
tree -L 2 -I 'node_modules|__pycache__'
```

### fd 命令（快速查找）
```bash
# 安装
brew install fd

# 使用
fd "pattern" /path
fd -e md .    # 只找 md 文件
fd -t f .       # 只找文件
```

### ripgrep 命令（快速搜索）
```bash
# 安装
brew install ripgrep

# 使用
rg "keyword" .
rg -t md "keyword" .
rg -i "keyword" .          # 不区分大小写
rg --type md "pattern" .
```

---

## 最佳实践

### 1. 搜索优化
- 使用 `fd` 或 `ripgrep` 替代 `find` 和 `grep`（更快）
- 先缩小搜索范围，再进行深度搜索
- 使用文件类型过滤减少搜索时间

### 2. 批量操作安全
- 操作前先用 `--dry-run` 查看会发生什么
- 批量删除前先列出文件确认
- 重要操作前先备份

### 3. 目录分析
- 使用 `-max-depth` 限制递归深度
- 使用 `-size` 过滤大文件
- 使用 `-mtime` 按时间筛选

---

## 常见任务

### 查找并处理 Markdown 文件
```bash
# 查找所有 md 文件
find . -name "*.md" -type f

# 统计 md 文件数量
find . -name "*.md" | wc -l

# 列出最大的 md 文件
find . -name "*.md" -exec ls -lh {} \; | sort -k5 -hr | head -5
```

### 搜索并替换内容
```bash
# 搜索所有匹配项
grep -rn "old_text" . --include="*.md"

# 替换（使用 sed）
find . -name "*.md" -exec sed -i '' 's/old_text/new_text/g' {} \;
```

### 清理临时文件
```bash
# 删除 .tmp 文件
find . -name "*.tmp" -delete

# 删除空目录
find . -type d -empty -delete

# 删除 30 天前的日志
find . -name "*.log" -mtime +30 -delete
```

---

## 安全提醒

⚠️ **批量操作前先确认**：
- 列出要操作的文件
- 确认不会误删重要文件
- 考虑先备份

⚠️ **删除操作不可逆**：
- `rm` 删除后无法恢复
- 大批量删除前仔细检查
- 考虑使用 `rm -i` 交互式删除

⚠️ **权限注意**：
- 某些操作可能需要 sudo
- 系统目录操作要谨慎
- 考虑文件权限问题
