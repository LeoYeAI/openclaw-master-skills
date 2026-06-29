# PyCaret setup() 参数深度分析 | Deep Dive into PyCaret setup() Parameters

本文档详细解释 PyCaret setup() 函数中各个参数的不同取值对 AutoML 结果的影响，帮助用户根据实际场景做出最佳选择。

> 文档基于 PyCaret 3.0 官方 API 文档

---

## 1. 数据缺失值处理 | Imputation

### imputation_type - 缺失值处理类型

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'simple'` | 简单插补（默认） | 大多数场景 | 快速，适合数据缺失比例<30% |
| `'iterative'` | 迭代插补（使用模型预测） | 缺失比例高、非随机缺失 | 更准确，但计算耗时 |
| `None` | 不处理 | 数据已完整或有意保留 | 可能导致模型训练失败 |

### numeric_imputation - 数值型缺失值填充

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'mean'` | 均值填充（默认） | 数据近似正态分布 | 保持均值，可能放大异常值影响 |
| `'median'` | 中位数填充 | 存在极端值/偏态分布 | 鲁棒性好，推荐金融/医疗数据 |
| `'mode'` | 众数填充 | 离散数值或存在高频值 | 可能扭曲分布 |
| `'knn'` | K近邻填充 | 特征间有相关性 | 更准确，但大数据集耗时 |
| `'drop'` | 删除含缺失的行 | 缺失比例<5% | 丢失数据，不推荐 |
| `int/float` | 指定固定值 | 业务有明确填充规则 | 需领域知识 |

**实战建议**：
```python
# 金融风控 - 建议用中位数
setup(data, numeric_imputation='median')

# 推荐系统 - 可用 knn
setup(data, numeric_imputation='knn')
```

### categorical_imputation - 类别型缺失值填充

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'mode'` | 众数填充（默认） | 大多数场景 | 简单有效 |
| `'constant'` | 填充为 "Unknown" | 缺失有业务含义 | 聚类任务默认用此值 |
| `'drop'` | 删除含缺失的行 | 缺失极少 | 可能丢失重要模式 |

---

## 2. 数据划分策略 | Data Splitting

### fold_strategy - 交叉验证策略

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'kfold'` | 标准K折 | 回归任务、平衡数据 | 标准baseline |
| `'stratifiedkfold'` | 分层K折（默认，分类） | 分类任务、不平衡数据 | 保持类别比例，更可靠 |
| `'groupkfold'` | 分组K折 | 存在分组结构（患者/用户） | 防止数据泄露 |
| `'timeseries'` | 时间序列分割 | 时间序列预测 | 防止未来信息泄露 |

**实战建议**：
```python
# 分类任务（默认）
setup(data, fold_strategy='stratifiedkfold')

# 回归任务
setup(data, fold_strategy='kfold')

# 纵向数据（同一患者多次就诊）
setup(data, fold_strategy='groupkfold', fold_groups='patient_id')
```

### data_split_stratify - 分层抽样

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `True` | 按目标变量分层（默认，分类） | 训练/测试集类别比例一致 |
| `False` | 随机划分（默认，回归） | 可能导致类别分布不一致 |
| `['col1', 'col2']` | 按指定列分层 | 多列组合分层 |

---

## 3. 特征工程 | Feature Engineering

### normalize_method - 归一化方法

| 值 | 说明 | 公式 | 适用场景 | AutoML 影响 |
|---|------|------|----------|-------------|
| `'zscore'` | Z-Score标准化（默认） | z = (x - μ) / σ | 大多数场景，数据近似正态 | 标准方法，均值0方差1 |
| `'minmax'` | 最小最大缩放 | x' = (x - min) / (max - min) | 数据有边界，神经网络 | 值映射到[0,1] |
| `'maxabs'` | 最大绝对值缩放 | x' = x / max(\|x\|) | 稀疏数据 | 不破坏稀疏性 |
| `'robust'` | 鲁棒缩放 | x' = (x - Q1) / (Q3 - Q1) | 存在 outliers | 使用四分位距，对异常值鲁棒 |

**实战建议**：
```python
# 标准场景
setup(data, normalize=True, normalize_method='zscore')

# 有异常值的数据
setup(data, normalize=True, normalize_method='robust')

# 稀疏矩阵/文本TF-IDF
setup(data, normalize=True, normalize_method='maxabs')
```

### transformation_method - 变换方法

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'yeo-johnson'` | Yeo-Johnson变换（默认） | 可处理负值和零值 | 使数据更接近正态分布 |
| `'quantile'` | 分位数变换 | 需要均匀分布 | 将数据映射到均匀/正态分布 |

**何时使用 transformation=True**：
- 特征严重偏态（skewness > 1）
- 线性模型（LR, SVM）表现不佳
- 某些算法对正态性有要求

### pca_method - PCA降维方法

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'linear'` | 线性PCA（默认） | 大多数场景 | 快速，效果好 |
| `'kernel'` | 核PCA | 非线性关系 | 保留非线性结构，但耗时 |
| `'incremental'` | 增量PCA | 大数据集（>100k行） | 内存友好 |

### pca_components - PCA保留成分数

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `None` | 保留所有成分 | 不降维，仅转换 |
| `int` | 保留n个主成分 | 指定数量 |
| `float (0-1)` | 保留解释方差比例 | 如0.95保留95%方差 |
| `'mle'` | MLE自动选择 | 智能选择，可能较好 |

---

## 4. 特征选择 | Feature Selection

### feature_selection_method - 特征选择方法

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'classic'` | SelectFromModel（默认） | 大多数场景 | 使用LightGBM计算重要性 |
| `'univariate'` | SelectKBest | 快速筛选 | 独立评估每个特征 |
| `'sequential'` | 序列前向/后向选择 | 精确筛选 | 耗时，特征多时不可用 |

### feature_selection_estimator - 特征重要性评估器

| 值 | 说明 | 适用场景 | AutoML 影响 |
|---|------|----------|-------------|
| `'lightgbm'` | LightGBM（默认） | 分类/回归 | 快速，效果好 |
| `'rf'` | Random Forest | 需要可解释性 | 稳定，但稍慢 |
| 自定义 | sklearn estimator | 特殊需求 | 灵活 |

### n_features_to_select - 选择特征数量

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `float (0-1)` | 保留比例，如0.2保留20% | 常用推荐值 |
| `int` | 保留数量 | 精确控制 |

---

## 5. 离群值处理 | Outlier Handling

### outliers_method - 离群值检测方法

| 值 | 全称 | 原理 | 适用场景 | AutoML 影响 |
|---|------|------|----------|-------------|
| `'iforest'` | Isolation Forest | 隔离异常点 | 大数据、任意分布 | 快速高效，默认推荐 |
| `'ee'` | Elliptic Envelope | 假设多元正态 | 数据接近正态分布 | 需要足够样本 |
| `'lof'` | Local Outlier Factor | 局部密度偏差 | 簇状分布数据 | 计算复杂度高 |

### outliers_threshold - 离群值比例

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `0.05` | 默认，移除5% | 平衡数据保留与清洗 |
| `0.01` | 保守，仅移除1% | 保留更多数据 |
| `0.1` | 激进，移除10% | 清洗更彻底 |

**实战建议**：
```python
# 标准场景
setup(data, remove_outliers=True, outliers_threshold=0.05)

# 金融风控（异常重要）
setup(data, remove_outliers=True, outliers_method='lof')

# 大数据
setup(data, remove_outliers=True, outliers_method='iforest')
```

---

## 6. 类别平衡 | Class Imbalance

### fix_imbalance_method - 平衡方法

| 值 | 全称 | 原理 | 适用场景 | AutoML 影响 |
|---|------|------|----------|-------------|
| `'SMOTE'` | Synthetic Minority Oversampling | 插值生成新样本 | 少数类样本>1000 | 默认推荐，效果好 |
| `'SMOTENC'` | SMOTE for Nominal and Continuous | 混合数据 | 含类别特征 | 混合数据首选 |
| `'ADASYN'` | Adaptive Synthetic | 自适应生成 | 严重不平衡 | 聚焦难点样本 |
| `'RandomUnderSampler'` | 随机下采样 | 删除多数类 | 多数类样本不多 | 可能丢失信息 |

**何时使用 fix_imbalance=True**：
- 少数类占比 < 20%
- 类别比例 > 1:10
- 评估指标选择 AUC/F1 而非 Accuracy

---

## 7. 多重共线性处理 | Multicollinearity

### remove_multicollinearity - 移除高相关特征

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `True` | 启用 | 移除相关性>threshold的特征 |
| `False` | 禁用（默认） | 保留所有特征 |

### multicollinearity_threshold - 相关性阈值

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `0.9` | 默认 | 移除高度相关的特征 |
| `0.95` | 宽松 | 保留更多特征 |
| `0.8` | 严格 | 更激进的特征筛选 |

---

## 8. 稀有类别处理 | Rare Category Handling

### rare_to_value - 稀有类别阈值

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `None` | 不处理 | 保留原始类别 |
| `0.05` | 少于5%视为稀有 | 合并稀有类别 |
| `0.1` | 少于10%视为稀有 | 更激进的合并 |

### rare_value - 稀有类别替换值

| 值 | 说明 | AutoML 影响 |
|---|------|-------------|
| `'rare'` | 替换为"rare"字符串 | 默认 |
| `'unknown'` | 替换为"unknown" | 更易理解 |

---

## 9. 特殊特征处理 | Special Feature Handling

### bin_numeric_features - 离散化数值特征

将连续数值特征转换为类别特征，使用 KMeans 聚类确定分割点。

```python
setup(data, bin_numeric_features=['age', 'income'])
```

**AutoML 影响**：
- 优点：可捕捉非线性关系
- 缺点：可能丢失信息

### group_features - 分组特征

```python
setup(data, group_features={'address': ['city', 'state', 'zip']})
```

生成统计特征：min, max, mean, std, median, mode

### ordinal_features - 有序类别

```python
setup(data, ordinal_features={
    'education': ['high_school', 'bachelor', 'master', 'phd'],
    'income': ['low', 'medium', 'high']
})
```

保留类别间的顺序信息。

---

## 10. GPU 配置 | GPU Configuration

### use_gpu 参数

| 值 | 说明 | 支持算法 |
|---|------|----------|
| `False` | CPU计算（默认） | 所有算法 |
| `True` | 自动选择GPU | XGBoost, CatBoost, LightGBM, LogisticRegression, Ridge, RF, KNN, SVM |
| `'force'` | 强制GPU | 仅GPU算法，否则报错 |

**注意**：GPU仅在数据>50,000行时启用。

---

## 11. 完整参数组合示例 | Complete Parameter Combinations

### 典型分类任务

```python
# 标准二分类
clf = setup(
    data,
    target='target',
    train_size=0.8,
    fold_strategy='stratifiedkfold',
    fold=5,
    numeric_imputation='mean',
    categorical_imputation='mode',
    normalize=True,
    normalize_method='zscore',
    fix_imbalance=True,
    fix_imbalance_method='SMOTE',
    session_id=42
)
```

### 金融风控任务

```python
# 金融风控 - 保守策略
clf = setup(
    data,
    target='fraud',
    numeric_imputation='median',          # 中位数，对异常值鲁棒
    categorical_imputation='constant',    # 缺失有含义
    normalize=True,
    normalize_method='robust',            # 鲁棒缩放
    remove_outliers=True,
    outliers_method='lof',               # 局部密度检测
    outliers_threshold=0.02,             # 保守
    fix_imbalance=True,
    fix_imbalance_method='SMOTE',
    remove_multicollinearity=True,
    multicollinearity_threshold=0.8,     # 严格
    session_id=42
)
```

### 高维数据（特征>100）

```python
# 高维数据
clf = setup(
    data,
    target='target',
    pca=True,
    pca_method='linear',
    pca_components=0.95,                  # 保留95%方差
    feature_selection=True,
    feature_selection_method='classic',
    n_features_to_select=0.3,            # 保留30%
    session_id=42
)
```

### 时间紧迫，快速建模

```python
# 快速建模
clf = setup(
    data,
    target='target',
    preprocess=True,                    # 默认预处理
    normalize=True,
    fold=3,                              # 减少折数
    turbo=True,                          # compare_models用turbo
    session_id=42
)
```

---

## 参数选择决策树

```
数据有缺失值?
├─ 是 → imputation_type='simple'
│       ├─ 数值型 → numeric_imputation='median' (有异常值) / 'mean' (正常)
│       └─ 类别型 → categorical_imputation='mode'
└─ 否 → 继续

数据不平衡?
├─ 是 → fix_imbalance=True
│       └─ fix_imbalance_method='SMOTE' (默认)
└─ 否 → 继续

数据有异常值?
├─ 是 → remove_outliers=True
│       ├─ 大数据 → outliers_method='iforest'
│       └─ 簇状分布 → outliers_method='lof'
└─ 否 → 继续

特征太多(>100)?
├─ 是 → pca=True / feature_selection=True
└─ 否 → 继续

特征需要缩放?
├─ 是 → normalize=True
│       ├─ 有异常值 → normalize_method='robust'
│       ├─ 稀疏数据 → normalize_method='maxabs'
│       └─ 其他 → normalize_method='zscore'
└─ 否 → 继续
```

---

## 参考来源

- PyCaret 官方文档: https://pycaret.readthedocs.io/
- PyCaret API Reference: https://pycaret.readthedocs.io/en/latest/api/classification.html
