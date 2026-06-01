# EMR Agent交互指南
EMR Agent是EMR的AI助手。
- 当用户需要诊断Serverless作业、Serverless实例、EMR On Ecs（或者EMR On Vke）服务或集群的时候，请调用expert.py脚本
    ```bash
    python ./scripts/emr_agent/expert.py --arg_key value
    ```
- 当用户需要查询Agent报告、聊天记录（会话记录）的时候，应该使用emr_agent_manager.py脚本
    ```bash
    python ./scripts/emr_agent/emr_agent_manager.py --arg_key value
    ```

## 诊断功能指南

### 发送诊断请求
EMR Agent支持自然语言交互，请求参数包括：
question：question中应该包含必要的信息，后面会讲到每种场景所需的必要信息
chat-id：EMR Agent是AI助手，具有会话功能。在发起诊断后，诊断结果中会包含chat-id字段，传入这个字段，可以就之前的话题与EMR Agent继续讨论。如果不传chat-id，则会发起新的会话。
```bash
# 注意，如果question有空格，应该用引号括起来
python ./scripts/emr_agent/expert.py --question "帮我诊断一下作业：325461534" [--chat-id session_6e6599ae-287f-4d33-b956-9284cb166ad2]
```

### 获取诊断结果
expert生成结果需要一定时间。脚本执行后，你会看到进程的pid，通过以下命令取回结果
```bash
# 查询result的方法，参数为异步任务的pid
python ./scripts/emr_agent/expert.py --get-result {pid}
```
注意：请仔细核对pid，不要使用错误的pid

### 作业诊断场景说明
作业分为两种，对于Serverless队列的作业来说，必要的信息是作业ID；对于Serverless实例（Serverless Olap）的SQL查询来说，必要的信息是查询ID和Serverless实例ID。示例
```bash
# 注意，如果question有空格，应该用引号括起来
python ./scripts/emr_agent/expert.py --question "帮我诊断一下作业：325461534"
```
```bash
# 主要，实例ID和查询ID都是uuid的格式，你要原封不动地使用正确ID，不要编造ID
python ./scripts/emr_agent/expert.py --question "帮我诊断olap sql，Serverless实例ID：cdw-443qkdc56b48kcegjird-rd，查询ID：9c7fe664-fa84-11f0-aae7-00163e752688"
```

### 集群诊断场景说明
集群分为两种，On Ecs集群和On VKE集群。诊断集群的必要信息包括：产品形态（On Ecs还是On Vke）和集群ID。请求示例如下：
```bash
python ./scripts/emr_agent/expert.py --question "帮我诊断一下EMR On Ecs的集群，集群ID为：emr-20c976f7cb93xxxxxx"
```

### 服务诊断场景说明
服务诊断的必要信息包括：产品形态（On Ecs还是On Vke）、集群ID和服务名称（比如HDFS、YARN、Spark、Hive）。请求示例如下：
```bash
# 注意，有时候用户也把服务称为应用，比如“Spark应用”
python ./scripts/emr_agent/expert.py --question "帮我诊断一下EMR On Vke集群的Spark服务，集群ID为：emr-20c976f7cb93xxxxxx"
```

### Serverless实例诊断场景说明
Serverless实例指全托管的Serverless Doris和Serverless Starrocks。其诊断的必要信息是Serverless实例ID。请求示例
```bash
python ./scripts/emr_agent/expert.py --question "帮我诊断一下Serverless Doris实例，实例ID是：cdw-443qkdc56b48kcegjird"
```

## 知识问答功能指南
EMR Agent专注于大数据领域和火山引擎EMR产品。当用户的问题涉及这些领域，而你的知识又不足以回答的时候，可以请求EMR Agent，示例如下：
```bash
python ./scripts/emr_agent/expert.py --question "Serverless EMR怎么创建队列呢"
```

## EMR Agent 会话和报告管理操作指南

会话和报告管理，需要调用emr_agent_manager.py，不同的场景，需要传入不同的action和body，调用示例如下
```bash
# 注意，body是转义后的json字符串，双引号括起来，否则命令行参数无法解析
python ./scripts/emr_agent/emr_agent_manager.py --action ListChats --body "{\"PageSize\": 10}"
```

### ListChats
**接口描述**  
获取当前用户在EMR Agent中的会话列表，支持按作业ID、集群ID、服务名称等条件筛选。

**Action**： `ListChats`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明 |
|--------|----------|----------|------|
| JobId | String | 否 | 作业ID |
| ClusterId | String | 否 | 集群ID。服务诊断时需要 |
| ServiceName | String | 否 | 服务名称。服务诊断时需要 |
| PageNum | Integer | 否 | 页码 |
| PageSize | Integer | 否 | 页大小 |

### GetChat
**接口描述**  
获取会话的聊天记录

**Action**： `GetChat`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明 |
|--------|----------|----------|------|
| ChatId | String | 否 | 会话ID |

### ListReports
**接口描述**  
获取当前用户在EMR Agent中的诊断报告列表。

**Action**： `ListReports`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明                                                     |
|--------|----------|----------|--------------------------------------------------------|
| ChatId | String | 否 | 会话ID（格式为：session_6e6599ae-287f-4d33-b956-9284cb166ad2） |
| ReportType | String | 否 | 报告类型。可选值：cluster（集群诊断）、service（服务诊断）、job作业诊断           |
| PageNum | Integer | 否 | 页码                                                     |
| PageSize | Integer | 否 | 页大小                                                    |


### GetReportResult
**接口描述**  
获取EMR Agent中诊断报告的详情。

**Action**： `GetReportResult`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明                                                        |
|--------|----------|----------|-----------------------------------------------------------|
| ReportId | String | 否 | 报告ID（格式为：emr-report-8f0fc069-0bf0-44d3-959b-329f6c73328f) |


# Requirements
- 不要去读脚本内容，按照格式执行即可
- expert.py执行较慢，建议轮询间隔不要小于1分钟，查询时，请仔细核对pid，不要填错
- 尽量不要创建临时文件，通过bash命令去执行。例如：
  - python ./scripts/emr_agent/expert.py --question "帮我诊断一下作业：325461534"
  - python ./scripts/emr_agent/emr_agent_manager.py --action ListChats --body "{\"PageSize\": 10}"
