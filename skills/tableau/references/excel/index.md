# Excel Input Format Reference

Excel (`.xlsx`) is the **native format** for tableau. A single `.xlsx` file contains multiple sheets — the `@TABLEAU` metasheet plus data sheets.

## File Structure

| Concept       | Excel                                 |
| ------------- | ------------------------------------- |
| **Workbook**  | One `.xlsx` file with multiple sheets |
| **Worksheet** | A sheet tab inside the `.xlsx`        |
| **Metasheet** | A sheet named `@TABLEAU`              |

Use the `xlsx` skill to create `.xlsx` files programmatically.

---

## @TABLEAU Metasheet

A special sheet named `@TABLEAU` that configures all worksheets in the workbook.

### Metasheet columns

| Column         | Description                                                                                                                                    |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `Sheet`        | Worksheet name. Use `#` as a special row for workbook-level options.                                                                           |
| `Alias`        | Alias for the sheet (becomes the proto message name / proto filename for `#` row)                                                              |
| `Mode`         | Sheet mode: `MODE_ENUM_TYPE`, `MODE_ENUM_TYPE_MULTI`, `MODE_STRUCT_TYPE`, `MODE_STRUCT_TYPE_MULTI`, `MODE_UNION_TYPE`, `MODE_UNION_TYPE_MULTI` |
| `OrderedMap`   | `true` to preserve insertion order of map keys                                                                                                 |
| `Index`        | Composite index, e.g. `(Type,Rarity)@TRIndex`                                                                                                  |
| `OrderedIndex` | Ordered index, e.g. `Level@LevelIndex`                                                                                                         |
| `Nested`       | `true` to enable dot-separated column name hierarchy                                                                                           |
| `Sep`          | Sheet-level separator for incell lists/maps (default `,`)                                                                                      |
| `Subsep`       | Sheet-level sub-separator for incell map key-value pairs (default `:`)                                                                         |
| `Patch`        | Patch mode for merging data                                                                                                                    |

### Example metasheet

```
| Sheet     | Alias     | Mode                   | OrderedMap | Index                 |
| #         | MyProto   |                        |            |                       |
| ItemConf  | ItemAlias |                        | true       | Type@TypeIndex        |
| FruitType |           | MODE_ENUM_TYPE         |            |                       |
| EnumTypes |           | MODE_ENUM_TYPE_MULTI   |            |                       |
| HeroConf  |           |                        |            | (Type,Rarity)@TRIndex |
| Struct    |           | MODE_STRUCT_TYPE_MULTI |            |                       |
| Union     |           | MODE_UNION_TYPE_MULTI  |            |                       |
```

- `Sheet=#` row sets **workbook-level** options (e.g., `Alias` becomes the proto filename)
- Each subsequent row configures one worksheet

---

## Data Sheet Layout

Standard **4-row header** followed by data rows:

```
| Row 1 (Namerow)  | ID                | Name   | Desc               | Tags     |
| Row 2 (Typerow)  | map<uint32, Item> | string | string             | []string |
| Row 3 (Noterow)  | Item's ID         | Name   | Item's description | Tags     |
| Row 4+ (Datarow) | 1                 | Apple  | A delicious fruit  | sweet,red|
|                  | 2                 | Orange | A citrus fruit     | sour     |
```

- **Namerow**: column names (used to generate proto field names)
- **Typerow**: tableau type expressions (see `types.md`)
- **Noterow**: human-readable notes (become proto field comments)
- **Datarow**: actual data (one or more rows)

### Parsing field notes from user descriptions

When a user describes fields like:

```
ID uint32 (垂直 map key), Name string (物品名称), BossPos .Position (Boss 坐标，跨列struct)
```

The text inside parentheses `(...)` is the **noterow value** for that field. Extract it exactly as written — it may contain extra context hints (e.g., "跨列struct", "单元格内struct") that describe the layout, but the full parenthesized text is still used as the note.

> ⚠️ Always use the **exact text inside the parentheses** as the noterow value. Both `Name string (物品名称)` and `Name string (note: 物品名称)` mean the noterow cell should contain `物品名称`.

### Column skipping

Columns starting with `#` are ignored by both protogen and confgen:

```
| ID               | Name   | #InternalNote  |
| map<uint32, Item>| string |                |
| Item ID          | Name   | Developer note |
| 1                | Apple  | needs review   |
```

### Multi-line cells (Alt+Enter)

Use **Alt+Enter** in Excel to put multiple lines in one cell. This is used in:
- Union definition sheets: each Field cell has `FieldName↵Type↵Note` on separate lines
- Combined name+type rows when `nameline`/`typeline` settings are configured

---

## Excel-Specific Features

| Feature              | Description                                                                    |
| -------------------- | ------------------------------------------------------------------------------ |
| **Multi-line cells** | Alt+Enter for newlines within a cell (used in union Field columns)             |
| **Unicode**          | Full UTF-8 support including CJK characters in names, notes, and data          |
| **Multiple sheets**  | Native support — `@TABLEAU` + data sheets + type-definition sheets in one file |
| **Column skipping**  | Prefix column name with `#` to exclude from processing                         |

---

## Complex Type Examples

The following examples apply to both Excel and CSV formats. In CSV, type expressions containing commas must be quoted and embedded quotes doubled (see [`../csv/index.md`](../csv/index.md) for quoting rules).

### Vertical Map with Constraints

```
| ID                                           | Name   | Price |
| map<uint32, Item>|{range:"1,100" unique:true} | string | int32 |
| Item ID                                      | Name   | Price |
| 1                                            | Apple  | 100   |
| 2                                            | Orange | 200   |
```

> **Auto-deduced `unique`**: Tableau automatically infers key uniqueness. Explicit `unique:true` is rarely needed.

### Horizontal List

Column naming pattern: `<VarName><N><FieldName>`, N starts at 1. **Every element must have ALL fields present.**

```
| Item1ID      | Item1Name    | Item2ID    | Item2Name    | Item3ID    | Item3Name    |
| [Item]uint32 | string       | uint32     | string       | uint32     | string       |
| Item1 ID     | Item1 name   | Item2 ID   | Item2 name   | Item3 ID   | Item3 name   |
| 1            | Apple        | 2          | Orange       | 3          | Banana       |
```

Example with Reward struct (ID + Num fields), 3 elements:

```
| Reward1ID      | Reward1Num | Reward2ID | Reward2Num | Reward3ID | Reward3Num |
| [Reward]uint32 | int32      | uint32    | int32      | uint32    | int32      |
| Reward1 ID     | Reward1 num| Reward2 ID| Reward2 num| Reward3 ID| Reward3 num|
| 1001           | 10         | 1002      | 5          | 1003      | 3          |
```

> ⚠️ If a user describes only `Reward1ID` and `Reward2Num`, they are listing *representative* columns. The full column set must include ALL fields for ALL elements.

### Nested Vertical Maps (Map-in-Map)

Two levels of vertical map nesting with a horizontal list inside:

```
| ID                  | Name   | Phase             | Item1ID      | Item1Num |
| map<uint32, Season> | string | map<int32, Phase> | [Item]uint32 | int32    |
| Season ID           | Name   | Phase             | Item1 ID     | Item1 num|
| 1                   | Spring | 1                 | 1001         | 10       |
| 1                   |        | 2                 | 2001         | 3        |
| 2                   | Summer | 1                 | 3001         | 20       |
| 2                   |        | 2                 | 3002         | 15       |
```

**Key fill rules based on auto-deduced uniqueness:**

| Key column          | Value type contains nested vertical map/list? | Auto-deduced unique | Fill rule                                                                                                                       |
| ------------------- | --------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `ID` (outer map)    | ✅ Yes — contains `map<int32, Phase>`          | ❌ Not unique        | **Repeat** the same ID across multiple rows for each inner-map entry; non-key fields (e.g. `Name`) only filled on the first row |
| `Phase` (inner map) | ❌ No — value only contains horizontal list    | ✅ Unique            | Each `(ID, Phase)` combination appears **exactly once**                                                                         |

### Cross-Cell Struct with Nested Struct

```
| ID               | RewardID      | RewardItemID | RewardItemNum |
| map<uint32, Task>| {Reward}int32 | {Item}int32  | int32         |
| Task ID          | Reward ID     | Item ID      | Item num      |
| 1                | 100           | 1001         | 10            |
```

### Union in Data Sheet

```
| ID               | TargetType                  | TargetField1 | TargetField2 |
| map<int32, Task> | {.Target}enum<.Target.Type> | union        | union        |
| Task ID          | Target type                 | Target field1| Target field2|
| 1                | Exchange                    | 9001         | 1001,10      |
| 2                | CheckIn                     | 1            |              |
```

### Field Properties

```
| ID               | Name                       | BuffId1                        |
| map<uint32, Item>| string|{refer:"ItemConf.ID"} | int32|{json_name:"buff_id_1"} |
| Item ID          | Item name                  | Buff ID                        |
| 1                | Apple                      | 100                            |
```

### Large-Scale Real-World Example

From the Activity test case — 64+ columns with deep nesting:

```
| ActivityID                              | ActivityName | ChapterID          | ChapterName | SectionID                       | SectionName | ... |
| map<uint32, Activity>|{range:"~,999999"}| string       | map<uint32, Chapter>| string      | [Section]uint32|{range:"~,100"} | string      | ... |
| 活动ID                                   | 活动名称      | 章节ID              | 章节名称     | 小节ID                           | 小节名称     | ... |
| 100001                                  | Activity1    | 1                  | Chapter1    | 1                               | Section1    | ... |
```

Features demonstrated:
- Range constraints with unbounded (`~`)
- Nested maps (`map<uint32, Activity>` containing `map<uint32, Chapter>`)
- Keyed lists (`[Section]uint32`)
- Well-known types (`datetime`, `duration`)
- Unicode (Chinese) in noterow
- Inline structs (`{int32 Id, string Desc, int32 Value}Info`)

---

## Sub-References

| File                                       | Contents                                                    |
| ------------------------------------------ | ----------------------------------------------------------- |
| [`enum.md`](enum.md)                       | Enum definition sheets (`MODE_ENUM_TYPE` / `_MULTI`)        |
| [`struct.md`](struct.md)                   | Struct definition sheets + cross-cell / incell struct usage |
| [`union.md`](union.md)                     | Union definition sheets (`MODE_UNION_TYPE` / `_MULTI`)      |
| [`list.md`](list.md)                       | List types: horizontal, vertical, incell                    |
| [`map.md`](map.md)                         | Map types: horizontal, vertical, incell                     |
| [`keyedlist.md`](keyedlist.md)             | Keyed list types                                            |
| [`nesting.md`](nesting.md)                 | Complex nesting: struct/list/map combinations               |
| [`field-property.md`](field-property.md)   | Field property options (`range`, `refer`, `unique`, etc.)   |
| [`wellknown-types.md`](wellknown-types.md) | Datetime, duration, fraction, comparator, version           |
| [`styling.md`](styling.md)                 | Color palette, auto-fit helpers, sheet layout patterns      |
