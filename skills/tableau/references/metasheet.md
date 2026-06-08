# Metasheet (`@TABLEAU`) Reference

The metasheet is a special worksheet that configures how tableau parses other worksheets in the same workbook.

## Format by Input Type

| Format | Location                                              |
| ------ | ----------------------------------------------------- |
| Excel  | A sheet named `@TABLEAU`                              |
| CSV    | A file named `<BookName>#@TABLEAU.csv`                |
| XML    | Comment block at file top: `<@TABLEAU>...</@TABLEAU>` |
| YAML   | A document with key `"@sheet": "@TABLEAU"`            |

If the metasheet is **empty or absent**, all non-metasheets are processed with default options.

The metasheet name can be customized via `proto.input.metasheetName` in config.yaml (must start with `@`).

## Per-Sheet Options

Each row in the metasheet applies to one worksheet. The `Sheet` column identifies the target sheet. Use `Sheet=#` to set options for the workbook itself (e.g., `Alias` for the proto file name).

| Option                   | Type   | Default        | Description                                                        |
| ------------------------ | ------ | -------------- | ------------------------------------------------------------------ |
| `Sheet`                  | string | _(required)_   | Worksheet name; `#` = workbook level                               |
| `Alias`                  | string | sheet name     | Proto message name alias; or proto filename when `Sheet=#`         |
| `Namerow`                | int    | 1              | Row number for column names                                        |
| `Typerow`                | int    | 2              | Row number for column types                                        |
| `Noterow`                | int    | 3              | Row number for column notes                                        |
| `Datarow`                | int    | 4              | First data row                                                     |
| `Nameline`               | int    | 0              | Line within cell for name (0=entire cell)                          |
| `Typeline`               | int    | 0              | Line within cell for type (0=entire cell)                          |
| `Sep`                    | string | `,`            | In-cell list/map separator                                         |
| `Subsep`                 | string | `:`            | In-cell key-value sub-separator                                    |
| `Transpose`              | bool   | false          | Swap rows and columns before parsing                               |
| `Nested`                 | bool   | false          | Use dot-separated column names for nested structs                  |
| `Merger`                 | string | —              | Glob or comma-separated list of workbooks to merge into this sheet |
| `Scatter`                | string | —              | Glob/list of workbooks to scatter (one output per workbook)        |
| `AdjacentKey`            | bool   | false          | Carry down key from nearest non-empty cell above                   |
| `FieldPresence`          | bool   | false          | Generate `optional` label on all basic-type fields                 |
| `Mode`                   | Mode   | `MODE_DEFAULT` | Special sheet mode (see below)                                     |
| `Optional`               | bool   | false          | All fields in this sheet are optional (column may be absent)       |
| `Patch`                  | Patch  | `PATCH_NONE`   | Sheet-level patch behavior                                         |
| `WithParentDir`          | bool   | false          | Create output subdirectory path from subdir structure              |
| `ScatterWithoutBookName` | bool   | false          | Scatter output files omit the book name prefix                     |
| `OrderedMap`             | bool   | false          | Generate OrderedMap accessor APIs for the first map field          |
| `Index`                  | string | —              | Index accessor specification (see below)                           |
| `OrderedIndex`           | string | —              | Same as Index but ordered                                          |
| `Labels`                 | string | —              | Key-value metadata labels (e.g., `"app:gamesvr,patch:merge"`)      |
| `LangOptions`            | map    | —              | Per-language loader overrides                                      |

## Sheet Modes

| Mode                     | Description                                                               |
| ------------------------ | ------------------------------------------------------------------------- |
| `MODE_DEFAULT`           | Normal data worksheet                                                     |
| `MODE_ENUM_TYPE`         | Sheet defines a single enum type                                          |
| `MODE_ENUM_TYPE_MULTI`   | Sheet contains multiple enum definitions (blocks separated by empty rows) |
| `MODE_STRUCT_TYPE`       | Sheet defines a single struct type                                        |
| `MODE_STRUCT_TYPE_MULTI` | Sheet contains multiple struct definitions                                |
| `MODE_UNION_TYPE`        | Sheet defines a single union (oneof) type                                 |
| `MODE_UNION_TYPE_MULTI`  | Sheet contains multiple union definitions                                 |

## Patch Types

| Value           | Behavior                                                                        |
| --------------- | ------------------------------------------------------------------------------- |
| `PATCH_NONE`    | No patching (default)                                                           |
| `PATCH_REPLACE` | Completely replace the existing data                                            |
| `PATCH_MERGE`   | Merge: scalars overwrite, messages merge recursively, lists append, maps upsert |

## Metasheet Examples

### Excel metasheet (`@TABLEAU` sheet)

```
| Sheet    | Alias      | Mode                 | OrderedMap | Index                 | OrderedIndex   |
| #        | MyProto    |                      |            |                       |                |
| ItemConf | ItemAliasC |                      | true       | Type@TypeIndex        |                |
| HeroConf |            |                      |            | (Type,Rarity)@TRIndex | Level@LvlIndex |
| FruitType|            | MODE_ENUM_TYPE       |            |                       |                |
| EnumTypes|            | MODE_ENUM_TYPE_MULTI |            |                       |                |
```

### CSV metasheet (`Book#@TABLEAU.csv`)

```csv
Sheet,Mode,OrderedMap,Alias
ItemConf,,true,
EnumTypes,MODE_ENUM_TYPE_MULTI,,
```

### XML metasheet comment

```xml
<!--
<@TABLEAU>
    <ItemConf Sheet="ItemConf" OrderedMap="true" />
    <HeroConf Sheet="HeroConf" Transpose="true" />
</@TABLEAU>
-->
```

### YAML metasheet document

```yaml
"@sheet": "@TABLEAU"
ItemConf:
  OrderedMap: true
  Alias: ItemAliasConf
HeroConf:
  Transpose: true
```

## Merger

Merges multiple workbooks sharing the same schema into a single output config:

```
| Sheet    | Merger           |
| ZoneConf | ZonePatch*.xlsx  |
```

- Glob patterns automatically exclude the main workbook itself
- Sub-workbooks do not need their own `@TABLEAU`
- Specific sheets: `Book2.xlsx#ZoneConf2,Book3.xlsx#ZoneConf3`
- CSV format: `Merger*.csv,Merger1#*.csv#MetasheetOptionMerger*`

Generated proto: `option (tableau.worksheet) = {name:"ZoneConf" merger:"ZonePatch*.xlsx"};`

## Scatter

Produces separate output files per matched workbook (same schema, different data):

```
| Sheet    | Scatter          | ScatterWithoutBookName |
| ZoneConf | Zone*.xlsx       | false                  |
```

- Output: `<BookName>_ZoneConf.json` per matched workbook
- With `ScatterWithoutBookName: true`: just `ZoneConf.json`

## Index / OrderedIndex

Generate fast-lookup accessor APIs. Syntax: `Column<SortCol1,SortCol2>@IndexName`

Examples:
- `ID@Item` — index by ID, name the accessor "Item"
- `ID<ID>@Item` — index by ID, sort results by ID
- `ID<Type,Priority>@Item` — index by ID, sort by Type then Priority
- `(ID,Name)@AwardItem` — composite index on (ID, Name)

## AdjacentKey

When `AdjacentKey: true`, empty cells in the key column inherit the nearest non-empty value above:

```
| ID | SubID | Value |
| 1  | 1     | Apple |
|    | 2     | Pear  |   <- ID treated as 1
|    | 3     | Grape |   <- ID treated as 1
| 2  | 1     | Cat   |
```

Useful for flat spreadsheets that logically group rows under a shared parent key.

## Labels

Attach metadata labels to sheets for downstream use:

```
| Sheet    | Labels                    |
| Scalar   | app:gamesvr,patch:merge   |
```

Labels are key-value pairs (colon-separated) with multiple entries separated by commas.
