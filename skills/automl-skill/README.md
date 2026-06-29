# AutoML Skill | 自动化机器学习技能

[English](#english) | [中文](#中文)

---

## English

### Overview

AutoML Skill is a powerful automated machine learning skill based on **PyCaret**, designed to help data scientists and developers quickly build end-to-end machine learning workflows with minimal code.

### Features

- 🚀 **Automated Model Selection** - Automatically compare multiple models and select the best one
- 🎯 **Automated Hyperparameter Tuning** - Optimize model parameters using Optuna/Hyperopt
- ⚡ **Automated Feature Engineering** - Data preprocessing, transformation, and feature selection
- 🔄 **Model Ensemble** - Support for Bagging, Boosting, Stacking, Blending
- 📊 **Model Interpretability** - SHAP, Permutation Importance support
- ☁️ **Production-Ready** - Model deployment to AWS, GCP, Azure
- 📈 **Statistical Enhancement** - Confidence intervals, hypothesis testing, significance analysis (statsmodels)

### Supported ML Tasks

| Module | Task Type | Description |
|--------|-----------|-------------|
| `pycaret.classification` | Classification | Binary & Multi-class classification |
| `pycaret.regression` | Regression | Regression prediction |
| `pycaret.clustering` | Clustering | Unsupervised clustering |
| `pycaret.anomaly` | Anomaly Detection | Outlier detection |
| `pycaret.time_series` | Time Series | Time series forecasting |
| `pycaret.nlp` | NLP | Text classification, Topic modeling |
| `pycaret.arules` | Association Rules | Market basket analysis |

### Statistical Enhancement (statsmodels)

When you need statistical inference, hypothesis testing, or confidence intervals, use statsmodels alongside PyCaret:

```python
# OLS Regression with statistical significance
import statsmodels.api as sm
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())  # R², F-test, P-values, confidence intervals

# Hypothesis Testing
from scipy import stats
t_stat, p_value = stats.ttest_ind(group1, group2)

# ARIMA Time Series
from statsmodels.tsa.arima.model import ARIMA
arima_model = ARIMA(data, order=(1,1,1)).fit()
```

### Quick Start

完整的 AutoML 工作流程：

```python
from pycaret.classification import *
import pandas as pd

# Step 1: Load Data
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# Step 2: Data Exploration
print(f"Train: {train.shape}, Test: {test.shape}")

# Step 3-4: Preprocessing & Feature Engineering
clf = setup(
    train,
    target='target',
    # Missing values
    numeric_imputation='median',
    categorical_imputation='mode',
    # Outliers
    remove_outliers=True,
    # Class balance
    fix_imbalance=True,
    # Feature scaling
    normalize=True,
    normalize_method='zscore',
    # Feature selection
    feature_selection=True,
    n_features_to_select=0.3,
    session_id=42
)

# Step 5: Model Selection
best = compare_models(sort='AUC')

# Step 6-7: Training & Tuning
tuned = tune_model(best, optimize='AUC', n_iter=30)

# Step 8-9: Evaluation & Interpretation
evaluate_model(tuned)
interpret_model(tuned)

# Step 10: Ensemble (optional)
# ensemble = ensemble_model(tuned)

# Step 11: Final Prediction
final = finalize_model(tuned)
predictions = predict_model(final, data=test)

# Step 12: Save
save_model(final, 'best_model')
```

### Documentation Structure

```
automl-skill/
├── SKILL.md                      # Main skill file
├── evals/
│   └── evals.json              # Test cases (30 examples)
└── references/                   # Detailed documentation
    ├── classification.md         # Classification module
    ├── regression.md           # Regression module
    ├── time_series.md          # Time series module
    ├── clustering.md           # Clustering module
    ├── anomaly.md             # Anomaly detection
    ├── nlp.md                 # NLP module
    ├── association_rules.md    # Association rules
    ├── utilities.md           # Utility functions
    └── setup_parameters_deep_dive.md  # Parameter guide
```

### When to Use This Skill

- Rapid prototyping and experiment iteration
- Feature engineering and data preprocessing
- Model selection and comparison
- Hyperparameter optimization
- Statistical inference and hypothesis testing
- Model deployment and production

---

## 中文

### 简介

AutoML Skill 是一个基于 **PyCaret** 的强大自动化机器学习技能，旨在帮助数据科学家和开发者用最少的代码快速构建端到端的机器学习工作流。

### 功能特点

- 🚀 **自动化模型选择** - 自动比较多个模型并选择最佳模型
- 🎯 **自动化超参数调优** - 使用 Optuna/Hyperopt 自动优化模型参数
- ⚡ **自动化特征工程** - 数据预处理、转换和特征选择
- 🔄 **模型集成** - 支持 Bagging、Boosting、Stacking、Blending
- 📊 **模型可解释性** - 支持 SHAP、Permutation Importance
- ☁️ **生产就绪** - 支持部署到 AWS、GCP、Azure
- 📈 **统计推断增强** - 置信区间、假设检验、显著性分析 (statsmodels)

### 支持的任务类型

| 模块 | 任务类型 | 说明 |
|------|----------|------|
| `pycaret.classification` | 分类 | 二分类和多分类 |
| `pycaret.regression` | 回归 | 回归预测 |
| `pycaret.clustering` | 聚类 | 无监督聚类 |
| `pycaret.anomaly` | 异常检测 | 离群点检测 |
| `pycaret.time_series` | 时间序列 | 时间序列预测 |
| `pycaret.nlp` | 自然语言处理 | 文本分类、主题建模 |
| `pycaret.arules` | 关联规则 | 购物篮分析 |

### 统计推断增强 (statsmodels)

当需要统计推断、假设检验、置信区间时，可以使用 statsmodels 补充 PyCaret：

```python
# OLS 回归（带统计显著性）
import statsmodels.api as sm
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())  # R², F检验, P值, 置信区间

# 假设检验
from scipy import stats
t_stat, p_value = stats.ttest_ind(group1, group2)

# ARIMA 时间序列
from statsmodels.tsa.arima.model import ARIMA
arima_model = ARIMA(data, order=(1,1,1)).fit()
```

### 快速开始

完整的 AutoML 工作流程：

```python
from pycaret.classification import *
import pandas as pd

# Step 1: 加载数据
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# Step 2: 数据探索
print(f"训练集: {train.shape}, 测试集: {test.shape}")

# Step 3-4: 数据预处理 + 特征工程
clf = setup(
    train,
    target='target',
    # 缺失值处理
    numeric_imputation='median',
    categorical_imputation='mode',
    # 异常值处理
    remove_outliers=True,
    # 类别平衡
    fix_imbalance=True,
    # 特征缩放
    normalize=True,
    normalize_method='zscore',
    # 特征选择
    feature_selection=True,
    n_features_to_select=0.3,
    session_id=42
)

# Step 5: 模型选择
best = compare_models(sort='AUC')

# Step 6-7: 训练与调优
tuned = tune_model(best, optimize='AUC', n_iter=30)

# Step 8-9: 评估与解释
evaluate_model(tuned)
interpret_model(tuned)

# Step 10: 集成（可选）
# ensemble = ensemble_model(tuned)

# Step 11: 最终预测
final = finalize_model(tuned)
predictions = predict_model(final, data=test)

# Step 12: 保存
save_model(final, 'best_model')
```

### 文档结构

```
automl-skill/
├── SKILL.md                      # 主技能文件
├── evals/
│   └── evals.json              # 测试用例 (30个示例)
└── references/                   # 详细文档
    ├── classification.md         # 分类模块
    ├── regression.md           # 回归模块
    ├── time_series.md          # 时间序列模块
    ├── clustering.md           # 聚类模块
    ├── anomaly.md             # 异常检测
    ├── nlp.md                 # NLP模块
    ├── association_rules.md    # 关联规则
    ├── utilities.md           # 工具函数
    └── setup_parameters_deep_dive.md  # 参数指南
```

### 使用场景

- 快速原型开发和实验迭代
- 特征工程和数据预处理
- 模型选择和比较
- 超参数优化
- 统计推断和假设检验
- 模型部署和生产

### 相关链接

- PyCaret 官方文档: https://pycaret.gitbook.io/docs
- PyCaret API 文档: https://pycaret.readthedocs.io/

---

*This skill is part of the automl-skill project. Future versions will integrate more AutoML libraries like AutoGluon, FLAML, etc.*
