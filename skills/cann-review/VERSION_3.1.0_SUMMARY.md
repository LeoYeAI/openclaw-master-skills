# 版本更新摘要 - v3.1.0

## 🎯 更新目标

扩展技能支持范围，从单纯的 C/C++ 扩展到 C/C++/Python，并去掉 "runtime" 限定词。

---

## 📊 变更统计

- **修改文件**: 3 个
- **新增内容**: +46 行
- **删除内容**: -13 行
- **净增**: +33 行

---

## ✨ 核心变更

### 1. 技能描述更新

**之前**：
```
你是一位资深的 C/C++ 代码工程师，专门负责审查 CANN runtime 项目的 Pull Request。
```

**现在**：
```
你是一位资深的 C/C++/Python 代码工程师，专门负责审查 CANN 项目的 Pull Request。
```

### 2. 支持的语言

**之前**：
- ✅ C
- ✅ C++

**现在**：
- ✅ C
- ✅ C++
- ✅ Python（新增）

### 3. 文件类型检查

**之前**：
```
- .c, .cc, .cpp, .h, .hpp
```

**现在**：
```
- .c, .cc, .cpp, .h, .hpp
- .py（新增）
```

---

## 🆕 新增功能

### Python 资源管理模式检查

检查 Python 代码中的资源管理问题：

```python
# ❌ 危险：忘记关闭文件
file = open('data.txt', 'r')
data = file.read()
# ... 忘记 file.close()

# ✅ 安全：使用 with 语句
with open('data.txt', 'r') as file:
    data = file.read()
# 自动关闭
```

**检查点**：
- 文件句柄管理（`with` 语句）
- 数据库连接管理
- 网络连接管理
- 锁的管理（`threading.Lock`）

### Python 异常处理模式检查

检查 Python 代码中的异常处理问题：

```python
# ❌ 危险：捕获所有异常但不处理
try:
    process_data(data)
except:
    pass  # 隐藏错误

# ✅ 安全：具体异常类型和适当处理
try:
    process_data(data)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

**检查点**：
- 避免 `except:` 捕获所有异常
- 异常处理的完整性
- 异常日志记录
- 异常重新抛出

---

## 📝 文档更新

### SKILL.md

- ✅ 更新技能描述
- ✅ 去掉 "runtime" 限定词
- ✅ 增加 Python 工程师角色

### README.md

- ✅ 更新标题：去掉 "Runtime"
- ✅ 更新描述：支持 C/C++/Python

### prompt.md

- ✅ 更新角色描述
- ✅ 扩展文件类型检查
- ✅ 增加 Python 资源管理模式
- ✅ 增加 Python 异常处理模式
- ✅ 更新标题为 "C/C++/Python 常见问题模式"

---

## 🔍 审查范围扩展

### C/C++ 检查（原有）

- ✅ 内存泄漏检查
  - `malloc/free` 配对
  - `new/delete` 配对
  - 智能指针使用
  - RAII 模式

- ✅ 安全漏洞检查
  - 缓冲区溢出
  - 空指针解引用
  - 类型转换安全
  - 边界检查

- ✅ 可读性检查
  - 命名规范
  - 注释完整性
  - 代码结构

### Python 检查（新增）

- ✅ 资源管理检查
  - 文件句柄管理
  - 上下文管理器（`with` 语句）
  - 数据库连接管理
  - 网络资源管理

- ✅ 异常处理检查
  - 避免裸 `except:`
  - 具体异常类型
  - 异常日志记录
  - 适当的异常传播

- ✅ 代码规范检查
  - PEP 8 规范
  - 类型提示
  - 文档字符串

---

## 📋 审查检查清单更新

### 新增 Python 检查项

```markdown
#### Python 资源管理
- [ ] 文件操作是否使用 `with` 语句
- [ ] 数据库连接是否正确关闭
- [ ] 网络连接是否正确管理
- [ ] 锁是否正确获取和释放

#### Python 异常处理
- [ ] 避免使用裸 `except:`
- [ ] 捕获具体异常类型
- [ ] 异常是否记录日志
- [ ] 异常是否适当传播

#### Python 代码规范
- [ ] 是否遵循 PEP 8
- [ ] 是否有类型提示
- [ ] 函数是否有文档字符串
- [ ] 变量命名是否清晰
```

---

## 🎯 使用场景

### 场景 1：C++ 代码审查

```bash
审查这个 PR: https://gitcode.com/cann/project/pull/123
```

审查 C++ 代码的内存泄漏、安全漏洞等问题。

### 场景 2：Python 代码审查

```bash
审查这个 PR: https://gitcode.com/cann/project/pull/456
```

审查 Python 代码的资源管理、异常处理等问题。

### 场景 3：混合代码审查

```bash
审查这个 PR: https://gitcode.com/cann/project/pull/789
```

同时审查 C++ 和 Python 代码，分别应用对应的检查规则。

---

## 📊 兼容性

### 向后兼容

- ✅ 完全兼容 v3.0.x 的所有功能
- ✅ 不影响现有 C/C++ 代码审查
- ✅ 配置文件无需修改

### 新功能

- ✅ 自动识别 Python 文件
- ✅ 应用 Python 特定的检查规则
- ✅ 在审查报告中包含 Python 检查结果

---

## 🚀 发布信息

- **版本**: v3.1.0
- **发布ID**: k97ab0base37sed2kqk9s7h3a1828h5m
- **发布时间**: 2026-03-04 12:00
- **ClawHub**: https://clawhub.com/skill/cann-review

---

## 🔄 升级指南

### 从 v3.0.x 升级

```bash
# 1. 更新技能
clawhub update cann-review

# 2. 验证更新
clawhub list | grep cann-review
# 输出: cann-review  3.1.0

# 3. 开始使用
# 无需额外配置，直接使用即可
```

### 从 v2.x 升级

```bash
# 1. 更新技能
clawhub update cann-review

# 2. 配置 Token（如果还没配置）
cd ~/.openclaw/workspace/skills/cann-review
./gitcode-api.sh setup

# 3. 验证
./test-api.sh
```

---

## 📚 相关文档

- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **配置指南**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **完整文档**: [README.md](README.md)
- **技能说明**: [SKILL.md](SKILL.md)

---

## 🎁 好处总结

### 对用户

- ✅ **更广泛**：支持 C/C++/Python 三种语言
- ✅ **更专业**：针对不同语言应用特定规则
- ✅ **更全面**：覆盖更多代码质量问题

### 对项目

- ✅ **更灵活**：不限于 runtime 项目
- ✅ **更通用**：适用于各种 CANN 项目
- ✅ **更强大**：多语言支持

---

## 🐛 已知问题

目前没有已知问题。如发现问题请及时反馈。

---

## 🔮 未来计划

1. **支持更多语言**：Go, Rust 等
2. **自定义规则**：允许用户自定义检查规则
3. **代码度量**：代码复杂度、测试覆盖率等
4. **智能建议**：基于历史数据的智能改进建议

---

## 📞 支持

如有问题或建议：
- 📖 查看文档：[README.md](README.md)
- 🧪 运行测试：`./test-api.sh`
- 📝 查看配置：[SETUP_GUIDE.md](SETUP_GUIDE.md)

---

**更新日期**: 2026-03-04
**版本**: v3.1.0
**维护者**: OpenClaw Team
