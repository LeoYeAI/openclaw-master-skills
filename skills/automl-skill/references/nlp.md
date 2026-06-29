# PyCaret NLP 模块 | NLP Module

自然语言处理任务的完整 API 参考文档。

## setup() 函数

```python
from pycaret.nlp import setup

# 基础用法
nlp = setup(data, target='text_column')

# 完整参数
nlp = setup(
    # ===== 必需参数 =====
    data,                                 # 数据框（必需）
    target,                              # 文本列名（必需）
    
    # ===== 特征指定 =====
    numeric_features=None,               # 数值特征
    categorical_features=None,           # 类别特征
    ignore_features=None,                # 忽略的特征
    
    # ===== 数据预处理 =====
    imputation_type='simple',           # 插补类型
    max_encoding_ohe=25,                # OHE 编码数
    encoding_method=None,                # 编码方法
    
    # ===== 文本处理 =====
    text_features_method='tf-idf',      # 文本特征方法: 'tf-idf', 'bow', 'embeddings'
    text_aggregation='sum',             # 聚合方式: 'sum', 'mean', 'median', 'max', 'min'
    text_feature_extract=None,          # 特征提取: None, 'tokenize'
    
    # ===== 降维 =====
    pca=False,
    pca_method='linear',
    pca_components=None,
    
    # ===== 聚类配置 =====
    clustering=False,                    # 是否进行聚类
    cluster_method='kmeans',           # 聚类方法
    
    # ===== 主题模型 =====
    topic_model=None,                   # 主题模型配置
    topic_model_name='lda',            # 模型名: 'lda', 'nmf', 'lsi', 'hdp'
    num_topics='auto',                  # 主题数量
    
    # ===== 系统选项 =====
    n_jobs=-1,
    html=True,
    session_id=None,
    log_experiment=False,
    experiment_name=None,
    verbose=True,
    profile=False
)
```

## 常用主题模型

```python
'lda'    # Latent Dirichlet Allocation
'nmf'    # Non-Negative Matrix Factorization
'lsi'    # Latent Semantic Indexing
'hdp'    # Hierarchical Dirichlet Process
```

## create_model()

```python
from pycaret.nlp import create_model

# 创建主题模型
lda = create_model('lda', num_topics=4)

# 带参数
lda = create_model('lda', num_topics=4, doc_topic_prior=0.1, topic_word_prior=0.01)
nmf = create_model('nmf', num_topics=4)
```

## tune_model()

```python
from pycaret.nlp import tune_model

# 调优
tuned = tune_model(lda)
```

## assign_model()

```python
from pycaret.nlp import assign_model

# 分配主题
results = assign_model(lda)
# 返回原始数据 + Topic 相关列
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'wordcloud'` | 词云 |
| `'frequency'` | 词频图 |
| `'ngram'` | N-gram 图 |
| `'sentiment'` | 情感分布 |
| `'dimension'` | 维度分布 |
| `'topic_distribution'` | 主题分布 |
| `'topic_model'` | 主题模型可视化 |

## evaluate_model()

```python
from pycaret.nlp import evaluate_model

evaluate_model(lda)
```

## predict_model()

```python
from pycaret.nlp import predict_model

# 预测新文本
predictions = predict_model(lda, data=new_texts)
```

## 完整工作流示例

```python
from pycaret.nlp import *

# 1. 加载数据
data = get_data('kiva')

# 2. 初始化
nlp = setup(data, target='loan_theme')

# 3. 创建主题模型
lda = create_model('lda', num_topics=4)

# 4. 调优
tuned = tune_model(lda)

# 5. 分配主题
results = assign_model(tuned)

# 6. 可视化
plot_model(tuned, plot='wordcloud')
plot_model(tuned, plot='frequency')
plot_model(tuned, plot='topic_distribution')

# 7. 评估
evaluate_model(tuned)
```

## 文本分类

```python
# 使用 pycaret.text 进行文本分类
from pycaret.text import *

clf = setup(data, target='target_column')
best = compare_models()
```

## 情感分析

```python
# 情感分析
sentiment = create_model('sentiment')
results = assign_model(sentiment)
```
