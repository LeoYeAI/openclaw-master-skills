# Enum Definition Sheets (Excel)

Enum types can be defined directly in Excel sheets. Set the `Mode` column in `@TABLEAU` metasheet to `MODE_ENUM_TYPE` or `MODE_ENUM_TYPE_MULTI`.

---

## Using a Predefined Enum in a Data Sheet

Reference a predefined enum (from `common.proto`) with the `.` prefix in the typerow:

```
| ID                | Type              |
| map<uint32, Item> | enum<.FruitType>  |
| Item's ID         | Fruit's type      |
| 1                 | 1                 |
| 2                 | Orange            |
| 3                 | FRUIT_TYPE_BANANA |
```

Three accepted cell value forms:
1. **Numeric**: `1`
2. **Full name**: `FRUIT_TYPE_BANANA`
3. **Alias**: `Orange`

> **Default**: always use the **alias** value (e.g., `Orange`) when filling enum cells in data sheets — it is the most readable form.

---

## Column Order

**Column order**: `[Number,] Name, Alias`

> ⚠️ **Column order is critical**: `Number` (optional) is col 1 when present, `Name` follows, `Alias` is last. Never put `Name` before `Number`.

| Column   | Required | Description                                                                                                                                                                     |
| -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Number` | No       | Integer value; auto-increments from 1 if omitted. **When present, it is always the first column.**                                                                              |
| `Name`   | Yes      | Proto enum value name, e.g. `FRUIT_TYPE_APPLE` (UPPER_SNAKE_CASE)                                                                                                               |
| `Alias`  | No       | Human-readable short name → stored as `(tableau.evalue).name` in proto. Can be English (`Apple`) or Chinese (`苹果`). Use the **exact alias text** from the user's description. |

### Parsing Number from user descriptions

When a user describes enum values without an explicit `Number` column header, **if the first token of each row is a plain integer, treat it as the `Number` value**.

Examples that all map to `Number | Name | Alias`:

```
# explicit "Number N, Name, Alias" prefix
Number 1, ITEM_TYPE_WEAPON, 武器
Number 2, ITEM_TYPE_ARMOR,  防具

# bare integer first
1, ITEM_TYPE_WEAPON, 武器
2, ITEM_TYPE_ARMOR,  防具

# table form with Number header
| Number | Name            | Alias |
| 1      | ITEM_TYPE_WEAPON | 武器  |
```

All three forms produce the same Excel sheet with `Number` as col 1.

---

## MODE_ENUM_TYPE — Single Enum in One Sheet

Set `Mode` to `MODE_ENUM_TYPE` in `@TABLEAU`. Sheet columns: `[Number,] Name, Alias`.

### Basic example

```
@TABLEAU:
| Sheet    | Mode           |
| ItemType | MODE_ENUM_TYPE |

ItemType sheet:
| Name            | Alias |
| ITEM_TYPE_FRUIT | Fruit |
| ITEM_TYPE_EQUIP | Equip |
| ITEM_TYPE_BOX   | Box   |
```

Generated proto:
```protobuf
// Generated from sheet: ItemType.
enum ItemType {
  ITEM_TYPE_INVALID = 0;
  ITEM_TYPE_FRUIT = 1 [(tableau.evalue).name = "Fruit"];
  ITEM_TYPE_EQUIP = 2 [(tableau.evalue).name = "Equip"];
  ITEM_TYPE_BOX   = 3 [(tableau.evalue).name = "Box"];
}
```

- `*_INVALID = 0` is **auto-generated** if not explicitly defined
- `Number` column is optional — auto-increments from 1 if omitted

### Specify Number column

Add a `Number` column to assign custom enum value numbers:

```
| Number | Name              | Alias   |
| 0      | ITEM_TYPE_UNKNOWN | Unknown |
| 10     | ITEM_TYPE_FRUIT   | Fruit   |
| 20     | ITEM_TYPE_EQUIP   | Equip   |
| 30     | ITEM_TYPE_BOX     | Box     |
```

Generated proto:
```protobuf
enum ItemType {
  ITEM_TYPE_UNKNOWN = 0 [(tableau.evalue).name = "Unknown"];
  ITEM_TYPE_FRUIT   = 10 [(tableau.evalue).name = "Fruit"];
  ITEM_TYPE_EQUIP   = 20 [(tableau.evalue).name = "Equip"];
  ITEM_TYPE_BOX     = 30 [(tableau.evalue).name = "Box"];
}
```

> **Note**: If you explicitly define value `0`, it overrides the auto-generated `*_INVALID`. Negative numbers are supported (e.g., `-1` for sentinel values like `JOB_TYPE_ALL`).

---

## MODE_ENUM_TYPE_MULTI — Multiple Enums in One Sheet

Set `Mode` to `MODE_ENUM_TYPE_MULTI`. Multiple enum types are defined in **blocks** separated by one or more blank rows.

### Block structure

Each block:
1. **Type-name row**: first cell = enum type name (PascalCase), second cell = note (optional)
2. **Header row**: `[Number,] Name, Alias`
3. **Value rows**: enum values

> ⚠️ The note column in the type-name row must use the **exact note text** from the user's description — e.g., if the user writes `ItemType (note: 道具类型)` or `ItemType (道具类型)`, fill the note cell with `道具类型`. Never substitute English descriptions.

### Example

```
@TABLEAU:
| Sheet | Mode                 |
| Enum  | MODE_ENUM_TYPE_MULTI |

Enum sheet:
| CatType  | CatType note       |            |
| Number   | Name               | Alias      |
| 1        | CAT_TYPE_RAGDOLL   | Ragdoll    |
| 2        | CAT_TYPE_PERSIAN   | Persian    |
| 3        | CAT_TYPE_SPHYNX    | Sphynx     |
|          |                    |            |
| DogType  | DogType note       |            |
| Number   | Name               | Alias      |
| 1        | DOG_TYPE_POODLE    | Poodle     |
| 2        | DOG_TYPE_BULLDOG   | Bulldog    |
| 3        | DOG_TYPE_DACHSHUND | Dachshund  |
|          |                    |            |
| BirdType | BirdType note      |            |
| Number   | Name               | Alias      |
| 1        | CANARY             | Canary     |
| 2        | WOODPECKER         | Woodpecker |
| 3        | OWL                | Owl        |
```

Generated proto:
```protobuf
// CatType note
enum CatType {
  option (tableau.etype) = {name:"EnumType" note:"CatType note"};
  CAT_TYPE_INVALID  = 0;
  CAT_TYPE_RAGDOLL  = 1 [(tableau.evalue).name = "Ragdoll"];
  CAT_TYPE_PERSIAN  = 2 [(tableau.evalue).name = "Persian"];
  CAT_TYPE_SPHYNX   = 3 [(tableau.evalue).name = "Sphynx"];
}

// DogType note
enum DogType {
  option (tableau.etype) = {name:"EnumType" note:"DogType note"};
  DOG_TYPE_INVALID   = 0;
  DOG_TYPE_POODLE    = 1 [(tableau.evalue).name = "Poodle"];
  DOG_TYPE_BULLDOG   = 2 [(tableau.evalue).name = "Bulldog"];
  DOG_TYPE_DACHSHUND = 3 [(tableau.evalue).name = "Dachshund"];
}

// BirdType note
enum BirdType {
  option (tableau.etype) = {name:"EnumType" note:"BirdType note"};
  BIRD_TYPE_INVALID    = 0;
  BIRD_TYPE_CANARY     = 1 [(tableau.evalue).name = "Canary"];
  BIRD_TYPE_WOODPECKER = 2 [(tableau.evalue).name = "Woodpecker"];
  BIRD_TYPE_OWL        = 3 [(tableau.evalue).name = "Owl"];
}
```

> **Note**: `(tableau.etype).name` is always the sheet name (e.g., `"EnumType"`), not the individual enum type name.

---

## Define and Use Enum in the Same Workbook

Enum types defined in one sheet can be referenced in data sheets of the same workbook using the `.` prefix:

```
@TABLEAU:
| Sheet    | Mode           |
| ItemType | MODE_ENUM_TYPE |
| ItemConf |                |

ItemType sheet:
| Number | Name            | Alias |
| 1      | ITEM_TYPE_FRUIT | Fruit |
| 2      | ITEM_TYPE_EQUIP | Equip |
| 3      | ITEM_TYPE_BOX   | Box   |

ItemConf sheet:
| ID               | Type            | Name   | Price  |
| map<int32, Item> | enum<.ItemType> | string | int32  |
| Item's ID        | Item's type     | Name   | Price  |
| 1                | Fruit           | Apple  | 40     |
| 2                | Fruit           | Orange | 20     |
| 3                | Equip           | Sword  | 10     |
```

Generated proto:
```protobuf
// Generated from sheet: ItemType.
enum ItemType {
  ITEM_TYPE_INVALID = 0;
  ITEM_TYPE_FRUIT = 1 [(tableau.evalue).name = "Fruit"];
  ITEM_TYPE_EQUIP = 2 [(tableau.evalue).name = "Equip"];
  ITEM_TYPE_BOX   = 3 [(tableau.evalue).name = "Box"];
}

message ItemConf {
  option (tableau.worksheet) = {name:"ItemConf"};
  map<int32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
  message Item {
    int32 id = 1 [(tableau.field) = {name:"ID"}];
    protoconf.ItemType type = 2 [(tableau.field) = {name:"Type"}];
    string name = 3 [(tableau.field) = {name:"Name"}];
    int32 price = 4 [(tableau.field) = {name:"Price"}];
  }
}
```

Generated JSON:
```json
{
    "itemMap": {
        "1": { "id": 1, "type": "ITEM_TYPE_FRUIT", "name": "Apple",  "price": 40 },
        "2": { "id": 2, "type": "ITEM_TYPE_FRUIT", "name": "Orange", "price": 20 },
        "3": { "id": 3, "type": "ITEM_TYPE_EQUIP", "name": "Sword",  "price": 10 }
    }
}
```

---

## Excel `write_enum_block` Helper (openpyxl)

When writing enum blocks in Python (openpyxl), the correct column order is:

```python
# type-name row: col1=type_name, col2=type_note
# header row: ['Number', 'Name', 'Alias']   ← MUST be this order
# data rows: (number, proto_name, alias)     ← e.g. (1, 'ITEM_TYPE_WEAPON', '武器')
write_enum_block(ws, r, 'ItemType', '道具类型', [
    (1, 'ITEM_TYPE_WEAPON', '武器'),
    (2, 'ITEM_TYPE_ARMOR',  '防具'),
    (3, 'ITEM_TYPE_POTION', '药水'),
])
```

> ⚠️ The alias column is always **last** (`Number`, `Name`, `Alias`). Never pass alias as the second argument to data rows.
