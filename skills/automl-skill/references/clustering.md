# PyCaret Clustering 模块 | Clustering Module

聚类任务的完整 API 参考文档。

## setup() 函数

```python
from pycaret.clustering import setup

# 基础用法（无 target 参数）
clu = setup(data)

# 完整参数
clu = setup(
    # ===== 必需参数 =====
    data,                                 # 数据框（必需）
    
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
    imputation_type='simple',            # 聚类只支持 'simple'
    numeric_imputation='mean',
    categorical_imputation='constant',  # 聚类默认 constant
    text_features_method='tf-idf',      # 文本方法
    max_encoding_ohe=-1,                # -1 表示全部用 OHE
    encoding_method=None,
    rare_to_value=None,
    rare_value='rare',
    
    # ===== 特征工程 =====
    polynomial_features=False,
    polynomial_degree=2,
    low_variance_threshold=None,
    remove_multicollinearity=False,
    multicollinearity_threshold=0.9,
    bin_numeric_features=None,
    
    # ===== 离群值处理 =====
    remove_outliers=False,
    outliers_method='iforest',
    outliers_threshold=0.05,
    
    # ===== 变换 =====
    transformation=False,
    transformation_method='yeo-johnson',
    normalize=False,
    normalize_method='zscore',
    
    # ===== 降维 =====
    pca=False,
    pca_method='linear',
    pca_components=None,
    
    # ===== 自定义 Pipeline =====
    custom_pipeline=None,
    custom_pipeline_position=-1,
    
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

## 常用聚类算法

```python
'kmeans'    # K-Means Clustering
'hclust'    # Hierarchical Clustering
'sc'        # Spectral Clustering
'meanshift' # Mean Shift Clustering
'ap'        # Affinity Propagation
'birch'     # BIRCH Clustering
'dbscan'    # DBSCAN
'kproto'    # K-Prototypes (for mixed data)
```

## create_model()

```python
from pycaret.clustering import create_model

# K-Means
kmeans = create_model('kmeans', num_clusters=3)

# 层次聚类
hclust = create_model('hclust', num_clusters=3)

# DBSCAN
dbscan = create_model('dbscan', eps=0.5, min_samples=5)

# 完整参数
model = create_model(
    'kmeans',
    num_clusters=4,
    round=4,
    verbose=True
)
```

## tune_model()

```python
from pycaret.clustering import tune_model

# 调优聚类模型
tuned = tune_model('kmeans')
```

## assign_model()

```python
from pycaret.clustering import assign_model

# 分配聚类标签
results = assign_model(model)
# 返回原始数据 + Cluster 列
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'cluster'` | Cluster PCA Plot (2D) |
| `'tsne'` | Cluster t-SNE (3D) |
| `'elbow'` | Elbow Plot |
| `'silhouette'` | Silhouette Plot |
| `'distance'` | Distance Plot |
| `'distribution'` | Distribution Plot |

## evaluate_model()

```python
from pycaret.clustering import evaluate_model

evaluate_model(model)
```

## predict_model()

```python
from pycaret.clustering import predict_model

# 预测新数据
predictions = predict_model(model, data=new_data)
```

## 评估指标

```python
from pycaret.clustering import get_metrics

metrics = get_metrics()
# 可用指标: silhouette, calinski_harabasz, davies_bouldin, rand
```

## 完整工作流示例

```python
from pycaret.clustering import *

# 1. 加载数据
data = get_data('jewellery')

# 2. 初始化
clu = setup(data, normalize=True)

# 3. 创建模型
kmeans = create_model('kmeans', num_clusters=4)

# 4. 调优
tuned = tune_model(kmeans)

# 5. 分配标签
results = assign_model(tuned)

# 6. 可视化
plot_model(tuned, plot='elbow')
plot_model(tuned, plot='silhouette')
plot_model(tuned, plot='cluster')

# 7. 评估
evaluate_model(tuned)

# 8. 预测新数据
predictions = predict_model(tuned, data=new_data)
```
