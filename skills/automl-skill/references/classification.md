# PyCaret Classification 模块 | Classification Module

分类任务的完整 API 参考文档。

## setup() 函数

```python
from pycaret.classification import setup

# 基础用法
clf = setup(data, target='target_column')

# 完整参数
clf = setup(
    # ===== 必需参数 =====
    data,                                 # 数据框（必需）
    target=-1,                           # 目标列索引/名称/序列
    
    # ===== 数据划分 =====
    train_size=0.7,                      # 训练集比例
    test_data=None,                      # 外部测试集
    data_split_shuffle=True,             # 是否打乱
    data_split_stratify=True,            # 分层抽样
    fold_strategy='stratifiedkfold',    # 折策略: 'kfold', 'stratifiedkfold', 'groupkfold'
    fold=10,                            # 交叉验证折数
    fold_shuffle=False,                  # 折是否打乱
    fold_groups=None,                    # 分组（用于 GroupKFold）
    
    # ===== 索引处理 =====
    index=True,                          # 索引处理: True/False/列名/位置
    
    # ===== 特征类型指定 =====
    numeric_features=None,              # 指定数值特征
    categorical_features=None,          # 指定类别特征
    ordinal_features=None,              # 有序类别: {'col': ['low', 'medium', 'high']}
    date_features=None,                 # 日期特征
    text_features=None,                 # 文本特征
    ignore_features=None,               # 忽略的特征
    keep_features=None,                 # 保留的特征
    
    # ===== 数据预处理 =====
    preprocess=True,                    # 是否预处理
    imputation_type='simple',           # 插补类型: 'simple', 'iterative', None
    numeric_imputation='mean',          # 数值型: 'mean', 'median', 'mode', 'knn'
    categorical_imputation='mode',      # 类别型: 'mode', 'constant'
    iterative_imputation_iters=5,      # 迭代插补次数
    numeric_iterative_imputer='lightgbm',  # 数值迭代插补器
    categorical_iterative_imputer='lightgbm',  # 类别迭代插补器
    text_features_method='tf-idf',      # 文本方法: 'tf-idf', 'bow'
    max_encoding_ohe=25,                # OHE 编码的最大类别数
    encoding_method=None,               # 编码方法（category_encoders）
    rare_to_value=None,                # 稀有类别阈值
    rare_value='rare',                  # 稀有类别替换值
    
    # ===== 特征工程 =====
    polynomial_features=False,          # 多项式特征
    polynomial_degree=2,                # 多项式阶数
    low_variance_threshold=None,       # 低方差阈值
    group_features=None,                # 分组特征
    drop_groups=False,                  # 是否删除分组特征
    remove_multicollinearity=False,    # 移除多重共线性
    multicollinearity_threshold=0.9,    # 多重共线性阈值
    bin_numeric_features=None,         # 离散化数值特征
    
    # ===== 离群值处理 =====
    remove_outliers=False,              # 是否移除离群值
    outliers_method='iforest',          # 方法: 'iforest', 'ee', 'lof'
    outliers_threshold=0.05,            # 离群值阈值
    
    # ===== 类别平衡 =====
    fix_imbalance=False,                # 是否平衡类别
    fix_imbalance_method='SMOTE',      # 平衡方法: 'SMOTE', 'RandomUnderSampler'
    
    # ===== 变换 =====
    transformation=False,                # 是否变换
    transformation_method='yeo-johnson',  # 变换方法
    normalize=False,                    # 是否归一化
    normalize_method='zscore',         # 归一化方法: 'zscore', 'minmax', 'maxabs', 'robust'
    
    # ===== 降维 =====
    pca=False,                         # 是否PCA
    pca_method='linear',               # PCA方法: 'linear', 'kernel', 'incremental'
    pca_components=None,               # PCA主成分数
    
    # ===== 特征选择 =====
    feature_selection=False,            # 是否特征选择
    feature_selection_method='classic', # 方法: 'classic', 'univariate'
    feature_selection_estimator='lightgbm',  # 选择器
    n_features_to_select=0.2,           # 选择特征比例/数量
    
    # ===== 自定义 Pipeline =====
    custom_pipeline=None,               # 自定义转换器
    custom_pipeline_position=-1,        # 位置
    
    # ===== 引擎配置 =====
    engine=None,                        # 引擎配置
    
    # ===== 系统选项 =====
    n_jobs=-1,                         # 并行任务数
    use_gpu=False,                     # 是否使用GPU
    html=True,                         # 是否显示HTML
    session_id=None,                   # 随机种子
    log_experiment=False,              # 记录实验
    experiment_name=None,               # 实验名称
    experiment_custom_tags=None,       # 自定义标签
    log_plots=False,                   # 自动记录图表
    log_profile=False,                  # 记录数据Profile
    log_data=False,                     # 记录数据
    verbose=True,                       # 详细输出
    memory=True,                        # 缓存
    profile=False,                      # 生成报告
    profile_kwargs={}                   # 报告参数
)
```

## 常用模型缩写

```python
# 线性模型
'lr'    # Logistic Regression
'ridge' # Ridge Classifier
'lda'   # Linear Discriminant Analysis
'qda'   # Quadratic Discriminant Analysis

# 树模型
'dt'    # Decision Tree
'rf'    # Random Forest
'et'    # Extra Trees

# Boosting
'gbc'      # Gradient Boosting Classifier
'ada'      # AdaBoost Classifier
'catboost' # CatBoost Classifier
'lightgbm' # LightGBM Classifier
'xgboost'  # XGBoost Classifier

# 其他
'nb'   # Naive Bayes
'svm'  # Support Vector Machine
'rbfsvm'  # RBF SVM
'knn'  # K-Nearest Neighbors
'mlp'  # Multi-Layer Perceptron
```

## compare_models()

```python
from pycaret.classification import compare_models

# 比较所有模型
best = compare_models()

# 指定模型
best = compare_models(include=['lr', 'dt', 'rf', 'xgboost'])

# 参数
best = compare_models(
    fold=5,
    round=4,
    sort='Accuracy',       # 排序指标
    n_select=1,
    turbo=True,
    verbose=True
)
```

## create_model()

```python
from pycaret.classification import create_model

# 创建模型
lr = create_model('lr')
rf = create_model('rf')

# 完整参数
model = create_model(
    estimator='rf',
    fold=5,
    round=4,
    verbose=True,
    **kwargs
)
```

## tune_model()

```python
from pycaret.classification import tune_model

# 调优模型
tuned = tune_model(model)

# 自定义网格
tuned = tune_model(
    model,
    custom_grid={'n_estimators': [100, 200], 'max_depth': [3, 5, 7]},
    optimize='Accuracy',
    n_iter=10
)
```

## ensemble_model()

```python
from pycaret.classification import ensemble_model

# Bagging
bagged = ensemble_model(model, method='Bagging')

# Boosting
boosted = ensemble_model(model, method='Boosting')
```

## blend_models() & stack_models()

```python
from pycaret.classification import blend_models, stack_models

# 融合
blended = blend_models(estimator_list=['lr', 'dt', 'rf'], method='soft')

# 堆叠
stacked = stack_models(
    estimator_list=['lr', 'dt', 'rf'],
    meta_model='lr'
)
```

## plot_model() 图表类型

| 图表 | 说明 |
|------|------|
| `'auc'` | ROC AUC 曲线 |
| `'pr'` | Precision-Recall 曲线 |
| `'confusion_matrix'` | 混淆矩阵 |
| `'threshold'` | 阈值分析 |
| `'learning_curve'` | 学习曲线 |
| `'validation_curve'` | 验证曲线 |
| `'manifold'` | 流形学习 |
| `'feature'` | 特征重要性 |
| `'feature_all'` | 所有特征重要性 |
| `'classification_report'` | 分类报告 |
| `'error'` | 预测误差 |
| `'calibration_curve'` | 校准曲线 |
| `'ks_statistic'` | KS 统计量 |
| `'lift_curve'` | Lift 曲线 |
| `'gain_curve'` | Gain 曲线 |

## evaluate_model()

```python
from pycaret.classification import evaluate_model

evaluate_model(model)
```

## predict_model()

```python
from pycaret.classification import predict_model

predictions = predict_model(model, data=new_data)
# 返回: Label, Score
```

## 评估指标

| 指标 | 说明 |
|------|------|
| Accuracy | 准确率 |
| AUC | ROC AUC |
| Recall | 召回率 |
| Precision | 精确率 |
| F1 | F1 分数 |
| Kappa | Cohen's Kappa |
| MCC | Matthews Correlation Coefficient |

## 完整工作流示例

```python
from pycaret.classification import *

# 1. 加载数据
data = get_data('breast_cancer')

# 2. 初始化
clf = setup(data, target='target', normalize=True)

# 3. 比较模型
best = compare_models()

# 4. 调优
tuned = tune_model(best)

# 5. 集成
ensemble = ensemble_model(tuned)

# 6. 评估
evaluate_model(ensemble)

# 7. 预测
predictions = predict_model(ensemble, data=test_data)

# 8. 保存
save_model(ensemble, 'best_model')
```
