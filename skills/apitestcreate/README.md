# API测试生成器

**版本**: 0.4.1
**类别**: 测试工具
**标签**: api, testing, openapi, swagger, create, automation

## 简介

API测试检查单生成器是一个根据接口规格自动生成全面测试点的工具。输入接口文档（支持OpenAPI/Swagger、简化定义或自然语言描述），自动输出结构化的测试用例清单，覆盖参数校验、业务逻辑、响应验证和常见陷阱。

## 特性

- 🤖 **智能解析**: 支持OpenAPI/Swagger、YAML/JSON、自然语言输入
- 📋 **全面覆盖**: 自动生成6大类测试点（参数、业务、响应、安全、性能、兼容性）
- 🎯 **优先级标注**: 测试点按P0/P1/P2分级
- ⚠️ **高频陷阱**: 内置100个高频易错点自动对照
- 📊 **统计报告**: 自动生成测试点数量统计

## 目录结构

```
api-test-checklist/
├── README.md                    # 本说明文档
├── SKILL.md                     # 主技能文件（Claude使用）
├── _meta.json                   # 元数据
├── scripts/                     # 可执行脚本
│   ├── generate-checklist.py    # 核心生成器
│   ├── validate-openapi.py      # OpenAPI验证工具
│   └── utils.py                 # 工具函数
├── references/                  # 参考文档
│   ├── test-case-design.md      # 测试用例设计方法
│   └── common-pitfalls.md       # 100个高频易错点
└── examples/                    # 示例
    ├── openapi-example.yaml     # OpenAPI示例
    └── simple-example.md        # 简化定义示例
```

## 快速开始

### 方式1：使用Claude Skill

直接告诉Claude你的接口定义：

```
我有以下接口，请生成测试检查单：
POST /api/users
参数：
  - username: string, 必填, 3-20字符
  - email: string, 必填, 邮箱格式
```

### 方式2：使用脚本生成

```bash
# 安装依赖
pip install -r requirements.txt

# 生成测试清单
python scripts/generate-checklist.py \
  --input examples/openapi-example.yaml \
  --output output/checklist.md

# 支持多种格式
python scripts/generate-checklist.py \
  --input "接口: POST /api/login 参数: username(string,必填) password(string,必填)" \
  --format text
```

### 方式3：编程调用

```python
from scripts.generate_checklist import APITestGenerator

# 初始化生成器
generator = APITestGenerator()

# 解析OpenAPI
api_spec = """
openapi: 3.0.0
paths:
  /api/users:
    post:
      summary: 创建用户
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 20
"""

# 生成测试清单
checklist = generator.generate_from_openapi(api_spec)
print(checklist)
```

## 输入格式支持

### 1. OpenAPI/Swagger

支持OpenAPI 3.0和Swagger 2.0规范。

**示例**: `examples/openapi-example.yaml`

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
                - email
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 20
                email:
                  type: string
                  format: email
```

### 2. 简化接口定义

```
接口名称: 创建用户
接口路径: POST /api/users
请求参数:
  - username: string, 必填, 3-20字符
  - email: string, 必填, 邮箱格式
  - age: integer, 可选, 0-150
返回字段:
  - id: integer
  - username: string
  - email: string
业务规则:
  - 用户名不能重复
  - 邮箱不能重复
```

### 3. 自然语言描述

```
登录接口：
- 路径：POST /api/auth/login
- 参数：用户名（必填，手机号或邮箱）、密码（必填，6-20位）
- 返回：token、用户信息
- 规则：密码错误5次锁定账号30分钟
```

## 输出格式

生成结构化的Markdown格式测试清单：

```markdown
## 接口：用户注册

### 基本信息
- 接口路径：POST /api/users/register
- 接口描述：用户注册接口

### 参数校验测试点

#### 1. username (string, 必填, 3-20字符)
| 测试场景 | 测试值 | 预期结果 | 优先级 |
|----------|--------|----------|--------|
| 正常值 | "testuser" | 成功 | P0 |
| 边界值-最小 | "abc" | 成功 | P1 |
| 边界值-最大 | "a"*20 | 成功 | P1 |
| 空值 | null/"" | 参数错误 | P0 |
| 特殊字符 | "<script>" | 参数错误 | P1 |

### 业务逻辑测试点
| 测试场景 | 前置条件 | 操作 | 预期结果 | 优先级 |
|----------|----------|------|----------|--------|
| 正常注册 | 无 | 提交有效数据 | 注册成功 | P0 |
| 用户名重复 | 用户已存在 | 相同用户名注册 | 返回已存在 | P0 |

### 安全测试点
| 测试场景 | 测试值 | 预期结果 | 优先级 |
|----------|------------|-----------------|----------|
| SQL注入 | "admin'--" | 参数错误 | P0 |

### 统计
- 参数校验：25个测试点
- 业务逻辑：6个测试点
- **总计：31个测试点**
```

## 测试点覆盖范围

### 1. 参数校验（自动生成）

| 参数类型 | 测试场景 |
|----------|----------|
| string | 长度边界、特殊字符、SQL注入、XSS、Unicode、格式校验 |
| integer | 取值范围、边界值、零值、负数、溢出、类型转换 |
| number | 精度、科学计数法、范围 |
| enum | 所有枚举值、无效值、大小写、null |
| boolean | true/false、字符串转换、数字转换 |
| array | 空数组、元素数量、重复元素、无效元素 |
| object | 完整对象、缺少必填、额外字段 |
| datetime | 有效日期、无效日期、格式、时区、闰年 |

### 2. 业务逻辑（按规则生成）

- 存在性校验（数据存在/不存在/已删除）
- 唯一性校验（重复数据）
- 状态转换校验（合法/非法转换）
- 权限校验（有权限/无权限/未登录）
- 关联校验（外键存在性）
- 数量限制（上限/下限）

### 3. 响应校验

- 结构完整性（code, message, data）
- 字段类型正确性
- 分页信息准确性
- 空结果处理（返回[]或null）

### 4. 安全测试

- SQL注入攻击
- XSS跨站脚本
- 认证绕过
- 越权访问
- 暴力破解

### 5. 性能测试建议

- 响应时间阈值
- 并发访问测试
- 大页码查询
- 批量操作限制

### 6. 兼容性测试

- 不同浏览器/客户端
- 不同环境（测试/生产）
- 不同版本共存

## 140个高频易错点

内置140个高频易错点自动对照，覆盖7大维度：

1. **请求层规范**（15项）：请求方法、请求头、协议、超时、编码
2. **参数处理**（30项）：必选/可选参数、格式类型、长度边界
3. **响应结果**（20项）：状态码、字段完整性、业务数据正确性
4. **业务逻辑**（15项）：幂等性、权限、状态流转、关联数据
5. **性能并发**（10项）：高并发、响应时间、资源占用、缓存
6. **安全兼容**（10项）：注入攻击、敏感数据、跨平台兼容
7. **补充测试项**（40项）：
   - **通用信息校验**（10项）：URL、请求方法、请求头、接口鉴权
   - **接口参数详细校验**（18项）：必填、选填、长度、类型、有效性、唯一性、关联项
   - **其他补充项**（12项）：幂等性、弱网环境、分布式、接口风格、敏感信息加密

详细清单见 `references/common-pitfalls.md`

## 进阶功能

### 自定义规则

创建 `config.json` 自定义测试规则：

```json
{
  "priority_rules": {
    "min_length": "P1",
    "sql_injection": "P0",
    "xss": "P0"
  },
  "custom_validators": {
    "phone_number": "^1[3-9]\\d{9}$",
    "id_card": "^[1-9]\\d{5}(18|19|20)\\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\\d{3}[0-9Xx]$"
  }
}
```

### 批量生成

```bash
# 批量处理多个接口
python scripts/generate-checklist.py \
  --input ./apis/*.yaml \
  --output ./output/ \
  --batch

# 生成测试代码
python scripts/generate-checklist.py \
  --input api-spec.yaml \
  --with-test-code \
  --framework pytest
```

## 开发与扩展

### 添加新参数类型

编辑 `scripts/utils.py`：

```python
# 在PARAM_TYPE_HANDLERS中添加新的处理器
def handle_custom_type(param_name, constraints):
    return [
        {"scenario": "正常值", "value": "valid_value", "expected": "success", "priority": "P0"},
        # ... 更多测试点
    ]
```

### 添加自定义业务规则

编辑 `scripts/generate-checklist.py`：

```python
# 在BUSINESS_RULE_PATTERNS中添加新规则
"custom_rule": {
    "pattern": r"必须包含(\\w+)",
    "generator": generate_custom_rule_tests
}
```

## 测试

```bash
# 运行单元测试
python -m pytest tests/

# 测试覆盖率
pytest --cov=scripts tests/

# 集成测试
python tests/integration_test.py
```

## 常见问题

### Q: 如何处理非标准的接口定义？
A: 使用 `--format text` 参数，提供自然语言描述

### Q: 如何自定义测试优先级？
A: 编辑 `config.json` 修改priority_rules

### Q: 支持哪些OpenAPI版本？
A: 支持OpenAPI 3.0和Swagger 2.0

### Q: 生成的测试点太多怎么办？
A: 使用 `--priority P0,P1` 参数只生成高优先级测试点

## 贡献

欢迎提交PR和Issue！

## 许可证

MIT License

## 更新日志

### v0.3.0 (2026-03-25)
- ✅ 添加可执行workflow脚本
- ✅ 统一使用中文文档
- ✅ 完善元数据信息
- ✅ 添加README.md
- ✅ 完善错误处理示例
- ✅ 添加单元测试

### v0.2.0 (2026-03-25)
- 添加100个高频易错点
- 优化输出格式
- 添加统计报告

### v0.1.0 (2026-03-25)
- 初始版本
- 基础测试点生成
- 支持OpenAPI/Swagger
