# PyCaret Time Series 模块 | Time Series Module

时间序列预测的完整 API 参考文档。

## setup() 函数

```python
from pycaret.time_series import setup

# 基础用法（不需要 target 参数）
ts = setup(data, fh=12)

# 完整参数
ts = setup(
    # ===== 必需参数 =====
    data,                                 # Series 或 DataFrame（必需）
    
    # ===== 目标指定 =====
    target=None,                         # 目标列名（DataFrame 时必需）
    index=None,                          # 日期索引列名
    
    # ===== 时间序列特有参数 =====
    fh=1,                                # 预测步长: 整数/列表
    seasonal_period=None,                # 季节周期: 整数/列表/'auto'
    sp_detection='auto',                 # 季节检测方法
    max_sp_to_consider=60,                # 最大季节周期
    remove_harmonics=False,              # 移除谐波
    harmonic_order_method='harmonic_max', # 谐波阶数方法
    num_sps_to_use=1,                    # 使用的季节周期数
    seasonality_type='mul',              # 季节类型: 'add', 'mul'
    point_alpha=None,                   # 点预测置信度
    coverage=0.9,                        # 预测区间覆盖率
    enforce_exogenous=True,              # 是否强制使用外生变量
    
    # ===== 交叉验证 =====
    fold_strategy='expanding',           # 折策略: 'expanding', 'sliding'
    fold=3,                             # 折数
    hyperparameter_split='all',         # 超参分割: 'all', 'train', 'test'
    ignore_seasonality_test=False,       # 忽略季节性检验
    
    # ===== 特征指定 =====
    ignore_features=None,               # 忽略的特征
    
    # ===== 目标变量处理 =====
    numeric_imputation_target=None,      # 目标插补: 'drift', 'linear', 'mean', 'median', 'bfill', 'ffill'
    transform_target=None,               # 目标变换: 'box-cox', 'log', 'sqrt', 'exp', 'cos'
    scale_target=None,                  # 目标缩放: 'zscore', 'minmax'
    fe_target_rr=None,                  # 目标特征工程
    
    # ===== 外生变量处理 =====
    numeric_imputation_exogenous=None,  # 外生变量插补
    transform_exogenous=None,            # 外生变量变换
    scale_exogenous=None,                # 外生变量缩放
    fe_exogenous=None,                  # 外生变量特征工程
    
    # ===== 系统选项 =====
    n_jobs=-1,
    use_gpu=False,
    custom_pipeline=None,
    html=True,
    session_id=None,
    log_experiment=False,
    experiment_name=None,
    experiment_custom_tags=None,
    log_plots=False,
    log_profile=False,
    log_data=False,
    engine=None,
    verbose=True,
    profile=False,
    profile_kwargs={},
    fig_kwargs={}
)
```

## 常用模型

```python
# 统计模型
'arima'     # ARIMA
'auto_arima'  # Auto ARIMA
'ets'       # Exponential Smoothing
'theta'     # Theta Method
'naive'     # Naive Forecaster
'snaive'    # Seasonal Naive
'grand_means'  # Grand Means
'polytrend' # Polynomial Trend

# 机器学习模型
'exp_smooth'  # Exponential Smoothing
'bulima'    # Basic Unobserved Components
'lr'        # Linear Regression
'ridge'     # Ridge Regression
'lasso'     # Lasso Regression
```

## compare_models()

```python
from pycaret.time_series import compare_models

# 比较所有模型
best = compare_models()

# 指定模型
best = compare_models(include=['arima', 'ets', 'theta'])

# 参数
best = compare_models(
    fold=3,
    sort='SMAPE',      # 排序指标: 'SMAPE', 'MAE', 'RMSE', 'MSE'
    n_select=1
)
```

## create_model()

```python
from pycaret.time_series import create_model

# 创建模型
arima = create_model('arima')
ets = create_model('ets')

# 带参数
arima = create_model('arima', seasonal_order=(1,1,1,12))
```

## tune_model()

```python
from pycaret.time_series import tune_model

# 调优
tuned = tune_model(arima)
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'ts'` | 时间序列图 |
| `'tsacf'` | ACF 图 |
| `'tspacf'` | PACF 图 |
| `'decomp'` | 分解图 |
| `'diagnostics'` | 诊断图 |
| `'cv'` | 交叉验证图 |
| `'forecast'` | 预测图 |
| `'residuals'` | 残差图 |

## check_stats()

```python
from pycaret.time_series import check_stats

# 平稳性检验
stats = check_stats()
```

## 评估指标

| 指标 | 说明 |
|------|------|
| SMAPE | 对称平均绝对百分比误差 |
| MAE | 平均绝对误差 |
| RMSE | 均方根误差 |
| MSE | 均方误差 |
| R2 | R² 决定系数 |

## 完整工作流示例

```python
from pycaret.time_series import *

# 1. 加载数据
data = get_data('airline')

# 2. 初始化
ts = setup(data, fh=12, seasonal_period=12)

# 3. 比较模型
best = compare_models()

# 4. 创建模型
model = create_model('arima')

# 5. 调优
tuned = tune_model(model)

# 6. 评估
evaluate_model(tuned)

# 7. 预测
predictions = predict_model(tuned, fh=24)

# 8. 保存
save_model(tuned, 'ts_model')
```

## 预测参数

```python
# 使用训练好的模型进行预测
predictions = predict_model(model, fh=24)
predictions = predict_model(model, horizon=24, step=1)
```
