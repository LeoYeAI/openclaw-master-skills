# Struct Types in Excel

This document covers all struct-related patterns in Excel worksheets: cross-cell struct, incell struct, predefined struct, and struct definition sheets.

---

## Cross-Cell Struct

**Syntax**: `{StructType}ColumnType` in the first column of the struct.

Each column name is prefixed with the struct variable name (same as struct type name by default), followed by the field name.

```
| PropertyID      | PropertyName    | PropertyDesc           |
| {Property}int32 | string          | string                 |
| Property's ID   | Property's Name | Property's Description |
| 1               | Orange          | A kind of sour fruit.  |
```

Generated proto:
```protobuf
message ItemConf {
  option (tableau.worksheet) = {name:"ItemConf"};
  Property property = 1 [(tableau.field) = {name:"Property"}];
  message Property {
    int32  id   = 1 [(tableau.field) = {name:"ID"}];
    string name = 2 [(tableau.field) = {name:"Name"}];
    string desc = 3 [(tableau.field) = {name:"Desc"}];
  }
}
```

> Cross-cell struct is typically used as the value type of a map or element type of a list.

---

## Incell Struct

All fields packed into a single cell, comma-separated.

**Syntax**: `{FieldType1 FieldName1, FieldType2 FieldName2, ...}StructType`

```
| ID               | Prop                                       |
| map<int32, Item> | {int32 ID,string Name,string Desc}Property |
| Item's ID        | Item's property                            |
| 1                | 1,Orange,A good fruit.                     |
| 2                | 2,Apple                                    |
| 3                | 3                                          |
```

Generated proto:
```protobuf
message ItemConf {
  map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
  message Item {
    uint32 id = 1 [(tableau.field) = {name:"ID"}];
    Property prop = 2 [(tableau.field) = {name:"Prop" span:SPAN_INNER_CELL}];
    message Property {
      int32  id   = 1 [(tableau.field) = {name:"ID"}];
      string name = 2 [(tableau.field) = {name:"Name"}];
      string desc = 3 [(tableau.field) = {name:"Desc"}];
    }
  }
}
```

Generated JSON (partial):
```json
{
    "itemMap": {
        "1": { "id": 1, "prop": { "id": 1, "name": "Orange", "desc": "A good fruit." } },
        "2": { "id": 2, "prop": { "id": 2, "name": "Apple",  "desc": "" } },
        "3": { "id": 3, "prop": { "id": 3, "name": "",       "desc": "" } }
    }
}
```

---

## Predefined Struct (Cross-Cell)

Reference a struct from `common.proto` using the `.` prefix:

```
| ID                | Prop1ID      | Prop1Value    | Prop2ID    | Prop2Value    |
| map<uint32, Item> | [.Prop]int32 | int32         | int32      | int32         |
| Item's ID         | Prop1's ID   | Prop1's value | Prop2's ID | Prop2's value |
| 1                 | 1            | 100           | 2          | 200           |
```

Generated proto:
```protobuf
message ItemConf {
  map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
  message Item {
    uint32 id = 1 [(tableau.field) = {name:"ID"}];
    repeated Prop prop_list = 2 [(tableau.field) = {name:"Prop" layout:LAYOUT_HORIZONTAL}];
  }
}
```

---

## Predefined Incell Struct

Use a predefined struct type in a single cell:

```
| ID                | Prop      |
| map<uint32, Item> | {.Property}|
| Item's ID         | Property  |
| 1                 | 1,Apple,A kind of delicious fruit. |
```

---

## Named Struct Variant

Same struct type but different variable names:

```
| RewardItemID               | CostItemID              |
| {Item(RewardItem)}int32    | {Item(CostItem)}int32   |
```

Both use type `Item` but are distinguished by variable names `RewardItem` and `CostItem`.

---

## Incell Struct with Custom Form (FORM_JSON / FORM_TEXT)

For complex predefined structs, configure the cell data format:

```
| Transform1                                    | Transform2                                    |
| {.Transform}|{form:FORM_TEXT}                 | {.Transform}|{form:FORM_JSON}                 |
| Transform1 (text format)                      | Transform2 (JSON format)                      |
| position:{x:1 y:2 z:3} rotation:{x:4 y:5 z:6}| {"position":{"x":1,"y":2,"z":3}}              |
```

- `FORM_TEXT`: protobuf text format
- `FORM_JSON`: protobuf JSON format

---

## Nested Struct (Struct in Struct)

```
| RewardID      | RewardItemID | RewardItemNum |
| {Reward}int32 | {Item}int32  | int32         |
| Reward's ID   | Item's ID    | Item's num    |
| 1             | 1            | 10            |
```

Generated proto:
```protobuf
message ItemConf {
  Reward reward = 1 [(tableau.field) = {name:"Reward"}];
  message Reward {
    int32 id = 1 [(tableau.field) = {name:"ID"}];
    Item item = 2 [(tableau.field) = {name:"Item"}];
    message Item {
      int32 id  = 1 [(tableau.field) = {name:"ID"}];
      int32 num = 2 [(tableau.field) = {name:"Num"}];
    }
  }
}
```

Generated JSON:
```json
{ "reward": { "id": 1, "item": { "id": 1, "num": 10 } } }
```

---

## MODE_STRUCT_TYPE — Single Struct Definition Sheet

Set `Mode` to `MODE_STRUCT_TYPE` in `@TABLEAU`. Sheet columns: `[Number,] Name, Type [, Note]`.

### Parsing Number from user descriptions

When a user describes struct fields without an explicit `Number` column header, **if the first token of each row is a plain integer, treat it as the `Number` value**.

Examples that all map to `Number | Name | Type`:

```
# explicit "Number N, Name, Type" prefix
Number 1, ID,  uint32
Number 20, Num, int32

# bare integer first
1, ID,  uint32
20, Num, int32
```

### Example

```
@TABLEAU:
| Sheet | Mode             |
| Item  | MODE_STRUCT_TYPE |

Item sheet:
| Name      | Type                                                   |
| ID        | uint32                                                 |
| Num       | int32                                                  |
| FruitType | enum<.FruitType>                                       |
| Feature   | []int32                                                |
| Prop      | map<int32, string>                                     |
| Detail    | {enum<.ItemType> Type, string Name, string Desc}Detail |
```

Generated proto:
```protobuf
// Generated from sheet: Item.
message Item {
  uint32 id = 1 [(tableau.field) = {name:"ID"}];
  int32 num = 2 [(tableau.field) = {name:"Num"}];
  protoconf.FruitType fruit_type = 3 [(tableau.field) = {name:"FruitType"}];
  repeated int32 feature_list = 4 [(tableau.field) = {name:"Feature" layout:LAYOUT_INCELL}];
  map<int32, string> prop_map = 5 [(tableau.field) = {name:"Prop" layout:LAYOUT_INCELL}];
  Detail detail = 6 [(tableau.field) = {name:"Detail" span:SPAN_INNER_CELL}];
  message Detail {
    protoconf.ItemType type = 1 [(tableau.field) = {name:"Type"}];
    string name = 2 [(tableau.field) = {name:"Name"}];
    string desc = 3 [(tableau.field) = {name:"Desc"}];
  }
}
```

### Specify Number column

```
| Number | Name      | Type             |
| 1      | ID        | uint32           |
| 20     | Num       | int32            |
| 30     | FruitType | enum<.FruitType> |
```

Generated proto uses those field numbers directly.

---

## MODE_STRUCT_TYPE_MULTI — Multiple Struct Definition Sheets

Set `Mode` to `MODE_STRUCT_TYPE_MULTI`. Multiple struct types in one sheet, separated by **one or more blank rows**.

### Block structure

Each block:
1. **Type-name row**: first cell = struct type name (PascalCase), second cell = note (optional)
2. **Header row**: `[Number,] Name, Type [, Note]`
3. **Field rows**: field definitions

> ⚠️ The note column in the type-name row must use the **exact note text** from the user's description — e.g., if the user writes `Position (note: 坐标)` or `Position (坐标)`, fill the note cell with `坐标`. Never substitute English descriptions.

### Example

```
@TABLEAU:
| Sheet  | Mode                   |
| Struct | MODE_STRUCT_TYPE_MULTI |

Struct sheet:
| Tree      | Tree note          |
| Name      | Type               |
| ID        | uint32             |
| Num       | int32              |
|           |                    |
| Pet       | Pet note           |
| Name      | Type               |
| Kind      | int32              |
| Tip       | []string           |
|           |                    |
| FruitShop | FruitShop note     |
| Name      | Type               |
| FruitType | enum<.FruitType>   |
| Prop      | map<int32, string> |
```

Generated proto:
```protobuf
message Tree {
  option (tableau.struct) = {name:"StructType" note:"Tree note"};
  uint32 id  = 1 [(tableau.field) = {name:"ID"}];
  int32  num = 2 [(tableau.field) = {name:"Num"}];
}

message Pet {
  option (tableau.struct) = {name:"StructType" note:"Pet note"};
  int32  kind = 1 [(tableau.field) = {name:"Kind"}];
  repeated string tip_list = 2 [(tableau.field) = {name:"Tip" layout:LAYOUT_INCELL}];
}

message FruitShop {
  option (tableau.struct) = {name:"StructType" note:"FruitShop note"};
  protoconf.FruitType fruit_type = 1 [(tableau.field) = {name:"FruitType"}];
  map<int32, string> prop_map = 2 [(tableau.field) = {name:"Prop" layout:LAYOUT_INCELL}];
}
```

> **Note**: `(tableau.struct).name` is always the sheet name (e.g., `"StructType"`), not the individual struct type name.
