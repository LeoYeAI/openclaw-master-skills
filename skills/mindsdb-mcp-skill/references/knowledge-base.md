# MindsDB 知识库 (KD/RAG) 构建指南

## 概述

MindsDB的知识库（Knowledge Database，简称KD）功能基于RAG（Retrieval-Augmented Generation）技术，允许你创建能够存储和检索结构化或非结构化数据的系统，支持智能问答、文档检索等AI应用。

## 核心概念

### RAG (Retrieval-Augmented Generation)
- **检索增强生成**: 结合向量检索和LLM生成
- **向量存储**: 将文本转换为向量进行相似性搜索
- **嵌入模型**: 将文本转换为数值向量的模型

### 知识库组件
1. **向量存储**: 存储文档的向量表示
2. **嵌入模型**: 用于文本向量化
3. **智能Agent**: 结合知识库进行问答的代理
4. **检索机制**: 基于相似度的文档检索

## 构建知识库的完整流程

### 步骤1: 创建RAG数据库

```sql
-- 创建知识库数据库
CREATE DATABASE my_knowledge_base 
WITH ENGINE = 'rag' 
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2';
```

**参数说明:**
- `ENGINE = 'rag'`: 使用RAG引擎
- `storage`: 向量存储类型
  - `vector_store`: 默认向量存储
  - `chroma`: Chroma向量数据库
  - `faiss`: FAISS向量索引
- `embedding_model`: 嵌入模型
  - `sentence-transformers/all-MiniLM-L6-v2`: 轻量级模型
  - `sentence-transformers/all-mpnet-base-v2`: 高质量模型
  - `openai/text-embedding-ada-002`: OpenAI嵌入

### 步骤2: 导入知识内容

#### 从PDF文件导入

```sql
-- 创建PDF数据源
CREATE DATABASE pdf_source
WITH ENGINE = 'files',
PARAMETERS = {
  'path': '/path/to/pdfs',
  'format': 'pdf'
};

-- 导入PDF内容到知识库
INSERT INTO my_knowledge_base (content, metadata)
SELECT text, {'source': 'manuals', 'type': 'pdf'} 
FROM pdf_source;
```

#### 从文本文件导入

```sql
-- 创建文本数据源
CREATE DATABASE text_source
WITH ENGINE = 'files',
PARAMETERS = {
  'path': '/path/to/texts',
  'format': 'txt'
};

-- 导入文本内容
INSERT INTO my_knowledge_base (content, metadata)
SELECT text, {'source': 'documents', 'type': 'text'} 
FROM text_source;
```

#### 从数据库导入

```sql
-- 从现有数据库表导入
INSERT INTO my_knowledge_base (content, metadata)
SELECT description, {'table': 'products', 'id': product_id} 
FROM mysql.products;

-- 从多个表导入
INSERT INTO my_knowledge_base (content, metadata)
SELECT 
  CONCAT(title, ' ', description) as content,
  {'table': 'articles', 'id': article_id, 'category': category}
FROM postgres.articles;
```

#### 从网页导入

```sql
-- 创建网页数据源
CREATE DATABASE web_source
WITH ENGINE = 'web',
PARAMETERS = {
  'urls': [
    'https://docs.example.com/guide',
    'https://docs.example.com/api'
  ]
};

-- 导入网页内容
INSERT INTO my_knowledge_base (content, metadata)
SELECT text, {'source': 'web', 'url': url} 
FROM web_source;
```

### 步骤3: 创建智能Agent

#### 基础Agent

```sql
-- 创建问答Agent
CREATE AGENT tech_support 
USING model={'provider':'openai','model_name':'gpt-4'},
       data={'knowledge_bases':['my_knowledge_base']};
```

**参数说明:**
- `model`: 使用的LLM模型
  - `provider`: 模型提供商（openai, anthropic, cohere等）
  - `model_name`: 具体模型名称
- `data`: 数据配置
  - `knowledge_bases`: 关联的知识库列表

#### 高级Agent配置

```sql
-- 创建高级Agent
CREATE AGENT customer_service
USING model={
        'provider':'anthropic',
        'model_name':'claude-3-opus',
        'temperature':0.7,
        'max_tokens':2000
      },
      data={
        'knowledge_bases':['my_knowledge_base', 'faq_db'],
        'context_window':4000,
        'retrieval_top_k':5
      };
```

**高级参数:**
- `temperature`: 生成温度（0-1）
- `max_tokens`: 最大生成token数
- `context_window`: 上下文窗口大小
- `retrieval_top_k`: 检索的文档数量

#### 多知识库Agent

```sql
-- 创建使用多个知识库的Agent
CREATE AGENT research_assistant
USING model={'provider':'openai','model_name':'gpt-4'},
      data={
        'knowledge_bases':[
          'research_papers',
          'technical_docs',
          'internal_knowledge'
        ]
      };
```

### 步骤4: 查询知识库

#### 简单问答

```sql
-- 使用Agent回答问题
SELECT answer FROM tech_support 
WHERE question='设备报错0xE1怎么处理？';
```

#### 带上下文的查询

```sql
-- 提供上下文信息
SELECT answer FROM tech_support 
WHERE question='如何在Windows上安装软件？'
  AND context='用户使用Windows 10系统';
```

#### 批量查询

```sql
-- 批量问答
SELECT 
  question,
  answer
FROM tech_support
WHERE question IN (
  '如何重置密码？',
  '如何联系客服？',
  '如何退款？'
);
```

#### 检索相关文档

```sql
-- 检索相似文档
SELECT 
  content,
  similarity,
  metadata
FROM my_knowledge_base
WHERE query='产品安装步骤'
ORDER BY similarity DESC
LIMIT 5;
```

## 高级功能

### 向量存储优化

#### 使用Chroma

```sql
CREATE DATABASE chroma_kb
WITH ENGINE = 'rag'
USING storage='chroma',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      chroma_config={
        'persist_directory':'./chroma_db',
        'collection_name':'knowledge'
      };
```

#### 使用FAISS

```sql
CREATE DATABASE faiss_kb
WITH ENGINE = 'rag'
USING storage='faiss',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      faiss_config={
        'index_type':'IVF',
        'nlist':100
      };
```

### 自定义嵌入模型

```sql
-- 使用HuggingFace模型
CREATE DATABASE custom_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2';

-- 使用OpenAI嵌入
CREATE DATABASE openai_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='openai/text-embedding-ada-002';
```

### 多模态支持

#### 图像知识库

```sql
-- 创建图像知识库
CREATE DATABASE image_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='openai/clip-vit-base-patch32';

-- 导入图像
INSERT INTO image_kb (content, metadata)
SELECT image_data, {'type': 'product_image', 'id': product_id}
FROM images;
```

#### 语音知识库

```sql
-- 创建语音知识库
CREATE DATABASE audio_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='openai/whisper-large-v3';

-- 导入语音
INSERT INTO audio_kb (content, metadata)
SELECT transcript, {'type': 'call_recording', 'date': call_date}
FROM call_records;
```

### 知识库管理

#### 更新知识

```sql
-- 更新现有知识
UPDATE my_knowledge_base
SET content = '新的内容',
    metadata = JSON_SET(metadata, '$.updated', NOW())
WHERE id = 123;
```

#### 删除知识

```sql
-- 删除特定知识
DELETE FROM my_knowledge_base
WHERE metadata->>'$.source' = 'old_manuals';
```

#### 知识库统计

```sql
-- 查看知识库统计
SELECT 
  COUNT(*) as total_documents,
  COUNT(DISTINCT metadata->>'$.source') as unique_sources,
  AVG(LENGTH(content)) as avg_content_length
FROM my_knowledge_base;
```

## 实际应用场景

### 场景1: 技术支持系统

```sql
-- 1. 创建技术文档知识库
CREATE DATABASE tech_docs
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2';

-- 2. 导入技术文档
INSERT INTO tech_docs (content, metadata)
SELECT 
  CONCAT(title, '\n', description, '\n', solution),
  {'category': category, 'severity': severity}
FROM technical_manuals;

-- 3. 创建支持Agent
CREATE AGENT support_agent
USING model={'provider':'openai','model_name':'gpt-4'},
      data={'knowledge_bases':['tech_docs']};

-- 4. 使用Agent回答问题
SELECT answer FROM support_agent
WHERE question='服务器无法启动，错误代码500';
```

### 场景2: 产品推荐系统

```sql
-- 1. 创建产品知识库
CREATE DATABASE product_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2';

-- 2. 导入产品信息
INSERT INTO product_kb (content, metadata)
SELECT 
  CONCAT(name, ' ', features, ' ', description),
  {'category': category, 'price': price, 'rating': rating}
FROM products;

-- 3. 创建推荐Agent
CREATE AGENT recommender
USING model={'provider':'openai','model_name':'gpt-3.5-turbo'},
      data={'knowledge_bases':['product_kb']};

-- 4. 获取推荐
SELECT answer FROM recommender
WHERE question='推荐一款适合办公的笔记本电脑，预算8000元';
```

### 场景3: 法律文档检索

```sql
-- 1. 创建法律知识库
CREATE DATABASE legal_kb
WITH ENGINE = 'rag'
USING storage='chroma',
      embedding_model='sentence-transformers/all-mpnet-base-v2';

-- 2. 导入法律文档
INSERT INTO legal_kb (content, metadata)
SELECT 
  document_text,
  {'type': doc_type, 'date': doc_date, 'jurisdiction': jurisdiction}
FROM legal_documents;

-- 3. 创建法律Agent
CREATE AGENT legal_assistant
USING model={'provider':'anthropic','model_name':'claude-3-opus'},
      data={'knowledge_bases':['legal_kb']};

-- 4. 法律咨询
SELECT answer FROM legal_assistant
WHERE question='根据劳动法，加班费如何计算？';
```

### 场景4: 医疗健康问答

```sql
-- 1. 创建医疗知识库
CREATE DATABASE medical_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2';

-- 2. 导入医疗文档
INSERT INTO medical_kb (content, metadata)
SELECT 
  CONCAT(symptoms, ' ', diagnosis, ' ', treatment),
  {'specialty': specialty, 'severity': severity}
FROM medical_records;

-- 3. 创建医疗Agent
CREATE AGENT health_assistant
USING model={'provider':'openai','model_name':'gpt-4'},
      data={'knowledge_bases':['medical_kb']};

-- 4. 健康咨询
SELECT answer FROM health_assistant
WHERE question='头痛伴随恶心可能是什么原因？';
```

## 性能优化

### 1. 批量导入

```sql
-- 批量导入提高效率
INSERT INTO my_knowledge_base (content, metadata)
SELECT text, metadata
FROM large_source
BATCH SIZE 1000;
```

### 2. 索引优化

```sql
-- 创建元数据索引
CREATE INDEX idx_source ON my_knowledge_base((metadata->>'$.source'));
CREATE INDEX idx_type ON my_knowledge_base((metadata->>'$.type'));
```

### 3. 缓存配置

```sql
-- 配置向量缓存
CREATE DATABASE cached_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      cache_config={
        'enabled': true,
        'size': '1GB',
        'ttl': 3600
      };
```

### 4. 分片策略

```sql
-- 按类别分片
CREATE DATABASE kb_shard_1
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      shard_config={
        'key': 'category',
        'value': 'technology'
      };
```

## 安全和权限

### 访问控制

```sql
-- 创建只读知识库
CREATE DATABASE public_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      access_control={
        'read_users': ['public'],
        'write_users': ['admin']
      };
```

### 数据加密

```sql
-- 加密知识库
CREATE DATABASE secure_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      encryption={
        'enabled': true,
        'algorithm': 'AES-256'
      };
```

### 审计日志

```sql
-- 启用审计
CREATE DATABASE audited_kb
WITH ENGINE = 'rag'
USING storage='vector_store',
      embedding_model='sentence-transformers/all-MiniLM-L6-v2',
      audit={
        'enabled': true,
        'log_queries': true,
        'log_access': true
      };
```

## 监控和维护

### 性能监控

```sql
-- 查询性能
SELECT 
  AVG(similarity) as avg_similarity,
  COUNT(*) as query_count,
  AVG(response_time) as avg_response_time
FROM my_knowledge_base.query_logs
WHERE query_time > NOW() - INTERVAL 1 DAY;
```

### 存储管理

```sql
-- 查看存储使用情况
SELECT 
  table_name,
  ROUND(data_length / 1024 / 1024, 2) as size_mb,
  ROUND(index_length / 1024 / 1024, 2) as index_mb
FROM information_schema.tables
WHERE table_schema = 'my_knowledge_base';
```

### 定期维护

```sql
-- 清理过期数据
DELETE FROM my_knowledge_base
WHERE metadata->>'$.created' < NOW() - INTERVAL 1 YEAR;

-- 重建索引
OPTIMIZE TABLE my_knowledge_base;
```

## 最佳实践

1. **选择合适的嵌入模型**
   - 轻量级任务: `all-MiniLM-L6-v2`
   - 高质量任务: `all-mpnet-base-v2`
   - 多语言: `paraphrase-multilingual-MiniLM-L12-v2`

2. **优化文档大小**
   - 理想长度: 200-500词
   - 避免过长文档
   - 合理分块处理

3. **元数据设计**
   - 包含关键信息
   - 便于过滤和检索
   - 保持结构化

4. **定期更新**
   - 及时更新知识
   - 删除过时内容
   - 维护知识质量

5. **性能监控**
   - 跟踪查询性能
   - 优化检索策略
   - 调整参数配置

## 故障排除

### 问题1: 检索结果不相关

**解决方案:**
- 检查嵌入模型是否合适
- 优化文档分块策略
- 调整retrieval_top_k参数
- 检查文档质量

### 问题2: 查询速度慢

**解决方案:**
- 使用更快的向量存储（FAISS）
- 减少检索文档数量
- 启用缓存
- 优化索引

### 问题3: Agent回答不准确

**解决方案:**
- 增加知识库内容
- 调整模型参数
- 提供更多上下文
- 使用更强大的模型

## 参考资源

- **MindsDB RAG文档**: https://docs.mindsdb.com/rag
- **向量数据库指南**: https://docs.mindsdb.com/vector-databases
- **Agent开发**: https://docs.mindsdb.com/agents
- **嵌入模型**: https://huggingface.co/models
