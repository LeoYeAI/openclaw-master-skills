# Luban 配置编辑器命令详解

本文档包含所有命令的详细参数说明和示例。

## 基础参数

**执行方式**：
```bash
python scripts/luban_helper.py <command> --data-dir <项目的Datas目录>
```

**注意**：PowerShell 中使用分号 `;` 作为命令分隔符，不要使用 `&&`。

---

## 枚举操作

### enum list - 列出所有枚举
```bash
python scripts/luban_helper.py enum list --data-dir DataTables/Datas
```

### enum get - 查询枚举详情
```bash
python scripts/luban_helper.py enum get test.ETestQuality --data-dir DataTables/Datas
```

### enum add - 新增枚举
```bash
python scripts/luban_helper.py enum add test.EWeaponType --values "SWORD=1:剑,BOW=2:弓,STAFF=3:法杖" --comment "武器类型" --data-dir DataTables/Datas
```

**参数**：
- `name`: 枚举全名（包含模块，如 `test.EWeaponType`）
- `--values`: 枚举值，格式 `name=value:alias,name2=value2:alias2`
- `--comment`: 枚举注释
- `--flags`: 是否为标志枚举（可选）

### enum delete - 删除枚举
```bash
python scripts/luban_helper.py enum delete test.EWeaponType --data-dir DataTables/Datas
python scripts/luban_helper.py enum delete test.EWeaponType --force --data-dir DataTables/Datas  # 强制删除
```

**参数**：
- `name`: 枚举名称
- `--force`: 强制删除，忽略引用检查

### enum update - 更新枚举属性
```bash
python scripts/luban_helper.py enum update test.EWeaponType --comment "武器类型枚举" --data-dir DataTables/Datas
python scripts/luban_helper.py enum update test.EWeaponType --flags --data-dir DataTables/Datas
```

---

## Bean 操作

### bean list - 列出所有 Bean
```bash
python scripts/luban_helper.py bean list --data-dir DataTables/Datas
```

### bean get - 查询 Bean 详情
```bash
python scripts/luban_helper.py bean get test.TestBean1 --data-dir DataTables/Datas
```

### bean add - 新增 Bean
```bash
python scripts/luban_helper.py bean add test.Weapon --fields "attack:int:攻击力,speed:float:攻击速度" --parent Item --comment "武器" --data-dir DataTables/Datas
```

**参数**：
- `name`: Bean 全名（包含模块）
- `--fields`: 字段定义，格式 `name:type:comment,name2:type2:comment2`
- `--parent`: 父类名称（可选）
- `--comment`: Bean 注释（可选）

### bean delete - 删除 Bean
```bash
python scripts/luban_helper.py bean delete test.Weapon --data-dir DataTables/Datas
python scripts/luban_helper.py bean delete test.Weapon --force --data-dir DataTables/Datas  # 强制删除
```

### bean update - 更新 Bean 属性
```bash
python scripts/luban_helper.py bean update test.ItemList --sep "|" --data-dir DataTables/Datas
python scripts/luban_helper.py bean update test.ItemList --comment "道具列表" --data-dir DataTables/Datas
```

**参数**：
- `--sep`: 分隔符（用于 list 类型元素分隔）
- `--comment`: 注释
- `--alias`: 别名
- `--parent`: 父类名称

**分隔符说明**：

| 分隔符 | 数据格式示例 | 说明 |
|--------|-------------|------|
| 默认 `;` | `1001,10;2003,50;5003,10` | 默认分隔符 |
| `|` | `1001,10|2003,50|5003,10` | 更清晰（推荐） |
| `#` | `1001,10#2003,50#5003,10` | 自定义分隔符 |

---

## 表操作

### table list - 列出所有表
```bash
python scripts/luban_helper.py table list --data-dir DataTables/Datas
```

### table get - 查询表详情
```bash
python scripts/luban_helper.py table get test.TbItem --data-dir DataTables/Datas
```

### table add - 新增配置表
```bash
# 默认创建自动导入格式：#Item-道具表.xlsx
python scripts/luban_helper.py table add test.TbItem --fields "id:int:道具ID,name:string:道具名称" --comment "道具表" --data-dir DataTables/Datas

# 使用传统方式（注册到 __tables__.xlsx）
python scripts/luban_helper.py table add test.TbItem --fields "id:int:道具ID,name:string:道具名称" --input "item.xlsx" --no-auto-import --data-dir DataTables/Datas
```

**参数**：
- `name`: 表全名（包含模块，如 `test.TbItem`）
- `--fields`: 字段定义，格式 `name:type:comment:group`（group 可选）
- `--comment`: 表注释
- `--no-auto-import`: 使用传统方式
- `--vertical`: 使用纵表模式
- `--input`: 数据文件名
- `--sheet`: Sheet名称
- `--index`: 主键定义
- `--groups`: 分组列表

**自动导入格式**：
- 文件名格式：`#表名-注释.xlsx`
- Luban 自动识别，无需在 `__tables__.xlsx` 中声明

### table delete - 删除配置表
```bash
python scripts/luban_helper.py table delete test.TbItem --data-dir DataTables/Datas
python scripts/luban_helper.py table delete test.TbItem --delete-data --data-dir DataTables/Datas  # 同时删除数据文件
```

### table update - 更新表属性
```bash
python scripts/luban_helper.py table update test.TbItem --comment "道具配置表" --data-dir DataTables/Datas
python scripts/luban_helper.py table update test.TbItem --input "item_v2.xlsx" --data-dir DataTables/Datas
```

### 纵表（单例表）
```bash
python scripts/luban_helper.py table add test.TbGlobalConfig --fields "guild_open_level:int:公会开启等级,bag_init_size:int:初始格子数" --comment "全局配置" --vertical --data-dir DataTables/Datas
```

**纵表结构**：
```
| ##column |          |          |         |
| ##var    | ##type   | ##       | ##group |
| guild_open_level | int | 公会开启等级 | c |
| bag_init_size    | int | 初始格子数   | c |
```

---

## 字段操作

### field list - 列出表的所有字段
```bash
python scripts/luban_helper.py field list test.TbItem --data-dir DataTables/Datas
```

### field add - 添加字段
```bash
python scripts/luban_helper.py field add test.TbItem desc --type "string" --comment "道具描述" --data-dir DataTables/Datas
```

**参数**：
- `table`: 表名称
- `name`: 字段名
- `--type`: 字段类型
- `--comment`: 字段注释（支持多行，用 `|` 分隔）
- `--group`: 字段分组（可选，不指定时自动推断）
- `--sheet`: Sheet名称
- `--position`: 插入位置（从0开始，-1表示末尾）

**分组自动推断规则**：
- `c` (客户端): name, desc, icon, image, model, effect, sound, ui 等显示相关
- `s` (服务器): server, logic, damage, hp, mp, exp, level, rate 等逻辑相关
- `cs` (两者): id, 其他无法明确判断的字段

### field update - 修改字段
```bash
python scripts/luban_helper.py field update test.TbItem desc --new-name "description" --comment "详细描述" --data-dir DataTables/Datas
```

**参数**：
- `table`: 表名称
- `name`: 原字段名
- `--new-name`: 新字段名
- `--type`: 新类型
- `--comment`: 新注释
- `--group`: 新分组
- `--sheet`: Sheet名称

### field delete - 删除字段（危险操作）
```bash
python scripts/luban_helper.py field delete test.TbItem desc --data-dir DataTables/Datas
```

**参数**：
- `--force`: 强制删除，跳过确认

**⚠️ 警告**：删除字段会同时删除该字段的所有数据。

### field disable / enable - 禁用/启用字段
```bash
python scripts/luban_helper.py field disable test.TbItem desc --data-dir DataTables/Datas
python scripts/luban_helper.py field enable test.TbItem desc --data-dir DataTables/Datas
```

---

## 数据行操作

### row list - 列出数据行
```bash
python scripts/luban_helper.py row list test.TbItem --data-dir DataTables/Datas
python scripts/luban_helper.py row list test.TbItem --start 10 --limit 20 --data-dir DataTables/Datas
```

### row get - 按字段值查询数据行
```bash
python scripts/luban_helper.py row get TbItem --field id --value 1004 --data-dir DataTables/Datas
python scripts/luban_helper.py row get TbItem --field name --value "屠龙刀" --data-dir DataTables/Datas
```

**返回示例**：
```json
{"id": 1004, "name": "烈焰剑", "type": "Weapon", "quality": 4}
```

### row query - 多条件查询
```bash
python scripts/luban_helper.py row query TbItem --conditions '{"type":"Weapon","quality":5}' --data-dir DataTables/Datas
python scripts/luban_helper.py row query TbItem --conditions '{"type":"Consumable"}' --limit 10 --data-dir DataTables/Datas
```

### row add - 添加数据行
```bash
python scripts/luban_helper.py row add test.TbItem --data '{"id":1001,"name":"宝剑","count":1}' --data-dir DataTables/Datas
```

### row update - 更新数据行
```bash
python scripts/luban_helper.py row update test.TbItem 0 --data '{"name":"神剑"}' --data-dir DataTables/Datas
```

### row delete - 删除数据行
```bash
python scripts/luban_helper.py row delete test.TbItem 0 --data-dir DataTables/Datas
python scripts/luban_helper.py row delete test.TbItem 0 --force --data-dir DataTables/Datas
```

---

## 批量操作

### batch fields - 批量添加字段
```bash
python scripts/luban_helper.py batch fields test.TbItem --data '[{"name":"price","type":"int","comment":"价格"},{"name":"quality","type":"int","comment":"品质"}]' --data-dir DataTables/Datas
```

### batch rows - 批量添加数据行
```bash
python scripts/luban_helper.py batch rows test.TbItem --data '[{"id":1001,"name":"宝剑"},{"id":1002,"name":"铁剑"}]' --data-dir DataTables/Datas
```

---

## 导入导出

### export - 导出表数据为 JSON
```bash
python scripts/luban_helper.py export test.TbItem --data-dir DataTables/Datas
python scripts/luban_helper.py export test.TbItem --output item_backup.json --data-dir DataTables/Datas
```

### import - 从 JSON 导入数据
```bash
python scripts/luban_helper.py import test.TbItem item_backup.json --data-dir DataTables/Datas
```

**参数**：
- `--mode`: 导入模式（`append` 追加，`replace` 替换）

---

## 验证功能

### validate - 验证表数据
```bash
python scripts/luban_helper.py validate test.TbItem --data-dir DataTables/Datas
python scripts/luban_helper.py validate --all --data-dir DataTables/Datas
```

**验证内容**：
- 表结构完整性（##var、##type 行）
- 字段定义检查
- 数据类型验证

---

## 其他命令

### ref - 引用完整性检查
```bash
python scripts/luban_helper.py ref test.RewardItem --data-dir DataTables/Datas
```

### template - 配置模板
```bash
python scripts/luban_helper.py template list --data-dir DataTables/Datas
python scripts/luban_helper.py template create item TbEquip --module test --data-dir DataTables/Datas
```

### rename - 重命名表
```bash
python scripts/luban_helper.py rename test.TbItem test.TbItemNew --data-dir DataTables/Datas
python scripts/luban_helper.py rename test.TbItem test.TbItemNew --migrate-data --data-dir DataTables/Datas
```

### copy - 复制表
```bash
python scripts/luban_helper.py copy test.TbItem test.TbItemCopy --data-dir DataTables/Datas
```

### diff - 差异对比
```bash
python scripts/luban_helper.py diff test.TbItem test.TbItemV2 --data-dir DataTables/Datas
```

### auto - 自动导入表操作
```bash
python scripts/luban_helper.py auto list --data-dir DataTables/Datas
python scripts/luban_helper.py auto create #Item --fields "id:int:ID,name:string:名称" --data-dir DataTables/Datas
```

### alias - 常量别名
```bash
python scripts/luban_helper.py alias list --data-dir DataTables/Datas
python scripts/luban_helper.py alias add ITEM0 1001 --comment "初始道具" --data-dir DataTables/Datas
python scripts/luban_helper.py alias resolve ITEM0 --data-dir DataTables/Datas
python scripts/luban_helper.py alias delete ITEM0 --data-dir DataTables/Datas
```

### tag - 数据标签
```bash
python scripts/luban_helper.py tag list test.TbItem --data-dir DataTables/Datas
python scripts/luban_helper.py tag add test.TbItem 2 dev --data-dir DataTables/Datas
python scripts/luban_helper.py tag remove test.TbItem 2 --data-dir DataTables/Datas
```

### variant - 字段变体
```bash
python scripts/luban_helper.py variant list test.TbItem name --data-dir DataTables/Datas
python scripts/luban_helper.py variant add test.TbItem name zh --data-dir DataTables/Datas
```

### multirow - 多行结构列表
```bash
python scripts/luban_helper.py multirow test.TbActivityReward rewards --data-dir DataTables/Datas
python scripts/luban_helper.py multirow test.TbActivityReward rewards --disable --data-dir DataTables/Datas
```

### type - 类型信息查询
```bash
python scripts/luban_helper.py type int --data-dir DataTables/Datas
python scripts/luban_helper.py type "list<int>" --data-dir DataTables/Datas
python scripts/luban_helper.py type "int?" --data-dir DataTables/Datas
```

### cache - 缓存操作
```bash
python scripts/luban_helper.py cache build --data-dir DataTables/Datas
python scripts/luban_helper.py cache clear --data-dir DataTables/Datas
```

### pref - 用户偏好设置
```bash
python scripts/luban_helper.py pref list --data-dir DataTables/Datas
python scripts/luban_helper.py pref set prefer_auto_import false --data-dir DataTables/Datas
python scripts/luban_helper.py pref get prefer_auto_import --data-dir DataTables/Datas
```

---

## 支持的类型

### 基本类型
| 类型 | 描述 |
|------|------|
| bool | 布尔值 |
| byte | uint8 |
| short | int16 |
| int | int32 |
| long | int64 |
| float | 单精度浮点 |
| double | 双精度浮点 |
| string | 字符串 |
| text | 本地化文本 |
| datetime | 时间戳 |

### 容器类型
| 类型 | 格式 | 示例 |
|------|------|------|
| array | `array<T>` | `array<int>` |
| list | `list<T>` | `list<int>` |
| set | `set<T>` | `set<int>` |
| map | `map<K,V>` | `map<int,string>` |

### 可空类型
在类型后加 `?` 表示可空：`int?`、`string?`、`MyBean?`

---

## Excel 数据填写格式

### 基本类型
| 类型 | 格式示例 |
|------|---------|
| int | `100` |
| string | `道具名称` |
| bool | `true` 或 `false` |
| float | `1.5` |

### 枚举类型
```
Weapon      # 枚举名
1           # 数值
```

### List 类型
```
# list<int>
1;2;3;4;5

# list<RewardItem> 简写格式（推荐）
1001,100;1002,20
```

### Map 类型
```
# map<int,string>
1,金币;2,钻石;3,体力
```
