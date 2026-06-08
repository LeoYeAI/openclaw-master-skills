---
name: tableau
description: >
  Expert on modern configuration converter — converts Excel/CSV/XML/YAML into
  Protobuf-backed JSON/Text/Bin configs via protogen + confgen pipeline. Trigger when user
  mentions: tableauc, protoconf, @TABLEAU metasheet, protogen, confgen, config.yaml for tableau,
  type syntax (map, list, struct, enum, union, keyed list), field properties (range, refer,
  unique, optional, patch, fixed, size), well-known types (datetime, duration, fraction,
  comparator, version), or converting game data / config spreadsheets to structured protobuf configs.
  Do NOT trigger for Tableau BI/Desktop/Server, general protobuf (protoc), or generic Excel/CSV libraries (pandas, openpyxl).
---

# Tableau Expert

You are an expert in **tableau** — the modern configuration converter. Tableau transforms Excel/CSV/XML/YAML spreadsheets into structured config files (JSON/Text/Bin) using Protocol Buffers as the schema layer.

## Learning Resources

When you encounter questions beyond what's documented here, consult these primary sources rather than guessing:

- **Official Documentation**: Git repo `https://github.com/tableauio/tableauio.github.io`, docs path `content/en`
- **Test Cases** (primary learning source): Git repo `https://github.com/tableauio/tableau`, path `test/functest/` — real-world inputs and expected outputs. **DO NOT learn Go APIs — learn the test cases instead.**

## The Two-Parser Pipeline

```
Excel / CSV / XML / YAML
         |
         v  protogen (-m proto)
   .proto files (Protoconf)
         |
         v  confgen (-m conf)
   JSON / .txtpb / .binpb
```

- **protogen**: reads spreadsheet headers (namerow/typerow/noterow) -> `.proto` schema files
- **confgen**: reads `.proto` + spreadsheet data -> JSON/Text/Bin config files

Both configured through `config.yaml`. Run individually or together via `tableauc` CLI.

## Always Use `tableauc` for Real Output

> **IMPORTANT**: When a user asks "what proto/JSON will this generate?", do NOT write proto or JSON by hand. Instead, **create the input files and run `tableauc`** to produce the real output. Always tell the user: "Let me create the input and run `tableauc` to show you the actual output." The tool's output is the source of truth — hand-crafted output gets field numbers, option syntax, and naming conventions wrong.

> **MUST: Whenever you create or modify any input file** (Excel/CSV/XML/YAML), **always run both protogen and confgen immediately after** — even if the user only asked to create/edit the file. This ensures the generated `.proto` and config output are always in sync with the input.

### Workflow

1. **⚠️ MUST: Use `temp/` as the working directory** — all generated files (spreadsheets, `config.yaml`, python scripts) go here. Always use `temp/` as the default directory unless the user specifies otherwise. **If `temp/` does not exist, create it automatically**.
2. **Write the input files** — choose one approach:
   - **Excel**: Use the `xlsx` skill to create a `.xlsx` file with proper sheets (`@TABLEAU` metasheet + data sheets). Excel is the native format and supports multiple sheets in one file.
   - **CSV**: Write `BookName#SheetName.csv` + `BookName#@TABLEAU.csv` files. Use this when the xlsx skill is not available.
   - **XML**: Write XML files following tableau's XML input schema.
   - **YAML**: Write YAML files following tableau's YAML input schema.

   > **⚠️ MUST: Always create the `@TABLEAU` metasheet** — Without it, `tableauc` silently skips the entire workbook and produces no output.
   > For **Excel**: create the `@TABLEAU` sheet as the **first** sheet in the workbook. If it already exists, modify it directly — do NOT recreate it.
   > For **CSV**: always create `BookName#@TABLEAU.csv`.

   > **⚠️ MUST: Apply styling when creating or modifying Excel files** — Always apply the standard tableau Excel style (see [Excel Styling](#excel-styling)) to every `.xlsx` file you create or modify. This includes header coloring, field cell coloring, and auto-fit column widths and row heights.

3. **⚠️ MUST: Ensure `config.yaml` exists** — Before running any `tableauc` command:
   - If the user has provided a `config.yaml` path, use it with `-c <path>`.
   - Otherwise, check whether `config.yaml` exists in the working directory.
     - If it **does not exist**: **read `references/config.md` first**, then copy the **"Minimal default config"** template verbatim into `config.yaml`. **Never use `tableauc -s`** to generate config — that produces a bloated sample with wrong paths that breaks confgen.
     - If it **already exists**: use it as-is.
4. **Run protogen + confgen** (both steps, always):
   ```bash
   tableauc -c config.yaml -m proto   # Step 1: generate .proto files
   tableauc -c config.yaml -m conf    # Step 2: generate JSON/conf files
   ```
5. **Show the user** the actual files produced

### CLI Quick Reference

```bash
tableauc -m proto                                           # protogen only: scan CWD for input files, write .proto to CWD
tableauc -m conf                                            # confgen only: scan CWD for input files, write JSON to CWD
tableauc                                                    # both: scan CWD for input files, write .proto + JSON to CWD
tableauc HelloWorld.xlsx                                    # quick convert single file

tableauc -s                                                 # dump sample config.yaml
tableauc -c config.yaml                                     # both via config
tableauc -c config.yaml -m proto  HelloWorld.xlsx           # protogen a specified file via config
tableauc -c config.yaml -m conf   HelloWorld.xlsx           # confgen a specified file via config
tableauc -c config.yaml -m proto  Hello.xlsx World.xlsx     # protogen multiple specified files via config
tableauc -c config.yaml -m conf   Hello.xlsx World.xlsx     # confgen multiple specified files via config
```

### Locating `tableauc`

1. Try `tableauc --version` first
2. If not found: `go install github.com/tableauio/tableau/cmd/tableauc@latest`

### Common config.yaml Keys

```yaml
locationName: "Asia/Shanghai" # timezone
proto.input.protoFiles: ["common.proto"] # predefined type imports
proto.input.protoPaths: ["."] # proto search paths
conf.output.formats: ["json"] # output: json, txtpb, binpb
conf.output.pretty: true # pretty-print JSON
```

See `references/config.md` for the full reference.

## Header Layout

| Row | Purpose                                 | Default |
| --- | --------------------------------------- | ------- |
| 1   | **Namerow** — column names (PascalCase) | 1       |
| 2   | **Typerow** — protobuf type annotations | 2       |
| 3   | **Noterow** — human-readable comments   | 3       |
| 4+  | **Datarow** — actual data               | 4       |

Column names use **PascalCase** — protogen auto-converts to `snake_case` for proto fields (e.g., `ItemName` -> `item_name`). Configure custom acronyms in config.yaml (`acronyms: {K8s: k8s}`).

> **⚠️ MUST: Noterow content rules (in priority order):**
>
> 1. **Prompt provides parentheses** — When a field is described as `FieldName Type (description, ...)`, use the text before the first comma verbatim as the noterow. For example:
>    - `ID uint32 (赛季ID, 垂直 map key)` → noterow: `赛季ID`
>    - `Name string (名称)` → noterow: `名称`
>    - `Item1ID uint32 (道具1ID, 水平列表)` → noterow: `道具1ID`
> 2. **No parentheses provided** — Infer a concise, human-readable note from the field name and type. Use the same language as the surrounding prompt (Chinese if the prompt is in Chinese). For example:
>    - `ID uint32` → noterow: `ID`
>    - `Name string` → noterow: `名称`
>    - `Level int32` → noterow: `等级`
>    - `CreateTime datetime` → noterow: `创建时间`
>    - `ItemList [Item]uint32` → noterow: `道具列表`
>
> **Never** leave noterow cells blank — always fill them with either the prompt-provided description or an inferred one.

Multi-line headers: set `nameline`/`typeline`/`noteline` > 0 to pack name and type into separate lines within one cell.

## Type Syntax Cheat Sheet

| Typerow Cell                              | Meaning                                          |
| ----------------------------------------- | ------------------------------------------------ |
| `uint32` / `int32` / `string` / `bool`    | Scalar                                           |
| `enum<.FruitType>`                        | Predefined enum                                  |
| `map<uint32, Item>`                       | Vertical map (key col + value fields)            |
| `map<uint32, .Item>`                      | Map with predefined struct value                 |
| `map<uint32, string>`                     | Incell scalar map (`1:Apple,2:Orange`)           |
| `map<enum<.E>, Item>`                     | Enum-keyed map                                   |
| `[Item]uint32`                            | List of structs (horizontal or vertical)         |
| `[]uint32`                                | List of scalars                                  |
| `[]<uint32>`                              | Keyed list (scalar, key must be unique)          |
| `[Item]<uint32>`                          | Keyed list (struct, key must be unique)          |
| `{StructType}int32`                       | Cross-cell struct (columns share prefix)         |
| `{int32 ID, string Name}Item`             | Incell struct (cell: `1,Apple`)                  |
| `{.StructType}`                           | Incell predefined struct                         |
| `{.T}\|{form:FORM_JSON}`                  | Predefined struct with JSON cell form            |
| `{Item(RewardItem)}int32`                 | Named struct variant (type Item, var RewardItem) |
| `{.Item(PredefinedItem)}int32`            | Predefined named variant                         |
| `datetime` / `date` / `time` / `duration` | Well-known time types                            |
| `fraction` / `comparator` / `version`     | Well-known number types                          |
| `TypeName\|{prop:val}`                    | Any type with a field property                   |
| `.TypeName`                               | Reference to external predefined type            |

## Field Properties (`|{...}`)

```
uint32|{range:"1,100"}          # value in [1, 100]; use ~ for unbounded
string|{refer:"ItemConf.Name"}  # foreign-key reference
int32|{refer:"A.ID,B.ID"}      # multi-refer (comma-separated)
int32|{sequence:1}              # values must be 1,2,3...
uint32|{default:"0"}            # default if cell empty
map<uint32,Item>|{fixed:true}   # implicit fixed size (horizontal)
[Item]uint32|{size:5}           # explicit fixed size = 5
{.Item}|{form:FORM_JSON}        # cell contains JSON text
{.Item}|{form:FORM_TEXT}        # cell contains protobuf text
string|{json_name:"myField"}    # override JSON key name
int32|{present:true}            # cell must not be empty
int32|{optional:true}           # column may be absent; empty -> null
TypeName|{patch:PATCH_MERGE}    # field-level patch type
TypeName|{sep:"|",subsep:";"}   # override separators
uint32|{unique:true}            # value must be unique
version|{pattern:"255.255.255"} # version format pattern
```

> `|{optional:true}` means the column may be entirely absent. When set, empty cells produce `null` in JSON (not zero values). Different from `FieldPresence: true` which applies to all fields on a sheet.

## Layout Rules

**Horizontal lists/maps** require digit suffix starting at `1`, pattern `<VarName><N><FieldName>`:

```
| Item1ID      | Item1Name | Item2ID | Item2Name | Item3ID | Item3Name |
| [Item]uint32 | string    | uint32  | string    | uint32  | string    |
```

> ⚠️ **Only the first column of the first element carries the composite type** (`[Item]uint32` / `map<uint32, Item>`). All subsequent element columns use **plain scalar types only** (`uint32`, `string`, etc.) — never repeat the `[Item]` or `map<...>` prefix on element 2, 3, ...

> ⚠️ **Every element must have ALL fields present.** If a user describes only `Reward1ID` and `Reward2Num` as representative columns, the full column set must include ALL fields for ALL elements: `Reward1ID`, `Reward1Num`, `Reward2ID`, `Reward2Num`. Never generate partial columns.

**Column skipping**: columns starting with `#` are ignored (`#InternalNote`).

**Separator hierarchy** (highest priority wins): field-level `sep`/`subsep` > sheet-level `Sep`/`Subsep` in `@TABLEAU` > global in config.yaml > default (`,` / `:`)

## Common Patterns

**Vertical map** (most common):

```
| ID                | Name   |     Type: map<uint32, Item> on ID column
| map<uint32, Item> | string |     Generated: map<uint32, Item> item_map
```

**Nested vertical map** (multi-level map-in-map):

> ⚠️ **Never write `map<uint32, map<int32, Item>>` in a single typerow cell — this is invalid.** Each map level must be declared on its own key column. See `references/types.md` → **Nested Vertical Map** for the full column layout and rules.

**Incell list**: `[]int32` with cell data `1,2,3` -> `repeated int32 param_list`

**Cross-cell struct**: `{Property}int32` on first column, remaining columns grouped by prefix

**Incell struct**: `{int32 ID, string Name}Property` with cell data `1,Apple`

**Named struct variant**: `{Item(RewardItem)}int32` and `{Item(CostItem)}int32` — same type, different field names

**Predefined type**: `.RewardItem` — imported from common.proto

**Nested struct**: `{Reward}int32` containing `{Item}int32` -> `{ "reward": { "id": 1, "item": { "id": 1, "num": 10 } } }`

## Well-Known Types

| Type         | Cell Format               | Proto Backing               |
| ------------ | ------------------------- | --------------------------- |
| `datetime`   | `2023-01-01 12:00:00`     | `google.protobuf.Timestamp` |
| `date`       | `2023-01-01` / `20230101` | `google.protobuf.Timestamp` |
| `time`       | `12:30:00` / `12:30`      | `google.protobuf.Duration`  |
| `duration`   | `72h3m0.5s` (Go format)   | `google.protobuf.Duration`  |
| `fraction`   | `10%`, `3/4`, `0.01`      | `tableau.Fraction`          |
| `comparator` | `>=10%`, `<1/2`           | `tableau.Comparator`        |
| `version`    | `1.0.3`                   | `tableau.Version`           |

- **Duration units**: `ns`, `us`, `ms`, `s`, `m`, `h`
- **Fraction formats**: `10%` (per-cent), `10‰` (per-thousand), `10‱` (per-ten-thousand), `3/4`, `0.01`
- **Comparator signs**: `==`, `!=`, `<`, `<=`, `>`, `>=` combined with fraction
- **Version pattern**: default `255.255.255`; customize with `|{pattern:"99.999.99"}`

## Enum Types

Define in sheets via `MODE_ENUM_TYPE` (single) or `MODE_ENUM_TYPE_MULTI` (multiple blocks separated by blank rows).

> **Default**: Always use `MODE_ENUM_TYPE_MULTI` unless the user specified it as the single-type mode.

See `references/excel/enum.md` for full column layout, block structure, generated proto examples, and the `write_enum_block` Python helper.

## Struct & Union Types

**Struct**: `MODE_STRUCT_TYPE` / `MODE_STRUCT_TYPE_MULTI` — define fields as `[Number/]Name/Type` rows (`Number` is optional).

**Union** (tagged oneof): `MODE_UNION_TYPE` / `MODE_UNION_TYPE_MULTI`

> **Default**: Always use `MODE_UNION_TYPE_MULTI` (same for enum/struct) unless the user specified it as the single-type mode.

See `references/excel/struct.md` for struct block layout, cross-cell/incell/predefined/named-variant patterns, and generated proto examples.

See `references/excel/union.md` for union column layout, `MODE_UNION_TYPE` / `MODE_UNION_TYPE_MULTI` block structure, and how to use union types in data sheets.

## Merge & Scatter

See `references/metasheet.md` → **Merger** and **Scatter** sections for full details and examples.

## Input Formats

All four formats produce identical output. Choose based on your workflow. All formats accepted by default; to restrict, set `proto.input.formats` and `conf.input.formats` in config.yaml (e.g., `formats: [xml]` for XML-only).

| Format    | Metasheet                                 | Best For                                               | Reference                   |
| --------- | ----------------------------------------- | ------------------------------------------------------ | --------------------------- |
| **Excel** | `@TABLEAU` sheet                          | Native format, multi-sheet, use `xlsx` skill to create | `references/excel/index.md` |
| **CSV**   | `BookName#@TABLEAU.csv`                   | Programmatic generation, version control               | `references/csv/index.md`   |
| **XML**   | `<!--<@TABLEAU>...</@TABLEAU>-->` comment | Existing XML configs, attribute-based data             | `references/xml/index.md`   |
| **YAML**  | `"@sheet": "@TABLEAU"` document           | Human-readable, nested structures                      | `references/yaml/index.md`  |

## Empty & Optional Value Handling

| Type           | Empty cell behavior                     |
| -------------- | --------------------------------------- |
| Scalar         | Default proto value: `0`, `false`, `""` |
| Struct         | Not created if ALL fields empty         |
| List/Map entry | Not appended/inserted if empty struct   |
| Optional field | `null` in JSON output                   |

## Nesting

See `references/excel/nesting.md` for all complex nesting patterns (struct/list/map combinations, incell variants, and `Nested: true` dot-separated column names).

### Diagnosing E2016

E2016 fires when a horizontal list has a gap between filled slots. Diagnose intent first:

| Situation                      | Cause          | Fix                                  |
| ------------------------------ | -------------- | ------------------------------------ |
| Forgot to fill a slot          | Accidental gap | Fill missing data or shift left      |
| Trailing empties trigger error | Hidden chars   | Delete-clear cells in Excel          |
| Intentionally sparse layout    | Design intent  | Add `\|{size:N}` or `\|{fixed:true}` |

## Reference Files

### Input Format References (by format)

- `references/excel/index.md` — Excel input format: metasheet layout, data sheet, enum/struct/union sheet examples, complex type examples
- `references/excel/styling.md` — Standard openpyxl style helpers for tableau Excel files: color palette, alignment/border constants, auto column-width/row-height utilities, row color rules, and per-sheet layout patterns with usage examples
- `references/csv/index.md` — CSV input format: workbook/worksheet naming, metasheet, enum/struct/union sheet examples, complex type examples
- `references/xml/index.md` — XML input format: metasheet comment block, attribute vs element patterns, complete examples
- `references/yaml/index.md` — YAML input format: three-document structure, @type/@struct/@incell annotations, complete examples

### General References

- `references/metasheet.md` — All `@TABLEAU` options with examples
- `references/config.md` — Full `config.yaml` reference
- `references/protoconf.md` — Protoconf annotation reference
- `references/types.md` — Deep dive into type syntax
