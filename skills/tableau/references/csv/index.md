# CSV Input Format Reference

> **CSV worksheet is identical to Excel worksheet.** All sheet layouts, type expressions, and features are the same — see [`../excel/index.md`](../excel/index.md) for the full guide. This document covers only CSV-specific concepts and syntax differences.

## Concepts

As Tableau recognizes the pattern `<BookName>#<SheetName>.csv`, a **CSV workbook** (Glob Pattern `<BookName>#*.csv`) is composed of multiple **CSV worksheets** (files) in the same directory.

| Concept       | CSV                                                                        |
| ------------- | -------------------------------------------------------------------------- |
| **Workbook**  | Glob pattern `<BookName>#*.csv` — all matching files in the same directory |
| **Worksheet** | A single file named `<BookName>#<SheetName>.csv`                           |
| **Metasheet** | A file named `<BookName>#@TABLEAU.csv`                                     |

**Example** — a CSV workbook `HelloWorld#*.csv` is composed of:

1. Worksheet `@TABLEAU`: `HelloWorld#@TABLEAU.csv` (metasheet)
2. Worksheet `ItemConf`: `HelloWorld#ItemConf.csv`
3. Worksheet `FruitType`: `HelloWorld#FruitType.csv`
4. Worksheet `HeroConf`: `HelloWorld#HeroConf.csv`

This is exactly equivalent to an Excel file `HelloWorld.xlsx` with sheets `@TABLEAU`, `ItemConf`, `FruitType`, `HeroConf`.

## Sheet Layouts & Type Definitions

All sheet layouts (`@TABLEAU` metasheet, data sheets, enum/struct/union definition sheets) are **identical to Excel** — see [`../excel/index.md`](../excel/index.md) for the full reference.

## Complex Type Examples

> All type expressions (map, list, struct, union, field properties, etc.) are identical to Excel. See [`../excel/index.md`](../excel/index.md) for the full set of examples.
>
> The only CSV-specific difference is **quoting**: values containing commas must be quoted, and embedded quotes are doubled.

### CSV Quoting Rules

| Situation                                 | CSV syntax                                     |
| ----------------------------------------- | ---------------------------------------------- |
| Value contains a comma (e.g. incell list) | `"1,2,3"`                                      |
| Type expression contains a comma          | `"map<uint32, Item>"`                          |
| Field property with quoted string         | `"map<uint32, Item>\|{range:""1,100""}"`       |
| `refer` option with quoted path           | `"string\|{refer:""ItemConf.ID""}"`            |
| `json_name` option                        | `"int32\|{json_name:""buff_id_1""}"`           |
| Multi-line union field cell               | `"ID↵uint32↵note"` (literal newline in quotes) |

> For full type examples (map, list, struct, union, field properties, etc.), see [`../excel/index.md`](../excel/index.md#complex-type-examples). The rules are identical — only the quoting syntax differs as shown above.
