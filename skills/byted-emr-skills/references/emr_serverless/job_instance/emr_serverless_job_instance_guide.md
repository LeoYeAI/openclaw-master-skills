# EMR Serverless 作业实例指南

本指南描述在 EMR Serverless 场景下的作业实例能力，包括：
- 任务提交：包含提交SparkSQL、PrestoSQL、SparkJar、PySpark、RayJob。
- 作业实例提交后的运维操作，包括：查询作业实例状态、获取结果、tracking url、提交日志（submission log）与执行日志（driver log）

## 前置条件

- 配置环境变量：
  - VOLCENGINE_AK
  - VOLCENGINE_SK
  - VOLCENGINE_REGION（默认 cn-beijing）
  - TOS_BUCKET_NAME：可选。用于提交 SparkJar / PySpark / RayJob 时，若资源参数传入本地路径，由 SDK 自动上传到该桶后再提交作业。
  - TOS_ENDPOINT：可选。用于 SDK 自动上传本地文件到 TOS 时指定 endpoint（不填时由 SDK 使用默认配置）。
- 安装 EMR Serverless SDK，调用 scripts/bin/install_serverless_sdk.sh 安装

## 注意事项
- PySpark 和 SparkJar底层实现是一样的，所以在PySpark任务实例信息里看到有Jar相关信息的是正常的
- 提交作业实例流程如下：
  - 创建提交任务脚本，进行任务提交，得到job_id
  - 创建作业实例状态获取脚本，基于job_id拿到作业实例状态
  - 基于作业实例状态，进行下一步判断
    - 当希望等待作业实例完成后继续执行相关操作，需要重新运行：作业实例状态获取脚本 拿到状态
      - 多次单独运行：作业实例状态获取脚本，拿到最新结果，直到任务结束
    - 直接返回当前状态
- SparkJar / PySpark / RayJob 的资源参数支持 `tos://` 与本地路径：
  - 传 `tos://`：直接提交。
  - 传本地路径：由 SDK 自动上传至 TOS 后提交（需要正确配置 TOS_BUCKET_NAME，必要时补充 TOS_ENDPOINT）。
- 作业实例状态/详情查询推荐使用 OpenAPI `QueryGetJobV2`
- EMR Serverless 作业运行时间比较长，不要擅自取消作业，等待轮询状态即可
- 当要求提交SparkSQL/PrestoSQL时，不要将其提交为PySpark

## 作业实例操作模板

### 提交SparkSQL作业实例
说明：
- `--query`：SQL 文本内容
- `--name`：作业实例名称（可选）
- `--queue`：队列名称（可选，不传使用 EMR_DEFAULT_QUEUE）
- `--compute-group`：计算组名称（可选，用于路由到指定计算组，默认 Default）

```bash
python ./scripts/on_serverless/emr_serverless_submit_cli.py sql \
  --engine spark \
  --name spark_sql \
  --query 'select 1' \
  --queue '公共队列' \
  --compute-group 'Default'
```

### 提交PrestoSQL作业实例
说明：
- `--query`：SQL 文本内容
- `--name`：作业实例名称（可选）
- `--queue`：队列名称（可选，不传使用 EMR_DEFAULT_QUEUE）
- `--compute-group`：计算组名称（可选，用于路由到指定计算组，默认 Default）

```bash
python ./scripts/on_serverless/emr_serverless_submit_cli.py sql \
  --engine presto \
  --name presto_sql \
  --query 'select 1' \
  --queue '公共队列' \
  --compute-group 'Default'
```
### 提交SparkJar作业实例

说明：
- `--jar`：Jar 包路径，支持本地路径与 `tos://` 路径
- `--main-class`：主类
- `--main-args`：main 参数，JSON 格式：`{"args":["--k","v"]}`（不传默认空）
- `--depend-jars/--files/--archives`：依赖列表，JSON 格式：`{"items":["tos://...","/local/path"]}`（不传默认空）
- `--queue`：队列名称（可选，不传使用 公共队列）
- `--compute-group`：计算组名称（可选，用于路由到指定计算组，默认 Default）
- 若 `--jar/--depend-jars/--files/--archives` 传入本地路径并依赖 SDK 自动上传 TOS：
  - 需要正确配置 `TOS_BUCKET_NAME`（必要时补充 `TOS_ENDPOINT`）
  - 提交 CLI 会自动将 `VOLCENGINE_AK/VOLCENGINE_SK` 注入到 conf（`serverless.spark.access.key/secret.key`）

```bash
python ./scripts/on_serverless/emr_serverless_submit_cli.py jar \
  --name spark_jar \
  --jar '/home/zzw.data/spark-example.jar' \
  --main-class 'com.xxx.' \
  --main-args '{"args":[]}' \
  --depend-jars '{"items":[]}' \
  --files '{"items":[]}' \
  --archives '{"items":[]}' \
  --queue '公共队列' \
  --compute-group 'Default'
```

### 提交PySpark作业实例

说明：
- `--script`：PySpark 脚本路径，支持本地路径与 `tos://` 路径
- `--args`：脚本参数，JSON 格式：`{"args":["--k","v"]}`（不传默认空）
- `--pyfiles/--depend-jars/--files/--archives`：依赖列表，JSON 格式：`{"items":["tos://...","/local/path"]}`（不传默认空）
- `--queue`：队列名称（可选，不传使用 公共队列）
- `--compute-group`：计算组名称（可选，用于路由到指定计算组，默认 Default）
- 若 `--script/--pyfiles/--depend-jars/--files/--archives` 传入本地路径并依赖 SDK 自动上传 TOS：
  - 需要正确配置 `TOS_BUCKET_NAME`（必要时补充 `TOS_ENDPOINT`）
  - 提交 CLI 会自动将 `VOLCENGINE_AK/VOLCENGINE_SK` 注入到 conf（`serverless.spark.access.key/secret.key`）

```bash
python ./scripts/on_serverless/emr_serverless_submit_cli.py pyspark \
  --name pyspark \
  --script '/home/zzw.data/spark-example.py' \
  --args '{"args":[]}' \
  --pyfiles '{"items":[]}' \
  --depend-jars '{"items":[]}' \
  --files '{"items":[]}' \
  --archives '{"items":[]}' \
  --queue '公共队列' \
  --compute-group 'Default'
```

### 提交RayJob作业实例

说明：
- `--entrypoint-resource`：入口资源路径，支持本地文件与 `tos://` 路径；通常要求为 zip 包
- `--entrypoint-cmd`：入口命令。示例：`python /home/ray/workdir/main.py`
- `--runtime-env`：Ray runtime_env，JSON 字符串（不传默认 `{}`）
- `--queue`：队列名称（可选，不传使用 公共队列）
- `--compute-group`：计算组名称（可选，用于路由到指定计算组，默认 Default）
- Ray 资源配置（可选，按需设置）：
  - `--head-cpu` / `--head-memory`
  - `--worker-cpu` / `--worker-memory` / `--worker-replicas`

```bash
python ./scripts/on_serverless/emr_serverless_submit_cli.py ray \
  --name ray_job \
  --entrypoint-cmd 'python /home/ray/workdir/main.py' \
  --entrypoint-resource 'tos://bucket/ray_bundle.zip' \
  --queue '公共队列' \
  --compute-group 'Default' \
  --head-cpu '4' \
  --head-memory '16Gi' \
  --worker-cpu '4' \
  --worker-memory '16Gi' \
  --worker-replicas 1 \
  --runtime-env '{}'
```

## 作业实例运维模板

以下示例统一使用命令行工具 `scripts/on_serverless/emr_serverless_cli.py` 调用 OpenAPI。
### 1. 查询作业实例详情（QueryGetJobV2）

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action QueryGetJobV2 \
  --method GET \
  --query '{"Id":"job_id"}'
```

### 2. 获取作业实例的tracking url（QueryGetTrackingURL）
注意！！不要取Job里的Progress字段
```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action QueryGetTrackingURL \
  --method GET \
  --query '{"Id":"job_id"}'
```
返回数据结构（示例）
```
{
    "Result": "http://xx:18080/bq-325738704/jobs?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyxxx"
}
```

### 3. 终止作业实例（QueryCancelQueryV2）

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action QueryCancelQueryV2 \
  --method POST \
  --body '{"Id":"job_id"}'
```

### 4. 获取作业实例提交日志（QueryFetchSubmitLog）
```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action QueryFetchSubmitLog \
  --method GET \
  --query '{"Id":"job_id","Position":"0","Limit":"100"}'
```

### 5. 获取作业实例执行/Driver日志（FetchDriverLog）
**请求参数**

| 参数 | 类型     | 是否必须 | 描述                                                      |
|------|--------|------|---------------------------------------------------------|
| FileName | String | N    | 文件类型，支持syslog 和stdout（注意！只有Spark作业实例支持，其他作业实例类型无需传递该参数） |
| Id | String | Y    | 作业实例id                                                  
| Keywords | String | N    | 搜索关键字（如果没有关键字需要搜索，务必不传该字段）                              |
| Offset | String | N    | 偏移量，从0开始                                                |
| Limit | String | N    | 日志行数                                                    |
| Order | String | N    | 排序方式，支持asc/desc 默认为asc，正序排序                             |

** 调用示例 **
```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action FetchDriverLog \
  --method GET \
  --query '{"FileName":"syslog","Id":"325738704","Keywords":"INFO","Limit":"100","Offset":"0","Order":"asc"}'
```
**返回示例**
```json
{
    "Result": {
        "Rows": [
            "26/03/13 14:33:54 INFO [spark-xx",
            "26/03/13 14:33:54 INFO [spark-ui"
        ],
        "Position": "0,1773383644106,65312194133446324,9690442",
        "IsFinished": false,
        "Limit": 100,
        "Offset": 1,
        "Total": 333
    }
}
```

**返回字段含义**

| 字段 | 含义     |
|----|--------|
| Rows | 日志内容   |


### 6. 作业实例列表查询（ListJobInstances）

**接口描述**

查询作业实例列表，支持按作业实例 ID、作业实例名称、队列、时间区间筛选，并支持分页。

**请求参数**

| 参数 | 类型 | 是否必须 | 描述 |
|------|------|----------|------|
| MatchId | String | N | 作业实例实例 ID 精确匹配 |
| MatchNameExact | String | N | 作业实例名称精确匹配 |
| StartTime | String | N | 开始日期，"yyyy-MM-dd"；不传时默认查询近 7 天 |
| EndTime | String | N | 结束日期，"yyyy-MM-dd" |
| Queue | String | N | 队列名称过滤条件 |
| Limit | Int | N | 单次返回数量，最大 100 |
| Offset | Int | N | 偏移量（分页） |

**请求方式**： GET  
**Action**： ListJobInstances  
**Version**： 2024-03-25

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListJobInstances \
  --method GET \
  --query '{"MatchId":"j-0001","MatchNameExact":"job_name","Queue":"my-queue","StartTime":"2024-03-01","EndTime":"2024-03-31","Limit":20,"Offset":0}'
```

**返回数据结构（示例）**

```json
{
  "Result": {
    "JobList": [
      {
        "Id": "325883976",
        "Name": "calculate_pi_ussagi",
        "Origin": "Client",
        "Status": 7,
        "Submitter": "xxx",
        "SqlType": "-",
        "StartTime": "2026-03-14 14:15:13",
        "JobType": "SparkJar",
        "Json": "{}",
        "EngineType": "Spark",
        "TrackingUrlEnabled": true,
        "SubmitLogEnabled": true,
        "DriverLogEnabled": true,
        "Duration": "00:00:00",
        "FinishTime": "2026-03-14 14:15:13",
        "QueueRole": "none",
        "DurationStage": "0",
        "DataleapTaskId": "",
        "QueueName": "test_luyifeng",
        "SubmitterType": "User",
        "QueueId": "xxx",
        "GroupId": "0",
        "Runtime": "Java",
        "GroupName": "Default",
        "LastOperator": "xxx"
      },
      {
        "Id": "325867798",
        "Name": "sparksql_test_select_1",
        "Origin": "Client",
        "Status": 5,
        "Submitter": "xxx",
        "SqlType": "DQL",
        "StartTime": "2026-03-14 11:12:58",
        "JobType": "SparkSQL",
        "Json": "SELECT 1 as test_value",
        "EngineType": "Spark",
        "TrackingUrlEnabled": true,
        "SubmitLogEnabled": true,
        "DriverLogEnabled": true,
        "Duration": "00:00:32",
        "FinishTime": "2026-03-14 11:13:30",
        "QueueRole": "none",
        "DurationStage": "0",
        "DataleapTaskId": "",
        "QueueName": "test_luyifeng",
        "SubmitterType": "User",
        "QueueId": "1481966xx",
        "GroupId": "0",
        "Runtime": "Java",
        "Cuh": 0.034,
        "BoltCuh": 0,
        "PrestoScanSize": 0,
        "PeakMemUsed": 15023996927,
        "TotalShuffleWrite": 66,
        "TotalShuffleRead": 66,
        "GroupName": "Default",
        "LastOperator": "zzw.data@bytedance.com"
      }
    ],
    "Total": 1
  }
}
```

#### 作业实例状态 Status对照码

| Status | 含义 |
|--------|------|
| 0 | 已创建 |
| 1 | 提交中 |
| 2 | 运行中 |
| 3 | 停止中 |
| 4 | 已终止 |
| 5 | 已完成 |
| 6 | 已失败 |
| 7 | 提交失败 |
| 8 | 启动中 |


### 7. 批量获取结果接口（QueryFetchResultsByBatch）

以csv形式获取返回结果，第一行是schema信息。

**请求参数**

| 参数 | 类型 | 是否必须 | 描述 |
|------|------|----------|------|
| taskId | String | 是 | 作业Id |
| position | String | 是 | 偏移地址，首次查询写0即可。后续查询用返回参数里的position值 |
| limit | String | 是 | 读取记录数 |
| skipLines | String | 否 | 跳过的行数，相当于offset，默认为0 |

**请求方式**： GET
**Action**： QueryFetchResultsByBatch
**Version**： 2024-03-25

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action QueryFetchResultsByBatch \
  --method GET \
  --query '{"taskId":"295636255","position":"0","limit":"10","skipLines":"0"}'
```

**返回参数**

| 参数 | 类型 | 描述 |
|------|------|------|
| position | String | 结果偏移地址 |
| isFinished | Boolean | 是否结束 |
| rows | list<map> | 返回结果 |
