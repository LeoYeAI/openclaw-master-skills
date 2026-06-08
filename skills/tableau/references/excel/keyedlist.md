# Keyed List in Excel

A keyed list is a `repeated` field where the first field serves as a unique key (but stays as `repeated`, not `map`). It allows aggregating multiple rows with the same key.

**Syntax**: `[ElemType]<ColumnType>` (angle brackets around the key type)

---

## Vertical Keyed List

### Scalar keyed list

Multiple rows are aggregated into one list:

```
| ID           |
| []<uint32>   |
| ID           |
| 1,2,3        |
| 4,5          |
| 6            |
```

Generated proto:
```protobuf
repeated uint32 id_list = 1 [(tableau.field) = {name:"ID" key:"ID" layout:LAYOUT_INCELL}];
```

Generated JSON:
```json
{ "idList": [1, 2, 3, 4, 5, 6] }
```

### Enum keyed list

```
| Type                     |
| []<enum<.FruitType>>     |
| Type                     |
| Apple,Orange             |
| FRUIT_TYPE_BANANA        |
| 0                        |
```

Generated proto:
```protobuf
repeated protoconf.FruitType type_list = 1 [(tableau.field) = {name:"Type" key:"Type" layout:LAYOUT_INCELL}];
```

### Struct keyed list

Rows with the same key are grouped together:

```
| ID               | PropID           | PropName    |
| [Item]<uint32>   | map<int32, Prop> | string      |
| Item's ID        | Prop's ID        | Prop's name |
| 1                | 1                | sweet       |
| 2                | 1                | sweet       |
| 2                | 2                | delicious   |
```

Generated proto:
```protobuf
repeated Item item_list = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
message Item {
  uint32 id = 1 [(tableau.field) = {name:"ID"}];
  map<int32, Prop> prop_map = 2 [(tableau.field) = {key:"PropID" layout:LAYOUT_VERTICAL}];
  message Prop {
    int32  prop_id   = 1 [(tableau.field) = {name:"PropID"}];
    string prop_name = 2 [(tableau.field) = {name:"PropName"}];
  }
}
```

Generated JSON:
```json
{
    "itemList": [
        { "id": 1, "propMap": { "1": { "propId": 1, "propName": "sweet" } } },
        { "id": 2, "propMap": {
            "1": { "propId": 1, "propName": "sweet" },
            "2": { "propId": 2, "propName": "delicious" }
        }}
    ]
}
```

---

## Incell Keyed List

### Incell scalar keyed list

```
| ID           |
| []<uint32>   |
| ID list      |
| 1,2,3        |
```

Generated proto:
```protobuf
repeated uint32 id_list = 1 [(tableau.field) = {name:"ID" key:"ID" layout:LAYOUT_INCELL}];
```

### Incell enum keyed list

```
| Param                      |
| []<enum<.FruitType>>       |
| Param list                 |
| 1,FRUIT_TYPE_ORANGE,Banana |
```

Generated proto:
```protobuf
repeated protoconf.FruitType type_list = 1 [(tableau.field) = {name:"Type" key:"Type" layout:LAYOUT_INCELL}];
```

---

## Keyed List vs Map

| Feature        | Keyed List `[Item]<uint32>`      | Map `map<uint32, Item>`          |
| -------------- | -------------------------------- | -------------------------------- |
| Proto type     | `repeated Item`                  | `map<uint32, Item>`              |
| Key uniqueness | Enforced (duplicate key = merge) | Enforced (duplicate key = error) |
| Ordering       | Preserved (insertion order)      | Not guaranteed                   |
| Access pattern | Iterate + find by key            | Direct key lookup                |
| Use case       | Ordered data with unique key     | Fast key-based lookup            |

---

## Map in Vertical Keyed List

A vertical keyed list can contain a nested vertical map:

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
  uint32 id   = 1 [(tableau.field) = {name:"ID"}];
  string name = 2 [(tableau.field) = {name:"Name"}];
  map<int32, Prop> prop_map = 3 [(tableau.field) = {key:"PropID" layout:LAYOUT_VERTICAL}];
  message Prop {
    int32 prop_id    = 1 [(tableau.field) = {name:"PropID"}];
    int64 prop_value = 2 [(tableau.field) = {name:"PropValue"}];
  }
}
```
