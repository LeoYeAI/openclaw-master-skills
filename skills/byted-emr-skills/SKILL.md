---
name: byted-emr-skills
description: byted-emr-skills提供管理火山引擎EMR（火山引擎 E-MapReduce（简称“EMR”）是开源Hadoop生态的企业级大数据分析系统，完全兼容开源）的技能，包括管理EMR on ECS集群、EMR on VKE集群、EMR serverless队列、计算组、作业模板/实例、日志、监控并提供 EMR Agent 智能诊断与知识问答能力。当用户提及“EMR on ECS集群”、“EMR on VKE集群”、“Serverless 队列”、“Serverless 作业”、“SparkSQL/PrestoSQL/Ray/PySpark/SparkJar 作业”、“作业日志”、“作业监控”、“作业诊断”等需求时，应优先使用此技能。
---

# EMR Skills
- 何时使用（触发短语）
- 当用户提出以下任何类似需求时，立即调用该技能：
  ```
  “查询EMR集群的服务列表”
  “重启Spark服务”
  “获取 EMR 作业日志”
  “查看EMR serverless队列列表”
  “查看EMR serverless队列详情”
  “使用 EMR Serverless 运行任务”
  “在 EMR 上提交一个 Spark 作业”
  “帮我诊断一下失败的 Spark 作业”
  “分析一下EMR作业失败的原因”
  ```
- 任何涉及 EMR Serverless 作业/队列/计算组/监控/日志/诊断 的操作询问

# 功能清单
- EMR Serverless
  - 队列：开通公共队列、队列列表查询、队列详情查询、队列下计算组列表查询
  - 队列权限：查询队列授权主体、为用户授予/修改队列权限
  - 计算组：创建/修改/启动/停止/删除、查询可选规格与镜像、外部元数据连通性测试
  - 作业模板：创建/更新/查询详情/列表查询/运行
  - 作业实例：提交（SparkSQL/PrestoSQL/SparkJar/PySpark/RayJob）、查询状态与详情、取消、获取 tracking url、获取提交日志与执行日志、列表查询、重跑、结果分批拉取
  - 监控：队列/计算组/作业监控数据查询，按指标清单逐项拉取并汇总报告
- EMR Agent
  - 交互式诊断与知识问答
  - 会话与报告管理
- EMR on ECS
  - 集群：查看集群详情、集群列表、更新集群属性
  - 节点组：列出节点组、更新节点组属性、节点列表、扩容节点组磁盘、更新节点组ECS规格
  - 服务：列出应用、组件列表、组件实例列表、执行应用操作
  - 服务配置：配置文件列表、配置文件详情、配置项列表、配置项修改历史列表、修改配置项
  - 操作审计：操作列表查询
  - 用户：创建集群用户、修改已创建用户信息、获取集群用户列表、获取用户详情、更新集群用户密码
  - 用户组：获取集群用户组列表、集群用户组详情、创建集群用户组、更新集群用户组
- EMR on VKE
  - 集群：查看集群列表、集群详情
  - 服务（应用）：查看服务列表、服务组件实例、重启服务或组件实例、查看服务配置参数、修改服务配置参数
  - 操作日志：查看操作日志列表、操作日志详情

# Initial Setup
- 确保已配置火山引擎 API 凭证：
```bash
export VOLCENGINE_AK="your-access-key"
export VOLCENGINE_SK="your-secret-key"
export VOLCENGINE_REGION="cn-beijing"
```
- 安装emr serverless sdk，调用scripts/bin/install_serverless_sdk.sh安装

# How to manage EMR
## 1. EMR on Serverless管理
- 针对全托管的 Serverless 形态，主要面向作业提交和资源队列管理。
- OpenAPI 推荐使用命令行工具：`python ./scripts/on_serverless/emr_serverless_cli.py --action <Action> --method <GET|POST> --query '<json>' --body '<json>'`
  - Region 默认从环境变量 `VOLCENGINE_REGION` 读取（默认 cn-beijing）
  - Service/Version 会根据 Action 自动推断（需要时也可显式传 `--service/--version`）
  - 自定义 endpoint（如 LAS）可额外传 `--endpoint las.cn-beijing.volcengineapi.com`
- 作业提交推荐使用命令行工具：`python ./scripts/on_serverless/emr_serverless_submit_cli.py <sql|jar|pyspark|ray> ...`
### 如何管理资源队列
- 支持的功能列表
  - 队列列表：查看所有资源队列及其配置（如最大资源、当前使用量）, 必须使用OpenAPI`ListTagQueue`查询队列列表。
  - 队列详情：获取队列的详细信息，包括绑定的网络、存储等, 必须使用OpenAPI`GetQueue`查询队列详情。
  - 队列监控：通过云监控接口获取队列近一天的资源使用率、作业数、失败作业数量等（需要云监控权限）。
  - 创建队列：一键创建公共队列, 必须使用OpenAPI`CreateQueueSilently`或`CreateOrderInOneStep`创建队列。
  - 队列计算组列表：获取指定队列下的计算组（Queue Component）列表与详情，必须使用OpenAPI`ListQueueComponent`查询队列计算组列表。
- 所有的队列功能操作详情，请严格按照`references/emr_serverless/queue/emr_serverless_queue_guide.md`中的说明进行操作。
### 如何管理队列权限
- 支持的功能列表
  - 获取队列权限列表：根据指定的队列，获取具有其权限的用户/用户组列表, 必须使用OpenAPI`ListAuthorizedPrincipalsForQueue`查询队列权限列表。
  - 模糊搜索队列权限：根据用户名模糊查询用户列表，同时判断用户是否已经具有指定队列的权限，必须使用OpenAPI`ListIAMUsersWithQueueRole`查询队列权限列表。
  - 添加用户权限：为用户授予指定数据对象的权限，必须使用OpenAPI`GrantQueuePrivilege`添加用户权限。
  - 修改用户的队列权限：修改用户对指定队列的权限, 必须使用OpenAPI`AlterQueuePrivilege`修改用户权限。
- 所有的功能操作详情，请严格按照`references/emr_serverless/privilege/emr_serverless_privilege_guide.md`中的说明进行操作。
### 如何管理作业模板
- 必须注意作业模板和作业实例的区别：
  - 作业模板：定义作业的通用配置，包括代码路径、参数、环境变量等。
  - 作业实例：基于作业模板创建的具体运行实例，包含作业 ID、运行参数、状态等。
- 支持的作业模板功能列表
  - 创建作业模板：定义作业模板（包含代码路径、参数、环境配置等），必须使用OpenAPI`CreateJobDefinition`创建作业模板。
  - 执行或运行作业模板：基于已有作业模板触发一次运行，必须使用OpenAPI`RunJobDefinition`执行作业模板。
  - 修改作业模板：修改作业模板（如执行资源、代码路径、入口命令等），但不影响已提交的作业实例，必须使用OpenAPI`AlterJobDefinition`修改作业模板。
  - 查询作业模板详情：获取作业模板的详细配置信息，必须使用OpenAPI`GetJobDefinition`查询作业模板详情。
  - 查询作业模板列表：获取所有已创建的作业模板列表，必须使用OpenAPI`ListJobDefinitions`查询作业模板列表。
- 所有作业模板（即作业定义）的详细操作指南，请严格按照`references/emr_serverless/job/emr_serverless_job_guide.md`中的说明进行操作。
### 如何管理作业实例
- 作业实例功能列表
  - 提交作业：支持 SparkSQL、PrestoSQL、SparkJar、PySpark、RayJob 等类型；SparkJar/PySpark/RayJob 支持作业执行脚本使用本地路径（由 SDK 自动上传至 TOS，细节见作业实例指南）。
  - 查询作业实例：推荐使用 OpenAPI `QueryGetJobV2` 获取状态与详情。
  - 终止作业实例：OpenAPI `QueryCancelQueryV2`。
  - 获取作业日志：OpenAPI `FetchDriverLog` / `QueryFetchSubmitLog`（支持关键字过滤）。
  - 分批获取结果数据：对于 SQL 类作业，可通过OpenAPI `QueryFetchResultsByBatch` 分批获取结果
  - 获取 Tracking url：OpenAPI `QueryGetTrackingURL`。
  - 作业实例列表：OpenAPI `ListJobInstances`。
- 所有作业实例的详细操作指南，请严格按照`references/emr_serverless/job_instance/emr_serverless_job_instance_guide.md`中的说明进行操作。
### 如何管理计算组（Serverless 资源单元）
- 创建/修改计算组配置。
- 查询计算组监控数据，支持监控总结和巡检。
### 如何查询操作日志
- 功能列表
  - 全局操作日志页面以及队列、计算组的操作列表查询
- 所有的操作日志查询，请严格按照`references/emr_serverless/operation_audit/emr_serverless_operation_audit_guide.md`中的说明进行操作。
### 如何查询队列、计算组、作业监控数据
- 功能列表
  - 队列计算组作业监控数据查询：获取队列、计算组、作业的监控数据，包括 CPU 利用率、内存利用率、作业数、失败作业数量等，必须使用OpenAPI`GetMetricData`查询队列、计算组、作业监控数据。
- 所有的队列计算组作业监控数据查询操作，请严格按照`references/emr_serverless/monitor/emr_serverless_monitor_guide.md`中的说明进行操作。

## 2. EMR Agent（EMR AI 助手）
### 如何进行交互式问题诊断和知识助手
- 功能列表
  - 适用于所有 EMR 形态，提供交互式问题诊断和知识问答。
### 如何管理诊断会话和报告管理
- 功能列表
  - 报告列表：获取历史诊断报告列表。
  - 查看报告详情：获取已有报告内容。
  - 会话列表：获取分析诊断和问答历史会话列表。
  - 查看会话详情：获取会话的详细信息，包括问题描述、回答内容、会话状态等。
- 所有分析诊断会话和报告操作，请严格按照`references/emr_agent/emr_agent_guide.md`中的说明进行操作。

## 3. EMR on ECS 集群管理
- 支持对基于 ECS 的传统 Hadoop 集群进行全生命周期管理。
### 如何管理集群
- 功能列表
  - 查看集群详情：获取集群基础信息、状态、计费类型、访问地址等，必须使用OpenAPI`GetCluster`查询集群详情。
  - 集群列表：按条件筛选、分页查询，必须使用OpenAPI`ListClusters`查询集群列表。
  - 更新集群属性：修改集群名称、描述等，必须使用OpenAPI`UpdateClusterAttribute`更新集群属性。
- 所有集群管理操作详情，请严格按照`references/emr_on_ecs/cluster/emr_on_ecs_cluster_guide.md`中的说明进行操作。
### 节点组管理
- 功能列表
  - 列出节点组：查看集群内的节点组（如 Master、Core、Task）及其配置，必须使用OpenAPI`ListNodeGroups`列出节点组列表。
  - 更新节点组属性：修改节点组名称、实例规格（支持升级）、磁盘扩容，必须使用OpenAPI`UpdateNodeGroupAttribute`更新节点组属性。
  - 节点列表：查看节点组内所有 ECS 实例的详细信息，必须使用OpenAPI`ListNodes`查询节点组内所有节点实例的详细信息。
  - 扩容节点组磁盘：扩容指定节点组的磁盘容量，必须使用OpenAPI`ResizeNodeGroupDisk`扩容节点组磁盘。
  - 更新节点组ECS规格：修改指定节点组的ECS实例规格，必须使用OpenAPI`UpdateNodeGroupEcsSpec`更新节点组ECS规格。
- 所有节点组管理操作详情，请严格按照`references/emr_on_ecs/node_group/emr_on_ecs_node_group_guide.md`中的说明进行操作。
### 应用管理
- 功能列表
  - 列出应用：查看集群已安装的大数据组件，必须使用OpenAPI`ListApplications`列出应用列表。
  - 组件列表：查看每个服务的角色分布，必须使用OpenAPI`ListComponents`列出组件列表。
  - 组件实例列表：查看每个组件的实例列表，必须使用OpenAPI`ListComponentInstances`列出组件实例的实例列表。
  - 执行应用操作：对组件进行启动、停止、重启、滚动重启等操作，必须使用OpenAPI`RunApplicationAction`执行应用操作。
- 所有应用管理操作详情，请严格按照`references/emr_on_ecs/application/emr_on_ecs_application_guide.md`中的说明进行操作。
### 应用配置管理
- 功能列表
  - 配置文件列表：查看集群中指定应用的配置文件列表，必须使用OpenAPI`ListApplicationConfigFiles`列出应用配置文件列表。
  - 配置文件详情：查看集群中指定应用的配置文件内容、修改时间等信息，必须使用OpenAPI`GetApplicationConfigFile`查询应用配置文件详情。
  - 配置项列表：查看集群中指定应用的配置项列表，包括配置项名称、当前值、默认值等信息，必须使用OpenAPI`ListApplicationConfigs`列出应用配置项列表。
  - 配置项修改历史列表：查看集群中指定应用的配置项修改历史列表，必须使用OpenAPI`ListApplicationConfigHistories`列出应用配置项修改历史列表。
  - 修改配置项：修改集群中指定应用的配置项值，必须使用OpenAPI`UpdateApplicationConfig`更新应用配置项。
- 所有应用配置管理操作详情，请严格按照`references/emr_on_ecs/application_config/emr_on_ecs_application_config_guide.md`中的说明进行操作。
### 操作审计管理
- 操作列表查询：查看集群中所有操作日志、支持分页查询，必须使用OpenAPI`ListOperations`列出操作列表。
- 所有操作审计管理操作详情，请严格按照`references/emr_on_ecs/operation/emr_on_ecs_operation_guide.md`中的说明进行操作。
### 用户管理
- 功能列表
  - 创建集群用户：为集群新增用户，需指定用户名、密码等信息，必须使用OpenAPI`CreateClusterUser`创建集群用户。
  - 修改已创建用户信息：修改指定集群中已存在用户的用户组或描述信息，必须使用OpenAPI`UpdateClusterUser`更新集群用户信息。
  - 获取集群用户列表：查询指定集群的用户信息列表，必须使用OpenAPI`ListClusterUsers`列出集群用户列表。
  - 获取用户详情: 查询指定集群的详细用户信息，必须使用OpenAPI`GetClusterUsers`查询集群用户详情。
  - 更新集群用户密码：修改指定集群中已存在用户的登录密码，必须使用OpenAPI`UpdateClusterUserPassword`更新集群用户密码。
- 所有用户管理操作详情，请严格按照`references/emr_on_ecs/user/emr_on_ecs_user_guide.md`中的说明进行操作。
### 用户组管理
- 功能列表
  - 获取集群用户组列表: 查询指定集群的用户组信息列表，必须使用OpenAPI`ListClusterUserGroups`列出集群用户组列表。
  - 集群用户组详情: 查询指定集群的详细用户组信息，必须使用OpenAPI`GetClusterUserGroups`查询集群用户组详情。
  - 创建集群用户组：为指定集群创建新的用户组，必须使用OpenAPI`CreateClusterUserGroup`创建集群用户组。
  - 更新集群用户组：修改指定集群中已存在用户组的描述或成员信息，必须使用OpenAPI`UpdateClusterUserGroup`更新集群用户组。
- 所有用户组管理操作详情，请严格按照`references/emr_on_ecs/user_group/emr_on_ecs_user_group_guide.md`中的说明进行操作。

## EMR on VKE 集群管理
- 所有集群管理操作详情，请严格按照`references/emr_on_vke/emr_on_vke_guide.md`中的说明进行操作。

# Available Scripts
- `scripts/on_serverless/emr_serverless_manager.py`：统一的 EMR Serverless OpenAPI 调用入口（manage_emr_serverless），用于队列/作业实例/计算组等运维类接口调用。
- `scripts/config/config.py`: 封装EMR所用到的配置、SDK Client构造等。
- `scripts/emr_agent/expert.py`：与 EMR Agent 交互，实现智能诊断和知识问答。
- `scripts/emr_agent/emr_agent_manager.py`：获取EMR Agent的会话列表，报告列表等。
- `scripts/bin/install_serverless_sdk.sh`：安装 EMR on Serverless 形态的 Python SDK，用于 Serverless 队列管理、作业提交等操作。
- `scripts/on_ecs/emr_on_ecs_manager.py`：统一的 EMR on ECS 形态的 OpenAPI 调用入口（manage_emr_on_ecs），用于集群/节点组/应用等运维类接口调用。
- `scripts/on_ecs/emr_on_ecs_cli.py`：EMR on ECS 形态的命令行工具，用于集群/节点组/应用等运维类接口调用。
- `scripts/on_vke/emr_on_vke_manager.py`：EMR on VKE 形态 产品的管理脚本

# References
- `references/emr_serverless/queue/emr_serverless_queue_guide.md`：EMR on Serverless形态的资源队列详细管理操作指南
- `references/emr_serverless/job_instance/emr_serverless_job_instance_guide.md`：EMR on Serverless形态的作业实例详细管理操作指南
- `references/emr_serverless/job/emr_serverless_job_guide.md`: EMR on Serverless形态的作业模板（即作业定义）管理操作指南
- `references/emr_serverless/compute/emr_serverless_compute_guide.md`: EMR on Serverless形态的计算组详细管理操作指南
- `references/emr_agent/emr_agent_guide.md`：EMR Agent 详细操作指南，包括问题分析、获取历史会话、获取历史诊断报告等。
- `references/emr_on_ecs/cluster/emr_on_ecs_cluster_guide.md`：EMR on ECS 集群管理操作指南，包括集群列表查询、集群详情查询、更新集群属性等。
- `references/emr_on_ecs/node_group/emr_on_ecs_node_group_guide.md`：EMR on ECS 节点组管理操作指南，包括节点组列表查询、节点组详情查询、更新节点组属性等。
- `references/emr_on_ecs/application/emr_on_ecs_application_guide.md`：EMR on ECS 应用管理操作指南，包括应用列表查询、组件列表查询、组件实例列表查询、执行应用操作等。
- `references/emr_on_ecs/application_config/emr_on_ecs_application_config_guide.md`：EMR on ECS 应用配置管理操作指南，包括配置文件列表查询、配置文件详情查询、配置项列表查询、配置项修改历史列表查询、修改配置项等。
- `references/emr_on_ecs/operation/emr_on_ecs_operation_guide.md`：EMR on ECS 操作审计管理操作指南，包括操作列表查询等。
- `references/emr_on_ecs/user/emr_on_ecs_user_guide.md`：EMR on ECS 用户管理操作指南，包括创建用户、修改用户信息、查询用户列表、查询用户详情、更新用户密码等。
- `references/emr_on_ecs/group/emr_on_ecs_group_guide.md`：EMR on ECS 用户组管理操作指南，包括查询用户组列表、查询用户组详情、创建用户组、更新用户组等。
- `references/emr_on_vke/emr_on_vke_guide.md`：EMR on VKE集群管理操作指南。包括查询集群列表和详情、查询服务列表与详情、查询操作日志列表与详情、重启服务、查询和更新服务配置参数等。

# Assets
- `assets/libs/python_serverless-1.*-py3-none-any.whl`: EMR on Serverless 形态的 Python SDK 包，用于 EMR Serverless 作业提交等操作。
- `assets/emr-serverless-job-template.json`：Serverless 作业提交模板，包含 PySpark 作业参数示例。

# Requirements
- 如果需要写临时文件（比如编写脚本、记录备忘录等），必须将文件放在./tmp文件夹下。
- 当遇到作业、服务、集群失败或者用户有诊断需求的时候，必须优先使用EMR Agent的诊断功能，而不是自己去分析诊断。EMR Agent诊断需要消耗一定时间，应该等待其诊断完成，不要中途kill诊断任务
- 不要去读取scripts下脚本的内容，按照guide文档的说明执行即可，除非你有必须读的理由（比如执行频繁遭遇失败需要排查问题或用户咨询实现细节等）
- 当你通过python代码引入script下的包时，你需要将emr-skills的根目录加入path：sys.path.append(${emr_skill_root})
- 当你通过python代码提交任务并等待完成时，你需要分为两个python脚本，先执行提交任务脚本，得到job_id后，再执行状态获取脚本；状态获取脚本不要在脚本内用While循环一直获取状态，而是应该仅获取一次状态，通过多次运行脚本持续获取状态
