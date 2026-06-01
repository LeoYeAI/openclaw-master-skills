# EMR on VKE 操作指南
> VKE: Volcengine Kubernetes Engine (VKE), a cloud-native Kubernetes Service.

查看和管理EMR On VKE产品，需要调用emr_on_vke_manager.py，不同的场景，需要传入不同的action和body，调用示例如下
```bash
# 注意，body是转义后的json字符串，双引号括起来，否则命令行参数无法解析
python ./scripts/emr_agent/emr_on_vke_manager.py --action GetVirtualCluster --body "{\"ClusterId\": \"emr-da4f1w57454036abe372\"}"
```


### ListVirtualClusters
**接口描述**  
查询集群列表

**Action**： `ListVirtualClusters`

**body**

| 参数名 | 参数类型         | 是否必选 | 说明                                                                                     |
|--------|--------------|------|----------------------------------------------------------------------------------------|
| ClusterName | String       | 否    | 集群名称（支持模糊搜索）                                                                           |
| ClusterStates | List[String] | 否    | 过滤集群状态：INIT 初始化中，INIT_FAILED 初始化失败，RUNNING 运行中，DELETING 删除中，DELETED 已删除。示例：["RUNNING"] |
| NextToken  | Integer      | 否    | 等同于pageNum，默认值是0                                                                       |
| MaxResults | Integer      | 否    | 最多返回多少条记录（默认100），相当于pagesize                                                           |

请求示例
```bash
python scripts/on_vke/emr_on_vke_manager.py --action ListVirtualClusters --body "{\"ClusterStates\": [\"RUNNING\"]}"

```

### GetVirtualCluster
**接口描述**  
查询集群详情

**Action**： `GetVirtualCluster`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明   |
|--------|----------|----------|------|
| ClusterId | String | 否 | 集群ID |


### ListOperations
**接口描述**  
查询集群的操作日志列表

**Action**： `ListOperations`

**body**

| 参数名       | 参数类型 | 是否必选 | 说明   |
|-----------|----------|------|------|
| ClusterId | String | 是    | 集群ID |


### GetOperation
**接口描述**  
查询集群的操作日志详情

**Action**： `GetOperation`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明         |
|--------|----------|------|------------|
| OperationId | String | 是    | 操作记录ID，示例：op-xxx |

### ListApplications
**接口描述**  
查询集群的应用列表

**Action**： `ListApplications`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明   |
|--------|----------|------|------|
| ClusterId | String | 是    | 集群ID |


### RebootApplications
**接口描述**  
重启应用（服务），比如重启spark服务、ray服务

**Action**： `RebootApplications`

**body**

| 参数名 | 参数类型         | 是否必选 | 说明         |
|--------|--------------|------|------------|
| ClusterId | String       | 是    | 集群ID       |
| ApplicationNames | List[String] | 是 | 应用名称列表，例如：["Spark"] |


### ListComponentInstances
**接口描述**  
查询服务的组件实例列表

**Action**： `ListComponentInstances`

**body**

| 参数名 | 参数类型 | 是否必选 | 说明   |
|--------|----------|------|------|
| ClusterId | String | 是    | 集群ID |
| ApplicationName | String | 是    | 应用名称，例如：Spark    |


### RebootComponentInstance
**接口描述**  
重启应用（服务）的组件，比如重启spark的SparkHistoryServer、SparkOperator

**Action**： `RebootComponentInstance`

**body**

| 参数名 | 参数类型   | 是否必选 | 说明                                                             |
|--------|--------|------|----------------------------------------------------------------|
| ClusterId | String | 是    | 集群ID                                                           |
| ApplicationName | String | 是    | 应用名称，例如：Spark                                                  |
|  ComponentName | String | 是    | 组件名称，例如：SparkHistoryServer                                     |
|  Namespace | String | 是    | 组件实例所在的VKE（K8S）Namespace。组件支持多个namespace中有部署实例，重启需要指定Namespace |
|  ComponentInstanceName | String | 否    | 组件实例名称。比如Ray服务，可以有多个RayCluster实例，这时候重启就需要指定实例名称    |

**请求示例**
```bash
python scripts/on_vke/emr_on_vke_manager.py --action RebootComponentInstance --body "{\"ClusterId\": \"emr-4xq2rwxnh92z82n68ywo\", \"ApplicationName\": \"Spark\", \"ComponentName\": \"SparkHistoryServer\", \"Namespace\": \"autotest-spark-001\"}"

```

### ListConfigs
**接口描述**  
获取应用配置参数

**Action**： `ListConfigs`

**body**

| 参数名 | 参数类型   | 是否必选 | 说明            |
|--------|--------|---|---------------|
| ClusterId | String | 是 | 集群ID          |
| ApplicationName | String | 是 | 应用名称，例如：Spark |

**返回结果**

| 参数名 | 参数类型   | 说明                                 |
|--------|--------|------------------------------------|
| ComponentName | String | 组件名称                               |
| ConfigFileName | String | 配置文件名称                             |
|  ConfigItemKey   | String | 配置项的key                            |
| ConfigItemValue | String | 配置项的value                          |
| Effective  | String | 是否已经生效。有些配置更改后需要重启生效，改字段可以看配置是否已生效 |


### UpdateConfig
**接口描述**  
更新服务配置参数

**Action**： `UpdateConfig`

**body**

| 参数名 | 参数类型         | 是否必选 | 说明                                                                                                                                               |
|--------|--------------|------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| ClusterId | String       | 是    | 集群ID                                                                                                                                             |
| ApplicationName | String | 是    | 应用名称，例如：Spark                                                                                                                                    |
| Remark | String  | 否    | 操作备注                                                                                                                                             |
| Items | List[Object] | 是  | 需要更新的配置列表，例如：[{"ConfigFileName":"spark-defaults.conf","ConfigItemKey":"spark.celeborn.rpc.askTimeout","ConfigItemValue":"640s"}] |

**Items 对象结构**

| 参数 | 类型 | 是否必填   | 说明 |
|------|------|--------|------|
| ConfigFileName | String | 是      | 配置文件名称 |
| ConfigItemKey | String | 是      | 配置项键名 |
| ConfigItemValue | String | 是      |  配置项值 |

**请求示例**
```bash
python scripts/on_vke/emr_on_vke_manager.py --action UpdateConfig --body "{\"ClusterId\": \"emr-4xq2rwxnh92z82n68ywo\", \"ApplicationName\": \"Spark\", \"Items\":[{\"ConfigFileName\":\"spark-defaults.conf\",\"ConfigItemKey\":\"spark.celeborn.rpc.askTimeout\",\"ConfigItemValue\":\"620s\"}],\"Remark\":\"测试\"}"

```

# Requirements
- 不要去读脚本内容，按照格式执行即可
- 尽量不要创建临时文件，通过bash命令去执行。例如：
  - python scripts/on_vke/emr_on_vke_manager.py --action GetVirtualCluster --body "{\"ClusterId\": \"emr-4xq2rwxnh66z82n68ywo\"}"
  - python scripts/on_vke/emr_on_vke_manager.py --action ListApplications --body "{\"ClusterId\": \"emr-4xq2rwxnh66z82n68ywo\"}"


