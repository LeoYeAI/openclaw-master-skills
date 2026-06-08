# Map Types in Excel

This document covers all map patterns in Excel worksheets: horizontal, vertical, incell, and their variants.

---

## Vertical Map (Default)

Key column first, then value fields. Each row is one map entry.

```
| ID                | Name        | Desc                          |
| map<uint32, Item> | string      | string                        |
| Item's ID         | Item's name | Item's desc                   |
| 1                 | Apple       | A kind of delicious fruit.    |
| 2                 | Orange      | A kind of sour fruit.         |
| 3                 | Banana      | A kind of calorie-rich fruit. |
```

Generated proto:
```protobuf
message ItemConf {
  map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
  message Item {
    uint32 id   = 1 [(tableau.field) = {name:"ID"}];
    string name = 2 [(tableau.field) = {name:"Name"}];
    string desc = 3 [(tableau.field) = {name:"Desc"}];
  }
}
```

Generated JSON:
```json
{
    "itemMap": {
        "1": { "id": 1, "name": "Apple",  "desc": "A kind of delicious fruit." },
        "2": { "id": 2, "name": "Orange", "desc": "A kind of sour fruit." },
        "3": { "id": 3, "name": "Banana", "desc": "A kind of calorie-rich fruit." }
    }
}
```

### Vertical predefined-struct map

```
| ID                | Num        |
| map<int32, .Item> | int32      |
| Item's ID         | Item's num |
| 1                 | 100        |
| 2                 | 200        |
```

Generated proto:
```protobuf
map<int32, protoconf.Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
```

---

## Horizontal Map

Elements are laid out in columns. Column naming pattern: `<VarName><N><FieldName>` where N starts at 1.

> ⚠️ **Every element must have ALL fields present.** Never omit a field for any element.

```
| Item1ID           | Item1Name    | Item2ID    | Item2Name    | Item3ID    | Item3Name    |
| map<uint32, Item> | string       | uint32     | string       | uint32     | string       |
| Item1's ID        | Item1's name | Item2's ID | Item2's name | Item3's ID | Item3's name |
| 1                 | Apple        | 2          | Orange       | 3          | Banana       |
```

Generated proto:
```protobuf
map<uint32, Item> item_map = 1 [(tableau.field) = {name:"Item" key:"ID" layout:LAYOUT_HORIZONTAL}];
message Item {
  uint32 id   = 1 [(tableau.field) = {name:"ID"}];
  string name = 2 [(tableau.field) = {name:"Name"}];
}
```

### Horizontal predefined-struct map

```
| Item1ID           | Item1Num    | Item2ID    | Item2Num    | Item3ID    | Item3Num    |
| map<int32, .Item> | int32       | int32      | int32       | int32      | int32       |
```

Generated proto:
```protobuf
map<int32, protoconf.Item> item_map = 1 [(tableau.field) = {name:"Item" key:"ID" layout:LAYOUT_HORIZONTAL}];
```

### Column-skipped horizontal map

```
| D                 | Prop1ID          |              | Prop1Value    | Prop2ID    |              | Prop2Value    |
| map<uint32, Item> | map<int32, Prop> |              | int32         | int32      |              | int32         |
```

---

## Incell Map

All entries in a single cell. Format: `key1:value1,key2:value2,...`

### Incell scalar map

```
| Item                               |
| map<uint32, string>                |
| Item key-value pairs               |
| 1:Apple,2:Orange,3:Banana,4,:Peach |
```

Generated proto:
```protobuf
map<uint32, string> item_map = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_INCELL}];
```

Generated JSON:
```json
{
    "itemMap": {
        "0": "Peach",
        "1": "Apple",
        "2": "Orange",
        "3": "Banana",
        "4": ""
    }
}
```

> **Note**: Entries without a key get key `0`. E.g., `1:Apple,2:Orange,,Peach` → `Peach` gets key `0`.

### Incell enum map

Both key and value can be enum types:

```
| Fruit                        | Flavor                         | Item                                    |
| map<enum<.FruitType>, int64> | map<int64, enum<.FruitFlavor>> | map<enum<.FruitType>, enum<.FruitFlavor>>|
| Fruits                       | Flavors                        | Items                                   |
| Apple:1,Orange:2             | 1:Fragrant,2:Sweet             | Apple:Fragrant,Orange:Sour              |
```

### Incell map with custom separators

```
| Props                              |
| map<string,string>\|{sep:";" subsep:"="} |
| Props                              |
| dog=cute;bird=noisy                |
```

---

## Enum-Keyed Map

Protobuf doesn't allow enum map keys directly. Tableau handles this by:
- Using `int32` as the actual proto map key type
- Reserving the enum type in the map value struct as the first field

```
| Type                         | Price  |
| map<enum<.FruitType>, Item>  | int32  |
| Fruit type                   | Price  |
| Apple                        | 100    |
| Orange                       | 200    |
| Banana                       | 300    |
```

Generated proto:
```protobuf
map<int32, Item> item_map = 1 [(tableau.field) = {key:"Type" layout:LAYOUT_VERTICAL}];
message Item {
  protoconf.FruitType type  = 1 [(tableau.field) = {name:"Type"}];
  int32               price = 2 [(tableau.field) = {name:"Price"}];
}
```

---

## Empty Key Map

If a map key cell is empty, it is treated as the default value of the key type (e.g., `0` for `uint32`).

---

## Fixed-Size Horizontal Map

### Implicit fixed size

```
| Item1ID           | Item1Name | Item2ID | Item2Name | Item3ID | Item3Name |
| map<uint32, Item>\|{fixed:true} | string | uint32 | string | uint32 | string |
```

### Explicit fixed size

```
| Item1ID           | Item1Name | Item2ID | Item2Name | Item3ID | Item3Name |
| map<uint32, Item>\|{size:2} | string | uint32 | string | uint32 | string |
```

With `size:2`, map items after the second are truncated.

Generated proto:
```protobuf
map<uint32, Item> item_map = 1 [(tableau.field) = {name:"Item" key:"ID" layout:LAYOUT_HORIZONTAL prop:{size:2}}];
```

---

## Nested Vertical Map (Map-in-Map)

> ⚠️ **Tableau does NOT support nested map syntax in a single typerow cell.** Never write `map<uint32, map<int32, Item>>` in one cell — this is invalid. Each map level must be declared on its own key column.

Two-level vertical map with a horizontal list inside:

```
| ID                  | Name   | Phase            | Item1ID      | Item1Num |
| map<uint32, Season> | string | map<int32, Phase>| [Item]uint32 | int32    |
| Season ID           | Name   | Phase            | Item1 ID     | Item1 num|
| 1                   | Spring | 1                | 1001         | 10       |
| 1                   |        | 2                | 2001         | 3        |
| 2                   | Summer | 1                | 3001         | 20       |
| 2                   |        | 2                | 3002         | 15       |
```

**Key fill rules:**

| Key column          | Contains nested vertical map/list? | Auto-deduced unique | Fill rule                                                                                              |
| ------------------- | ---------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------ |
| `ID` (outer map)    | ✅ Yes                              | ❌ Not unique        | **Repeat** the same ID across multiple rows; non-key fields (e.g. `Name`) only filled on the first row |
| `Phase` (inner map) | ❌ No                               | ✅ Unique            | Each `(ID, Phase)` combination appears **exactly once**                                                |

Generated proto:
```protobuf
map<uint32, Season> season_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Season {
  string name = 1;
  map<int32, Phase> phase_map = 2 [(tableau.field) = {key:"Phase" layout:LAYOUT_VERTICAL}];
  message Phase {
    repeated Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_HORIZONTAL}];
    message Item { uint32 id = 1; int32 num = 2; }
  }
}
```

---

## Nesting Summary

| Pattern                         | Typerow example                                     | Description                      |
| ------------------------------- | --------------------------------------------------- | -------------------------------- |
| Struct in vertical map          | `map<uint32,Item>` + `{Prop}int32`                  | Struct field inside map value    |
| Incell struct in vertical map   | `map<uint32,Item>` + `{int32 ID,int32 Num}Item`     | Incell struct field              |
| Horizontal map in vertical map  | `map<uint32,Item>` + `map<int32,Prop>` (horizontal) | Nested horizontal map            |
| Vertical map in vertical map    | `map<uint32,Item>` + `map<int32,Prop>` (vertical)   | Nested vertical map              |
| Incell map in vertical map      | `map<uint32,Item>` + `map<int32,string>` (incell)   | Incell map field                 |
| Horizontal list in vertical map | `map<uint32,Item>` + `[Prop]int32`                  | Horizontal list inside map value |
| Vertical list in vertical map   | `map<uint32,Item>` + `[Prop]int32` (vertical)       | Vertical list inside map value   |
| Incell list in vertical map     | `map<uint32,Item>` + `[]int32`                      | Incell list field                |

For detailed nesting examples, see [`nesting.md`](nesting.md).
