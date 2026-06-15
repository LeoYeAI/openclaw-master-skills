# API测试分析文档生成器 - 快速开始

## 安装

### 方式1：使用pip安装依赖（推荐）

```bash
cd d:/code/autotestplatformnew/.codebuddy/skills/api-test-create
pip install -r requirements.txt
```

### 方式2：无需安装（基础功能）

如果只需要基本功能（不支持YAML格式），可以直接使用，无需安装任何依赖。

## 快速使用

### 步骤1：准备接口定义

#### 选项A：OpenAPI/Swagger格式（推荐）

创建文件 `api.yaml`：

```yaml
openapi: 3.0.0
info:
  title: 用户管理API
  version: 1.0.0
paths:
  /api/users:
    post:
      summary: 创建用户
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 20
                password:
                  type: string
                  minLength: 6
                  maxLength: 20
                email:
                  type: string
                  format: email
      responses:
        '200':
          description: 成功
```

#### 选项B：简化定义格式

创建文件 `api-simple.md`：

```markdown
接口名称: 创建用户
接口路径: POST /api/users
请求参数:
  - username: string, 必填, 3-20字符
  - password: string, 必填, 6-20字符
  - email: string, 可选, 邮箱格式
业务规则:
  - 用户名必须唯一
  - 邮箱必须唯一
```

### 步骤2：生成测试分析文档

#### 生成单个接口的测试分析

```bash
cd d:/code/autotestplatformnew/.codebuddy/skills/api-test-create/scripts

# 使用OpenAPI格式
python generate-checklist.py --input api.yaml --output test-analysis.md

# 使用简化格式
python generate-checklist.py --input api-simple.md --format simple --output test-analysis.md
```

#### 批量生成（多个接口）

如果你有包含多个接口的OpenAPI文件：

```bash
python generate-checklist.py --input full-api-spec.yaml --output complete-test-analysis.md
```

### 步骤3：查看生成的文档

生成的 `test-analysis.md` 文件将包含：

```markdown
# 用户管理API - API测试分析文档

**生成日期**：2025-03-26 08:30:00
**文档版本**：v1.0

## 详细测试分析

### 创建用户

#### 基本信息
- **接口路径**：POST /api/users
- **接口描述**：创建用户
- **认证**：否

#### 请求参数分析

##### username (string, 必填)
**约束条件**：
- 最小长度：3
- 最大长度：20

**参数校验测试点分析**：

| 测试场景 | 测试值说明 | 预期结果 | 优先级 | 测试目的 |
|----------|------------|----------|--------|----------|
| 正常值-最小长度 | aaa | 成功 | P1 | 验证下边界 |
| 正常值-典型值 | abcde | 成功 | P0 | 验证典型场景 |
| 正常值-最大长度 | a*20 | 成功 | P1 | 验证上边界 |
| 异常值-小于最小长度 | aa | 参数错误 | P1 | 验证越下界 |
| 异常值-超过最大长度 | a*21 | 参数错误 | P1 | 验证越上界 |
| 异常值-null | null | 参数错误 | P0 | 验证必填约束 |
| 安全-SQL注入 | ' OR '1'='1 | 参数错误 | P0 | 验证SQL注入防护 |
| 安全-XSS攻击 | <script>alert(1)</script> | 参数错误 | P0 | 验证XSS防护 |

**风险分析**：🔴 高风险

##### password (string, 必填)
...

#### 业务逻辑测试点分析

| 测试场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 测试目的 |
|----------|----------|----------|----------|--------|----------|
| 正常业务流程 | 数据准备完成 | 执行业务操作 | 业务成功 | P0 | 验证核心功能 |
| 用户名重复 | 用户名已存在 | 创建相同用户 | 业务错误（已存在） | P0 | 验证唯一性约束 |

#### 响应验证测试点分析

**成功响应（2xx）验证**：

| 验证项 | 验证内容 | 优先级 | 验证方法 |
|--------|----------|--------|----------|
| 响应结构 | 包含code, message, data字段 | P0 | 检查JSON结构 |
| 状态码 | 与业务结果匹配（200/201） | P0 | 检查HTTP状态码 |

#### 安全测试点分析

**认证安全**：

| 测试场景 | 测试操作 | 预期结果 | 风险等级 | 测试目的 |
|----------|----------|----------|----------|----------|
| 未认证访问 | 不携带Token调用接口 | 返回401 Unauthorized | 🔴 高 | 验证认证拦截 |
| Token过期 | 使用过期Token | 返回401 | 🔴 高 | 验证Token过期处理 |

#### 性能测试点分析

**响应时间要求**：
- P0接口：< 200ms (95分位)
- P1接口：< 500ms (95分位)

**压力测试场景**：

| 场景 | 并发数 | 持续时间 | 预期结果 | 关注点 |
|------|--------|----------|----------|--------|
| 基准测试 | 1 | 10分钟 | 响应稳定 | 基准响应时间 |
| 负载测试 | 10 | 30分钟 | 成功率>99.9% | 系统负载 |
```

## 命令行参数

### 基本用法

```bash
python generate-checklist.py --input <输入文件> --output <输出文件>
```

### 参数说明

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| --input | -i | 输入文件（必需） | --input api.yaml |
| --output | -o | 输出文件 | --output analysis.md |
| --format | -f | 输入格式：openapi/simple | --format simple |
| --config | -c | 配置文件 | --config config.json |
| --api-name | -n | API名称 | --api-name "用户管理API" |

### 示例

```bash
# 基础用法
python generate-checklist.py -i api.yaml -o analysis.md

# 使用简化格式
python generate-checklist.py -i simple.md -f simple -o analysis.md

# 指定API名称
python generate-checklist.py -i api.yaml -n "订单系统API" -o order-test-analysis.md

# 不指定输出（打印到控制台）
python generate-checklist.py -i api.yaml
```

## 使用场景

### 场景1：为新接口设计测试方案

当你开发新接口时：

1. 编写接口定义（OpenAPI或简化格式）
2. 运行本工具生成测试分析文档
3. 根据文档评审测试点是否完整
4. 补充遗漏的测试场景
5. 将文档作为测试设计依据

### 场景2：评审现有接口测试覆盖

当你需要评审现有接口时：

1. 从代码提取接口定义
2. 运行本工具生成测试分析文档
3. 对比现有测试用例
4. 识别遗漏的测试点
5. 完善测试用例集

### 场景3：生成测试方案文档

当你需要输出测试方案时：

1. 准备完整接口定义
2. 运行本工具生成测试分析文档
3. 补充业务背景和风险分析
4. 作为测试方案交付物
5. 与团队评审确认

## 输出说明

### 文档结构

生成的Markdown文档包含：

1. **文档信息**：生成日期、版本
2. **接口清单**：所有接口的概览
3. **详细测试分析**：
   - 接口基本信息
   - 请求参数分析（每个参数）
   - 业务逻辑测试点
   - 响应验证测试点
   - 安全测试点
   - 性能测试点
4. **测试执行建议**：执行顺序、优先级
5. **风险分析**：高风险接口识别

### 优先级说明

- **P0（Critical）**：核心功能，必须测试
- **P1（High）**：重要功能，建议测试
- **P2（Medium）**：一般功能，选择测试
- **P3（Low）**：次要功能，可延后测试

## 高级配置

### 自定义优先级规则

创建 `config.json`：

```json
{
  "priority_rules": {
    "required_missing": "P0",
    "sql_injection": "P0",
    "xss": "P0",
    "authorization": "P0",
    "boundary_normal": "P1",
    "boundary_invalid": "P1",
    "optional": "P2"
  }
}
```

使用配置：

```bash
python generate-checklist.py -i api.yaml -c config.json -o analysis.md
```

## 最佳实践

### 1. 接口定义要清晰
- 明确参数类型、约束、必填项
- 添加详细的描述信息
- 包含业务规则说明

### 2. 定期更新分析文档
- 接口变更后重新生成
- 补充遗漏的测试点
- 更新风险分析

### 3. 结合团队评审
- 生成文档后团队评审
- 补充业务特定场景
- 确认测试优先级

### 4. 作为测试依据
- 基于文档设计测试用例
- 确保测试点全覆盖
- 跟踪测试执行情况

## 常见问题

### Q1: 支持哪些输入格式？

**A**: 支持OpenAPI/Swagger（JSON/YAML）和简化定义格式（Markdown）。

### Q2: 是否需要安装依赖？

**A**: 基础功能无需安装，如需支持YAML格式，需安装PyYAML。

### Q3: 如何生成多个接口的测试分析？

**A**: 在OpenAPI文件中定义所有接口，工具会生成完整的测试分析文档。

### Q4: 如何自定义测试点？

**A**: 当前版本不支持自定义测试点，可以手动编辑生成的文档进行补充。

### Q5: 文档生成后如何使用？

**A**: 作为测试设计依据，评审测试覆盖，指导测试执行，补充到测试方案中。

## 技术支持

如遇到问题：

1. 查看日志输出
2. 检查输入文件格式
3. 验证参数配置
4. 参考examples目录示例

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.5.0 | 2025-03-26 | 简化功能，专注测试分析文档生成 |
| v0.4.1 | 2025-03-26 | 完整测试用例生成 |

---

**说明**：本工具专注于生成详细的API测试分析文档，帮助测试人员设计全面的测试方案。生成的文档需要结合业务实际进行评审和补充。
