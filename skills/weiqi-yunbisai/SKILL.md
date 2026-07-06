---
name: 云比赛网围棋数据查询
description: weiqi-yunbisai 云比赛网围棋比赛数据查询 - 支持比赛列表、分组信息、对阵数据、排名计算。当用户需要"查比赛"、"云比赛网"、"围棋比赛"时使用此技能。
tags: ["围棋", "weiqi", "go", "比赛", "云比赛网", "排名", "对阵"]
---

# 云比赛网完整数据查询

> **🔒 安全说明**: 本技能通过云比赛网公开 API 查询围棋比赛公开数据。所有请求仅读取公开的赛事信息、分组数据和比赛结果，不涉及任何敏感信息或未经授权的访问。代码开源可审计。
>
> **v1.1.1 安全更新**: 已修复潜在 HTML 注入漏洞，所有从 API 获取的数据（选手名、比赛标题等）在生成 HTML 报告前均进行转义处理。


## 功能描述
完整的云比赛网(yunbisai.com)围棋比赛数据查询技能包，支持从比赛发现到个人对局记录的全流程查询。

## 依赖安装
```bash
pip3 install requests
```

---

## 🚀 快速查询工具（带性能跟踪）

**脚本**: `scripts/query.py`

### 功能特性
- ✅ 比赛列表查询（支持多页自动抓取）
- ✅ 分组信息查询
- ✅ 分组选手查询
- ✅ 完整对阵数据获取
- ✅ 自动排名计算（积分/对手分/累进分）
- ✅ **详细性能计时** - 每个步骤耗时统计

### 使用方法

```bash
# 查询广东省最近1个月的比赛
python3 scripts/query.py

# 查询浙江省最近3个月的比赛
python3 scripts/query.py --area "浙江省" --month 3

# 关键词搜索（在所有比赛中搜索含"秦山"的比赛）
python3 scripts/query.py --area "浙江省" --month 6 --keyword "秦山"

# 查询指定比赛的分组
python3 scripts/query.py --event-id 12345

# 查询分组并计算完整排名
python3 scripts/query.py --event-id 12345 --group-id 67890 --ranking

# 查询指定轮次对阵表
python3 scripts/query.py --event-id 12345 --group-id 67890 --matchups 1

# JSON 输出（含性能数据）
python3 scripts/query.py --event-id 12345 --group-id 67890 --ranking --json

# 静默模式（减少日志输出）
python3 scripts/query.py --group-id 67890 --ranking --quiet
```

### 区域搜索说明

**重要**：搜索特定省份比赛时，使用 `--area` 参数：

```bash
# ✅ 正确用法 - 使用完整省份名称
python3 scripts/query.py --area "浙江省" --month 3
python3 scripts/query.py --area "广东省" --month 1

# ✅ 配合关键词快速定位比赛
python3 scripts/query.py --area "浙江省" --keyword "秦山核电"
```

**区域代码参考**：
- `广东省`、`浙江省`、`江苏省`、`山东省` ...

### 输出格式规则

脚本根据数据量自动选择输出格式：

- **≤ 10 行**：单行 Markdown 格式（便于阅读和复制）
- **> 10 行**：自动导出为 HTML 文件（手机端优化），同时显示前10条预览

**单行格式示例（≤10行）：**
```
📋 找到 10 场比赛

• [12345] **2026年某省第X届"XX杯"业余围棋段级位赛** | 城市: 某市 | 日期: 2026-03-29
• [12346] **2026年某市围棋友谊赛** | 城市: 某市 | 日期: 2026-03-21
...

📋 排名列表

1. **选手A** | 积分: 12 | 对手分: 48 | 累进分: 42 | 6胜0负
2. **选手B** | 积分: 10 | 对手分: 44 | 累进分: 40 | 5胜1负
...
```

**HTML 导出示例（>10行）：**
```
📊 排名数据已导出到 HTML 文件: /tmp/ranking_1234567890.html
   共 67 条记录

📋 前10名预览:

1. **选手A** | 积分: 16 | 对手分: 88 | 累进分: 72 | 8胜0负
2. **选手B** | 积分: 14 | 对手分: 96 | 累进分: 70 | 7胜1负
...

... 还有 57 名选手
```

**HTML 文件特点（手机端优化）：**
- 📱 **完美适配手机**：响应式设计，适配各种屏幕尺寸
- 🎨 **卡片式布局**：列表项采用卡片设计，易于滑动浏览
- 🏷️ **视觉层次分明**：排名、姓名、数据清晰分离
- 🥇 **前3名特殊标识**：前三名红色高亮显示
- 🎖️ **前8名获奖标识**：第4-8名橙色标识，并带"获奖"标签
- 📌 **固定头部**：标题栏随页面滚动固定顶部
- 👆 **点击反馈**：点击时有视觉反馈效果
- 🚫 **禁止缩放**：优化移动端浏览体验

### 📤 文件发送方式

当通过 QQ 等即时通讯工具发送时，使用 `<qqmedia>` 标签发送 HTML 文件：

```
对阵表已生成：
<qqmedia>/tmp/matchups_xxx.html</qqmedia>
```

**注意**：
- 必须使用 `<qqmedia>绝对路径</qqmedia>` 格式
- 文件大小需小于 10MB
- 系统会根据扩展名自动识别为文件类型

### 性能报告示例

```
==================================================
⏱️  性能计时报告
==================================================
  获取所有轮次对阵          :    0.555s ( 99.9%)
  获取第1轮对阵             :    0.220s ( 39.6%)
  获取第2轮对阵             :    0.064s ( 11.6%)
  获取第3轮对阵             :    0.065s ( 11.6%)
  ...
  计算排名                  :    0.000s (  0.0%)
--------------------------------------------------
  步骤累计                  :    1.109s
  总耗时                    :    0.555s
==================================================
```

---

## 技能链条

## 技能链条

### 1️⃣ 获取比赛列表
**API**: `https://data-center.yunbisai.com/api/lswl-events`

**用途**: 获取某个区域/时间段的所有围棋比赛

**参数**:
- `areaNum`: 区域（如广东省）
- `month`: 最近多少个月
- `eventType`: 2（围棋）
- `page`: 页码
- `PageSize`: 每页数量

**示例**:
```bash
curl -s "https://data-center.yunbisai.com/api/lswl-events?page=1&eventType=2&month=1&areaNum=%E6%9F%90%E7%9C%81&PageSize=50"
```

**返回**: event_id, title, city_name, play_num 等

---

### 2️⃣ 获取比赛分组
**API**: `https://open.yunbisai.com/api/event/feel/list`

**用途**: 获取指定比赛的所有分组

**参数**:
- `event_id`: 比赛ID
- `page`: 1
- `pagesize`: 500

**示例**:
```bash
curl -s -H "Referer: https://www.yunbisai.com/" \
  "https://open.yunbisai.com/api/event/feel/list?event_id=12345&page=1&pagesize=500"
```

**返回**: group_id, groupname, 选手列表, 排名, 积分

**关键字段**:
- `group_id`: 分组唯一标识
- `groupname`: 组别名称（如"5段及以上组"）
- `participantname`: 选手姓名
- `rank_num`: 排名
- `integral`: 积分
- `vicsum`/`faisum`: 胜/负场数

---

### 3️⃣ 获取分组选手
**API**: `https://open.yunbisai.com/api/event/feel/list`

**用途**: 获取指定分组的详细选手信息

**参数**:
- `event_id`: 比赛ID
- `group_id`: 分组ID
- `page`: 1
- `pagesize`: 200

**示例**:
```bash
curl -s -H "Referer: https://www.yunbisai.com/" \
  "https://open.yunbisai.com/api/event/feel/list?event_id=12345&group_id=67890&page=1&pagesize=200"
```

---

### 4️⃣ 获取对局详情
**API**: `https://api.yunbisai.com//request/Group/Againstplan`

**用途**: 获取某组某轮的详细对阵表

**参数**:
- `groupid`: 分组ID
- `bout`: 轮次（1, 2, 3...）

**示例**:
```bash
curl -s -A "Mozilla/5.0" \
  "https://api.yunbisai.com//request/Group/Againstplan?groupid=67890&bout=1"
```

**返回关键字段**:
- `total_bout`: 总轮数
- `rows`: 对局列表
  - `p1`, `p2`: 选手姓名
  - `p1_score`, `p2_score`: 得分（2=胜, 1=和, 0=负）
  - `seatnum`: 台号
  - `p1_teamname`, `p2_teamname`: 所属团队

---

### 5️⃣ 统计选手成绩
**流程**:
1. 获取第1轮得到 `total_bout`
2. 遍历所有轮次（1 到 total_bout）
3. 累加每个选手的得分
4. 按总分排序

**计分规则**:
- 胜: 2分
- 和: 1分
- 负: 0分

**重要**: 使用 `p1_score` / `p2_score` 字段（0=负, 1=和, 2=胜），**不要**使用 `p1_result` / `p2_result`

---

### 5️⃣ 排名计算规则

#### 1. 个人积分
- 胜：2分
- 和：1分  
- 负：0分

#### 2. 对手分
所有已赛对手的个人积分之和

#### 3. 累进分
每轮结束后的累计积分之和

示例：4胜1负选手的累进分
- 第1轮后：2分
- 第2轮后：4分
- 第3轮后：6分
- 第4轮后：8分
- 第5轮后：8分（负）
- 累进分 = 2+4+6+8+8 = **28分**

#### 4. 排名优先级
1. **个人积分**（高者优先）
2. **对手分**（高者优先）
3. **累进分**（高者优先）

#### 5. 轮空处理
- 轮空选手的对手是 `None` / `null`
- 轮空获胜也得2分
- 轮空对手的积分（0分）不计入对手分

#### 6. 未完成轮次的处理 ⚠️

**重要**：计算排名时，必须检查每一轮是否已经完成。

**判断方法**：
```python
# 如果一轮中所有对局的 p1_score 和 p2_score 都是 0.0
# 说明该轮对阵表已出，但比赛尚未完成
is_round_completed = any(
    m.get('p1_score') not in [None, 0.0] or m.get('p2_score') not in [None, 0.0]
    for m in round_data
)
```

**处理规则**：
- ✅ **已完成的轮次**：正常计入排名计算
- ❌ **未完成的轮次**：**不得计入**排名计算，即使对阵表已发布

**错误示例**：
> 某比赛第2轮，所有对局 p1_score=0.0, p2_score=0.0，表示比赛还在进行中。若此时计入排名，会导致所有选手都是0分，排名计算错误。

**正确做法**：
> 只计算已完成的轮次（如第1轮），未完成的轮次等比赛结束后再更新。

---

### 6️⃣ 查询特定选手
**流程**:
1. 通过比赛列表找到 `event_id`
2. 获取比赛所有选手，筛选出目标选手
3. 得到 `group_id` 和基本信息
4. 遍历该组所有轮次对局
5. 筛选出目标选手的每轮对局

---

## 完整使用示例

### 示例1：查找某选手在指定比赛的成绩
```python
import requests

# 配置
player_name = "张三"
event_id = 12345  # 示例比赛ID

# 步骤1：获取比赛所有选手，找到目标选手的分组
response = requests.get(
    f"https://open.yunbisai.com/api/event/feel/list?event_id={event_id}&page=1&pagesize=500",
    headers={"Referer": "https://www.yunbisai.com/"}
)

for row in response.json()['datArr']['rows']:
    if row['participantname'] == player_name:
        group_id = row['group_id']
        print(f"找到！组别: {row['groupname']}, 排名: {row['rank_num']}")
        break

# 步骤2：获取该组所有轮次对局
total_bout = 8  # 从API获取
base_url = "https://api.yunbisai.com//request/Group/Againstplan"

for bout in range(1, total_bout + 1):
    response = requests.get(f"{base_url}?groupid={group_id}&bout={bout}")
    # 处理对局数据...
```

---

## 已掌握的实战案例

### 个人成绩查询示例

| 选手 | 比赛 | 组别 | 成绩 | 排名 |
|------|------|------|------|------|
| 选手A | 示例杯 | 儿童组 (12345) | 14分 (7胜2负) | 第7名 |
| 选手B | 示例杯 | 少年组 (12346) | 14分 (7胜3负) | - |
| 选手C | 示例赛 | 5段组 (12347) | 14分 (7胜1负) | 第10名 |

### 分组排行榜案例

#### 案例1: 示例比赛 - 4段组
- **event_id**: 12345
- **group_id**: 67890
- **参赛人数**: 15人
- **比赛轮次**: 5轮

| 排名 | 姓名 | 积分 | 对手分 | 累进分 | 战绩 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 | 选手A | 10 | 28 | 30 | 5胜0负 |
| 🥈 | 选手B | 8 | 30 | 20 | 4胜1负 |
| 🥉 | 选手C | 8 | 20 | 24 | 4胜1负 |
| 4 | 选手D | 6 | 36 | 24 | 3胜2负 |
| 5 | 选手E | 6 | 22 | 16 | 3胜2负 |

**排名分析**:
- 第2名 vs 第3名：同积8分，第2名对手分更高(30>20)
- 第6名：仅2胜，但对手分高达36，说明对手实力强

#### 案例2: 示例比赛 - 3段组
- **event_id**: 12345
- **group_id**: 67891
- **参赛人数**: 24人
- **比赛轮次**: 5轮

| 排名 | 姓名 | 积分 | 对手分 | 累进分 | 战绩 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 | 选手F | 8 | 34 | 26 | 4胜1负 |
| 🥈 | 选手G | 8 | 30 | 28 | 4胜1负 |
| 🥉 | 选手H | 8 | 30 | 22 | 4胜1负 |

**排名分析**:
- 前5名同积8分，按对手分排名
- 第2名 vs 第3名：对手分相同(30)，比较累进分(28>22)

---

## 触发指令

```
"查一下XXX在YYY比赛的成绩"
"获取ZZZ比赛的分组信息"
"列出AAA组的所有对局"
"统计BBB选手每轮的胜负"
```

---

## 排名计算完整代码

```python
import json

# 读取各轮对阵数据
rounds_data = []
for bout in range(1, total_bout + 1):
    with open(f'group{bout}.json', 'r') as f:
        data = json.load(f)
        rounds_data.append(data['datArr']['rows'])

# 初始化选手数据
players = {}

# 第一轮：初始化所有选手（跳过None轮空）
for match in rounds_data[0]:
    for key, name_key, team_key in [('p1id', 'p1', 'p1_teamname'), ('p2id', 'p2', 'p2_teamname')]:
        pid = match.get(key)
        name = match.get(name_key)
        team = match.get(team_key) or ''
        if pid and name and pid not in players:
            players[pid] = {
                'name': name, 'team': team,
                'wins': 0, 'losses': 0, 'draws': 0,
                'score': 0, 'opponents': [],
                'progressive': []  # 每轮累计积分
            }

# 逐轮解析 - 使用p1_score和p2_score计算积分
for round_idx, round_data in enumerate(rounds_data, 1):
    for match in round_data:
        p1_id = match.get('p1id')
        p2_id = match.get('p2id')
        p1_score = float(match.get('p1_score') or 0)  # 0=负, 1=和, 2=胜
        p2_score = float(match.get('p2_score') or 0)
        
        # 处理p1
        if p1_id and p1_id in players:
            if p2_id and match.get('p2') and p2_id in players:
                players[p1_id]['opponents'].append(p2_id)
            if p1_score == 2.0:
                players[p1_id]['wins'] += 1
            elif p1_score == 0.0:
                players[p1_id]['losses'] += 1
            else:
                players[p1_id]['draws'] += 1
            players[p1_id]['score'] += p1_score
        
        # 处理p2
        if p2_id and p2_id in players:
            if p1_id and match.get('p1') and p1_id in players:
                players[p2_id]['opponents'].append(p1_id)
            if p2_score == 2.0:
                players[p2_id]['wins'] += 1
            elif p2_score == 0.0:
                players[p2_id]['losses'] += 1
            else:
                players[p2_id]['draws'] += 1
            players[p2_id]['score'] += p2_score
        
        # 记录每轮后的累计积分（累进分）
        for pid in [p1_id, p2_id]:
            if pid and pid in players:
                players[pid]['progressive'].append(players[pid]['score'])

# 计算对手分和累进分
for pid, p in players.items():
    p['opponent_score'] = sum(players[oid]['score'] for oid in p['opponents'] if oid in players)
    p['progressive_score'] = sum(p['progressive'])

# 排序：个人积分 > 对手分 > 累进分
sorted_players = sorted(
    players.items(),
    key=lambda x: (x[1]['score'], x[1]['opponent_score'], x[1]['progressive_score']),
    reverse=True
)

# 输出排行榜
for i, (pid, p) in enumerate(sorted_players, 1):
    print(f"{i}. {p['name']} | 积分:{int(p['score'])} | 对手分:{int(p['opponent_score'])} | 累进分:{int(p['progressive_score'])}")
```

**关键要点：**
1. 使用 `p1_score` / `p2_score`（0/1/2）计算积分，**不要**用 `p1_result` / `p2_result`
2. 只添加有名字的选手（`name is not None`），跳过轮空
3. 轮空对手的积分（0分）不计入对手分
4. 每轮结束后记录累计积分（累进分）
5. 排序优先级：**个人积分 > 对手分 > 累进分**

---

## 输出规范

查询选手对局情况时，必须同时提供：

1. **对局详情** - 每轮对手、胜负、得分
2. **对手分** - 所有对手的总积分之和（通过遍历所有轮次累计）
3. **累进分** - 每轮累计得分的累加（第1轮累计 + 第2轮累计 + ...）

示例格式：
```
【对局记录】
轮次 | 对手 | 结果 | 得分
...

【对手分统计】
对手总分: XXX 分

【累进分统计】  
累进分合计: XXX 分
```

---

## 附加API参考

### 获取比赛列表（替代方案）
**API**: `https://data-center.yunbisai.com/api/lswl-events`

**参数**:
- `areaNum`: 区域（URL编码，如广东省=%E5%B9%BF%E4%B8%9C%E7%9C%81）
- `month`: 最近多少个月（1, 3, 6, 12）
- `eventType`: 2（围棋）
- `PageSize`: 每页数量

**示例**:
```bash
curl -s "https://data-center.yunbisai.com/api/lswl-events?page=1&areaNum=%E5%B9%BF%E4%B8%9C%E7%9C%81&month=1&eventType=2&PageSize=36"
```

**返回字段**:
- `event_id`: 比赛ID
- `title`: 比赛名称
- `city_name`: 城市
- `cname`: 主办单位
- `min_time`/`max_time`: 比赛时间
- `play_num`: 参赛人数
- `contact`/`linkMan`: 联系人及电话

---

## 触发指令汇总

```
# 比赛查询
"查一下最近X个月[地区]的围棋比赛"
"列出[地区]最近的围棋赛事"

# 分组查询
"查询比赛ID为XXX的分组信息"
"获取比赛XXX的所有组别"
"列出比赛XXX的选手名单"

# 排名计算
"查一下[event_id]比赛[group_name]组的排名"
"计算[event_id]比赛[group_name]组的排行榜"

# 个人成绩
"查一下XXX在YYY比赛的成绩"
"统计BBB选手每轮的胜负"
```

---

## 数据来源
- **平台**: 云比赛网 (yunbisai.com)
- **数据类型**: 围棋比赛、分组信息、对阵表、选手成绩

