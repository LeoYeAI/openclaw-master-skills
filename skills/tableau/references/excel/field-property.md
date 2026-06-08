# Field Properties in Excel

Field properties are appended to the typerow cell using `|{...}` syntax:

```
| ID                                          | Name                        |
| map<uint32, Item>|{range:"1,100" unique:true}| string|{refer:"ItemConf.ID"} |
```

---

## Option `range`

Constrains the value range of a field. Format: `"left,right"` (both inclusive). Use `~` for unbounded.

Supported for:
- **number**: value range, e.g. `"1,10"`, `"1,~"`, `"~,10"`
- **string**: count of UTF-8 code points

Examples:
```
map<uint32, Item>|{range:"1,100"}    # key must be in [1, 100]
string|{range:"1,50"}                # string length 1–50 chars
map<uint32, Item>|{range:"~,999999"} # key ≤ 999999 (unbounded lower)
```

---

## Option `unique`

Ensures field values are unique within the list/map.

```
map<uint32, Item>|{unique:true}
```

> **Auto-deduced `unique`**: Tableau automatically infers key uniqueness for map keys. Explicit `unique:true` is rarely needed.

---

## Option `refer`

Similar to a **FOREIGN KEY** constraint in SQL. Ensures this field's value exists in at least one of the referenced columns.

Format: `"SheetName(SheetAlias).ColumnName[,SheetName(SheetAlias).ColumnName]..."`

Examples:
```
map<uint32, Reward>|{refer:"ItemConf.ID"}                  # single-refer, no alias
map<uint32, Reward>|{refer:"ItemConf.ID,EquipConf.ID"}     # multi-refer, no alias
map<uint32, Reward>|{refer:"Sheet1(ItemConf).ID"}          # single-refer with alias
```

- Without alias: **sheet name** is the generated protobuf message name
- With alias: **sheet alias** is the generated protobuf message name

---

## Option `sequence`

Ensures this field's value follows a sequence starting from the given value. Can be used for any fields, even in nested list/map.

```
map<uint32, Item>|{sequence:1}   # map key must follow sequence starting at 1
int32|{sequence:1}               # parent list/map elements must follow sequence starting at 1
```

---

## Option `default`

If set, uses this value as the default when the cell is empty (not present).

```
string|{default:"unknown"}
int32|{default:"0"}
```

---

## Option `fixed`

If set to `true`, auto-detects the fixed size of a horizontal list/map from the header row.

```
[Item]uint32|{fixed:true}        # implicit fixed size
map<uint32, Item>|{fixed:true}   # implicit fixed size
```

See [`list.md`](list.md) and [`map.md`](map.md) for examples.

---

## Option `size`

Specifies the explicit fixed size of a horizontal list/map.

```
[Item]uint32|{size:3}            # exactly 3 elements
map<uint32, Item>|{size:3}       # exactly 3 entries
```

---

## Option `form`

Specifies the cell data format for incell struct fields.

| Value       | Description                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------- |
| `FORM_TEXT` | Protobuf [text format](https://developers.google.com/protocol-buffers/docs/text-format-spec) |
| `FORM_JSON` | Protobuf [JSON format](https://developers.google.com/protocol-buffers/docs/proto3#json)      |

```
{.Transform}|{form:FORM_TEXT}    # cell: "position:{x:1 y:2 z:3}"
{.Transform}|{form:FORM_JSON}    # cell: '{"position":{"x":1,"y":2,"z":3}}'
```

---

## Option `json_name`

Explicitly specifies the JSON field name (overrides the default camelCase conversion).

```
| Rarity_1                      | SpecialEffect_2                    |
| int32|{json_name:"rarity_1"}  | int32|{json_name:"specialEffect_2"} |
```

---

## Option `present`

If set to `true`, the cell cannot be empty — an error is reported if it is.

```
uint32|{present:true}
```

---

## Option `optional`

If set to `true`, the field's column (table formats) or name (document formats) can be absent.

```
string|{optional:true}
```

---

## Option `patch`

See field-level patch in [`metasheet.md`](../metasheet.md).

---

## Option `sep`

**Field-level** separator for incell list elements or incell map items. Overrides the sheet-level `sep`.

```
[]int32|{sep:"!"}                # cell: "1!2!3"
map<string,string>|{sep:";"}     # cell: "a:1;b:2"
```

---

## Option `subsep`

**Field-level** sub-separator for key-value pairs in incell maps or struct fields in incell struct lists. Overrides the sheet-level `subsep`.

```
map<string,string>|{sep:";" subsep:"="}   # cell: "dog=cute;bird=noisy"
```

---

## Option `cross`

Specifies the count of crossed nodes/cells/fields for composite types (list, map) with cardinality.

For union list fields:
- `0`: incell list
- `> 0`: horizontal list occupying N fields
- `< 0`: horizontal list occupying all following fields

---

## Option `pattern`

Specifies the pattern for scalar fields, list elements, or map values.

### Version pattern

```
version|{pattern:"255.255.255"}       # default: each component 0–255
version|{pattern:"99.999.99.999.99.999"}  # 6-component version
```

See [`wellknown-types.md`](wellknown-types.md) for version examples.

---

## Combined Example

```
| ActivityID                               | ActivityName | ChapterID           |
| map<uint32, Activity>|{range:"~,999999"} | string       | map<uint32, Chapter>|
| 活动ID                                    | 活动名称      | 章节ID               |
| 100001                                   | Activity1    | 1                   |
```

Features:
- `range:"~,999999"` — key must be ≤ 999999
- Unicode (Chinese) in noterow is fully supported
