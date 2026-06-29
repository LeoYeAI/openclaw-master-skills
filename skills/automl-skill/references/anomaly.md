# PyCaret Anomaly 模块 | Anomaly Detection Module

异常检测任务的完整 API 参考文档。

## setup() 函数

```python
from pycaret.anomaly import setup

# 基础用法
ano = setup(data)

# 参数与 Clustering 模块基本相同
ano = setup(
    data,
    index=True,
    numeric_features=None,
    categorical_features=None,
    ordinal_features=None,
    date_features=None,
    text_features=None,
    ignore_features=None,
    keep_features=None,
    preprocess=True,
    imputation_type='simple',
    numeric_imputation='mean',
    categorical_imputation='constant',
    text_features_method='tf-idf',
    max_encoding_ohe=-1,
    encoding_method=None,
    rare_to_value=None,
    rare_value='rare',
    polynomial_features=False,
    polynomial_degree=2,
    low_variance_threshold=None,
    remove_multicollinearity=False,
    multicollinearity_threshold=0.9,
    bin_numeric_features=None,
    remove_outliers=False,
    outliers_method='iforest',
    outliers_threshold=0.05,
    transformation=False,
    transformation_method='yeo-johnson',
    normalize=False,
    normalize_method='zscore',
    pca=False,
    pca_method='linear',
    pca_components=None,
    custom_pipeline=None,
    custom_pipeline_position=-1,
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

## 常用异常检测算法

```python
'iforest'   # Isolation Forest
'ee'        # Elliptic Envelope
'lof'       # Local Outlier Factor
'svm'       # One-Class SVM
'pca'       # PCA-based Outlier Detection
'kde'       # Kernel Density Estimation
```

## create_model()

```python
from pycaret.anomaly import create_model

# Isolation Forest
iforest = create_model('iforest')

# Elliptic Envelope
ee = create_model('ee')

# Local Outlier Factor
lof = create_model('lof')

# One-Class SVM
svm = create_model('svm')

# 带参数
iforest = create_model('iforest', contamination=0.1, random_state=42)
```

## tune_model()

```python
from pycaret.anomaly import tune_model

# 调优
tuned = tune_model('iforest')
```

## assign_model()

```python
from pycaret.anomaly import assign_model

# 分配异常标签
results = assign_model(model)
# 返回原始数据 + Cluster 列 (1=正常, -1=异常)
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'tsne'` | t-SNE 可视化 |
| `'umap'` | UMAP 可视化 |
| `'cluster'` | Cluster PCA Plot |

## evaluate_model()

```python
from pycaret.anomaly import evaluate_model

evaluate_model(model)
```

## predict_model()

```python
from pycaret.anomaly import predict_model

# 预测新数据
predictions = predict_model(model, data=new_data)
# 返回 Label (1=正常, -1=异常) 和 Score
```

## 完整工作流示例

```python
from pycaret.anomaly import *

# 1. 加载数据
data = get_data('outlier')

# 2. 初始化
ano = setup(data, normalize=True)

# 3. 创建模型
iforest = create_model('iforest', contamination=0.05)

# 4. 调优
tuned = tune_model(iforest)

# 5. 分配标签
results = assign_model(tuned)

# 6. 可视化
plot_model(tuned, plot='tsne')

# 7. 评估
evaluate_model(tuned)

# 8. 预测新数据
predictions = predict_model(tuned, data=new_data)
```
