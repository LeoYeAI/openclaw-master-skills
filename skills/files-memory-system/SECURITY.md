# 安全实践指南 - 文件删除机制

> 本文档记录 files-memory-system 中文件删除的安全实践，避免后续改动破坏安全机制。

## 🎯 核心原则

**永远优先使用 `trash` 命令，避免直接使用 `rm -rf`**

## 📋 背景

### 问题来源
- 原始 `install.sh` 使用 `rm -rf` 删除旧版本 skill
- 被 VirusTotal 标记为 suspicious patterns
- 触发安全警报："检测到潜在危险操作"

### 解决方案
使用 `trash` 命令代替 `rm -rf`：
- 文件移至回收站，可恢复
- 避免永久删除
- 符合现代操作系统标准行为

## 🔧 实现机制

### 当前实现 (install.sh)

```bash
# 安全删除逻辑
if command -v trash &> /dev/null; then
    trash "$TARGET_DIR"
    echo "   ✅ 已移至回收站 (trash)"
else
    rm -rf "$TARGET_DIR"
    echo "   ✅ 已删除 (rm -rf)"
fi
```

### 关键特性

| 特性 | 说明 |
|------|------|
| **优先 trash** | 如果系统有 trash 命令，优先使用 |
| **回退机制** | trash 不可用时，回退到 rm -rf |
| **用户确认** | 删除前必须用户输入 y 确认 |
| **明确提示** | 显示要删除的路径、原因、影响范围 |

## ⚠️ 重要提醒

### 不要这样做

❌ **不要恢复使用纯 `rm -rf`**
```bash
# 危险！不要这样改
rm -rf "$TARGET_DIR"  # 永久删除，无法恢复
```

❌ **不要删除用户确认步骤**
```bash
# 危险！不要这样改
# 删除前不询问用户
```

❌ **不要扩大删除范围**
```bash
# 危险！不要这样改
rm -rf /workspace/  # 会删除所有数据！
```

### 应该这样做

✅ **保持 trash 优先逻辑**
```bash
if command -v trash &> /dev/null; then
    trash "$TARGET_DIR"
else
    rm -rf "$TARGET_DIR"
fi
```

✅ **保持用户确认**
```bash
read -p "确认删除? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    exit 0
fi
```

✅ **保持明确提示**
```bash
echo "即将删除: $TARGET_DIR"
echo "(仅删除此 skill 目录，不影响其他数据)"
```

## 📝 更新记录

| 日期 | 改动 | 作者 |
|------|------|------|
| 2026-03-24 | 使用 trash 代替 rm -rf | files-memory-system 开发群组 |
| 2026-03-24 | 增强删除前提示信息 | files-memory-system 开发群组 |

## 🔗 相关文件

- `scripts/install.sh` - 包含安全删除逻辑
- `SECURITY.md` - 本文档

## 📚 参考

- [trash-cli 项目](https://github.com/andreafrancia/trash-cli) - 跨平台的 trash 命令实现
- [VirusTotal 安全扫描](https://www.virustotal.com) - 文件安全检测平台

---

**最后更新**: 2026-03-24
**维护者**: files-memory-system 开发群组
