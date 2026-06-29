---
name: automl-skill
description: >
  AutoML 自动化机器学习技能 | Automated Machine Learning Skill.
  基于 PyCaret 进行低代码机器学习建模，支持分类、回归、聚类、异常检测、时间序列预测、自然语言处理和关联规则挖掘等任务。
  未来将集成更多 AutoML 库（如 AutoGluon、FLAML 等）。
  当用户需要快速构建机器学习模型、自动化模型选择、超参数调优、模型集成、特征工程或进行 AutoML 实验时使用此技能。
  适用于数据科学家、公民数据科学家、机器学习工程师和希望快速原型开发的人员。
  触发关键词：AutoML、机器学习自动化、PyCaret、分类模型、回归模型、聚类、异常检测、时间序列、文本分类、模型调优、模型比较、特征选择、统计检验、显著性检验、A/B测试。
  Trigger keywords in English: AutoML, automated machine learning, PyCaret, classification, regression, clustering, anomaly detection, time series forecasting, NLP, text mining, model tuning, model comparison, feature engineering, statistical test, significance testing, A/B testing.
---

# PyCaret AutoML 技能指南 | PyCaret AutoML Skill Guide

本技能帮助用户使用 PyCaret 快速构建端到端的机器学习工作流。PyCaret 是一个开源的低代码机器学习库，可以将数百行代码简化为几行。

This skill helps users build end-to-end machine learning workflows using PyCaret, an open-source low-code ML library that simplifies hundreds of lines of code into just a few lines.

## 核心功能 | Core Capabilities

- **自动化模型选择** - 自动比较多个模型并选择最佳模型
- **自动化超参数调优** - 使用 Optuna/Hyperopt 自动优化模型参数
- **自动化特征工程** - 自动进行数据预处理、特征转换和特征选择
- **模型集成** - 支持 Bagging、Boosting、Stacking、Blending
- **模型可解释性** - 支持 SHAP、Permutation Importance 等解释方法
- **模型部署就绪** - 生成可复现的生产级 Pipeline
- **统计推断增强** - 支持置信区间、假设检验、统计显著性分析

---

## 统计推断增强 | Statistical Enhancement (statsmodels)

当需要统计推断、假设检验、置信区间时，可以使用 statsmodels 补充 PyCaret：

### 线性回归模型
```python
import statsmodels.api as sm

# OLS 回归（带统计显著性）
X = sm.add_constant(X)  # 添加截距
model = sm.OLS(y, X).fit()
print(model.summary())  # R², F检验, P值, 置信区间
```

### 广义线性模型 (GLM)
```python
# 二项分布 GLM (Logistic 回归)
glm_model = sm.GLM(y, X, family=sm.families.Binomial()).fit()

# 泊松回归 (计数数据)
poisson_model = sm.GLM(y, X, family=sm.families.Poisson()).fit()
```

### 假设检验
```python
from scipy import stats

# t 检验
t_stat, p_value = stats.ttest_ind(group1, group2)

# 卡方检验
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

# ANOVA
f_stat, p_value = stats.f_oneway(*groups)
```

### 时间序列分析
```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ARIMA 模型
arima_model = ARIMA(train_data, order=(1,1,1)).fit()
forecast = arima_model.forecast(steps=12)

# 季节性 SARIMAX
sarimax_model = SARIMAX(data, order=(1,1,1), seasonal_order=(1,1,1,12)).fit()
```

### 统计诊断
```python
# 残差自相关检验 (Durbin-Watson)
from statsmodels.stats.stattools import durbin_watson
dw = durbin_watson(model.resid)

# 异方差检验
from statsmodels.stats.diagnostic import het_breuschpagan
bp_test = het_breuschpagan(model.resid, model.model.exog)

# 正态性检验
from scipy import stats
shapiro_stat, shapiro_p = stats.shapiro(model.resid)
```

### 混合效应模型 (随机效应)
```python
# 混合线性模型 (Panel Data / 多层次数据)
from statsmodels.regression.mixed_linear_model import MixedLM
mixed_model = MixedLM(y, X, groups=group_var).fit()
```

### PyCaret + statsmodels 组合使用
```python
# 1. 用 PyCaret 快速建模和选择模型
from pycaret.classification import *
clf = setup(data, target='target')
best = compare_models()
tuned = tune_model(best)

# 2. 用 statsmodels 做统计推断
import statsmodels.api as sm
# 获取 PyCaret 模型的特征和预测
X_with_const = sm.add_constant(X_test)
sm_model = sm.Logit(y_test, X_with_const).fit(disp=0)
print(sm_model.summary())  # 系数显著性 P值
```

---

## 支持的机器学习任务 | Supported ML Tasks

| 模块 | Module | 任务类型 | Task Type | 参考文档 |
|------|--------|----------|------------|----------|
| pycaret.classification | Classification | 二分类、多分类 | Binary, Multi-class | [classification.md](references/classification.md) |
| pycaret.regression | Regression | 回归预测 | Regression | [regression.md](references/regression.md) |
| pycaret.clustering | Clustering | 无监督聚类 | Unsupervised Clustering | [clustering.md](references/clustering.md) |
| pycaret.anomaly | Anomaly Detection | 异常检测 | Outlier Detection | [anomaly.md](references/anomaly.md) |
| pycaret.time_series | Time Series | 时间序列预测 | Time Series Forecasting | [time_series.md](references/time_series.md) |
| pycaret.nlp | NLP | 文本分类、主题建模 | Text Classification, Topic Modeling | [nlp.md](references/nlp.md) |
| pycaret.arules | Association Rules | 关联规则挖掘 | Market Basket Analysis | [association_rules.md](references/association_rules.md) |

---

## 快速开始 | Quick Start

### 1. 选择您的任务类型

根据您的机器学习任务，选择相应的模块：

- **分类问题** → 使用 `pycaret.classification`
- **回归问题** → 使用 `pycaret.regression`
- **客户分群** → 使用 `pycaret.clustering`
- **异常检测** → 使用 `pycaret.anomaly`
- **时间预测** → 使用 `pycaret.time_series`
- **文本分析** → 使用 `pycaret.nlp`
- **购物篮分析** → 使用 `pycaret.arules`

### 2. 标准 AutoML 工作流 | Standard AutoML Workflow

完整的 AutoML 工作流程包含以下步骤：

#### Step 1: 数据收集与加载 | Data Collection & Loading
```python
# 数据加载
import pandas as pd
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# 或使用 PyCaret 内置数据集
from pycaret.classification import get_data
data = get_data('breast_cancer')
```

#### Step 2: 数据理解与探索 | Data Understanding & EDA
```python
# 基本信息
print(f"数据形状: {data.shape}")
print(f"数据类型:\n{data.dtypes}")

# 缺失值分析
missing = data.isnull().sum()
missing_pct = (missing / len(data) * 100).round(2)
print(f"缺失值比例:\n{pd.concat([missing, missing_pct], axis=1)}")

# 目标变量分布
data['target'].value_counts()

# 数值特征统计
data.describe()
```

#### Step 3: 数据预处理 | Data Preprocessing (setup 中自动完成)
```python
# 初始化环境 - 数据预处理配置
clf = setup(
    data,
    target='target',

    # ===== 缺失值处理 =====
    numeric_imputation='mean',       # 数值型: mean/median/mode/knn/iterative
    categorical_imputation='mode',   # 类别型: mode/constant

    # ===== 异常值处理 =====
    remove_outliers=True,           # 移除异常值
    outliers_method='iforest',      # iforest/ee/lof
    outliers_threshold=0.05,        # 异常值比例

    # ===== 类别不平衡处理 =====
    fix_imbalance=True,             # 处理类别不平衡
    fix_imbalance_method='SMOTE',  # SMOTE/ADASYN/RandomOverSampler

    # ===== 数据类型指定 =====
    numeric_features=['age', 'income', 'score'],
    categorical_features=['city', 'gender', 'occupation'],
    date_features=['Date', 'created_at'],

    session_id=42
)
```

#### Step 4: 特征工程 | Feature Engineering (setup 中自动完成)
```python
clf = setup(
    data,
    target='target',

    # ===== 特征缩放 =====
    normalize=True,                 # 归一化
    normalize_method='zscore',     # zscore/minmax/maxabs/robust

    # ===== 特征变换 =====
    transformation=True,            # 变换使数据更接近正态分布
    transformation_method='yeo-johnson',  # yeo-johnson/quantile

    # ===== 特征选择 =====
    feature_selection=True,         # 特征选择
    feature_selection_method='classic',      # classic/univariate/sequential
    n_features_to_select=0.2,     # 选择20%最重要特征

    # ===== 降维 =====
    pca=True,                      # PCA降维
    pca_method='linear',           # linear/kernel/incremental
    pca_components=0.95,           # 保留95%方差

    # ===== 多重共线性处理 =====
    remove_multicollinearity=True,
    multicollinearity_threshold=0.9,

    # ===== 特征编码 =====
    ordinal_features={'education': ['high_school', 'bachelor', 'master', 'phd']},
    high_cardinality_features='frequency',  # 处理高基数类别特征

    # ===== 特征交互 =====
    polynomial_features=True,
    polynomial_degree=2,

    # ===== 分箱（离散化） =====
    bin_numeric_features=['age', 'income'],

    session_id=42
)
```

#### Step 5: 模型选择 | Model Selection
```python
# 比较所有模型
best_model = compare_models()

# 指定模型列表比较
best_model = compare_models(include=['lr', 'rf', 'xgboost', 'catboost', 'lightgbm'])

# 快速模式（排除耗时模型）
best_model = compare_models(turbo=True)

# 按特定指标排序
best_model = compare_models(sort='F1')  # 对于不平衡数据
```

#### Step 6: 模型训练 | Model Training
```python
# 创建模型
model = create_model('rf')

# 指定模型参数
model = create_model('xgboost', n_estimators=100, max_depth=5)
```

#### Step 7: 超参数调优 | Hyperparameter Tuning
```python
# 自动调优
tuned_model = tune_model(model)

# 自定义调优
tuned_model = tune_model(
    model,
    custom_grid={
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7, None],
        'learning_rate': [0.01, 0.1, 0.3]
    },
    optimize='Accuracy',           # 分类: Accuracy/AUC/Recall/Precision/F1/MCC
                                  # 回归: RMSE/MSE/MAE/R2/RMSLE/MAPE
    choose_better=True,            # 返回更好的模型
    n_iter=50                      # 迭代次数
)
```

#### Step 8: 模型评估 | Model Evaluation
```python
# 交互式评估
evaluate_model(tuned_model)

# 各种评估图表
plot_model(tuned_model, plot='auc')                # ROC曲线
plot_model(tuned_model, plot='confusion_matrix')   # 混淆矩阵
plot_model(tuned_model, plot='classification_report')  # 分类报告
plot_model(tuned_model, plot='learning_curve')    # 学习曲线
plot_model(tuned_model, plot='feature')            # 特征重要性
plot_model(tuned_model, plot='residuals')          # 残差图（回归）
plot_model(tuned_model, plot='error')              # 预测误差

# 交叉验证结果
results = pull()  # 获取当前实验结果
```

#### Step 9: 模型解释 | Model Interpretation
```python
# SHAP 解释
interpret_model(tuned_model)

# Permutation Importance
interpret_model(tuned_model, plot='correlation')

# 局部解释
interpret_model(tuned_model, plot='reason', observation=0)
```

#### Step 10: 模型集成 | Model Ensemble
```python
# Bagging
bagged = ensemble_model(tuned_model, method='Bagging')

# Boosting
boosted = ensemble_model(tuned_model, method='Boosting')

# 融合多个模型
blended = blend_models(
    estimator_list=['lr', 'dt', 'rf', 'xgboost'],
    method='soft',                  # soft/hard
    weights=[1, 2, 3, 2]           # 各模型权重
)

# 堆叠
stacked = stack_models(
    estimator_list=['lr', 'dt', 'rf'],
    meta_model='xgboost',
    restack=False                   # 是否允许基础模型使用原始特征
)
```

#### Step 11: 最终模型训练与预测 | Final Model Training & Prediction
```python
# 在全部数据上训练最终模型
final_model = finalize_model(tuned_model)

# 预测
predictions = predict_model(final_model, data=test)

# 预测概率（分类）
predictions = predict_model(
    final_model,
    data=test,
    probability_threshold=0.7       # 自定义阈值
)
```

#### Step 12: 模型保存与部署 | Model Save & Deployment
```python
# 保存模型（包含完整Pipeline）
save_model(final_model, 'my_model')

# 保存实验配置
save_experiment('my_experiment')

# 加载模型
loaded_model = load_model('my_model')

# 部署到云平台
deploy_model(
    final_model,
    platform='aws',                 # aws/gcp/azure
    authentication={
        'bucket': 'my-bucket'
    }
)

# 创建Web应用
create_app(final_model, app_path='app.py')

# 创建REST API
create_api(final_model, api_name='predict', api_file='predict.py')

# 创建Docker
create_docker('my_model', docker_path='Dockerfile')
```

---

## AutoML 完整流程示例 | Complete AutoML Pipeline Example

```python
from pycaret.classification import *
import pandas as pd

# ========== Step 1: 数据加载 ==========
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# ========== Step 2: 数据探索 ==========
print(f"训练集: {train.shape}, 测试集: {test.shape}")
print(f"缺失值:\n{train.isnull().sum()}")
print(f"目标分布:\n{train['target'].value_counts()}")

# ========== Step 3-4: 数据预处理 + 特征工程 ==========
clf = setup(
    train,
    target='target',

    # 数据预处理
    numeric_imputation='median',
    categorical_imputation='mode',
    remove_outliers=True,
    outliers_method='iforest',
    fix_imbalance=True,
    fix_imbalance_method='SMOTE',

    # 特征工程
    normalize=True,
    normalize_method='zscore',
    feature_selection=True,
    n_features_to_select=0.3,
    remove_multicollinearity=True,
    polynomial_features=True,
    polynomial_degree=2,

    # 划分配置
    train_size=0.8,
    fold_strategy='stratifiedkfold',
    fold=5,

    session_id=42
)

# ========== Step 5: 模型选择 ==========
best = compare_models(sort='AUC')

# ========== Step 6-7: 训练与调优 ==========
tuned = tune_model(best, optimize='AUC', n_iter=30)

# ========== Step 8-9: 评估与解释 ==========
evaluate_model(tuned)
interpret_model(tuned)

# ========== Step 10: 集成（可选） ==========
# ensemble = ensemble_model(tuned)

# ========== Step 11: 最终预测 ==========
final = finalize_model(tuned)
predictions = predict_model(final, data=test)

# ========== Step 12: 保存 ==========
save_model(final, 'best_model')
```

---

## 通用 API 参考 | Common API Reference

详细内容请参考 [utilities.md](references/utilities.md)

### 数据加载

```python
from pycaret.classification import get_data

# 列出数据集
all_datasets = get_data('index')

# 加载数据集
data = get_data('breast_cancer')
```

### 配置管理

```python
from pycaret.classification import get_config, set_config

# 获取配置
X_train = get_config('X_train')

# 设置配置
set_config('seed', 123)
```

### 模型操作

```python
# 比较模型
best = compare_models()

# 创建模型
model = create_model('rf')

# 调优模型
tuned = tune_model(model)

# 集成
ensemble = ensemble_model(model)

# 预测
predictions = predict_model(model, data=new_data)

# 保存/加载
save_model(model, 'my_model')
loaded = load_model('my_model')
```

---

## 详细文档索引 | Detailed Documentation Index

| 模块 | 包含内容 | 文件 |
|------|----------|------|
| 参数深度分析 | setup参数选择指南、决策树、实战配置 | [setup_parameters_deep_dive.md](references/setup_parameters_deep_dive.md) |
| Classification | setup 参数、模型列表、评估指标、工作流 | [classification.md](references/classification.md) |
| Regression | setup 参数、回归模型、评估指标、工作流 | [regression.md](references/regression.md) |
| Time Series | 时间序列特有参数、预测、季节性 | [time_series.md](references/time_series.md) |
| Clustering | 聚类算法、轮廓系数、分配标签 | [clustering.md](references/clustering.md) |
| Anomaly | 异常检测算法、可视化 | [anomaly.md](references/anomaly.md) |
| NLP | 主题模型、文本处理、词云 | [nlp.md](references/nlp.md) |
| Association Rules | 关联规则、支持度、置信度 | [association_rules.md](references/association_rules.md) |
| Utilities | 通用函数、部署、应用生成 | [utilities.md](references/utilities.md) |

---

## 代码模板 | Code Templates

### 分类任务模板

```python
from pycaret.classification import *

data = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

clf = setup(data, target='target', train_size=0.8)
best = compare_models()
tuned = tune_model(best)
ensemble = ensemble_model(tuned)
predictions = predict_model(ensemble, data=test)
save_model(ensemble, 'classifier')
```

### 回归任务模板

```python
from pycaret.regression import *

data = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

reg = setup(data, target='price', normalize=True)
best = compare_models()
tuned = tune_model(best, optimize='RMSE')
predictions = predict_model(tuned, data=test)
save_model(tuned, 'regressor')
```

### 时间序列模板

```python
from pycaret.time_series import *

data = get_data('airline')
ts = setup(data, fh=12, seasonal_period=12)
best = compare_models()
model = create_model('arima')
predictions = predict_model(model, fh=24)
```

---

## 最佳实践 | Best Practices

1. **数据预处理**: 使用 `normalize=True`, `remove_outliers=True` 等参数
2. **模型选择**: 用 `compare_models(turbo=True)` 快速验证
3. **超参数调优**: 根据时间预算设置 `n_iter`
4. **模型集成**: 复杂任务使用 `ensemble_model` 或 `stack_models`
5. **生产部署**: 使用 `finalize_model()` 在全量数据上训练
