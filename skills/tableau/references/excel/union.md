# Union Definition Sheets (Excel)

Union types (tagged discriminated unions) can be defined in Excel sheets. Set `Mode` in `@TABLEAU` to `MODE_UNION_TYPE` or `MODE_UNION_TYPE_MULTI`.

> **Default recommendation**: Always use `MODE_UNION_TYPE_MULTI` unless the sheet contains exactly one union type.

---

## Column Reference

| Column    | Required | Description                                                                                   |
| --------- | -------- | --------------------------------------------------------------------------------------------- |
| `Number`  | No       | Custom field number for the variant (and its enum value). Auto-increments from 1 if omitted.  |
| `Name`    | Yes      | Variant name (used as message type name and enum value name)                                  |
| `Alias`   | No       | Alias for the enum value (`(tableau.evalue).name`)                                            |
| `Type`    | No       | Override the default message type for this variant (see below)                                |
| `Field1`  | No       | First field. Each cell: **line1=field name, line2=type, line3=note** (Alt+Enter for newlines) |
| `Field2+` | No       | Additional fields (same multi-line format)                                                    |

### `Type` column — supported values

| Value                      | Example                         |
| -------------------------- | ------------------------------- |
| Scalar                     | `int32`, `string`               |
| Enum                       | `enum<.FruitType>`              |
| Global predefined struct   | `.Item`                         |
| Custom named incell struct | `{uint32 ID, int64 Damage}Boss` |
| Local predefined struct    | `MyLocalStruct`                 |

### Field columns — supported types

Scalar, enum, well-known types (`datetime`, `duration`), incell struct (`{uint32 ID, int64 Damage}Boss`), incell list (`[]int32`), incell map (`map<int32, int64>`).

---

## MODE_UNION_TYPE — Single Union in One Sheet

Set `Mode` to `MODE_UNION_TYPE`. Columns: `[Number,] Name, Alias, [Type,] Field1, Field2, ...`

### Basic example

```
@TABLEAU:
| Sheet  | Mode            |
| Target | MODE_UNION_TYPE |

Target sheet:
| Name  | Alias      | Field1                  | Field2                      | Field3                           |
| PVP   | AliasPVP   | ID↵uint32↵Note          | Damage↵int64↵Note           | Type↵enum<.FruitType>↵Note       |
| PVE   | AliasPVE   | Hero↵[]uint32↵Note      | Dungeon↵map<int32,int64>    |                                  |
| Skill | AliasSkill | StartTime↵datetime↵Note | Duration↵duration↵Note      |                                  |
```

(↵ = Alt+Enter newline in Excel cell)

Generated proto:
```protobuf
// Generated from sheet: Target.
message Target {
  option (tableau.union) = {name:"Target"};

  Type type = 9999 [(tableau.field) = {name:"Type"}];
  oneof value {
    option (tableau.oneof) = {field:"Field"};
    PVP   pvp   = 1; // Bound to enum value: TYPE_PVP.
    PVE   pve   = 2; // Bound to enum value: TYPE_PVE.
    Skill skill = 3; // Bound to enum value: TYPE_SKILL.
  }
  enum Type {
    TYPE_INVALID = 0;
    TYPE_PVP   = 1 [(tableau.evalue).name = "AliasPVP"];
    TYPE_PVE   = 2 [(tableau.evalue).name = "AliasPVE"];
    TYPE_SKILL = 3 [(tableau.evalue).name = "AliasSkill"];
  }
  message PVP {
    uint32 id = 1 [(tableau.field) = {name:"ID"}];
    int64 damage = 2 [(tableau.field) = {name:"Damage"}];
    protoconf.FruitType type = 3 [(tableau.field) = {name:"Type"}];
  }
  message PVE {
    repeated uint32 hero_list = 1 [(tableau.field) = {name:"Hero" layout:LAYOUT_INCELL}];
    map<int32, int64> dungeon_map = 2 [(tableau.field) = {name:"Dungeon" layout:LAYOUT_INCELL}];
  }
  message Skill {
    google.protobuf.Timestamp start_time = 1 [(tableau.field) = {name:"StartTime"}];
    google.protobuf.Duration  duration   = 2 [(tableau.field) = {name:"Duration"}];
  }
}
```

---

## MODE_UNION_TYPE_MULTI — Multiple Unions in One Sheet (Recommended)

Set `Mode` to `MODE_UNION_TYPE_MULTI`. Multiple union types in one sheet, separated by **one or more blank rows**.

### Block structure

Each block:
1. **Type-name row**: first cell = union type name (PascalCase), second cell = note (optional)
2. **Header row**: `[Number,] Name, Alias, [Type,] Field1, Field2, ...`
3. **Variant rows**: variant name, alias, then Field columns

> ⚠️ The note column in the type-name row must use the **exact note text** from the user's description — e.g., if the user writes `WishTarget (note: 愿望目标)` or `WishTarget (愿望目标)`, fill the note cell with `愿望目标`. Never substitute English descriptions.

### Example

```
@TABLEAU:
| Sheet | Mode                  |
| Union | MODE_UNION_TYPE_MULTI |

Union sheet:
| WishTarget   | WishTarget note |                   |                          |
| Name         | Alias           | Field1            | Field2                   |
| Higher       | WishHigher      | Height↵int32      |                          |
| Richer       | WishRicher      | ID↵uint32         | Bank↵map<int32,string>   |
|              |                 |                   |                          |
| HeroTarget   | HeroTarget note |                   |                          |
| Name         | Alias           | Field1            | Field2            | Field3      |
| StarUp       | HeroStarUp      | ID↵uint32         | Star↵int32        |             |
| LevelUp      | HeroLevelUp     | ID↵[]uint32       | Level↵int32       | Super↵bool  |
|              |                 |                   |                          |
| BattleTarget | BattleTarget note|                  |                          |
| Name         | Alias           | Field1            | Field2                   | Field3                              |
| PVP          | BattlePVP       | BattleID↵int32    | Damage↵int64             |                                     |
| PVE          | BattlePVE       | HeroID↵[]int32    | Dungeon↵map<int32,int64> | Boss↵{uint32 ID, int64 Damage}Boss  |
```

Generated proto:
```protobuf
message WishTarget {
  option (tableau.union) = {name:"UnionType" note:"WishTarget note"};
  Type type = 9999 [(tableau.field) = {name:"Type"}];
  oneof value {
    option (tableau.oneof) = {note:"WishTarget note" field:"Field"};
    Higher higher = 1;
    Richer richer = 2;
  }
  enum Type {
    TYPE_INVALID = 0;
    TYPE_HIGHER = 1 [(tableau.evalue).name = "WishHigher"];
    TYPE_RICHER = 2 [(tableau.evalue).name = "WishRicher"];
  }
  message Higher { int32 height = 1 [(tableau.field) = {name:"Height"}]; }
  message Richer {
    uint32 id = 1 [(tableau.field) = {name:"ID"}];
    map<int32, string> bank_map = 2 [(tableau.field) = {name:"Bank" layout:LAYOUT_INCELL}];
  }
}

message BattleTarget {
  option (tableau.union) = {name:"UnionType" note:"BattleTarget note"};
  // ...
  message PVE {
    repeated int32 hero_id_list = 1 [(tableau.field) = {name:"HeroID" layout:LAYOUT_INCELL}];
    map<int32, int64> dungeon_map = 2 [(tableau.field) = {name:"Dungeon" layout:LAYOUT_INCELL}];
    Boss boss = 3 [(tableau.field) = {name:"Boss" span:SPAN_INNER_CELL}];
    message Boss { uint32 id = 1; int64 damage = 2; }
  }
}
```

> **Note**: `(tableau.union).name` is always the sheet name (e.g., `"UnionType"`), not the individual union type name.

### Chinese alias example (real-world pattern)

User prompt:
```
新增union类型 Target (目标)：
1, Login,      登录,    Days int32 (登录天数)
2, Logout,     登出
3, GameOver,   单局结束, FightType []int32 (战斗类型), Score int32 (游戏分数), Dungeon map[int32]int64 (游戏关卡)

新增union类型 Condition (条件)：
10, PlayerLevel, 玩家等级, Level int32 (等级)
15, Login,       登录,     Days int32 (登录天数), Phase {int32 Phase, int32 SubPhase}Phase (阶段)
17, GameOver,    单局结束,  FightType []int32 (战斗类型), Score int32 (游戏分数), Dungeon map[int32]int64 (游戏关卡)
```

Parsed Excel layout (sheet name: `Union`, mode: `MODE_UNION_TYPE_MULTI`):

```
| Target      | 目标 |          |          |          |          |          |
| Number | Name        | Alias    | Field1                    | Field2                  | Field3                         |
| 1      | Login       | 登录     | Days↵int32↵登录天数        |                         |                                |
| 2      | Logout      | 登出     |                           |                         |                                |
| 3      | GameOver    | 单局结束  | FightType↵[]int32↵战斗类型 | Score↵int32↵游戏分数     | Dungeon↵map<int32,int64>↵游戏关卡 |
|        |             |          |                           |                         |                                |
| Condition | 条件     |          |          |          |          |          |
| Number | Name        | Alias    | Field1                    | Field2                  | Field3                         |
| 10     | PlayerLevel | 玩家等级  | Level↵int32↵等级           |                         |                                |
| 15     | Login       | 登录     | Days↵int32↵登录天数        | Phase↵{int32 Phase, int32 SubPhase}Phase↵阶段 |              |
| 17     | GameOver    | 单局结束  | FightType↵[]int32↵战斗类型 | Score↵int32↵游戏分数     | Dungeon↵map<int32,int64>↵游戏关卡 |
```

Key parsing rules applied:
- `Target (目标)` → type-name row: first cell = `Target`, second cell = `目标`
- `1, Login, 登录, Days int32 (登录天数)` → `Number=1`, `Name=Login`, `Alias=登录`, `Field1=Days↵int32↵登录天数`
- `2, Logout, 登出` → `Number=2`, `Name=Logout`, `Alias=登出`, no fields
- Fields with `(note)` parentheses: use text before first comma as noterow (e.g., `Days int32 (登录天数)` → note=`登录天数`)

---

## Specify Number Column

Add a `Number` column before `Name` to assign custom field numbers (also used as enum value numbers):

```
| Number | Name  | Alias      | Field1                  |
| 1      | PVP   | AliasPVP   | ID↵uint32               |
| 20     | PVE   | AliasPVE   | Hero↵[]uint32           |
| 30     | Skill | AliasSkill | StartTime↵datetime      |
```

### Parsing Number from user descriptions

When a user describes union variants without an explicit `Number` column header, **if the first token of each row is a plain integer, treat it as the `Number` value**.

Examples that all map to `Number | Name | Alias | ...`:

```
# explicit "Number N, Name, Alias" prefix
Number 1,  PVP,   AliasPVP
Number 20, PVE,   AliasPVE

# bare integer first
1,  PVP,   AliasPVP
20, PVE,   AliasPVE
```

### Parsing Alias from user descriptions

The general variant row format in user prompts is:

```
[Number,] Name, Alias, [Fields...]
```

**The third comma-separated token is always the `Alias`** — fill it directly into the Excel `Alias` column. Never leave `Alias` blank when the user has provided it.

Common prompt patterns and their mappings:

```
# Number, Name, Alias(Chinese), Fields
1, Login,    登录,    Days int32 (登录天数)
2, Logout,   登出
3, GameOver, 单局结束, FightType []int32 (战斗类型), Score int32 (游戏分数)

# Number, Name, Alias(English), Fields
1,  PVP,   AliasPVP,   ID uint32, Damage int64
20, PVE,   AliasPVE,   Hero []uint32
```

Both map to:

```
| Number | Name     | Alias    | Field1              | Field2              |
| 1      | Login    | 登录     | Days↵int32↵登录天数  |                     |
| 2      | Logout   | 登出     |                     |                     |
| 3      | GameOver | 单局结束  | FightType↵[]int32↵战斗类型 | Score↵int32↵游戏分数 |
```

> ⚠️ **Never auto-generate alias values** (e.g., `TargetLogin`, `CondPlayerLevel`) when the user has already provided an alias in the prompt. Use the exact text from the prompt — whether Chinese or English.

Generated proto:
```protobuf
oneof value {
  PVP   pvp   = 1;  // Bound to enum value: TYPE_PVP.
  PVE   pve   = 20; // Bound to enum value: TYPE_PVE.
  Skill skill = 30; // Bound to enum value: TYPE_SKILL.
}
enum Type {
  TYPE_INVALID = 0;
  TYPE_PVP   = 1;
  TYPE_PVE   = 20;
  TYPE_SKILL = 30;
}
```

---

## Specify Type Column

Add a `Type` column after `Alias` to override the default message type for each variant:

```
| Name   | Alias      | Type                          | Field1 |
| Fruit  | AliasFruit | enum<.FruitType>              |        |
| Point  | AliasPoint | int32                         |        |
| Boss   | AliasBoss  | {uint32 ID, int64 Damage}Boss |        |
| Empty  | AliasEmpty |                               |        |
```

---

## Using Unions in Data Sheets

Reference a union type in a data sheet using `{.UnionType}enum<.UnionType.Type>`:

```
| ID             | TargetType                  | TargetField1 | TargetField2 |
| map<int32,Task>| {.Target}enum<.Target.Type> | union        | union        |
| Task ID        | Target type                 | Field1       | Field2       |
| 1              | AliasPVP                    | 1            | 10           |
| 2              | AliasPVE                    | 1,Equip      | 1,2,3        |
```

- The `union` keyword in subsequent columns tells tableau these are union payload fields
- The type column uses `{.Target}enum<.Target.Type>` to reference the union type and its discriminator enum
- **Default**: always use the **alias** value (e.g., `AliasPVP`) when filling union type enum cells in data sheets — it is the most readable form

### How many `FieldN` columns to add

> ⚠️ **The number of `union` columns must equal the maximum field count across ALL variants of the referenced union type** — i.e., the variant row with the most fields in the union definition sheet determines N.

**Rule**: scan every variant row in the union type block; count the non-empty `Field` cells in each row; use the largest count as N.

**Example**: given the `Target` union defined as:

```
| Number | Name     | Alias    | Field1                     | Field2               | Field3                          |
| 1      | Login    | 登录     | Days↵int32↵登录天数         |                      |                                 |
| 2      | Logout   | 登出     |                            |                      |                                 |
| 3      | GameOver | 单局结束  | FightType↵[]int32↵战斗类型  | Score↵int32↵游戏分数  | Dungeon↵map<int32,int64>↵游戏关卡 |
```

- `Login` has 1 field, `Logout` has 0, `GameOver` has **3** → N = **3**
- The data sheet must have exactly **3** `union` columns: `TargetField1`, `TargetField2`, `TargetField3`

```
| TargetType                  | TargetField1 | TargetField2 | TargetField3 |
| {.Target}enum<.Target.Type> | union        | union        | union        |
```

Never add fewer columns than the maximum (tableauc will error) and never add extra columns beyond the maximum (they are ignored but misleading).

Generated proto:
```protobuf
message TaskConf {
  option (tableau.worksheet) = {name:"TaskConf"};
  map<int32, Task> task_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
  message Task {
    int32 id = 1 [(tableau.field) = {name:"ID"}];
    protoconf.Target target = 2 [(tableau.field) = {name:"Target"}];
    int32 progress = 3 [(tableau.field) = {name:"Progress"}];
  }
}
```

Generated JSON (partial):
```json
{
    "taskMap": {
        "1": { "id": 1, "target": { "type": "TYPE_PVP", "pvp": { "id": 1, "damage": "10" } } },
        "2": { "id": 2, "target": { "type": "TYPE_PVE", "pve": { "heroList": [1,2,3] } } }
    }
}
```
