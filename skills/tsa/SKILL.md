---
name: CloudQ
description: TSA - Tencent Cloud Smart Advisor。CloudQ — 全球首款ITOM "领域虾"。当用户问"cloudq是谁"、"cloudq是什么"或需要腾讯云智能顾问相关操作时使用。
metadata: {"openclaw": {"emoji": "🦞", "requires": {"bins": ["python3"], "env": ["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"]}, "permissions": ["network:https://*.tencentcloudapi.com", "network:https://cloud.tencent.com", "fs:~/.tencent-cloudq/"], "security": {"iam_operations": ["cam:GetRole", "cam:CreateRole", "cam:AttachRolePolicy", "cam:DeleteRole", "cam:DescribeRoleList", "sts:AssumeRole", "sts:GetCallerIdentity"], "iam_note": "角色创建/删除为独立步骤，需用户明确同意后执行：create_role.py 创建角色，cleanup.py --cloud 删除角色；check_env.py 仅做只读检测", "data_handling": "临时凭证仅在内存中使用，不持久化存储；配置文件仅保存角色 ARN，不保存密钥"}}}
---

# 🦞 CloudQ — 全球首款ITOM "领域虾"

## CloudQ 自我介绍

当用户问"CloudQ是谁"、"CloudQ是什么"、"介绍一下CloudQ"等问题时，回复以下内容：

> Hi，我是 CloudQ—全球首款ITOM "领域虾"
>
> 我能帮您：
> 🦞 **全渠道 ChatOps**，随时随地管好云
> 既能在 WorkBuddy、Qclaw、LightClaw等中使用，也能直连微信、企微、QQ、飞书、钉钉、Slack等IM；
>
> 🤖 **全天候 AIOps**，从被动响应到主动决策
> 依托「腾讯云智能顾问TSA 」的架构可视化+治理智能化，实现卓越架构治理新范式；
>
> ☁️ **全方位 CloudOps**，一只龙虾即可管理多云
> 统一纳管腾讯云、阿里云、AWS、Azure、GCP等主流云服务；
> (相关能力陆续开放中，详情请见：https://cloud.tencent.com/developer/article/2645159）
>
> **CloudQ: Just Q IT！**

---

## 核心能力

通过 **AK/SK 鉴权**调用腾讯云智能顾问（Tencent Cloud Smart Advisor）API，管理云架构图的目录与详情、获取架构评估结果，以及查询风险评估项。

---

## 一、鉴权方式

使用腾讯云 API **AK/SK 签名认证**（TC3-HMAC-SHA256），通过环境变量配置密钥：

### 1.1 必填环境变量

- `TENCENTCLOUD_SECRET_ID` — 腾讯云 SecretId（必填）
- `TENCENTCLOUD_SECRET_KEY` — 腾讯云 SecretKey（必填）

密钥获取地址：https://console.cloud.tencent.com/cam/capi

**环境变量必须永久写入 shell 配置文件**，确保新会话中仍然生效：

Linux / macOS（写入 `~/.bashrc` 或 `~/.zshrc`）：
```bash
echo 'export TENCENTCLOUD_SECRET_ID="your-secret-id"' >> ~/.bashrc
echo 'export TENCENTCLOUD_SECRET_KEY="your-secret-key"' >> ~/.bashrc
source ~/.bashrc
```

Windows PowerShell（写入用户级环境变量）：
```powershell
[Environment]::SetEnvironmentVariable("TENCENTCLOUD_SECRET_ID", "your-secret-id", "User")
[Environment]::SetEnvironmentVariable("TENCENTCLOUD_SECRET_KEY", "your-secret-key", "User")
```

### 1.2 角色配置（免密登录需要）

为生成控制台免密登录链接，需要配置 CAM 角色。角色配置分为 **检测** 和 **创建** 两个独立步骤，角色创建属于 IAM 写入操作，**必须在用户明确同意后才能执行**。

#### 步骤一：环境检测（只读）

运行环境自检脚本，检测依赖、版本更新、密钥、角色配置状态：

```bash
python3 {baseDir}/check_env.py
```

自检脚本 **仅做只读检测**，不会创建或修改任何资源。返回码含义：
- `0` = 环境就绪（密钥 + 角色全部正常）
- `1` = Python 版本不满足要求
- `2` = AK/SK 未配置或无效
- `3` = 角色未配置（需要执行步骤二）
- `4` = Skill 版本过旧，请更新 Skill

脚本首次运行时会自动检查本地 `_meta.json` 中的版本号与远端最新版本是否一致，若发现新版本则提示更新并退出（返回码 `4`）。可通过 `--skip-update` 参数跳过版本检查。

#### 步骤二：角色创建（需用户同意）

当 `check_env.py` 返回码为 `3`（角色未配置）时，**必须**向用户展示角色创建方案并等待同意：

**向用户说明以下内容**：
1. 将创建 CAM 角色 `advisor`，仅用于免密登录控制台查看智能顾问信息
2. 将关联策略 `QcloudAdvisorFullAccess`（智能顾问只读访问权限，不影响其他云资源）
3. 信任策略仅允许当前账号扮演此角色
4. 用户可随时在 CAM 控制台删除此角色

**用户同意后**，执行角色创建脚本：

```bash
python3 {baseDir}/scripts/create_role.py
```

脚本输出 JSON 格式结果，`success: true` 表示创建成功并已保存配置。

**用户拒绝时**，提供手动配置方式（方式二、三、四）。

#### 方式二：配置向导（交互式选择已有角色）

运行配置向导，从已有角色中选择，或交互式创建新角色：

```bash
python3 {baseDir}/scripts/setup_role.py
```

#### 方式三：简化配置

只需提供角色名称，系统自动获取账号 UIN。将以下内容写入 shell 配置文件（如 `~/.bashrc` 或 `~/.zshrc`）：

```bash
echo 'export TENCENTCLOUD_ROLE_NAME="advisor"' >> ~/.bashrc
source ~/.bashrc
```

系统会自动调用 API 获取您的账号 UIN，并拼接完整的 roleArn。

#### 方式四：完整配置（高级用户）

手动设置完整的角色 ARN，写入 shell 配置文件（如 `~/.bashrc` 或 `~/.zshrc`）：

```bash
echo 'export TENCENTCLOUD_ROLE_ARN="qcs::cam::uin/100001234567:roleName/advisor"' >> ~/.bashrc
source ~/.bashrc
```

### 1.3 可选环境变量

- `TENCENTCLOUD_TOKEN` — 临时密钥 Token（使用临时密钥时设置）
- `TENCENTCLOUD_ROLE_SESSION` — 角色会话名称（默认 `advisor-session`）
- `TENCENTCLOUD_STS_DURATION` — 临时凭证有效期秒数（默认 `3600`，即 1 小时；最大 `43200`，即 12 小时）

> **注意**：所有环境变量均需永久写入 shell 配置文件（如 `~/.bashrc`、`~/.zshrc`），`export` 仅对当前会话生效，新开会话会丢失。

### 1.4 配置优先级

系统按以下优先级加载角色配置：

1. 环境变量 `TENCENTCLOUD_ROLE_ARN`（完整 ARN）
2. 配置文件 `~/.tencent-cloudq/config.json`
3. 环境变量 `TENCENTCLOUD_ROLE_NAME` + 自动获取账号 UIN

---

## 二、前置检查（初始化工作流）

每次操作前必须先执行环境检测。初始化分为 **版本检查**、**环境检测** 和 **角色创建** 三个阶段，角色创建属于 IAM 写入操作，必须在用户明确同意后才能执行。

### 2.1 初始化工作流（必须严格按顺序执行）

**第一步：运行环境检测**

```bash
python3 {baseDir}/check_env.py
```

脚本会依次执行以下检测：
1. 检查 Python 版本（需要 3.7+）
2. 检查 Skill 版本更新（读取本地 `_meta.json` 版本，与远端最新版本对比）
3. 检查 AK/SK 配置
4. 验证 AK/SK 有效性
5. 检查免密登录角色配置
6. 验证角色扮演

根据返回码判断状态：
- `0` = 环境就绪，可以正常使用所有功能
- `1` = Python 版本不满足要求 → 提示用户升级 Python
- `2` = AK/SK 未配置或无效 → 提示用户配置密钥
- `3` = 角色未配置 → 执行第二步
- `4` = Skill 版本过旧 → 提示用户更新 Skill

**版本检查说明**：脚本首次运行时会自动对比本地版本与远端版本。若远端有新版本，脚本会输出当前版本和最新版本号，并以返回码 `4` 退出。网络不可用或远端接口异常时，版本检查会被跳过，不影响后续检测。可通过 `--skip-update` 参数主动跳过版本检查。

**第二步：向用户展示角色创建方案**（仅当返回码为 3 时）

向用户说明即将执行的 IAM 操作，**等待用户明确同意**：

> 免密登录功能需要创建一个 CAM 角色，以下是创建方案：
> - **角色名称**：`advisor`
> - **关联策略**：`QcloudTAGFullAccess`（标签全读写权限）、`QcloudAdvisorFullAccess`（智能顾问全读写权限）
> - **信任策略**：仅允许当前账号扮演此角色
> - **用途**：仅用于生成控制台免密登录链接，不影响其他云资源
> - 您可随时在 [CAM 控制台](https://console.cloud.tencent.com/cam/role) 删除此角色
>
> 是否同意创建？

**第三步：执行角色创建**（仅在用户同意后）

```bash
python3 {baseDir}/scripts/create_role.py
```

脚本输出 JSON 格式结果，`success: true` 表示创建成功。

**第四步：再次运行环境检测，确认环境就绪**

```bash
python3 {baseDir}/check_env.py
```

返回码 `0` 表示初始化完成，所有功能可用。

### 2.2 静默模式（供脚本内部调用）

```bash
python3 {baseDir}/check_env.py --quiet
```

静默模式下仅输出错误信息，适合其他脚本调用获取环境状态。角色未配置时返回码 `3`，**不会自动创建角色**。

### 2.3 跳过版本检查

```bash
python3 {baseDir}/check_env.py --skip-update
```

跳过远端版本对比，直接进行后续环境检测。适用于离线环境或已知无需更新的场景。可与 `--quiet` 组合使用。

---

## 三、API 调用方式

所有接口通过统一的签名脚本调用，服务固定参数：
- **service**: `advisor`
- **host**: `advisor.tencentcloudapi.com`
- **version**: `2020-07-21`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com <Action> 2020-07-21 '<payload>' [region]
```

---

## 四、可用接口（共 6 个）

所有接口频率限制均为 **20 次/秒**。使用某个接口前，**必须先加载对应的接口文档**获取参数、返回值和展示规则等详细信息。

### 4.1 DescribeArch — 获取云架构详情

获取指定云架构图的详细信息。必填参数：`ArchId`、`Username`。
- **触发词**："架构详情"、"查看架构图"、"架构图详情"
- **详细文档**：使用前加载 `{baseDir}/references/DescribeArch.md`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com DescribeArch 2020-07-21 '{"ArchId":"arch-xxx","Username":"user1"}'
```

### 4.2 DescribeArchList — 获取云架构列表

分页获取云架构图列表，支持按名称、关键词、文件夹等筛选。必填参数：`PageNumber`、`PageSize`。
- **触发词**："架构列表"、"所有架构图"、"云架构列表"
- **详细文档**：使用前加载 `{baseDir}/references/DescribeArchList.md`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com DescribeArchList 2020-07-21 '{"PageNumber":1,"PageSize":10}'
```

### 4.3 ListDirectoryV2 — 新版目录查询

查询云架构图的目录树结构。无必填参数。
- **触发词**："查询目录"、"目录列表"、"架构目录"
- **详细文档**：使用前加载 `{baseDir}/references/ListDirectoryV2.md`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com ListDirectoryV2 2020-07-21 '{}'
```

### 4.4 ListUnorganizedDirectory — 查询待整理目录

查询新版目录下的待整理（未归类）目录结构。无必填参数。
- **触发词**："待整理目录"、"未归类架构"、"待整理"
- **详细文档**：使用前加载 `{baseDir}/references/ListUnorganizedDirectory.md`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com ListUnorganizedDirectory 2020-07-21 '{}'
```

### 4.5 DescribeStrategies — 获取风险评估项列表

查询全量风险评估项（巡检项），支持客户端按产品/分组/风险等级筛选。无必填参数。
- **触发词**："风险评估"、"巡检项"、"评估项"、"风险项"、"安全检查"、"云资源风险"
- **详细文档**：使用前加载 `{baseDir}/references/DescribeStrategies.md`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com DescribeStrategies 2020-07-21 '{}'
```

### 4.6 DescribeLastEvaluation — 获取架构图最近一次评估结果

获取指定架构图的 Well-Architected 评估结果，含总分、各维度得分和治理建议。必填参数：`ArchId`。
- **触发词**："架构评估"、"评估结果"、"架构图得分"、"Well-Architected"、"架构巡检结果"
- **详细文档**：使用前加载 `{baseDir}/references/DescribeLastEvaluation.md`

```bash
python3 {baseDir}/scripts/tcloud_api.py advisor advisor.tencentcloudapi.com DescribeLastEvaluation 2020-07-21 '{"ArchId":"arch-xxx"}'
```

---

## 五、免密登录链接生成

当接口返回结果中包含架构图（含 `ArchId` 字段）时，**必须**调用免密登录脚本为用户生成腾讯云控制台直达链接，用户点击即可免登录跳转到对应页面。架构图列表场景下，只需为**第一张架构图**生成免密链接。

> **⚠️ 重要**：免密登录链接**每次都必须重新生成**，不可缓存或复用之前生成的链接。每次向用户展示时，都必须重新调用 `login_url.py` 生成新的链接。

### 5.1 前置条件

为生成免密登录链接，需要先完成角色配置。请按「二、前置检查」中的初始化工作流完成角色配置（检测 → 用户同意 → 创建角色 → 确认就绪）。

也可以通过以下方式手动配置角色：

**配置向导**
```bash
python3 {baseDir}/scripts/setup_role.py
```

**简化配置**（写入 `~/.bashrc` 或 `~/.zshrc`）
```bash
echo 'export TENCENTCLOUD_ROLE_NAME="advisor"' >> ~/.bashrc && source ~/.bashrc
```

**完整配置**（写入 `~/.bashrc` 或 `~/.zshrc`）
```bash
echo 'export TENCENTCLOUD_ROLE_ARN="qcs::cam::uin/100001234567:roleName/advisor"' >> ~/.bashrc && source ~/.bashrc
```

可选环境变量:
- `TENCENTCLOUD_ROLE_SESSION` — 角色会话名称（默认 `advisor-session`）
- `TENCENTCLOUD_STS_DURATION` — 临时凭证有效期秒数（默认 `3600`，即 1 小时；最大 `43200`，即 12 小时）

> **提示**: 详细配置说明请参考"一、鉴权方式"章节

### 5.2 调用方式

```bash
python3 {baseDir}/scripts/login_url.py "<目标页面URL>"
```

架构图控制台页面 URL 格式：`https://console.cloud.tencent.com/advisor?archId={ArchId}`

### 5.3 调用示例

```bash
# 为指定架构图生成免密链接
python3 {baseDir}/scripts/login_url.py \
  "https://console.cloud.tencent.com/advisor?archId=arch-gvqocc25"

# 跳转到智能顾问首页
python3 {baseDir}/scripts/login_url.py \
  "https://console.cloud.tencent.com/advisor"
```

### 5.4 返回示例

```json
{
  "success": true,
  "action": "GenerateLoginURL",
  "data": {
    "loginUrl": "https://cloud.tencent.com/login/roleAccessCallback?algorithm=sha256&secretId=...&token=...&signature=...&s_url=https%3A%2F%2Fconsole.cloud.tencent.com%2Fadvisor%3FarchId%3Darch-gvqocc25",
    "targetUrl": "https://console.cloud.tencent.com/advisor?archId=arch-gvqocc25",
    "expireSeconds": 3600
  },
  "requestId": "xxx"
}
```

| 字段 | 说明 |
|------|------|
| `loginUrl` | 免密登录完整 URL，用户点击可直接跳转控制台 |
| `targetUrl` | 登录后跳转的目标页面 |
| `expireSeconds` | 链接有效期（秒） |

### 5.5 展示规则

免密登录 URL 非常长，**严禁直接展示完整 URL**。每次展示时**必须重新调用脚本生成新链接**（链接不可复用），并以 Markdown 超链接格式展示：

```
[跳转控制台](免密登录URL)
```

示例输出：

```
架构图名称：生产环境架构
架构图 ID：arch-gvqocc25
[跳转控制台](https://cloud.tencent.com/login/roleAccessCallback?algorithm=sha256&secretId=...&token=...&signature=...&s_url=https%3A%2F%2Fconsole.cloud.tencent.com%2Fadvisor%3FarchId%3Darch-gvqocc25)
```

列表场景示例（仅第一张架构图附带免密链接）：

```
1. 生产环境架构（arch-abc123）— [跳转控制台](免密登录URL)
2. 测试环境架构（arch-def456）
3. 预发布环境架构（arch-ghi789）
```

### 5.6 工作流程：查询架构并生成控制台链接

当用户查询架构图时，完整流程如下：

```bash
# 第一步：查询架构列表
RESULT=$(python3 {baseDir}/scripts/tcloud_api.py \
  advisor advisor.tencentcloudapi.com \
  DescribeArchList 2020-07-21 \
  '{"PageNumber":1,"PageSize":10}')

# 第二步：从结果中提取 ArchId（假设取第一个）
ARCH_ID=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
arch_list = data.get('data', {}).get('ArchList', [])
if arch_list:
    print(arch_list[0]['ArchId'])
")

# 第三步：为该架构图生成免密登录链接
LOGIN_RESULT=$(python3 {baseDir}/scripts/login_url.py \
  "https://console.cloud.tencent.com/advisor?archId=${ARCH_ID}")

# 第四步：提取 loginUrl 并以超链接形式展示
LOGIN_URL=$(echo "$LOGIN_RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('data', {}).get('loginUrl', ''))
")

# 输出给用户（Markdown 超链接格式，注意：每次都必须重新生成链接）
echo "[跳转控制台](${LOGIN_URL})"
```

### 5.7 实现原理

1. **STS AssumeRole** — 使用 AK/SK 调用 STS 服务扮演指定角色，获取临时凭证（TmpSecretId、TmpSecretKey、Token）
2. **签名生成** — 使用临时密钥对登录回调 URL 进行 HMAC-SHA256 签名
3. **拼接 URL** — 将临时凭证、签名、目标页面 URL 拼接为免密登录链接
4. 用户点击链接 → 腾讯云验证签名 → 自动登录 → 跳转到目标页面

---

## 六、统一输出格式

所有接口调用的输出均为统一的 JSON 格式，通过 `success` 字段区分成功与失败。

### 成功响应

```json
{
  "success": true,
  "action": "DescribeArchList",
  "data": { ... },
  "requestId": "9cbe807c-..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | Boolean | 固定为 `true` |
| `action` | String | 调用的接口名称 |
| `data` | Object | 接口返回的业务数据（已去除 RequestId） |
| `requestId` | String | 腾讯云请求 ID，用于问题排查 |

### 失败响应

```json
{
  "success": false,
  "action": "DescribeArchList",
  "error": {
    "code": "AuthFailure.SecretIdNotFound",
    "message": "The SecretId is not found, please ensure that your SecretId is correct."
  },
  "requestId": "ed93f3cb-..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | Boolean | 固定为 `false` |
| `action` | String | 调用的接口名称 |
| `error.code` | String | 错误码 |
| `error.message` | String | 错误描述 |
| `requestId` | String | 腾讯云请求 ID（网络错误时为空） |

### 特殊错误码（脚本层面）

| 错误码 | 含义 |
|--------|------|
| `MissingParameter` | 脚本调用缺少必要参数 |
| `MissingCredentials` | 未配置 AK/SK 环境变量 |
| `NetworkError` | 网络请求失败，无法连接 API |
| `ParseError` | 响应不是有效的 JSON |

### 常见 API 错误码

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `AuthFailure.SecretIdNotFound` | SecretId 不存在 | 检查 TENCENTCLOUD_SECRET_ID |
| `AuthFailure.SignatureFailure` | 签名错误 | 检查 TENCENTCLOUD_SECRET_KEY |
| `AuthFailure.SignatureExpire` | 签名过期 | 检查本地时间是否准确 |
| `AuthFailure.TokenFailure` | Token 错误 | 检查 TENCENTCLOUD_TOKEN |
| `AuthFailure.UnauthorizedOperation` | 未授权 | 检查 CAM 策略 |
| `ResourceNotFound` | 资源不存在 | 检查 ArchId 等参数是否正确 |
| `InvalidParameter` | 参数错误 | 检查请求参数格式和类型 |
| `InvalidParameterValue` | 参数取值错误 | 检查参数值范围 |
| `RequestLimitExceeded` | 频率限制 | 降低调用频率（限 20 次/秒） |

---

## 七、注意事项

1. **密钥安全**：严禁将 AK/SK 硬编码在代码中，必须通过环境变量传入
2. **权限控制**：建议使用子账号密钥，角色关联 `QcloudTAGFullAccess` 和 `QcloudAdvisorFullAccess` 策略
3. **临时密钥**：生产环境推荐使用 STS 临时密钥，设置 `TENCENTCLOUD_TOKEN`
4. **频率限制**：所有接口限制 20 次/秒（维度：API + 接入地域 + 子账号）
5. **地域选择**：默认 `ap-guangzhou`，Region 为可选参数
6. **跨平台支持**：所有脚本均使用纯 Python 实现，支持 Windows / Linux / macOS，无需 curl、openssl、jq 等外部依赖
7. **免密链接有效期**：默认 1 小时（3600 秒），可通过 `TENCENTCLOUD_STS_DURATION` 调整（最大 43200 秒，即 12 小时）
8. **架构图免密链接**：当返回结果包含架构图时，只需为**第一张架构图**生成免密登录控制台链接，并以 `[跳转控制台](免密登录URL)` 超链接形式展示，严禁直接展示完整 URL。**每次展示都必须重新调用 `login_url.py` 生成新链接，不可缓存或复用之前生成的链接**
9. **评估项控制台链接**：评估项不需要免密登录链接，直接展示控制台 URL：`https://console.cloud.tencent.com/advisor/assess?strategyName={URL编码后的Name}`
10. **按需加载接口文档**：使用某个接口前，必须先通过 `read_file` 加载 `{baseDir}/references/<Action>.md` 获取完整的参数说明、返回字段、展示格式等详细信息

---

## 八、安全与权限声明

### 8.1 所需凭证

本 Skill 需要以下环境变量才能正常运行：

| 环境变量 | 必填 | 说明 |
|---------|------|------|
| `TENCENTCLOUD_SECRET_ID` | **是** | 腾讯云 API SecretId |
| `TENCENTCLOUD_SECRET_KEY` | **是** | 腾讯云 API SecretKey |

密钥仅通过环境变量读取，**不会**被写入文件、日志或网络传输中。

### 8.2 IAM 操作声明

本 Skill 包含以下 CAM（访问管理）操作。**写入类操作仅由独立脚本 `scripts/create_role.py` 执行，且必须在用户明确同意后才会运行**。`check_env.py` 仅执行只读检测操作。

| API 操作 | 类型 | 所在脚本 | 说明 |
|---------|------|---------|------|
| `sts:GetCallerIdentity` | 只读 | `check_env.py` / `create_role.py` | 获取当前账号 UIN |
| `cam:GetRole` | 只读 | `check_env.py` / `create_role.py` | 检查角色是否存在 |
| `cam:DescribeRoleList` | 只读 | `setup_role.py` | 列出可用角色供用户选择 |
| `cam:CreateRole` | **写入** | `scripts/create_role.py` | 创建 `advisor` 角色（需用户明确同意后执行） |
| `cam:AttachRolePolicy` | **写入** | `scripts/create_role.py` | 关联 `QcloudAdvisorFullAccess` 策略（随角色创建执行） |
| `sts:AssumeRole` | 敏感 | `login_url.py` | 扮演角色获取临时凭证（用于生成免密登录链接） |
| `cam:DeleteRole` | **写入** | `scripts/cleanup.py` | 删除 `advisor` 角色（仅 `--cloud` 模式，需用户明确确认） |

### 8.3 数据安全

- **临时凭证**：STS AssumeRole 获取的临时凭证仅在内存中使用，不持久化存储
- **配置文件**：`~/.tencent-cloudq/config.json` 仅保存角色 ARN 和账号 UIN，**不保存任何密钥**
- **文件权限**：配置目录设为 `700`，配置文件设为 `600`，仅当前用户可读写
- **SSL 验证**：所有 HTTPS 请求均启用完整的 SSL 证书验证，不支持跳过验证
- **网络访问**：仅连接腾讯云官方 API 域名（`*.tencentcloudapi.com`）和登录域名（`cloud.tencent.com`）

### 8.4 配置清理

用户可随时运行清理脚本删除本机上的所有配置和缓存：

```bash
# 交互式清理（逐项确认）
python3 {baseDir}/scripts/cleanup.py

# 一键清理所有本地配置
python3 {baseDir}/scripts/cleanup.py --all

# 一键清理所有本地配置 + 云端 advisor 角色
python3 {baseDir}/scripts/cleanup.py --all --cloud
```

清理范围：
- 配置目录 `~/.tencent-cloudq/`（含 `config.json`）
- 临时缓存 `{系统临时目录}/.tcloud_advisor_uin_cache`
- 环境变量 `TENCENTCLOUD_*` 系列（`SECRET_ID`、`SECRET_KEY`、`TOKEN`、`ROLE_ARN`、`ROLE_NAME`、`ROLE_SESSION`、`STS_DURATION`），脚本会自动检测已设置的变量并生成对应平台的清理命令（`source` 脚本 / PowerShell 脚本）
- 云端 CAM 角色 `advisor`（仅 `--cloud` 模式，需配置 AK/SK）
