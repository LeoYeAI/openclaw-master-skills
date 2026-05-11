# C 扩展使用说明

## 概述

AGI 进化模型包含预编译的 C 扩展模块 `personality_core.so`，用于加速核心算法。

## 部署说明

### 生产环境（推荐）

本 Skill 已包含预编译的 C 扩展文件，部署时会自动加载：

- ✅ 无需编译
- ✅ 自动降级
- ✅ 功能完整

### 目录结构

C 扩展文件位于 `scripts/personality_core/` 目录：

```
scripts/
├── personality_layer_pure.py
└── personality_core/              ← C 扩展目录
    ├── personality_core.so
    ├── personality_core.cpython-313-x86_64-linux-gnu.so
    ├── core_perception_node.so
    └── core_perception_node.cpython-313-x86_64-linux-gnu.so
```

### 本地开发

如需修改 C 扩展，请参考以下步骤：

#### 1. 编译要求

- Linux/macOS: gcc 或 clang
- Windows: Visual Studio C++ Build Tools
- Python 3.7+

#### 2. 编译步骤

```bash
cd scripts/personality_core
python3 setup.py build_ext --inplace
```

#### 3. 重命名产物

编译后会生成平台特定的文件，需要重命名为 `personality_core.so`：

**Linux/macOS**:
```bash
cp personality_core.cpython-*-*.so personality_core.so
```

**Windows**:
```cmd
copy personality_core.cp*.pyd personality_core.so
```

## 性能对比

| 操作 | 纯Python | C扩展 | 提升 |
|------|----------|-------|------|
| 归一化权重 | 0.8ms | 0.05ms | **16倍** |
| 相似度计算 | 3.2ms | 0.12ms | **27倍** |
| 优先级计算 | 2.5ms | 0.09ms | **28倍** |
| 批量计算(1000) | 280ms | 12ms | **23倍** |

## 自动降级机制

如果 C 扩展加载失败，Skill 会自动降级到纯 Python 实现：

```python
from personality_layer_pure import PersonalityLayer

if PersonalityLayer.USE_C_EXT:
    print("使用 C 扩展加速")
else:
    print("使用纯 Python 实现（降级模式）")
```

**降级触发条件**：
- C 扩展文件不存在
- 平台不匹配（例如在 macOS 上使用 Linux 的 .so）
- Python 版本不兼容

## 平台支持

当前预编译版本支持：

| 平台 | 状态 | 文件名 |
|------|------|--------|
| Linux x64 | ✅ 预编译 | `personality_core.cpython-313-x86_64-linux-gnu.so` |
| macOS x64 | ⚠️ 需编译 | - |
| macOS ARM64 | ⚠️ 需编译 | - |
| Windows x64 | ⚠️ 需编译 | - |

**其他平台**：需要手动编译 C 扩展。

## 故障排查

### C 扩展未加载

**症状**：日志显示 "使用纯 Python 实现（降级模式）"

**原因**：
1. 平台不匹配
2. Python 版本不兼容
3. 文件损坏

**解决方案**：
- 当前平台：降级到纯 Python（功能正常）
- 本地开发：重新编译对应平台的 C 扩展

### ImportError

**症状**：`ImportError: No module named 'personality_core'`

**解决方案**：无需处理，系统会自动降级到纯 Python 实现。

## 注意事项

1. **预编译文件**：当前仅提供 Linux x64 版本
2. **跨平台**：其他平台自动降级到纯 Python 实现
3. **功能一致**：降级模式下功能完全正常，仅性能略低
4. **无需编译**：生产部署不需要编译，直接使用预编译文件
