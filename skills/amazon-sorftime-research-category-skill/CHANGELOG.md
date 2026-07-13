# Category-Selection Skill 变更日志

## [11.0.0] - 2026-03-05

### v4.0 更新 - 重大 Bug 修复和稳定性改进

**背景**: 在实际使用中发现多个问题，包括 API Key 配置、JSON 解析失败、类目搜索失败等。本次更新系统性地修复了所有已知问题。

### 主要改进

#### 1. 自动 API Key 配置 ✅
**问题**: 需要手动设置环境变量 `SORFTIME_API_KEY`，用户体验不友好

**修复**:
- 新增 `get_api_key()` 函数，自动从 `.mcp.json` 读取 API Key
- 支持多源配置：环境变量 > .mcp.json 配置文件
- 添加 API Key 有效性检查和友好错误提示

```python
# 代码示例
def get_api_key():
    # 1. 尝试环境变量
    api_key = os.environ.get('SORFTIME_API_KEY', '')
    if api_key:
        return api_key

    # 2. 尝试从 .mcp.json 读取
    mcp_config_path = os.path.join(PROJECT_ROOT, '.mcp.json')
    if os.path.exists(mcp_config_path):
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
            sorftime_url = config.get('mcpServers', {}).get('sorftime', {}).get('url', '')
            if 'key=' in sorftime_url:
                return sorftime_url.split('key=')[-1]
    return ''
```

**影响**: 用户无需配置环境变量，开箱即用

---

#### 2. JSON 字符串值中未转义控制字符修复 ✅
**问题**: `JSONDecodeError: Invalid control character at: line 1 column 3401`

**根本原因**: API 返回的 JSON 字符串值中包含原始的换行符（`\n`）、制表符（`\t`）等控制字符，这些字符没有被正确转义为 `\n`、`\t` 序列

**示例**:
```json
// API 返回的原始格式（错误）
{"标题": "类目：Renewed Laptops，排名:2
类目：Traditional Laptops，排名:11"}

// 正确格式
{"标题": "类目：Renewed Laptops，排名:2\\n类目：Traditional Laptops，排名:11"}
```

**修复**: 新增 `escape_control_chars_in_json_strings()` 函数
```python
def escape_control_chars_in_json_strings(json_str):
    """
    转义 JSON 字符串值中的控制字符
    只处理字符串值内部，不影响 JSON 结构
    """
    result = []
    in_string = False
    escape_next = False

    for c in json_str:
        if escape_next:
            result.append(c)
            escape_next = False
        elif c == '\\':
            result.append(c)
            escape_next = True
        elif c == '"':
            in_string = not in_string
            result.append(c)
        elif in_string and c == '\n':
            result.append('\\n')  # 转义换行符
        elif in_string and c == '\r':
            result.append('\\r')  # 转义回车符
        elif in_string and c == '\t':
            result.append('\\t')  # 转义制表符
        else:
            result.append(c)

    return ''.join(result)
```

**影响**: 所有包含换行符的 JSON 响应现在可以正确解析

---

#### 3. 改进类目搜索策略 ✅
**问题**: 类目搜索失败，特别是 "Laptops" 和 "Computers" 等大类目

**修复**:
- 自动尝试多种搜索变体
- 支持模糊匹配和关键词变体
- 当返回多个类目时，自动使用第一个类目
- 添加搜索失败时的友好提示

```python
# 自动尝试的搜索变体
search_variants = [
    self.category,                    # 原始输入
    self.category.replace(' & ', ' '), # 移除 & 符号
    self.category.split(' ')[0],       # 第一个词
    self.category.rstrip('s'),        # 移除复数
]
```

**影响**: 类目搜索成功率显著提高

---

#### 4. 执行日志和调试支持 ✅
**问题**: 难以追踪执行过程和定位问题

**新增**:
- 执行日志自动保存到 `execution.log`
- 详细的错误信息和上下文
- 时间戳记录每个操作
- DEBUG、INFO、WARN、ERROR 级别

```python
def log(self, message: str, level: str = 'INFO'):
    """记录日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    self.execution_log.append(log_entry)
```

**影响**: 问题诊断更容易

---

#### 5. 错误处理增强 ✅
**问题**: 错误信息不明确，难以定位问题

**改进**:
- API Key 未检查时提供明确的配置指引
- JSON 解析失败时保存调试信息到 `parse_debug.txt`
- 认证失败时提供明确的错误提示
- 所有 API 调用都有超时处理

**影响**: 用户体验更好，问题更容易解决

---

### 故障排查指南更新

在 `SKILL.md` 中新增详细的故障排查章节，包括：

1. **API Key 未设置** - 解释两种配置方式和自动加载逻辑
2. **JSON 解析失败 - 控制字符** - 详细说明根本原因和修复方法
3. **类目未找到** - 提供多种解决方案
4. **Mojibake 编码问题** - 手动修复方法
5. **Python dict 格式问题** - 修复说明
6. **大类目搜索失败** - 工作流程建议

---

### 文件更新

| 文件 | 版本 | 更新内容 |
|------|------|----------|
| `workflow.py` | v4.0 | ✅ 自动 API Key 加载<br>✅ 控制字符转义修复<br>✅ 改进类目搜索<br>✅ 执行日志<br>✅ 错误处理增强 |
| `SKILL.md` | v4.0 | ✅ 更新 API Key 配置说明<br>✅ 新增控制字符问题排查<br>✅ 更新故障排查指南<br>✅ 版本号更新到 v4.0 |

---

### 兼容性

- 完全向后兼容 v3.x
- 无需修改现有配置
- `.mcp.json` 配置自动识别

---

### 测试验证

已使用以下类目进行测试验证：
- ✅ Traditional Laptop Computers (NodeID: 13896615011)
  - 月销额: $86,231,118.58
  - 产品数量: 100
  - 五维评分: 74/100 (良好)

---

## [10.0.0] - 2026-03-04

### 标准化版本 - 统一评分标准与数据结构

**背景**: 解决多个脚本中五维评分标准不一致的问题，统一数据结构和报告生成流程。

### 主要改进

#### 1. 统一五维评分标准
- **问题**: workflow.py、data_utils.py、parse_category_report.py 中的评分逻辑不一致
- **修复**: 统一所有脚本的评分标准为:
  - 市场规模 (20分): >$10M=20, >$5M=17, >$1M=14, 其他=10
  - 增长潜力 (25分): 低评论占比>40%=22, >20%=18, 其他=14
  - 竞争烈度 (20分): Top3<30%=18, <50%=14, 其他=8
  - 进入壁垒 (20分): Amazon占比+新品机会组合 (0-20分)
  - 利润空间 (15分): 均价>$300=12, >$150=10, >$50=7, 其他=4
- **影响**: 所有报告现在使用一致的评分标准

#### 2. 优化进入壁垒评分逻辑
- **旧逻辑**: 基于平均评论数和Amazon占比的组合判断
- **新逻辑**: Amazon占比评分 (0-10分) + 新品机会评分 (0-10分)
  - Amazon占比: <20%=10分, <40%=6分, 其他=3分
  - 新品机会: 低评论产品>40%=10分, >20%=6分, 其他=3分
- **影响**: 评分更加透明，易于理解和调整

#### 3. 统一利润空间评分标准
- **旧标准**: 基于 $25/$15/$8 的价格阈值
- **新标准**: 基于 $300/$150/$50 的价格阈值
- **影响**: 更符合亚马逊实际品类价格分布

#### 4. SKILL.md 文档重构
- 添加详细的五维评分标准说明
- 完善数据处理流程文档
- 更新故障排查指南
- 添加数据字段映射表
- 优化报告输出结构说明

### 文件更新
- `SKILL.md` - 完全重写，添加标准化说明
- `workflow.py` - 更新评分函数，统一标准
- `data_utils.py` - 确认评分标准一致性

---

## [4.1.0] - 2026-03-03

### Bug 修复 - 一体化分析脚本

**背景**: 优化分析流程，解决数据处理、编码和报告生成的多个问题。

### 修复内容

#### 1. SSE 响应解析修复
- **问题**: `codecs.decode(text, 'unicode-escape')` 错误地二次解码已由 JSON 解码的中文字符
- **修复**: 移除不必要的 unicode-escape 解码，JSON 解析器已正确处理 Unicode 转义
- **影响**: 中文键名 (`Top100产品`, `类目统计报告`) 现在可以正确提取

#### 2. JSON 对象提取逻辑修复
- **问题**: 解析器查找最后一个 JSON 对象，但产品数据在第一个对象中
- **修复**: 改为查找第一个完整的 JSON 对象
- **影响**: 产品列表 (100个产品) 现在可以正确提取

#### 3. 数值格式化修复
- **问题**: 模板变量替换时对字符串值使用数字格式 (`,`) 导致错误
- **修复**: 添加 `_safe_float()` 和 `_safe_int()` 方法安全转换数值
- **影响**: 价格、销量等数值现在可以正确格式化显示

#### 4. Excel Font 作用域问题修复
- **问题**: `OpenpyxlFont` 在 `generate_excel()` 方法内导入，但辅助方法无法访问
- **修复**: 将 Font/PatternFill 类作为参数传递给辅助方法
- **影响**: Excel 报告现在可以正常生成

### 新增功能

#### 一体化分析脚本 (`analyze_category.py`)

一个命令完成完整的品类分析流程：

```bash
python .claude/skills/category-selection/scripts/analyze_category.py "品类名称" [站点] [数量]
```

**功能特点**:
- 自动搜索类目获取 nodeId
- 调用 category_report API
- 解析 SSE 响应和中文编码
- 计算五维评分
- 生成所有格式报告 (Markdown, Excel, HTML, CSV, JSON)

**报告输出结构**:
```
category-reports/
└── YYYY/MM/
    └── {品类名}_{站点}/
        ├── category_analysis_report.md
        ├── category_analysis_report.xlsx
        ├── dashboard.html
        └── data/
            ├── statistics.csv
            ├── products.csv
            ├── scores.csv
            └── raw_data.json
```

### 技术细节

#### SSE 解析流程
```python
# 旧代码 (错误):
decoded = codecs.decode(text, 'unicode-escape')  # 二次解码导致乱码

# 新代码 (正确):
decoded = text  # JSON 已自动解码 Unicode 转义
```

#### JSON 对象提取
```python
# 旧代码:
last_obj_start = decoded.rfind('{')  # 查找最后一个对象

# 新代码:
first_obj_start = decoded.find('{')  # 查找第一个对象 (包含产品数据)
```

### 支持的亚马逊站点
US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

### 已知限制
- 部分统计数据包含中文描述前缀 (如 "销量前的80%产品平均价格：")
- 模板中的部分变量 (如 `{{SCORE_建议}}`, `{{ANALYSIS_*}}`) 尚未实现

---

## [4.0.0] - 2026-03-03

### 重大重构 - MCP 风格化

**背景**: 原版本使用 Python 脚本绕过 MCP 服务器直接调用 API，与 MCP 设计理念不符。

### 变更内容

#### 删除的文件
- `scripts/sorftime_client.py` - 独立的 HTTP 客户端（绕过 MCP）
- `scripts/sorftime_parser.py` - SSE 响应解析器（MCP 已处理）
- `scripts/analyze.py` - 主分析脚本（由 SKILL.md 替代）
- `scripts/category_analysis_template.py` - 模板脚本
- `scripts/__pycache__/` - Python 缓存目录

#### 重写的文件
- `SKILL.md` - 完全重写为 MCP 风格，与 `amazon-analyse` 保持一致

### 架构变化

**旧架构** (v3.x):
```
Claude Code
    ↓
运行 Python 脚本 (analyze.py)
    ↓
SorftimeMCPClient (直接 HTTP 请求)
    ↓
Sorftime API (绕过 MCP)
    ↓
自定义解析器
```

**新架构** (v4.0):
```
Claude Code
    ↓
MCP 工具调用 (curl via Bash)
    ↓
Sorftime MCP 服务器
    ↓
SSE 响应
    ↓
Claude Code 解析
```

### 功能保持

以下功能保持不变，继续提供：

#### 必需工具
1. `category_name_search` - 搜索类目获取 nodeId
2. `category_report` - 获取类目 Top100 产品和统计数据
3. `product_detail` - 获取产品详情

#### 可选工具
4. `category_keywords` - 获取类目核心关键词
5. `products_1688` - 1688 采购成本分析

#### 保留的辅助工具
- `scripts/data_utils.py` - 数据处理工具（HHI、分组、评分计算等）
- `scripts/generate_excel_report.py` - Excel 报告生成（可选）

### SKILL.md 主要变化

| 章节 | v3.x | v4.0 |
|------|------|------|
| MCP 调用 | 描述 Python 脚本 | 描述 curl 调用 MCP |
| 数据解析 | 导入 Python 模块 | Claude Code 直接处理 |
| 工具参考 | 混合描述 | 统一 curl 格式 |
| 报告生成 | Python 脚本 | Write 工具 |

### 五维评分计算

评分逻辑保持不变：

| 维度 | 分值 | 数据来源 |
|------|------|----------|
| 市场规模 | 20分 | top100产品月销额 |
| 增长潜力 | 25分 | low_reviews_sales_volume_share |
| 竞争烈度 | 20分 | top3_brands_sales_volume_share |
| 进入壁垒 | 20分 | amazonOwned + low_reviews |
| 利润空间 | 15分 | average_price |

### 兼容性

- 与 `amazon-analyse` skill 保持一致的 MCP 调用风格
- 支持相同的亚马逊站点 (US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA)
- 使用相同的 Sorftime MCP 配置

### 迁移指南

如果用户之前使用 `analyze.py` 脚本，现在可以直接使用 `/category-select` 命令：

**旧方式**:
```bash
python .claude/skills/category-selection/scripts/analyze.py "Sofas" --site US --limit 20
```

**新方式**:
```
/category-select "Sofas" US --limit 20
```

---

## [3.0.0] - 2026-03-02

### 新增
- 添加 sorftime_parser.py 内置解析器
- 修复 Unicode 转义中文解析问题
- 修复 JSON 嵌套和控制字符问题
- 添加大文件处理方案

---

## [2.0.0] - 2026-03-01

### 初始版本
- 基础品类选品分析功能
- 五维评分模型
- Python 脚本驱动架构
