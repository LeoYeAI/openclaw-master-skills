# PyCaret 通用工具函数 | Utility Functions

所有 PyCaret 模块通用的辅助函数和工具。

## 数据加载

### get_data()

```python
from pycaret.classification import get_data

# 列出所有可用数据集
all_datasets = get_data('index')

# 加载数据集
data = get_data('breast_cancer')
data = get_data('iris')
data = get_data('boston')
data = get_data('juice')
data = get_data('bank')
data = get_data('credit')
```

## 配置管理

### get_config()

```python
from pycaret.classification import get_config

# 获取各种配置
X_train = get_config('X_train')
X_test = get_config('X_test')
y_train = get_config('y_train')
y_test = get_config('y_test')
pipeline = get_config('pipeline')
target = get_config('target_param')

# 所有可用配置
# 'X', 'X_train', 'X_test', 'y', 'y_train', 'y_test'
# 'X_train_transformed', 'X_test_transformed'
# 'target_param', 'pipeline', 'data', 'seed'
# 'n_jobs_param', 'html_param', 'master_pipeline'
```

### set_config()

```python
from pycaret.classification import set_config

# 修改配置
set_config('seed', 123)
set_config('n_jobs_param', -1)
set_config('html_param', False)
```

## 模型管理

### models()

```python
from pycaret.classification import models

# 获取所有可用模型
all_models = models()

# 只返回模型ID
model_ids = models()['ID'].tolist()
```

### get_metrics()

```python
from pycaret.classification import get_metrics

# 获取所有指标
metrics = get_metrics()
```

### add_metric() / remove_metric()

```python
from pycaret.classification import add_metric, remove_metric

# 添加自定义指标
add_metric(
    name='my_metric',
    score_func=my_score_function,
    greater_is_better=True
)

# 删除指标
remove_metric('my_metric')
```

## 日志与结果

### pull()

```python
from pycaret.classification import pull

# 获取评估结果
results = pull()
```

### get_logs()

```python
from pycaret.classification import get_logs

# 获取实验日志
logs = get_logs()
```

## 工具函数

### pycaret.utils

```python
from pycaret.utils import check_metric
from pycaret.utils import enable_colab, disable_colab
from pycaret.utils import version

# 检查指标
accuracy = check_metric(y_true, y_pred, 'Accuracy')

# Colab 优化
enable_colab()
disable_colab()

# 版本
print(version())
```

### check_fold()

```python
from pycaret.classification import check_fold

fold_params = check_fold()
```

## 模型部署

### save_model()

```python
from pycaret.classification import save_model

# 保存模型
save_model(model, 'my_model')
save_model(model, 'my_model', model_format='pickle')
```

### load_model()

```python
from pycaret.classification import load_model

# 加载模型
loaded_model = load_model('my_model')
```

### deploy_model()

```python
from pycaret.classification import deploy_model

# AWS
deploy_model(model, 'my_model', platform='aws', 
             authentication={'bucket_name': 'my-bucket'})

# GCP
deploy_model(model, 'my_model', platform='gcp',
             authentication={'project': 'my-project', 'bucket': 'my-bucket'})

# Azure
deploy_model(model, 'my_model', platform='azure',
             authentication={'storage_account': 'myaccount', 'container': 'mycontainer'})
```

## 应用生成

### create_app()

```python
from pycaret.classification import create_app

# 创建 Streamlit 应用
app = create_app(model)
```

### create_api()

```python
from pycaret.classification import create_api

# 创建 FastAPI
api = create_api(model, api_name='predict')
```

### create_docker()

```python
from pycaret.classification import create_docker

# 创建 Docker 文件
docker_file = create_docker('my_model')
```

## 完整 API 速查表

| 函数 | 功能 |
|------|------|
| `setup()` | 初始化环境 |
| `get_data()` | 加载数据集 |
| `models()` | 获取可用模型 |
| `compare_models()` | 比较模型 |
| `create_model()` | 创建模型 |
| `tune_model()` | 调优模型 |
| `ensemble_model()` | 集成模型 |
| `blend_models()` | 融合模型 |
| `stack_models()` | 堆叠模型 |
| `automl()` | 自动 ML |
| `predict_model()` | 预测 |
| `evaluate_model()` | 评估 |
| `plot_model()` | 绘图 |
| `interpret_model()` | 解释 |
| `finalize_model()` | 最终训练 |
| `save_model()` | 保存 |
| `load_model()` | 加载 |
| `deploy_model()` | 部署 |
| `get_config()` | 获取配置 |
| `set_config()` | 设置配置 |
| `pull()` | 获取结果 |
| `get_logs()` | 获取日志 |
| `get_metrics()` | 获取指标 |
| `add_metric()` | 添加指标 |
| `calibrate_model()` | 校准模型 |
| `optimize_threshold()` | 优化阈值 |
| `dashboard()` | 仪表板 |
| `create_app()` | 创建应用 |
| `create_api()` | 创建 API |
| `create_docker()` | 创建 Docker |
