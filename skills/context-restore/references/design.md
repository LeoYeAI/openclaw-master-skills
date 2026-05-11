# Context-Restore 设计决策文档

> 本文档记录 context-restore skill 的关键设计决策和架构选择。
> 使用说明请参考 [SKILL.md](../SKILL.md)

---

## 1. 架构设计

### 1.1 模块结构

```
restore_context.py (单一职责文件)
├── load_compressed_context()      # 加载层
├── parse_metadata()                # 解析层
├── extract_*()                     # 提取层（operations/projects/tasks）
├── format_*_report()               # 格式化层
└── restore_context()              # 主入口
```

### 1.2 设计原则

| 原则 | 实现方式 |
|------|---------|
| 单一职责 | 每个函数只做一件事 |
| 开闭原则 | 新增级别只需添加 format_* 函数 |
| 依赖倒置 | 输出格式化与业务逻辑分离 |
| 组合优于继承 | 通过函数参数控制行为 |

---

## 2. 关键设计决策

### 2.1 为什么使用三级恢复级别？

**决策**：实现 minimal/normal/detailed 三级恢复

**权衡分析**：
- **单级别**：简单但不够灵活
- **两级**：平衡但场景覆盖不足
- **三级**：覆盖快速确认、日常使用、深度回顾三个核心场景

**结论**：三级是最佳平衡点，符合用户实际使用模式。

### 2.2 为什么支持 JSON 和纯文本两种格式？

**决策**：自动检测并支持两种格式

**原因**：
1. context-save 可能输出 JSON 或压缩文本
2. 保持向后兼容
3. 简化 context-save 的输出要求

**实现**：
```python
try:
    return json.loads(content)
except json.JSONDecodeError:
    return content  # 降级为纯文本
```

### 2.3 为什么使用函数式设计而非类？

**决策**：使用纯函数 + 主入口函数

**理由**：
1. 更简单的测试（无状态）
2. 更易于理解和维护
3. 减少样板代码
4. 便于其他技能调用具体函数

---

## 3. API 设计

### 3.1 主入口函数

```python
def restore_context(
    filepath: str = DEFAULT_CONTEXT_FILE,
    level: str = LEVEL_NORMAL
) -> str:
    """
    从压缩文件中恢复上下文并生成报告。
    """
```

**设计要点**：
- 默认参数覆盖 90% 使用场景
- 返回字符串而非对象（简化 CLI 输出）
- 供其他技能使用时提供 `get_context_summary()`

### 3.2 供其他技能使用的摘要函数

```python
def get_context_summary(filepath: str = DEFAULT_CONTEXT_FILE) -> dict:
    """
    返回结构化字典，供其他技能集成使用。
    """
```

**返回结构**：
```python
{
    'success': bool,
    'metadata': dict,
    'operations': list,
    'projects': list,
    'tasks': list,
    'memory_highlights': list
}
```

---

## 4. 错误处理策略

### 4.1 降级机制

```
Detailed → Normal → Minimal → 空上下文
    ↓          ↓         ↓
  解析失败   格式错误   文件不存在
```

### 4.2 错误码定义

| 错误类型 | 处理方式 | 用户可见消息 |
|---------|---------|-------------|
| `FileNotFoundError` | 静默返回空上下文 | "未找到历史上下文" |
| `PermissionError` | 记录日志，返回错误 | "无法访问上下文文件" |
| `UnicodeDecodeError` | 尝试不同编码 | "文件编码错误" |
| `json.JSONDecodeError` | 降级为纯文本 | （无提示，自动处理） |
| `ValueError` | 抛出异常 | "无效的恢复级别" |

---

## 5. 性能考虑

### 5.1 性能目标

| 操作 | 目标耗时 |
|------|---------|
| 文件加载 | < 100ms |
| JSON 解析 | < 50ms |
| 文本提取 | < 20ms |
| 格式化输出 | < 30ms |
| **总计** | **< 200ms** |

### 5.2 优化策略

- **惰性加载**：只加载需要的文件
- **正则预编译**：高频正则表达式编译后复用
- **缓存元数据**：重复调用时缓存解析结果

---

## 6. 扩展计划

### 6.1 短期扩展（已规划）

- [ ] 智能恢复级别检测（根据用户问题自动判断）
- [ ] 项目聚焦模式（只恢复指定项目）
- [ ] 差异恢复（只显示变更部分）

### 6.2 长期扩展（待评估）

- [ ] 上下文版本比较
- [ ] 多会话协调恢复
- [ ] 时间范围过滤

---

## 7. 测试策略

### 7.1 测试覆盖

```
tests/
├── test_restore_basic.py      # 基础功能测试
│   ├── test_load_json         # JSON 加载
│   ├── test_load_text         # 文本加载
│   └── test_file_not_found   # 错误处理
├── test_restore_levels.py     # 级别测试
│   ├── test_minimal_output    # Minimal 级别
│   ├── test_normal_output     # Normal 级别
│   └── test_detailed_output   # Detailed 级别
└── test_integration.py        # 集成测试
    ├── test_cli_args          # 命令行参数
    └── test_summary_api       # API 摘要接口
```

---

## 8. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-06 | 初始版本，实现三级恢复级别 |

---

## 参考资料

- [SKILL.md](../SKILL.md) - 完整使用说明
- [restore_context.py](../scripts/restore_context.py) - 完整代码实现
- OpenClaw Skill 编写规范
