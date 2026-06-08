---
name: "assethub"
description: "资产管理系统AI助手(openclaw技能)。用于资产查询、维修报修、盘点管理、折旧计算等资产全生命周期管理"
version: "2.0.3"
metadata: { "openclaw": { "emoji": "📦", "requires": { "apis": ["需要配置"] } } }
---

# AssetHub 资产管理系统 API 技能

> ⚠️ 安全提示：请勿在配置文件中存储明文密码，建议使用环境变量或运行时输入

**配置文件**: `~/.assethub/config.json`

资产管理系统 API 助手，支持资产查询、维修报修、盘点管理等。

**Base URL**: `http://160ttth72797.vicp.fun:59745/api`
**认证**: 动态 Token (每次调用自动获取)

---

## v4.0 新特性

- ✅ 每次调用自动获取 Token (安全)
- ✅ 支持配置文件多租户切换
- ✅ 数据缓存减少 API 调用
- ✅ 自动重试机制
- ✅ 交互式 REPL 模式

## v4.1 新增

- ✅ 支持获取全量数据（分页自动遍历）
- ✅ 默认 pageSize 改为 1000

## v4.2 新增

- ✅ 未配置密码时，交互式提示输入用户名/密码/租户ID

---

## 快速开始

### 方式一: 交互式模式 (推荐)

```bash
ASSETHUB_PASS=密码 python query.py -i
```

### 方式二: 命令行

```bash
ASSETHUB_PASS=密码 python query.py stats
```

### 方式三: 配置文件

创建 `~/.assethub/config.json`:

```json
{
    "base_url": "http://160ttth72797.vicp.fun:59745/api",
    "tenant_id": "2",
    "username": "su",
    "password": "你的密码",
    "token_cache_seconds": 300,
    "cache_ttl": 60,
    "max_retries": 3
}
```

### 环境变量 (优先级最高)

```bash
export ASSETHUB_URL=http://160ttth72797.vicp.fun:59745/api
export ASSETHUB_TENANT=2
export ASSETHUB_USER=su
export ASSETHUB_PASS=密码
```

---

## 常用查询

### 查询资产列表

```bash
# 查询所有资产 (前300条)
curl -s "http://160ttth72797.vicp.fun:59745/api/assets?page=1&pageSize=300" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

**筛选参数:**
- `keyword` - 关键词搜索
- `department` / `department_new` - 部门筛选
- `status` - 资产状态（在用/闲置/维修/报废）
- `category_id` - 资产分类ID
- `location` - 存放地点

```bash
# 查询手术室资产
curl -s "http://160ttth72797.vicp.fun:59745/api/assets?page=1&pageSize=300" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" | jq '.data.list[] | select(.department_new | contains("手术室"))'

# 查询在用资产
curl -s "http://160ttth72797.vicp.fun:59745/api/assets?page=1&pageSize=300&status=在用" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 查询单个资产详情

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/assets/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 维修管理

### 查询维修申请

```bash
# 所有维修申请
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/requests?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"

# 按状态筛选
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/requests?status=待审批" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 创建维修申请

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/maintenance/requests \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_code": "资产编码",
    "fault_description": "故障描述",
    "fault_level": "一般/紧急/严重",
    "request_person": "报修人",
    "department": "报修部门"
  }'
```

### 查询维修工单

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/workorders?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 查询维修日志

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/logs?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 部门与用户

### 查询部门列表

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/departments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 查询用户列表

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/users?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 盘点管理

### 查询盘点任务

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/inventory?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 采购管理

### 查询采购申请

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/procurement/requests?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 折旧管理

### 查询折旧明细

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/asset-depreciation/depreciation?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 创建报修申请

### 创建维修申请

⚠️ **注意**: 创建维修申请是高风险操作，需要：
1. 添加 `Idempotency-Key` 请求头
2. 二次确认（系统返回 confirmToken 后再确认一次）

```bash
# 第一次请求 (获取确认token)
IDEMPOTENCY_KEY=$(openssl rand -hex 16)

RESP=$(curl -s -X POST http://160ttth72797.vicp.fun:59745/api/maintenance/requests \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -d '{
    "asset_code": "资产编码",
    "asset_name": "资产名称",
    "fault_description": "故障描述",
    "fault_level": "一般",
    "request_person": "报修人",
    "department": "部门"
  }')

# 如果返回 requiresConfirmation=true，则需要二次确认
CONFIRM_TOKEN=$(echo $RESP | jq -r '.confirmToken')

curl -X POST http://160ttth72797.vicp.fun:59745/api/maintenance/requests \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -H "X-Risk-Confirm-Token: $CONFIRM_TOKEN" \
  -d '{
    "asset_code": "资产编码",
    "asset_name": "资产名称",
    "fault_description": "故障描述",
    "fault_level": "一般",
    "request_person": "报修人",
    "department": "部门"
  }'
```

**fault_level 可选值:** 一般、紧急、严重

---

## 资产盘点

### 查询盘点任务

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/inventory?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 创建盘点任务

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/inventory \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "2026年3月手术室盘点",
    "planned_date": "2026-03-25",
    "department": "手术室（崇山）"
  }'
```

---

## 采购申请

### 创建采购申请

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/procurement/requests \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_name": "新资产名称",
    "specification": "规格型号",
    "quantity": 1,
    "estimated_price": 50000,
    "purpose": "采购用途",
    "department": "申请部门",
    "applicant": "申请人"
  }'
```

---

## 资产调拨

### 查询调拨申请

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/transfer?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 创建调拨申请

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/transfer \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_code": "资产编码",
    "from_department": "调出部门",
    "to_department": "调入部门",
    "transfer_reason": "调拨原因"
  }'
```

---

## 资产报废

### 查询报废申请

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/scrapping?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 创建报废申请

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/scrapping \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_code": "资产编码",
    "asset_name": "资产名称",
    "scrapping_reason": "报废原因",
    "estimated_value": 0,
    "applicant": "申请人"
  }'
```

---

## 资产定位

### 查询资产位置

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/asset-location/assets/{assetCode}/location" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 更新资产位置

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/asset-location/assets/{assetCode}/location \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "building_name": "5号楼",
    "room_number": "401",
    "floor": "4"
  }'
```

---

## 常用查询示例

### 按部门统计资产

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/assets?page=1&pageSize=300" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" | jq '
  [.data.list[].department_new] | group_by(.) | map({department: .[0], count: length}) | sort_by(.count) | reverse
'
```

### 资产价值汇总

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/assets?page=1&pageSize=300" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" | jq '
  [.data.list[] | select(.purchase_price != null) | .purchase_price | tonumber] | add
'
```

### 查询高价值资产 (TOP 10)

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/assets?page=1&pageSize=300" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" | jq '
  .data.list | sort_by(.purchase_price | tonumber) | reverse | .[0:10] | .[] | {name: .asset_name, price: .purchase_price, dept: .department_new}
'
```

---

## 常见问题

### Q: 登录失败提示"登录尝试过于频繁"
A: API 有频率限制，等待5分钟后重试。

### Q: 如何查看资产分类?
A: 查询资产时返回的 `category_name` 字段即为分类名称。

### Q: 资产状态有哪些?
A: 在用、闲置、维修、报废、调配中

---

---

## 预防性维护

### 查询维护计划

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/plans?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 查询维护模板

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/templates?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 查询维修费用

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/costs?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

### 查询维修统计

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/maintenance/analytics" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 资产分类

### 查询资产分类

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/asset-categories" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 资产标签

### 打印资产标签

```bash
curl -X POST http://160ttth72797.vicp.fun:59745/api/asset-labels/print \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_codes": ["资产编码1", "资产编码2"],
    "printer": "打印机名称"
  }'
```

---

## 资产验收

### 查询验收记录

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/acceptance?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 计量检定

### 查询计量记录

```bash
curl -s "http://160ttth72797.vicp.fun:59745/api/quality-control/metrology?page=1&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: 2"
```

---

## 完整 API 模块列表

| 模块 | 路径 | 接口数 |
|------|------|--------|
| 资产 | `/assets` | 16 |
| 维修维护 | `/maintenance` | 92 |
| 采购管理 | `/procurement` | 11 |
| 部门 | `/departments` | 6 |
| 用户 | `/users` | 15 |
| 盘点 | `/inventory` | 18 |
| 资产定位 | `/asset-location` | 13 |
| 物联网 | `/iot` | 48 |
| 技术资料 | `/technical-documents` | 59 |
| 质量控制 | `/quality-control` | 30 |
| 折旧 | `/asset-depreciation` | 10 |
| 权限 | `/roles-permissions` | 18 |
| 验收 | `/acceptance` | 12 |
| 调拨 | `/transfer` | 7 |
| 报废 | `/scrapping` | 11 |
| 资产分类 | `/asset-categories` | 6 |
| 资产标签 | `/asset-labels` | 5 |

---

**完整 API 文档**: `memory/assethub_api.md` (688个接口)
**快速索引**: `memory/assethub_api_index.md`

---

## 快速查询命令 (v2.0)

使用 `scripts/query.py` 快速查询:

```bash
# 仪表盘
python3 scripts/assethub/query.py dashboard

# 资产查询
python3 scripts/assethub/query.py assets 手术室
python3 scripts/assethub/query.py asset <资产ID>

# 维修管理
python3 scripts/assethub/query.py repair
python3 scripts/assethub/query.py workorder
python3 scripts/assethub/query.py plans
python3 scripts/assethub/query.py costs

# 统计报表
python3 scripts/assethub/query.py stats
python3 scripts/assethub/query.py stats-by-dept
python3 scripts/assethub/query.py stats-by-category
python3 scripts/assethub/query.py stats-by-status
python3 scripts/assethub/query.py stats-value
python3 scripts/assethub/query.py stats-age

# 专项查询
python3 scripts/assethub/query.py top 20
python3 scripts/assethub/query.py idle-assets
python3 scripts/assethub/query.py expiring-warranty 30
python3 scripts/assethub/query.py repair-trend
python3 scripts/assethub/query.py repair-by-dept

# 部门资产
python3 scripts/assethub/query.py dept-assets 手术室
```

---

## 完整命令列表

| 命令 | 说明 |
|------|------|
| dashboard | 仪表盘视图 |
| assets [关键词] | 资产列表 |
| asset \<id\> | 资产详情 |
| repair | 维修申请 |
| workorder | 维修工单 |
| plans | 维护计划 |
| costs | 维修费用 |
| department / dept | 部门列表 |
| dept-assets \<部门\> | 某部门资产 |
| categories | 资产分类统计 |
| inventory | 盘点任务 |
| procurement | 采购申请 |
| transfer | 调拨申请 |
| scrapping | 报废申请 |
| location \<编码\> | 资产位置 |
| acceptance | 验收记录 |
| metrology | 计量记录 |
| stats | 综合统计 |
| stats-by-dept | 按部门统计 |
| stats-by-category | 按分类统计 |
| stats-by-status | 按状态统计 |
| stats-value | 价值分布 |
| stats-age | 年限分布 |
| top [n] | 高价值资产 |
| idle-assets | 闲置资产 |
| expiring-warranty [天] | 即将过保 |
| repair-trend | 维修趋势 |
| repair-by-dept | 部门维修统计 |
| help | 帮助 |

---

**技能版本**: 2.0
**最后更新**: 2026-03-21

---

## 高级分析命令 (v3.0)

```bash
# 全面分析
python3 scripts/assethub/query.py analysis-full
python3 scripts/assethub/query.py analysis-dept 手术室
python3 scripts/assethub/query.py analysis-repair
python3 scripts/assethub/query.py analysis-warranty
python3 scripts/assethub/query.py analysis-depreciation

# 导出功能
python3 scripts/assethub/query.py export-csv
python3 scripts/assethub/query.py export-summary

# 工具
python3 scripts/assethub/query.py validate
python3 scripts/assethub/query.py dashboard
```

---

## 完整命令列表 (v3.0)

| 分类 | 命令 | 说明 |
|------|------|------|
| **查询** | assets [关键词] | 资产列表 |
| | asset \<id\> | 资产详情 |
| | repair | 维修申请 |
| | workorder | 维修工单 |
| | plans | 维护计划 |
| | costs | 维修费用 |
| | department / dept | 部门列表 |
| | dept-assets \<部门\> | 部门资产 |
| | inventory | 盘点任务 |
| | procurement | 采购申请 |
| | transfer | 调拨申请 |
| | scrapping | 报废申请 |
| | location \<编码\> | 资产位置 |
| | acceptance | 验收记录 |
| | metrology | 计量记录 |
| **统计** | stats | 综合统计 |
| | stats-by-dept | 按部门统计 |
| | stats-by-category | 按分类统计 |
| | stats-by-status | 按状态统计 |
| | stats-value | 价值分布 |
| | stats-age | 年限分布 |
| | top [n] | 高价值资产 |
| | idle-assets | 闲置资产 |
| | expiring-warranty [天] | 即将过保 |
| | repair-trend | 维修趋势 |
| | repair-by-dept | 部门维修 |
| **分析** | analysis-full | 全面分析报告 |
| | analysis-dept \<部门\> | 部门资产分析 |
| | analysis-repair | 维修深度分析 |
| | analysis-warranty | 保修分析 |
| | analysis-depreciation | 折旧分析 |
| **导出** | export-csv | 导出CSV |
| | export-summary | 导出汇总报表 |
| **工具** | dashboard | 仪表盘 |
| | validate | 验证API |
| | help | 帮助 |

---

**技能版本**: 3.0
**代码行数**: 454
**最后更新**: 2026-03-21

---

## 提醒与报表功能 (v3.1)

```bash
# 提醒功能
python3 scripts/assethub/query.py warranty-reminder    # 保修到期提醒
python3 scripts/assethub/query.py idle-reminder       # 闲置资产提醒
python3 scripts/assethub/query.py pending-reminder   # 待审批维修提醒
python3 scripts/assethub/query.py daily-summary       # 每日汇总报告

# 详细报表
python3 scripts/assethub/query.py report-dept        # 部门详细报表
python3 scripts/assethub/query.py report-category     # 分类详细报表
```

---

## 完整命令列表 (v3.1)

| 分类 | 命令 | 说明 |
|------|------|------|
| **查询** | assets [关键词] | 资产列表 |
| | asset \<id\> | 资产详情 |
| | repair | 维修申请 |
| | workorder | 维修工单 |
| | plans | 维护计划 |
| | costs | 维修费用 |
| | department / dept | 部门列表 |
| | dept-assets \<部门\> | 部门资产 |
| | inventory | 盘点任务 |
| | procurement | 采购申请 |
| | transfer | 调拨申请 |
| | scrapping | 报废申请 |
| | location \<编码\> | 资产位置 |
| | acceptance | 验收记录 |
| | metrology | 计量记录 |
| **统计** | stats | 综合统计 |
| | stats-by-dept | 按部门统计 |
| | stats-by-category | 按分类统计 |
| | stats-by-status | 按状态统计 |
| | stats-value | 价值分布 |
| | stats-age | 年限分布 |
| | top [n] | 高价值资产 |
| | idle-assets | 闲置资产 |
| | expiring-warranty [天] | 即将过保 |
| | repair-trend | 维修趋势 |
| | repair-by-dept | 部门维修 |
| **分析** | analysis-full | 全面分析报告 |
| | analysis-dept \<部门\> | 部门资产分析 |
| | analysis-repair | 维修深度分析 |
| | analysis-warranty | 保修分析 |
| | analysis-depreciation | 折旧分析 |
| **导出** | export-csv | 导出CSV |
| | export-summary | 导出汇总报表 |
| **提醒** | warranty-reminder | 保修到期提醒 |
| | idle-reminder | 闲置资产提醒 |
| | pending-reminder | 待审批提醒 |
| | daily-summary | 每日汇总报告 |
| **报表** | report-dept | 部门详细报表 |
| | report-category | 分类详细报表 |
| **工具** | dashboard | 仪表盘 |
| | validate | 验证API |
| | help | 帮助 |

---

**技能版本**: 3.1
**代码行数**: 565
**最后更新**: 2026-03-21
