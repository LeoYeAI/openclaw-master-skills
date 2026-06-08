# Complex Nesting in Excel

This document covers all complex nesting patterns: struct/list/map combinations in Excel worksheets.

---

## Struct in Struct

### Cross-cell struct in struct

```
| RewardID      | RewardItemID | RewardItemNum |
| {Reward}int32 | {Item}int32  | int32         |
| Reward's ID   | Item's ID    | Item's num    |
| 1             | 1            | 10            |
```

Generated proto:
```protobuf
Reward reward = 1 [(tableau.field) = {name:"Reward"}];
message Reward {
  int32 id = 1 [(tableau.field) = {name:"ID"}];
  Item item = 2 [(tableau.field) = {name:"Item"}];
  message Item { int32 id = 1; int32 num = 2; }
}
```

Generated JSON: `{ "reward": { "id": 1, "item": { "id": 1, "num": 10 } } }`

### Predefined struct in struct

```
| RewardID      | RewardItemID | RewardItemNum |
| {Reward}int32 | {.Item}int32 | int32         |
```

Generated proto:
```protobuf
message Reward {
  int32 id = 1;
  protoconf.Item item = 2 [(tableau.field) = {name:"Item"}];
}
```

### Incell struct in struct

```
| RewardID      | RewardItem                |
| {Reward}int32 | {int32 ID, int32 Num}Item |
| Reward's ID   | Reward's item             |
| 1             | 1,100                     |
```

Generated proto:
```protobuf
message Reward {
  int32 id = 1;
  Item item = 2 [(tableau.field) = {name:"Item" span:SPAN_INNER_CELL}];
  message Item { int32 id = 1; int32 num = 2; }
}
```

---

## Struct in List

### Struct in vertical list

```
| ID           | Name        | PropID      | PropValue    |
| [Item]uint32 | string      | {Prop}int32 | int64        |
| Item's ID    | Item's name | Prop's ID   | Prop's value |
| 1            | Apple       | 1           | 10           |
| 2            | Orange      | 2           | 20           |
| 3            | Banana      |             |              |
```

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  Prop prop   = 3 [(tableau.field) = {name:"Prop"}];
  message Prop { int32 id = 1; int64 value = 2; }
}
```

### Struct as first field in horizontal list

```
| Reward1ItemID       | Reward1ItemNum | Reward1Name   | Reward2ItemID | Reward2ItemNum | Reward2Name   |
| [Reward]{Item}int32 | int32          | string        | int32         | int32          | string        |
| Item1's ID          | Item1's num    | Reward's name | Item2's ID    | Item2's num    | Reward's name |
| 1                   | 10             | Lotto         | 10            | 100            | Super Lotto   |
```

Generated proto:
```protobuf
repeated Reward reward_list = 1 [(tableau.field) = {name:"Reward" layout:LAYOUT_HORIZONTAL}];
message Reward {
  Item item = 1 [(tableau.field) = {name:"Item"}];
  message Item { int32 id = 1; int32 num = 2; }
  string name = 2;
}
```

### Predefined struct as first field in horizontal list

```
| Reward1ItemID        | Reward1ItemNum | Reward1Name   | Reward2ItemID | Reward2ItemNum | Reward2Name   |
| [Reward]{.Item}int32 | int32          | string        | int32         | int32          | string        |
```

Generated proto:
```protobuf
message Reward {
  protoconf.Item item = 1 [(tableau.field) = {name:"Item"}];
  string name = 2;
}
```

### Incell struct as first field in horizontal list

```
| Reward1Item                       | Reward1Name   | Reward2Item    | Reward2Name   |
| [Reward]{int32 ID, int32 Num}Item | string        | Item           | string        |
| Reward1's item                    | Reward's name | Reward2's item | Reward's name |
| 1,10                              | Lotto         | 2,20           | Super Lotto   |
```

---

## Struct in Map

### Struct in vertical map

```
| ID                 | ItemID      | ItemNum    |
| map<int32, Reward> | {Item}int32 | int32      |
| Reward's ID        | Item's ID   | Item's Num |
| 1                  | 1           | 10         |
| 2                  | 2           | 20         |
```

Generated proto:
```protobuf
map<int32, Reward> reward_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Reward {
  int32 id = 1;
  Item item = 2 [(tableau.field) = {name:"Item"}];
  message Item { int32 id = 1; int32 num = 2; }
}
```

### Incell struct in vertical map

```
| ID                 | Item                      |
| map<int32, Reward> | {int32 ID, int32 Num}Item |
| Reward's ID        | Item's info               |
| 1                  | 1,100                     |
| 2                  | 2,200                     |
```

---

## List in List

### Horizontal list in horizontal list

```
| Reward1Item1ID      | Reward1Item1Num | Reward1Item2ID | Reward1Item2Num | Reward1Name   | Reward2Item1ID | Reward2Item1Num | Reward2Name   |
| [Reward][Item]int32 | int32           | int32          | int32           | string        | int32          | int32           | string        |
| Item1's ID          | Item1's num     | Item2's ID     | Item2's num     | Reward's name | Item1's ID     | Item1's num     | Reward's name |
| 1                   | 10              | 2              | 20              | Lotto         | 10             | 100             | Super Lotto   |
```

Generated proto:
```protobuf
repeated Reward reward_list = 1 [(tableau.field) = {name:"Reward" layout:LAYOUT_HORIZONTAL}];
message Reward {
  repeated Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_HORIZONTAL}];
  message Item { int32 id = 1; int32 num = 2; }
  string name = 2;
}
```

Generated JSON:
```json
{
    "rewardList": [
        { "itemList": [{"id":1,"num":10},{"id":2,"num":20}], "name": "Lotto" },
        { "itemList": [{"id":10,"num":100}], "name": "Super Lotto" }
    ]
}
```

### Incell list in horizontal list

```
| Task1Param    | Task2Param | Task3Param |
| [Task][]int32 | []int32    | []int32    |
| Task1         | Task2      | Task3      |
| 1,2           | 3,4        | 5,6,7      |
```

Generated proto:
```protobuf
repeated Task task_list = 1 [(tableau.field) = {name:"Task" layout:LAYOUT_HORIZONTAL}];
message Task {
  repeated int32 param_list = 1 [(tableau.field) = {name:"Param" layout:LAYOUT_INCELL}];
}
```

---

## Map in List

### Horizontal map in vertical list

```
| ID           | Name        | Prop1ID          | Prop1Value    | Prop2ID    | Prop2Value    |
| [Item]uint32 | string      | map<int32, Prop> | int64         | int32      | int64         |
| Item's ID    | Item's name | Prop1's ID       | Prop1's value | Prop2's ID | Prop2's value |
| 1            | Apple       | 1                | 10            | 2          | 20            |
| 2            | Orange      | 3                | 30            |            |               |
```

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  map<int32, Prop> prop_map = 3 [(tableau.field) = {name:"Prop" key:"ID" layout:LAYOUT_HORIZONTAL}];
  message Prop { int32 id = 1; int64 value = 2; }
}
```

### Vertical map in vertical keyed list

```
| ID               | Name        | PropID           | PropValue    |
| [Item]<uint32>   | string      | map<int32, Prop> | int64        |
| Item's ID        | Item's name | Prop's ID        | Prop's value |
| 1                | Apple       | 1                | 10           |
| 2                | Orange      | 1                | 20           |
| 2                | Banana      | 2                | 30           |
```

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  map<int32, Prop> prop_map = 3 [(tableau.field) = {key:"PropID" layout:LAYOUT_VERTICAL}];
  message Prop { int32 prop_id = 1; int64 prop_value = 2; }
}
```

### Incell map in vertical list

```
| ID           | Props                      |
| [Item]uint32 | map<int32, string>         |
| Item's ID    | Item's props               |
| 1            | 1:sour,2:sweet,3:delicious |
| 2            | 1:sour,2:sweet             |
| 3            | 1:sour                     |
```

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id = 1;
  map<int32, string> props_map = 2 [(tableau.field) = {name:"Props" layout:LAYOUT_INCELL}];
}
```

---

## List in Map

### Horizontal list in vertical map

```
| ID                | Name        | Prop1ID     | Prop1Value    | Prop2ID    | Prop2Value    |
| map<uint32, Item> | string      | [Prop]int32 | int64         | int32      | int64         |
| Item's ID         | Item's name | Prop1's ID  | Prop1's value | Prop2's ID | Prop2's value |
| 1                 | Apple       | 1           | 10            | 2          | 20            |
| 2                 | Orange      | 3           | 30            |            |               |
```

Generated proto:
```protobuf
map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  repeated Prop prop_list = 3 [(tableau.field) = {name:"Prop" layout:LAYOUT_HORIZONTAL}];
  message Prop { int32 id = 1; int64 value = 2; }
}
```

### Vertical list in vertical map

```
| ID                | Name        | PropID      | PropValue    |
| map<uint32, Item> | string      | [Prop]int32 | int64        |
| Item's ID         | Item's name | Prop's ID   | Prop's value |
| 1                 | Apple       | 1           | 10           |
| 2                 | Orange      | 1           | 20           |
| 2                 | Banana      | 2           | 30           |
```

Generated proto:
```protobuf
map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  repeated Prop prop_list = 3 [(tableau.field) = {layout:LAYOUT_VERTICAL}];
  message Prop { int32 prop_id = 1; int64 prop_value = 2; }
}
```

### Incell list in vertical map

```
| ID                | Prop         |
| map<uint32, Item> | []int32      |
| Item's ID         | Item's props |
| 1                 | 10,20,30     |
| 2                 | 10,20        |
```

### Incell struct list in vertical map

```
| ID                  | Item                        |
| map<uint32, Reward> | []{uint32 ID,int32 Num}Item |
| Reward's ID         | Reward's items              |
| 1                   | 1001:10,1002:20,1003:30     |
| 2                   | 2001:10,2002:20             |
```

Generated proto:
```protobuf
map<uint32, Reward> reward_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Reward {
  uint32 id = 1;
  repeated Item item_list = 2 [(tableau.field) = {name:"Item" layout:LAYOUT_INCELL span:SPAN_INNER_CELL}];
  message Item { uint32 id = 1; int32 num = 2; }
}
```

---

## Map in Map

### Horizontal map in vertical map

```
| ID                | Name        | Prop1ID          | Prop1Value    | Prop2ID    | Prop2Value    |
| map<uint32, Item> | string      | map<int32, Prop> | int64         | int32      | int64         |
| Item's ID         | Item's name | Prop1's ID       | Prop1's value | Prop2's ID | Prop2's value |
| 1                 | Apple       | 1                | 10            | 2          | 20            |
| 2                 | Orange      | 3                | 30            |            |               |
```

Generated proto:
```protobuf
map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  map<int32, Prop> prop_map = 3 [(tableau.field) = {name:"Prop" key:"ID" layout:LAYOUT_HORIZONTAL}];
  message Prop { int32 id = 1; int64 value = 2; }
}
```

### Vertical map in vertical map

```
| ID                | Name        | PropID           | PropValue    |
| map<uint32, Item> | string      | map<int32, Prop> | int64        |
| Item's ID         | Item's name | Prop's ID        | Prop's value |
| 1                 | Apple       | 1                | 10           |
| 2                 | Orange      | 1                | 20           |
| 2                 | Orange      | 2                | 30           |
```

Generated proto:
```protobuf
map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id   = 1;
  string name = 2;
  map<int32, Prop> prop_map = 3 [(tableau.field) = {key:"PropID" layout:LAYOUT_VERTICAL}];
  message Prop { int32 prop_id = 1; int64 prop_value = 2; }
}
```

### Incell map in vertical map

```
| ID                | Props                      |
| map<uint32, Item> | map<int32, string>         |
| Item's ID         | Item's props               |
| 1                 | 1:sour,2:sweet,3:delicious |
| 2                 | 1:sour,2:sweet             |
```

---

## Infinite Nesting (Nested Column Names)

When `Nested: true` is set in `@TABLEAU`, column names use dot-separated prefixes to encode hierarchy:

```
@TABLEAU:
| Sheet      | Nested |
| LoaderConf | true   |

LoaderConf sheet:
| ServerType                     | ServerConfType          | ServerConfConditionType | ServerConfConditionValue |
| map<enum<.ServerType>, Server> | [Conf]<enum<.ConfType>> | [Condition]<int32>      | int32                    |
| Server name                    | Sheet name              | Condition type          | Condition value          |
| SERVER_TYPE_GAME               | CONF_TYPE_CLOUD         | 0                       | 113                      |
| SERVER_TYPE_ACTIVITY           | CONF_TYPE_CLOUD         |                         |                          |
|                                | CONF_TYPE_LOCAL         | 9                       | 34                       |
```

Generated proto:
```protobuf
message LoaderConf {
  option (tableau.worksheet) = {name:"LoaderConf" nested:true};
  map<int32, Server> server_map = 1 [(tableau.field) = {name:"Server" key:"Type" layout:LAYOUT_VERTICAL}];
  message Server {
    ServerType type = 1;
    repeated Conf conf_list = 2 [(tableau.field) = {name:"Conf" key:"Type" layout:LAYOUT_VERTICAL}];
    message Conf {
      ConfType type = 1;
      repeated Condition condition_list = 2 [(tableau.field) = {name:"Condition" key:"Type" layout:LAYOUT_VERTICAL}];
      message Condition { int32 type = 1; int32 value = 2; }
    }
  }
}
```

**Key fill rules for nested vertical structures:**
- Outer key columns: **repeat** the same value across multiple rows for each inner entry; non-key fields only filled on the first row
- Inner key columns: each combination appears **exactly once** if the value contains no further nesting
