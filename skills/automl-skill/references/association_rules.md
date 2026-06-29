# PyCaret Association Rules 模块 | Association Rules Module

关联规则挖掘任务的完整 API 参考文档。

## setup() 函数

```python
from pycaret.arules import setup

# 基础用法
arules = setup(data, transaction_id='transaction_id', item_features='item')

# 完整参数
arules = setup(
    # ===== 必需参数 =====
    data,                                 # 数据框（必需）
    transaction_id,                      # 交易ID列（必需）
    item_features=None,                  # 商品特征列
    
    # ===== 数据处理 =====
    encoding_method=None,                # 编码方法
    freq_threshold=0.01,                # 频繁项集阈值
    
    # ===== 系统选项 =====
    n_jobs=-1,
    html=True,
    session_id=None,
    verbose=True,
    profile=False
)
```

## create_model()

```python
from pycaret.arules import create_model

# 创建关联规则模型
model = create_model()

# 完整参数
model = create_model(
    metric='confidence',                # 评估指标
    threshold=0.5,                      # 阈值
    min_support=0.001,                 # 最小支持度
    max_length=10                       # 最大项集长度
)
```

## 评估指标

| 指标 | 说明 |
|------|------|
| support | 支持度 |
| confidence | 置信度 |
| lift | 提升度 |

## assign_model()

```python
from pycaret.arules import assign_model

# 获取关联规则
rules = assign_model(model)
# 返回关联规则表
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'network'` | 关联网络图 |
| `'matrix'` | 关联矩阵图 |
| `'sunburst'` | 旭日图 |

## 完整工作流示例

```python
from pycaret.arules import *

# 1. 加载数据
data = get_data('market')

# 2. 初始化
arules = setup(data, transaction_id='Item', item_features='Amount')

# 3. 创建模型
model = create_model(
    metric='confidence',
    threshold=0.5,
    min_support=0.01
)

# 4. 获取规则
rules = assign_model(model)

# 5. 可视化
plot_model(model, plot='network')
plot_model(model, plot='matrix')

# 6. 查看规则
print(rules.head(10))
```

## 常用参数说明

- **metric**: 评估指标，可选 'support', 'confidence', 'lift'
- **threshold**: 阈值，过滤低于此值的规则
- **min_support**: 最小支持度
- **max_length**: 项集最大长度

## 示例数据格式

交易数据格式示例：

| transaction_id | item |
|----------------|------|
| 1 | Apple |
| 1 | Banana |
| 1 | Milk |
| 2 | Banana |
| 2 | Bread |
| 3 | Apple |
| 3 | Bread |
| 3 | Milk |
| 3 | Banana |

或使用 One-Hot 编码格式：

| transaction_id | Apple | Banana | Bread | Milk |
|----------------|-------|--------|-------|------|
| 1 | 1 | 1 | 0 | 1 |
| 2 | 0 | 1 | 1 | 0 |
| 3 | 1 | 1 | 1 | 1 |
