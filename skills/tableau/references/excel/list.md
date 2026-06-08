# List Types in Excel

This document covers all list patterns in Excel worksheets: horizontal, vertical, incell, and their variants.

---

## Vertical List (Default)

Rows stack vertically. Each row is one list element.

```
| ID           | Name   |
| [Item]uint32 | string |
| Item's ID    | Name   |
| 1            | Apple  |
| 2            | Orange |
| 3            | Banana |
```

Generated proto:
```protobuf
message ItemConf {
  repeated Item item_list = 1 [(tableau.field) = {layout:LAYOUT_VERTICAL}];
  message Item {
    uint32 id   = 1 [(tableau.field) = {name:"ID"}];
    string name = 2 [(tableau.field) = {name:"Name"}];
  }
}
```

---

## Horizontal List

Elements are laid out in columns. Column naming pattern: `<VarName><N><FieldName>` where N starts at 1.

> ⚠️ **Every element must have ALL fields present.** Never omit a field for any element.

```
| Item1ID      | Item1Name    | Item2ID    | Item2Name    | Item3ID    | Item3Name    |
| [Item]uint32 | string       | uint32     | string       | uint32     | string       |
| Item1's ID   | Item1's name | Item2's ID | Item2's name | Item3's ID | Item3's name |
| 1            | Apple        | 2          | Orange       | 3          | Banana       |
```

Generated proto:
```protobuf
message ItemConf {
  repeated Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_HORIZONTAL}];
  message Item {
    uint32 id   = 1 [(tableau.field) = {name:"ID"}];
    string name = 2 [(tableau.field) = {name:"Name"}];
  }
}
```

Generated JSON:
```json
{
    "itemList": [
        { "id": 1, "name": "Apple" },
        { "id": 2, "name": "Orange" },
        { "id": 3, "name": "Banana" }
    ]
}
```

### Horizontal list with Reward struct (ID + Num fields)

```
| Reward1ID      | Reward1Num | Reward2ID | Reward2Num | Reward3ID | Reward3Num |
| [Reward]uint32 | int32      | uint32    | int32      | uint32    | int32      |
```

> ⚠️ **Common mistake**: If a user describes only `Reward1ID` and `Reward2Num`, they are listing *representative* columns. The full column set must include ALL fields for ALL elements: `Reward1ID`, `Reward1Num`, `Reward2ID`, `Reward2Num`, `Reward3ID`, `Reward3Num`.

### Column-skipped horizontal list

Columns can be skipped (e.g., for a name column that doesn't belong to the struct):

```
| D                 | Prop1ID     |              | Prop1Value    | Prop2ID    |              | Prop2Value    |
| map<uint32, Item> | [Prop]int32 |              | int32         | int32      |              | int32         |
| Item's ID         | Prop1's ID  | Prop1's name | Prop1's value | Prop2's ID | Prop2's name | Prop2's value |
```

---

## Incell List

All items in a single cell, comma-separated.

```
| Params  |
| []int32 |
| Params  |
| 1,2,3   |
```

Generated proto:
```protobuf
repeated int32 param_list = 1 [(tableau.field) = {name:"Param" layout:LAYOUT_INCELL}];
```

### Incell enum list

```
| Param                      |
| []enum<.FruitType>         |
| Param list                 |
| 1,FRUIT_TYPE_ORANGE,Banana |
```

### Incell struct list

```
| Item                        |
| []{uint32 ID,int32 Num}Item |
| Items                       |
| 1001:10,1002:20,1003:30     |
```

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_INCELL span:SPAN_INNER_CELL}];
message Item { uint32 id = 1; int32 num = 2; }
```

### Incell predefined struct list

```
| Item      |
| []{.Item} |
| Items     |
| 1:100,2:200,3:300 |
```

---

## Fixed-Size Horizontal List

### Implicit fixed size (auto-detect from header)

```
| Item1ID        | Item1Name    | Item2ID    | Item2Name    | Item3ID    | Item3Name    |
| [Item]uint32\|{fixed:true} | string | uint32 | string | uint32 | string |
```

### Explicit fixed size

```
| Item1ID        | Item1Name    | Item2ID    | Item2Name    | Item3ID    | Item3Name    |
| [Item]uint32\|{size:2} | string | uint32 | string | uint32 | string |
```

With `size:2`, elements after the second are truncated. Empty elements within the fixed size are still generated (as zero-value structs).

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_HORIZONTAL prop:{size:2}}];
```

---

## Predefined Struct List (Horizontal)

```
| Item1ID           | Item1Num    | Item2ID    | Item2Num    | Item3ID    | Item3Num    |
| [.Item]int32      | int32       | int32      | int32       | int32      | int32       |
```

Generated proto:
```protobuf
repeated protoconf.Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_HORIZONTAL}];
```

---

## List with Custom Separator

```
| IDs               |
| []int32\|{sep:"!"} |
| IDs               |
| 1!2!3             |
```

---

## Nesting Summary

| Pattern                         | Typerow example                               | Description                        |
| ------------------------------- | --------------------------------------------- | ---------------------------------- |
| Struct in vertical list         | `[Item]uint32` + `{Prop}int32`                | Struct field inside list element   |
| Incell struct in vertical list  | `[Item]uint32` + `{int32 ID,int64 Value}Prop` | Incell struct field                |
| Struct in horizontal list       | `[Reward]{Item}int32`                         | First field is a cross-cell struct |
| Predefined struct in horiz list | `[Reward]{.Item}int32`                        | First field is predefined struct   |
| Incell struct in horiz list     | `[Reward]{int32 ID,int32 Num}Item`            | First field is incell struct       |
| List in list (horiz)            | `[Reward][Item]uint32`                        | Nested list                        |
| Incell list in horiz list       | `[Task][]int32`                               | Each element has an incell list    |

For detailed nesting examples, see [`nesting.md`](nesting.md).
