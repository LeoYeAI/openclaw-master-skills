# PyCaret Regression 模块 | Regression Module

回归任务的完整 API 参考文档。

## setup() 函数

```python
from pycaret.regression import setup

# 基础用法
reg = setup(data, target='target_column')

# 完整参数（与 Classification 类似，但增加了 transform_target）
reg = setup(
    # ===== 必需参数 =====
    data,                                 # 数据框（必需）
    target=-1,                           # 目标列
    
    # ===== 数据划分 =====
    train_size=0.7,
    test_data=None,
    data_split_shuffle=True,
    data_split_stratify=False,            # 回归通常不用分层
    fold_strategy='kfold',              # 回归默认用 kfold
    fold=10,
    fold_shuffle=False,
    fold_groups=None,
    
    # ===== 索引处理 =====
    index=True,
    
    # ===== 特征类型指定 =====
    numeric_features=None,
    categorical_features=None,
    ordinal_features=None,
    date_features=None,
    text_features=None,
    ignore_features=None,
    keep_features=None,
    
    # ===== 数据预处理 =====
    preprocess=True,
    imputation_type='simple',
    numeric_imputation='mean',
    categorical_imputation='mode',
    iterative_imputation_iters=5,
    numeric_iterative_imputer='lightgbm',
    categorical_iterative_imputer='lightgbm',
    text_features_method='tf-idf',
    max_encoding_ohe=25,
    encoding_method=None,
    rare_to_value=None,
    rare_value='rare',
    
    # ===== 特征工程 =====
    polynomial_features=False,
    polynomial_degree=2,
    low_variance_threshold=None,
    group_features=None,
    drop_groups=False,
    remove_multicollinearity=False,
    multicollinearity_threshold=0.9,
    bin_numeric_features=None,
    
    # ===== 离群值处理 =====
    remove_outliers=False,
    outliers_method='iforest',
    outliers_threshold=0.05,
    
    # ===== 目标变换（回归特有）=====
    transform_target=False,              # 是否变换目标变量
    transform_target_method='yeo-johnson',  # 变换方法
    
    # ===== 变换 =====
    transformation=False,
    transformation_method='yeo-johnson',
    normalize=False,
    normalize_method='zscore',
    
    # ===== 降维 =====
    pca=False,
    pca_method='linear',
    pca_components=None,
    
    # ===== 特征选择 =====
    feature_selection=False,
    feature_selection_method='classic',
    feature_selection_estimator='lightgbm',
    n_features_to_select=0.2,
    
    # ===== 自定义 Pipeline =====
    custom_pipeline=None,
    custom_pipeline_position=-1,
    
    # ===== 引擎配置 =====
    engine=None,
    
    # ===== 系统选项 =====
    n_jobs=-1,
    use_gpu=False,
    html=True,
    session_id=None,
    log_experiment=False,
    experiment_name=None,
    experiment_custom_tags=None,
    log_plots=False,
    log_profile=False,
    log_data=False,
    verbose=True,
    memory=True,
    profile=False,
    profile_kwargs={}
)
```

## 常用模型缩写

```python
# 线性模型
'lr'      # Linear Regression
'ridge'   # Ridge Regression
'lasso'   # Lasso Regression
'en'      # Elastic Net
'lar'     # Least Angle Regression
'br'      # Bayesian Ridge

# 树模型
'dt'      # Decision Tree Regressor
'rf'      # Random Forest Regressor
'et'      # Extra Trees Regressor

# Boosting
'gbr'     # Gradient Boosting Regressor
'ada'     # AdaBoost Regressor
'catboost' # CatBoost Regressor
'lightgbm' # LightGBM Regressor
'xgboost'  # XGBoost Regressor

# 其他
'knn'     # K-Nearest Neighbors Regressor
'mlp'     # MLP Regressor
```

## compare_models()

```python
from pycaret.regression import compare_models

# 比较所有模型
best = compare_models()

# 指定模型
best = compare_models(include=['lr', 'rf', 'xgboost'])

# 参数
best = compare_models(
    fold=5,
    round=4,
    sort='R2',           # 排序指标: 'R2', 'RMSE', 'MSE', 'MAE'
    n_select=1,
    turbo=True
)
```

## create_model()

```python
from pycaret.regression import create_model

# 创建模型
lr = create_model('lr')
rf = create_model('rf')
```

## tune_model()

```python
from pycaret.regression import tune_model

# 调优模型
tuned = tune_model(model, optimize='RMSE')
tuned = tune_model(model, optimize='R2')
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'residuals'` | 残差图 |
| `'error'` | 预测误差 |
| `'cooks'` | Cook's Distance |
| `'rfe'` | 递归特征消除 |
| `'learning_curve'` | 学习曲线 |
| `'validation_curve'` | 验证曲线 |
| `'manifold'` | 流形学习 |
| `'feature'` | 特征重要性 |
| `'feature_all'` | 所有特征重要性 |
| `'parameter'` | 模型参数 |

## 评估指标

| 指标 | 说明 |
|------|------|
| R2 | R² 决定系数 |
| RMSE | 均方根误差 |
| MSE | 均方误差 |
| MAE | 平均绝对误差 |
| MSLE | 均方对数误差 |
| MAPE | 平均绝对百分比误差 |

## 完整工作流示例

```python
from pycaret.regression import *

# 1. 加载数据
data = get_data('boston')

# 2. 初始化
reg = setup(data, target='medv', normalize=True, remove_outliers=True)

# 3. 比较模型
best = compare_models()

# 4. 调优
tuned = tune_model(best, optimize='RMSE')

# 5. 集成
ensemble = ensemble_model(tuned)

# 6. 评估
evaluate_model(ensemble)

# 7. 预测
predictions = predict_model(ensemble, data=test_data)

# 8. 保存
save_model(ensemble, 'best_regression_model')
```
