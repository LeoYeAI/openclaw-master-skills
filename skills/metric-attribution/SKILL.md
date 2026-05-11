---
name: metric-attribution
description: |
  对指标波动进行综合归因诊断，定位导致指标变化的关键因子、维度和外部事件。当用户需要分析指标波动原因、定位指标变化的根因、做因子拆解归因（如 GMV = UV × 转化率 × 客单价）、或理解指标为什么涨跌时，必须使用此 Skill。
  触发场景包括但不限于：用户提到"归因""归因分析""波动分析""波动归因""根因分析""根因""下钻分析""下钻归因""为什么涨了""为什么跌了""为什么下降""为什么增长""什么原因""哪个维度导致""贡献度分析""贡献度""因子拆解""因子分解""驱动因素""影响因素""变化原因""差异分析"，或用户对某个指标的变化表达了疑问、希望了解变化背后的原因时，都应使用此 Skill。
  即使用户没有直接说"归因"二字，只要其意图是理解指标变化的原因或定位问题维度，也应触发此 Skill。
  **重要：本 Skill 通过组合调用 Gateway API 获取指标数据，在本地进行归因计算，结合外部事件检索，最终输出综合归因诊断报告。构建查询前，必须先通过 Gateway API 检索相关指标和维度信息，禁止凭记忆猜测指标名或维度名。**
permissions:
  - env:read 
  - network:outbound 
env_vars:
  - name: "CAN_API_KEY"
    description: "Aloudata CAN网关API访问密钥，需用户自行在~/.openclaw/.env中配置"
    required: true
domain_whitelist:
  - "gateway.can.aloudata.com" 
version: "1.0.4"
author: "Aloudata"
homepage: "https://aloudata.com/"
metadata.openclaw: {"emoji": "🔍"}
---

# 指标波动归因诊断 Skill

归因分析的核心目标是回答"指标为什么变了"。这不是单一步骤能完成的任务——它是一个**诊断流程**，需要综合运用多种分析手段，最终汇聚为一个完整的归因结论。

诊断遵循"先定性再定位再找因"的逻辑：先搞清楚变了多少（Step 1），再拆解是哪个业务环节出了问题（Step 2），然后定位到具体的维度和维度值（Step 3），接着关联外部事件寻找根因（Step 4），最后综合所有发现给出结论（Step 5）。

```
┌───────────────────────────────────────────────────────────────┐
│                     归因诊断全流程                              │
│                                                               │
│  Step 1  确认波动事实 → 变了多少？跟什么比？                     │
│     ↓                                                         │
│  Step 2  因子拆解 → 哪个业务环节出了问题？（定性）               │
│     ↓                                                         │
│  Step 3  维度归因 → 问题环节在哪些维度上集中？（定位）            │
│     ↓         ↘ 发现集中点 → 继续下钻到更细维度                  │
│  Step 4  外部事件关联 → 天气？节假日？竞对？行业政策？（找因）     │
│     ↓                                                         │
│  Step 5  综合诊断结论 → 汇总所有发现，输出归因报告                │
│                                                               │
│  * 并非每次都需走完全部步骤，根据复杂度灵活调整                    │
│  * 每步的发现逐步积累，最终在 Step 5 统一收口                    │
└───────────────────────────────────────────────────────────────┘
```

**为什么先因子拆解（Step 2）再维度归因（Step 3）？**

因子拆解回答的是"哪个环节坏了"（流量？转化？客单价？），维度归因回答的是"在哪里坏了"（哪个渠道？哪个地区？）。先知道是哪个环节出了问题，维度归因才有方向——不用对着总指标盲扫所有维度，而是针对问题因子精准下钻。

举例：GMV 下降 10%。如果直接做维度归因，你可能发现"Retail 渠道贡献了 70% 的下降"，但还是不知道 Retail 是流量少了还是转化差了。如果先做因子拆解，发现"转化率下降是主因"，再对转化率做维度归因，直接就定位到"Retail 渠道的转化率环比降了 18%"。每一步都在收窄范围，效率高得多。

当然，如果指标没有明确的业务公式可以拆解（Step 2 不适用），直接跳到 Step 3 做维度归因即可。

---

## 0. 接口信息（复用 Gateway API）

本 Skill 复用 metric-query 的 Gateway API 体系。所有 API 调用规则与 metric-query 完全一致。

### Gateway 搜索 API（检索指标和维度）

**搜索指标**: GET `https://gateway.can.aloudata.com/api/metrics/search?keyword={关键词,可逗号分隔}&pageSize={数量}`
**单指标维度**: GET `https://gateway.can.aloudata.com/api/metrics/{metricName}/dimensions?keyword={可选过滤词,支持逗号分隔多关键词}`
**批量指标维度**: GET `https://gateway.can.aloudata.com/api/metrics/dimensions?metricNames={指标1,指标2}&keyword={可选过滤词,支持逗号分隔多关键词}`

**认证方式**：所有请求必须携带 API Key，通过请求头 `X-API-Key` 传递（也可通过 `?apikey=` 查询参数传递）。未携带或无效 Key 将返回 401。

**调用铁律**：
1. **所有请求必须加 API Key 认证头 `-H "X-API-Key: $CAN_API_KEY"`**，`$CAN_API_KEY` 从环境变量读取（用户需在 `~/.openclaw/.env` 中配置 `CAN_API_KEY=cgk-xxxxxxxx`）
2. URL 中文参数必须 URL 编码，使用 `--data-urlencode` + `-G`

> 示例：
> ```bash
> curl -H "X-API-Key: $CAN_API_KEY" "https://gateway.can.aloudata.com/api/metrics/search?pageSize=5" --data-urlencode "keyword=销售额" -G
> curl -H "X-API-Key: $CAN_API_KEY" "https://gateway.can.aloudata.com/api/metrics/retail_amt/dimensions"
> # 维度多关键词过滤（逗号分隔，匹配任一即返回，匹配范围包括维度名/展示名/描述/维度值样本）
> curl -H "X-API-Key: $CAN_API_KEY" "https://gateway.can.aloudata.com/api/metrics/retail_amt/dimensions" --data-urlencode "keyword=渠道,地区,品牌" -G
> ```

### 指标查询 API（执行数据查询）

**接口**: POST `https://gateway.can.aloudata.com/api/metrics/query`

用 heredoc 传 JSON body（因 timeConstraint 含单引号，禁止用 `-d '...'`）：
```bash
curl -X POST "https://gateway.can.aloudata.com/api/metrics/query" \
  -H "X-API-Key: $CAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{JSON请求体}
EOF
```

**请求体格式与 metric-query 完全一致**，遵守 metric-query Skill 的全部 9 条铁律和构建规范（包括 NOW() 使用、metricDefinitions 注册、占比/排名陷阱、heredoc 传参等）。

---

## Step 1：确认波动事实

归因的起点是搞清楚"到底变了多少"和"跟什么比"。基准选错，后面全白做。

### 1.1 确定对比基准

| 用户说 | 对比基准 | 实现方式 |
|-------|---------|---------|
| "环比下降了""跟上月比" | 上一周期 | `__sameperiod__mom__` 系列 |
| "同比下降了""跟去年比" | 去年同期 | `__sameperiod__yoy__` 系列 |
| "跟目标差多少""没达标" | 目标值 | 需用户提供目标值，或从系统获取 |
| "为什么降了"（未说基准） | **默认环比** | 推断后与用户确认；若涉及季节性行业，建议同比 |

**当用户未明确基准时**：不要直接假设，先向用户确认。例如："您说的下降是跟上个月比（环比），还是跟去年同期比（同比）？如果这个行业有明显的季节性，建议用同比来排除季节因素。"

### 1.2 查询总体变化量

通过 Gateway 检索指标后，先查整体变化：

```bash
# 搜索指标
curl -H "X-API-Key: $CAN_API_KEY" "https://gateway.can.aloudata.com/api/metrics/search?pageSize=5" --data-urlencode "keyword=销售额" -G

# 查整体环比变化
curl -X POST "https://gateway.can.aloudata.com/api/metrics/query" \
  -H "X-API-Key: $CAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
    "metrics": ["retail_amt", "retail_amt__sameperiod__mom__value", "retail_amt__sameperiod__mom__growthvalue", "retail_amt__sameperiod__mom__growth"],
    "timeConstraint": "DateTrunc(['metric_time'], \"MONTH\") = DATEADD(DateTrunc(NOW(), \"MONTH\"), -1, \"MONTH\")"
}
EOF
```

产出：**明确的数字事实**——指标从 X 变到了 Y，变化了 Z（变化率 W%）。后续分析都基于此展开。

### 1.3 观察时间趋势（可选但推荐）

查近几个月趋势，判断是异常波动还是持续趋势：

```json
{
    "metrics": ["retail_amt"],
    "dimensions": ["metric_time__month"],
    "timeConstraint": "DateTrunc(['metric_time'], \"MONTH\") >= DATEADD(DateTrunc(NOW(), \"MONTH\"), -6, \"MONTH\") AND DateTrunc(['metric_time'], \"MONTH\") < DateTrunc(NOW(), \"MONTH\")",
    "orders": [{"metric_time__month": "asc"}]
}
```

---

## Step 2：因子拆解（定性——哪个业务环节出了问题）

先弄清楚"是哪个环节坏了"，后续的维度归因才有靶子。

### 2.1 判断是否适用

因子拆解的前提是指标有明确的业务公式。**如果有公式，必须先做这一步**；如果没有，直接跳到 Step 3。

**常见拆解公式**：

| 复合指标 | 拆解公式 | 因子含义 |
|---------|---------|---------|
| GMV / 销售额 | UV × 转化率 × 客单价 | 流量 × 转化 × 价格 |
| 销售额 | 购买人数 × 客单价 | 客数 × 价格 |
| 销售额 | 订单数 × 件单价 × 连带率 | 订单量 × 价格 × 购买深度 |
| 利润 | 收入 - 成本 | 收入端 vs 成本端 |

如果用户没有明确给出公式，根据业务常识推断并与用户确认。例如用户问"GMV 为什么降了"，可以主动提议："我来按 UV × 转化率 × 客单价 拆解看看是哪个环节的问题？"

### 2.2 获取因子数据

通过 Gateway 搜索各因子对应的指标，然后查询当期和基准期的值：

```bash
# 搜索相关因子指标
curl -H "X-API-Key: $CAN_API_KEY" "https://gateway.can.aloudata.com/api/metrics/search?pageSize=10" --data-urlencode "keyword=UV,转化率,客单价,购买人数" -G
```

```json
{
    "metrics": ["visitor_cnt", "buyer_cnt", "AOV",
                "visitor_cnt__sameperiod__mom__value",
                "buyer_cnt__sameperiod__mom__value",
                "AOV__sameperiod__mom__value"],
    "timeConstraint": "DateTrunc(['metric_time'], \"MONTH\") = DATEADD(DateTrunc(NOW(), \"MONTH\"), -1, \"MONTH\")"
}
```

如果某些因子没有直接对应的指标，用 metricDefinitions + expr 计算：
```json
"metricDefinitions": {
    "cvr": { "expr": "[buyer_cnt]/[visitor_cnt]" }
}
```

### 2.3 计算因子贡献

**乘法公式 Y = A × B × C**：

当各因子变化率较小（均 < 20%）时，可用近似法：
```
ΔY% ≈ ΔA% + ΔB% + ΔC% + 交叉项
A 对 Y 的贡献 ≈ ΔA% / ΔY%
```

当变化率较大时，使用 **Shapley 值分解**确保精确性：

```python
import itertools, math

def shapley_decomposition(factors_base, factors_current):
    """
    factors_base: dict, 如 {"UV": 10000, "CVR": 0.05, "AOV": 200}
    factors_current: dict, 如 {"UV": 12000, "CVR": 0.045, "AOV": 210}
    返回各因子对总变化量的 Shapley 贡献
    """
    factor_names = list(factors_base.keys())
    n = len(factor_names)

    contributions = {}
    for name in factor_names:
        shapley_val = 0
        others = [fn for fn in factor_names if fn != name]
        for subset_size in range(n):
            for subset in itertools.combinations(others, subset_size):
                subset_set = set(subset)
                val_with, val_without = 1, 1
                for fn in factor_names:
                    if fn == name:
                        val_with *= factors_current[fn]
                        val_without *= factors_base[fn]
                    elif fn in subset_set:
                        val_with *= factors_current[fn]
                        val_without *= factors_current[fn]
                    else:
                        val_with *= factors_base[fn]
                        val_without *= factors_base[fn]
                weight = math.factorial(subset_size) * math.factorial(n - subset_size - 1) / math.factorial(n)
                shapley_val += weight * (val_with - val_without)
        contributions[name] = shapley_val
    return contributions
```

**加法公式 Y = A + B + C**：直接看各项的变化量即可，无需复杂分解。

**加法 + 乘法混合**：先按加法拆，再对乘法项分别做 Shapley。

### 2.4 瀑布图可视化

因子拆解的结果用**瀑布图（Waterfall Chart）**呈现最为直观——起点是基准值，终点是当期值，中间每一段代表一个因子的贡献量，正向贡献向上（绿色），负向贡献向下（红色），一眼就能看出哪个环节拖了后腿、哪个环节在撑场。

使用 Python + matplotlib 生成瀑布图：

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

def waterfall_chart(factors, contributions, base_value, current_value, title, save_path):
    """
    factors: list, 因子名称列表，如 ["UV", "转化率", "客单价", "交叉项"]
    contributions: list, 各因子的贡献量（绝对值变化量，非百分比），如 [+20000, -15000, +5000, -500]
    base_value: float, 基准期总值
    current_value: float, 当期总值
    title: str, 图表标题
    save_path: str, 保存路径
    """
    labels = ["基准值"] + factors + ["当期值"]
    values = [base_value] + contributions + [current_value]

    # 计算瀑布图的底部位置和柱子高度
    bottoms = [0]
    heights = [base_value]
    running = base_value
    for c in contributions:
        if c >= 0:
            bottoms.append(running)
            heights.append(c)
        else:
            bottoms.append(running + c)
            heights.append(abs(c))
        running += c
    bottoms.append(0)
    heights.append(current_value)

    colors = ["#4472C4"]  # 基准值：蓝色
    for c in contributions:
        colors.append("#2E7D32" if c >= 0 else "#C62828")  # 正向绿，负向红
    colors.append("#4472C4")  # 当期值：蓝色

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, heights, bottom=bottoms, color=colors, width=0.6, edgecolor='white')

    # 在柱子上标注数值
    for i, (bar, val) in enumerate(zip(bars, values)):
        if i == 0 or i == len(values) - 1:
            text = f"{val:,.0f}"
            y_pos = bar.get_y() + bar.get_height() + base_value * 0.01
        else:
            text = f"{'+' if val >= 0 else ''}{val:,.0f}"
            y_pos = bar.get_y() + bar.get_height() + base_value * 0.01
        ax.text(bar.get_x() + bar.get_width()/2, y_pos, text,
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 添加连接线
    for i in range(len(bars) - 1):
        x1 = bars[i].get_x() + bars[i].get_width()
        x2 = bars[i+1].get_x()
        y = bars[i].get_y() + bars[i].get_height() if i == 0 else bottoms[i] + heights[i]
        ax.plot([x1, x2], [y, y], color='gray', linewidth=0.8, linestyle='--')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel("指标值")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
```

**在报告中使用**：将生成的瀑布图图片嵌入诊断报告（如果是 HTML 报告直接嵌入，如果是 Markdown 报告则引用图片路径）。

### 2.5 因子拆解的产出

这一步结束后，你应该能回答：
- "变化主要发生在哪个业务环节？"（如：转化率下降是主因，贡献了 65%）
- "各因子各贡献了多少？"（瀑布图直观呈现）

**这个结论直接决定 Step 3 的方向**——Step 3 的维度归因应优先围绕贡献最大的因子展开，而不是对着总指标盲扫。

---

## Step 3：维度归因（定位——问题在哪些维度上集中）

知道了是哪个环节出了问题（Step 2），现在要定位"这个环节的问题集中在哪里"。

如果 Step 2 找到了主因子（如转化率），这一步就**针对该因子**做维度归因和下钻。如果 Step 2 不适用（指标没有拆解公式），则直接对总指标做维度归因。

### 3.1 横向扫描：多维度并行分析

#### 选择归因维度

查询指标（或主因子指标）的可用维度：
```bash
curl -H "X-API-Key: $CAN_API_KEY" "https://gateway.can.aloudata.com/api/metrics/{metricName}/dimensions"
```

从可用维度中选取 3-5 个业务上最可能影响波动的维度：
- 用户指定了 → 优先用户的
- 未指定 → 优先选渠道、地区、产品线、品牌等业务实体维度
- 避免粒度过细的维度（如 SKU），除非用户要求

#### 对每个维度查询变化量

```json
{
    "metrics": ["{指标}", "{指标}__sameperiod__mom__value", "{指标}__sameperiod__mom__growthvalue"],
    "dimensions": ["{维度名}"],
    "timeConstraint": "DateTrunc(['metric_time'], \"MONTH\") = DATEADD(DateTrunc(NOW(), \"MONTH\"), -1, \"MONTH\")",
    "orders": [{"{指标}__sameperiod__mom__growthvalue": "asc"}]
}
```

**注意**：这里的 `{指标}` 应该是 Step 2 发现的主因子对应的指标（如转化率对应的 buyer_cnt 和 visitor_cnt），而不一定是用户最初问的总指标。

#### 计算贡献度

```
维度值变化量 = 当期值 - 基准值
总变化量 = Σ 所有维度值的变化量（应等于 Step 1 的总体变化量，作为校验）
贡献度 = 维度值变化量 / |总变化量| × 100%
```

分母用**绝对值**，正贡献=拉动增长，负贡献=拖累下降。

#### Highlight 主要贡献因素

计算完贡献度后，按以下规则标记主要贡献者，让关键发现一眼可见：

| 贡献度（绝对值） | 标记 | 含义 |
|----------------|------|------|
| ≥ 30% | 🔴 **主要贡献者** | 必须重点分析，作为下钻对象 |
| 10% ~ 30% | 🟡 次要贡献者 | 值得关注，可选择性下钻 |
| < 10% | 无标记 | 影响较小，一般不需下钻 |

#### 评估各维度的解释力

- **集中度**：个别维度值贡献了大部分变化？（如某渠道贡献 70% 的下降）→ 维度解释力强
- **业务可解释性**：数据发现在业务上说得通？

如果所有维度的解释力都很弱（变化均匀分布，没有 🔴 标记的维度值），说明可能不是结构性变化，而是整体性因素在起作用 → 在 Step 4 外部事件中寻找解释。

### 3.2 纵向下钻：逐层深入

当某个维度值贡献了显著变化量，追问"这个维度值内部，又是哪个子维度导致的"。

#### 确定下钻路径

维度从粗到细：
```
一级渠道 → 二级渠道 → 地区 → 城市
品类大类 → 品类中类 → 品牌
```

#### 执行下钻

对贡献最大的维度值（top 1-2），添加 filters 限定后，在下一层维度上做归因：

```json
{
    "metrics": ["{指标}", "{指标}__sameperiod__mom__value", "{指标}__sameperiod__mom__growthvalue"],
    "dimensions": ["{下一层维度}"],
    "filters": ["[{上层维度}]= \"{贡献最大的值}\""],
    "timeConstraint": "..."
}
```

#### 下钻终止条件

- 找到了足够具体的根因
- 变化在当前层级均匀分布，没有集中点
- 层数达到 3-4 层
- 数据量过少，不具统计意义

### 3.3 维度归因的产出

这一步结束后，你应该能回答：
- "问题因子的变化主要集中在哪个维度？"
- "具体到哪个维度值贡献最大？"
- "下钻后的根因路径是什么？"

结合 Step 2 的因子拆解，你现在应该有了一条完整的因果链条，例如：
> "GMV 下降 10% → 主因是转化率下降（贡献 65%）→ 转化率下降集中在 Retail 渠道（贡献 70%）→ 进一步下钻发现华东区降幅最大"

---

## Step 4：外部事件关联（找因——为什么会这样）

内部数据告诉你"什么变了"和"在哪里变了"，但根本原因往往在外部——天气、节假日、竞对、政策等。这一步为前面的数据发现寻找外部解释。

### 4.1 判断是否需要外部关联

以下信号提示需要关注外部因素：
- **维度归因没有明显集中点**：变化均匀分布，说明是"整体性"因素
- **变化与季节性模式不符**：如夏季空调销量反而下降
- **变化幅度异常大**：超出正常波动，通常有外部触发
- **用户主动提及外部因素**

实际上，即使维度归因有明显集中点，也建议检索外部事件作为佐证——"Retail 渠道转化率下降"是事实，但"为什么 Retail 转化率会下降"可能需要外部信息来回答。

### 4.2 外部事件检索

根据业务领域和波动时间段，搜索相关外部事件：

| 外部因素 | 搜索关键词示例 | 典型影响模式 |
|---------|-------------|------------|
| **天气/自然灾害** | "{地区} {月份} 天气 极端 暴雨 高温" | 影响线下客流、物流配送 |
| **节假日/大促** | "{月份} 节假日 促销节 双十一 618" | 大促前后蓄水-爆发-回落周期 |
| **竞对动作** | "{行业} 竞争对手 促销 降价 新品发布" | 价格战导致转化率/客单价变化 |
| **行业政策** | "{行业} 政策 法规 监管 新规" | 合规成本上升、品类受限 |
| **宏观经济** | "消费信心指数 {月份} CPI 就业" | 整体消费意愿变化 |
| **平台规则** | "{平台名} 算法 流量规则 搜索排名" | 流量分配变化导致 UV 波动 |

使用 WebSearch 工具进行搜索（如果可用），或提示用户确认已知的外部事件。

### 4.3 事件与数据对齐

找到候选外部事件后，验证其与数据发现的一致性：

**时间对齐**：事件发生时间与指标变化时间匹配？（事件应在变化之前或同期）

**空间对齐**：地区性事件（如某地暴雨），该地区数据是否确实异常？用 Step 3 的维度归因结果验证。

**方向对齐**：事件预期影响方向与实际变化一致？（暴雨 → 线下客流减少 → 线下渠道确实下降了）

**量级对齐**：事件影响范围是否足以解释变化量级？

### 4.4 外部关联的产出

- "有哪些外部事件可能影响了指标？"
- "这些外部事件与数据发现是否一致？"
- "哪些是有数据支撑的确定性结论，哪些是基于外部信息的推测？"

---

## Step 5：综合诊断结论

将所有发现汇总，形成完整的归因报告。

### 5.1 报告结构

```markdown
# 指标波动归因诊断报告

## 1. 波动概况
- **分析指标**：{指标名称}
- **分析时段**：{当期} vs {基准期}
- **当期值**：{值} | **基准值**：{值}
- **变化量**：{±变化量}（{变化率}%）
- **趋势判断**：{突发异常 / 持续趋势 / 季节性波动}

## 2. 归因发现

### 2.1 因子拆解（哪个环节出了问题）

**瀑布图**：（嵌入 Step 2 生成的瀑布图，直观展示各因子正负贡献）

![因子拆解瀑布图]({waterfall_chart_path})

| 因子 | 当期值 | 基准值 | 因子变化率 | 对总量贡献 | 贡献度 |
|------|-------|-------|----------|----------|-------|
| **{因子A}** 🔴 | xxx | xxx | {±X.X%} | {±xxx} | **{XX%}** |
| {因子B} | xxx | xxx | {±X.X%} | {±xxx} | {XX%} |
| {因子C} | xxx | xxx | {±X.X%} | {±xxx} | {XX%} |

→ 主要问题环节：**{因子A}**（贡献了 XX% 的变化）

### 2.2 维度归因（问题集中在哪里）

针对主因子 **{因子A}** 做维度归因，定位问题集中在哪里。

**Highlight 规则**：贡献度 ≥ 30% 的维度值标记为 🔴 主要贡献者，10%-30% 标记为 🟡 次要贡献者。

| 维度 | 维度值 | 当期值 | 基准值 | 变化量 | 贡献度 | 标记 |
|-----|-------|-------|-------|-------|-------|------|
| {维度1} | {值A} | xxx | xxx | {±xxx} | **{XX%}** | 🔴 主因 |
| {维度1} | {值B} | xxx | xxx | {±xxx} | {XX%} | 🟡 次因 |
| {维度1} | {值C} | xxx | xxx | {±xxx} | {XX%} | |

**下钻路径**：🔴 {维度1值A} → 🔴 {维度2值X} → 🔴 {维度3值Y}，贡献了总变化的 XX%

### 2.3 外部事件（为什么会这样）

| 事件 | 发生时间 | 影响范围 | 与数据的一致性 |
|-----|---------|---------|-------------|
| {事件1} | {时间} | {范围} | {高/中/低} |

## 3. 归因结论

综合以上分析，本次{指标名}的{变化方向}主要由以下因素导致：

1. **主因**：{一句话说清核心原因，串联因子→维度→外部事件}
   - 数据支撑：{因子拆解和维度归因的关键数字}
   - 外部佐证：{相关外部事件，如有}

2. **次因**：{第二重要的原因}
   - 数据支撑：...

3. **其他因素**：{其他较小的影响因素}

## 4. 建议关注
- {基于归因结论给出的可操作建议}
- {需要持续监控的指标或维度}
```

### 5.2 报告撰写原则

**结论驱动，数据支撑**：先说结论，再给证据。读者最关心"为什么变了"和"怎么办"，不关心分析过程。

**区分确定性**：数据直接证明的（"数据显示转化率下降贡献了 65%"）vs 基于外部信息的推测（"推测与竞对促销有关"）。

**给出完整因果链条**：最有价值的归因不是单点发现，而是一条串联 Step 2→3→4 的链条：
> "销售额环比下降 12%，主因是转化率下降了 18%（贡献总下降的 65%）。转化率下降集中在 Retail 渠道（贡献 70%），进一步下钻发现华东区降幅最大（贡献 45%）。推测与该区域同期竞对大力度促销活动有关。"

---

## 通用规范

### 查询构建

所有 API 查询遵守 metric-query 的全部铁律和规范，特别注意：
- 相对时间必须用 `NOW()`，禁止硬编码日期
- `metricDefinitions` 中每个 key 必须在 `metrics` 数组中注册
- `curl` 用 heredoc 传 JSON body
- 维度值严格按 Gateway 返回的原始写法

### 查询效率

归因分析通常需要多次查询。为减少查询次数：
- 利用 `__sameperiod__` 系列一次获取当期值、基准值和变化量
- 多次查询的 timeConstraint 保持一致
- Step 3 维度归因时，可以同时查多个维度（分别放在不同查询中）

### 数值计算

- 贡献度分母用总变化量的**绝对值**，避免负数导致符号混淆
- 各维度值贡献度之和应约等于 100%，作为校验（偏差 > 5% 需排查）
- 因子拆解时基准值为 0 → 标注"基准期无数据，无法计算变化率"
- 百分比类指标（如转化率）：明确区分"百分点变化"和"变化率"

---

## 常见错误模式

**❌ 未确认基准就开始分析**：用户说"指标降了"但没说跟什么比。先确认基准。

**❌ 跳过因子拆解直接扫维度**：如果指标有业务公式，先拆解才能让后续维度归因有方向。否则只知道"Retail 下降了"，不知道是 Retail 的哪个环节出了问题。

**❌ 只做因子拆解不做维度归因**：知道"转化率下降是主因"还不够，得进一步定位到哪个渠道、哪个地区的转化率降了。

**❌ 只看内部数据不关联外部事件**：数据告诉你"在哪里变了"，但"为什么变"往往需要外部信息来回答。特别是当维度归因结果均匀分布时，更要找外部因素。

**❌ 贡献度分母用了带符号的值**：总变化量为负时符号反转。分母必须用绝对值。

**❌ 因子拆解忽略交叉项**：因子变化率 > 10% 时，近似分解误差不可忽略。用 Shapley 分解或至少报告交叉项。

**❌ 下钻过深，数据量不足**：每层下钻缩小数据范围，数据量太少时结论不可靠。

**❌ 混淆"百分点变化"和"变化率"**：转化率从 5% 降到 4% → 百分点变化 -1pp，变化率 -20%。

**❌ 把数据关联当因果**：维度归因发现的是"关联"，因果推断需结合外部事件和业务逻辑。

---

## 分析质量检查清单

1. ✅ 对比基准已确认且合理
2. ✅ 总体变化量已量化（有具体数字和百分比）
3. ✅ 因子拆解（如适用）：各因子贡献之和等于总变化量
4. ✅ 因子拆解（如适用）：交叉项已检查
5. ✅ 维度归因：围绕主因子（而非总指标）展开
6. ✅ 维度归因：各维度值贡献度之和约等于 100%
7. ✅ 维度归因：对贡献最大的维度值做了下钻（至少尝试一层）
8. ✅ 外部事件：至少检索了相关时间段的外部事件
9. ✅ 外部事件：与数据发现做了一致性对齐
10. ✅ 综合结论串联了因子→维度→外部事件的完整链条
11. ✅ 结论区分了确定性发现和推测性判断
12. ✅ 给出了可操作的业务建议
13. ✅ 百分比口径一致（百分点 vs 变化率）
14. ✅ 所有查询遵守 metric-query 铁律
15. ✅ 因子拆解生成了瀑布图（如适用）
16. ✅ 维度归因中主要贡献者（≥30%）已用 🔴 标记 highlight
