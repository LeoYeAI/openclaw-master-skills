# YAML Input Format Reference

YAML files use a multi-document structure with `---` separators. A single `.yaml` file contains up to three sections: metasheet, schema, and data.

## Three-Part Document Structure

```yaml
# Part 1: Metasheet (configures sheet options)
"@sheet": "@TABLEAU"
---
# Part 2: Schema (defines types — the "@" prefix on sheet name marks this as schema)
"@sheet": "@YamlItemConf"
ID: uint32
Name: string
---
# Part 3: Data (actual values — no "@" prefix)
"@sheet": YamlItemConf
ID: 1
Name: Apple
```

- **`"@sheet": "@TABLEAU"`** — metasheet document (optional; if absent, all sheets processed with defaults)
- **`"@sheet": "@SheetName"`** — schema document (type definitions, `@` prefix)
- **`"@sheet": SheetName`** — data document (actual values, no `@` prefix)

## Metasheet Configuration

```yaml
"@sheet": "@TABLEAU"
"YamlItemConf":
  OrderedMap: true
  Alias: ItemAlias
"YamlHeroConf":
  Transpose: true
"YamlEnumConf":
  Mode: MODE_ENUM_TYPE
"YamlMergerConf":
  Merger: "Merger*.yaml"
"YamlPatchConf":
  Patch: PATCH_MERGE
  Optional: true
  FieldPresence: true
  Scatter: "../overlays/*/Env.yaml"
  ScatterWithoutBookName: true
  WithParentDir: true
```

All standard metasheet options are supported as YAML keys under each sheet name.

## Type Annotations

YAML uses special `@`-prefixed keys to define types:

| Annotation  | Purpose                     | Example                                 |
| ----------- | --------------------------- | --------------------------------------- |
| `"@type"`   | Declare type of a field     | `"@type": "[Item]"`                     |
| `"@struct"` | Define struct fields inline | `"@struct": {ID: uint32, Name: string}` |
| `"@incell"` | Mark as incell layout       | `"@incell": true`                       |
| `"@key"`    | Custom map key field name   | `"@key": CustomKey`                     |

## Scalar Types

```yaml
# Schema
"@sheet": "@ItemConf"
ID: uint32
Num: int32
Value: uint64
Weight: int64
Percentage: float
Ratio: double
Name: string
Blob: bytes
OK: bool
---
# Data
"@sheet": ItemConf
ID: 1
Num: 10
Value: 20
Weight: 30
Percentage: 0.5
Ratio: 3.14159
Name: apple
Blob: "VGFibGVhdQ=="   # base64 of "Tableau"
OK: true
```

## Enum Types

```yaml
# Schema
"@sheet": "@ItemConf"
ID: uint32
Type: "enum<.FruitType>"
Desc: string
---
# Data
"@sheet": ItemConf
ID: 1
Type: FRUIT_TYPE_APPLE
Desc: A kind of delicious fruit.
```

Enum values use full constant names (`FRUIT_TYPE_APPLE`) or aliases (`Apple`).

## Struct Types

### General struct (`@type` + `@struct`)

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "[Item]"
  "@struct":
    ID: uint32
    Name: string
---
# Data
"@sheet": ItemConf
Items:
  - ID: 1
    Name: apple
  - ID: 2
    Name: orange
```

### General struct (`@type` + inline fields)

When fields are mixed directly with `@type`, no `@struct` wrapper needed:

```yaml
# Schema
"@sheet": "@ItemConf"
Item:
  "@type": "{Item}"
  ID: uint32
  StartTime: datetime
  Expiry: duration
---
# Data
"@sheet": ItemConf
Item:
  ID: 1
  StartTime: 2024-10-01 10:10:10
  Expiry: 1h
```

### Reuse same-level struct

Reference a previously defined struct by name:

```yaml
# Schema
"@sheet": "@ItemConf"
Item:
  "@type": "{Item}"
  ID: uint32
  StartTime: datetime
  Expiry: duration
NewItem: "{Item}"   # reuses the Item struct defined above
---
# Data
"@sheet": ItemConf
Item:
  ID: 1
  StartTime: 2024-10-01 10:10:10
  Expiry: 1h
NewItem:
  ID: 2
  StartTime: 2026-10-01 10:10:10
  Expiry: 2h
```

### Predefined struct (external)

Dot prefix for imported types from *common.proto*:

```yaml
# Schema
"@sheet": "@ItemConf"
Item: "{.Item}"
---
# Data
"@sheet": ItemConf
Item:
  ID: 1
  Num: 10
```

### Incell struct (inline syntax)

```yaml
# Schema
"@sheet": "@ItemConf"
Item: "{uint32 ID, int32 Num}Item"
---
# Data
"@sheet": ItemConf
Item: "1, 10"
```

### Incell struct (`@type` + `@incell`)

```yaml
# Schema
"@sheet": "@ItemConf"
Item:
  "@type": "{Item}"
  "@incell": true
  ID: uint32
  Num: int32
---
# Data
"@sheet": ItemConf
Item: "1, 10"
```

### Incell predefined struct

```yaml
# Schema
"@sheet": "@ItemConf"
Item:
  "@type": "{.Item}"
  "@incell": true
---
# Data
"@sheet": ItemConf
Item: "1, 10"
```

## List Types

### Scalar list

```yaml
# Schema
"@sheet": "@ItemConf"
Items: "[int32]"
---
# Data
"@sheet": ItemConf
Items: [1, 2, 3]
```

### Enum list

```yaml
# Schema
"@sheet": "@ItemConf"
Fruits: "[enum<.FruitType>]"
---
# Data
"@sheet": ItemConf
Fruits: [FRUIT_TYPE_APPLE, FRUIT_TYPE_ORANGE, FRUIT_TYPE_BANANA]
```

### Incell scalar list

```yaml
# Schema — method 1: shorthand syntax
"@sheet": "@ItemConf"
Items: "[]int32"

# Schema — method 2: @type + @incell
Items:
  "@type": "[int32]"
  "@incell": true
---
# Data
"@sheet": ItemConf
Items: "1, 2, 3"
```

### Incell enum list

```yaml
# Schema
"@sheet": "@ItemConf"
Fruits: "[]enum<.FruitType>"
---
# Data
"@sheet": ItemConf
Fruits: "FRUIT_TYPE_APPLE, FRUIT_TYPE_ORANGE, FRUIT_TYPE_BANANA"
```

### Struct list

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "[Item]"
  "@struct":
    ID: uint32
    Num: int32
---
# Data
"@sheet": ItemConf
Items:
  - ID: 1
    Num: 10
  - ID: 2
    Num: 20
```

### Predefined struct list

```yaml
# Schema
"@sheet": "@ItemConf"
Items: "[.Item]"
---
# Data
"@sheet": ItemConf
Items:
  - ID: 1
    Num: 10
  - ID: 2
    Num: 20
```

### List in list

```yaml
# Schema
"@sheet": "@ItemConf"
Countries:
  "@type": "[Country]"
  "@struct":
    Country: string
    Desc: string
    Items:
      "@type": "[Item]"
      "@struct":
        Name: string
        Num: int32
---
# Data
"@sheet": ItemConf
Countries:
  - Country: USA
    Desc: A country in North America.
    Items:
      - Name: apple
        Num: 10
      - Name: orange
        Num: 20
  - Country: China
    Desc: A country in East Asia.
    Items:
      - Name: apple
        Num: 100
      - Name: orange
        Num: 200
```

### Map in list

```yaml
# Schema
"@sheet": "@ItemConf"
Countries:
  "@type": "[Country]"
  "@struct":
    Country: string
    Desc: string
    Items:
      "@type": "map<string, Item>"
      "@struct":
        "@key": Name
        Num: int32
---
# Data
"@sheet": ItemConf
Countries:
  - Country: USA
    Desc: A country in North America.
    Items:
      apple:
        Num: 10
      orange:
        Num: 20
  - Country: China
    Desc: A country in East Asia.
    Items:
      apple:
        Num: 100
      orange:
        Num: 200
```

## Map Types

### Scalar map

```yaml
# Schema
"@sheet": "@ItemConf"
Items: "map<uint32, string>"
---
# Data
"@sheet": ItemConf
Items:
  1: dog
  2: bird
  3: cat
```

### Enum key map

```yaml
# Schema
"@sheet": "@ItemConf"
Items: "map<enum<.FruitType>, string>"
---
# Data
"@sheet": ItemConf
Items:
  FRUIT_TYPE_APPLE: apple
  FRUIT_TYPE_ORANGE: orange
  FRUIT_TYPE_BANANA: banana
```

### Enum key-value map

```yaml
# Schema
"@sheet": "@ItemConf"
Items: "map<enum<.FruitType>, enum<.FruitFlavor>>"
---
# Data
"@sheet": ItemConf
Items:
  FRUIT_TYPE_APPLE: FRUIT_FLAVOR_FRAGRANT
  FRUIT_TYPE_ORANGE: FRUIT_FLAVOR_SOUR
  FRUIT_TYPE_BANANA: FRUIT_FLAVOR_SWEET
```

### Incell scalar map

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "map<uint32, string>"
  "@incell": true
---
# Data
"@sheet": ItemConf
Items: "1:dog,2:bird,3:cat"
```

### Incell enum map

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "map<enum<.FruitType>, enum<.FruitFlavor>>"
  "@struct": CustomMapValue
  "@incell": true
---
# Data
"@sheet": ItemConf
Items: "FRUIT_TYPE_APPLE:FRUIT_FLAVOR_FRAGRANT, FRUIT_TYPE_ORANGE:FRUIT_FLAVOR_SOUR"
```

### Struct map

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "map<uint32, Item>"
  "@struct":
    Name: string
    Num: int32
---
# Data
"@sheet": ItemConf
Items:
  1:
    Name: apple
    Num: 10
  2:
    Name: orange
    Num: 20
  3:
    Name: banana
    Num: 30
```

### Enum key struct map

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "map<enum<.FruitType>, EnumItem>"
  "@struct":
    Name: string
    Num: int32
---
# Data
"@sheet": ItemConf
Items:
  FRUIT_TYPE_APPLE:
    Name: apple
    Num: 10
  FRUIT_TYPE_ORANGE:
    Name: orange
    Num: 20
  FRUIT_TYPE_BANANA:
    Name: banana
    Num: 30
```

### Custom key struct map

```yaml
# Schema
"@sheet": "@ItemConf"
Items:
  "@type": "map<uint32, Item>"
  "@struct":
    "@key": CustomKey   # custom key field name
    Name: string
    Num: int32
---
# Data
"@sheet": ItemConf
Items:
  1:
    Name: apple
    Num: 10
  2:
    Name: orange
    Num: 20
```

### List in map

```yaml
# Schema
"@sheet": "@ItemConf"
Countries:
  "@type": "map<string, Country>"
  "@struct":
    Desc: string
    Items:
      "@type": "[Item]"
      "@struct":
        Name: string
        Num: int32
---
# Data
"@sheet": ItemConf
Countries:
  USA:
    Desc: A country in North America.
    Items:
      - Name: apple
        Num: 10
      - Name: orange
        Num: 20
  China:
    Desc: A country in East Asia.
    Items:
      - Name: apple
        Num: 100
      - Name: orange
        Num: 200
```

### Map in map

```yaml
# Schema
"@sheet": "@ItemConf"
Countries:
  "@type": "map<string, Country>"
  "@struct":
    Desc: string
    Items:
      "@type": "map<string, Item>"
      "@struct":
        "@key": Name
        Num: int32
---
# Data
"@sheet": ItemConf
Countries:
  USA:
    Desc: A country in North America.
    Items:
      apple:
        Num: 10
      orange:
        Num: 20
  China:
    Desc: A country in East Asia.
    Items:
      apple:
        Num: 100
      orange:
        Num: 200
```

## Union Types

### Predefined union (cross-cell)

```yaml
# Schema
"@sheet": "@ItemConf"
Target: "{.Target}"
---
# Data
"@sheet": ItemConf
Target:
  Type: PVP
  Field1: 1
  Field2: 10
  Field3: "Apple,Orange,Banana"
```

### Predefined union (incell text form)

Use `|{form:FORM_TEXT}` for protobuf text format encoding:

```yaml
# Schema
"@sheet": "@ItemConf"
Target:
  "@type": "{.Target}|{form:FORM_TEXT}"
  "@incell": true
---
# Data
"@sheet": ItemConf
Target: "type:TYPE_PVE pve:{mission:{id:1 level:100 damage:999} heros:1 heros:2 heros:3 dungeons:{key:1 value:10} dungeons:{key:2 value:20} dungeons:{key:3 value:30}}"
```

### Predefined union list

```yaml
# Schema
"@sheet": "@ItemConf"
Targets: "[.Target]"
---
# Data
"@sheet": ItemConf
Targets:
  - Type: Story
    Field1: "1001,10"
    Field2: "1:Apple,2:Orange"
    Field3: "Fragrant:1,Sour:2"
  - Type: Skill
    Field1: 1
    Field2: 2
```

- Union reference uses `{.TypeName}` syntax: `"{.Target}"`
- Incell union uses protobuf text format with `|{form:FORM_TEXT}`
- Data fields mapped to `Field1`, `Field2`, etc. (matching the union's `oneof` field binding)

## Field Properties

Append `|{...}` to type strings:

```yaml
# Schema
"@sheet": "@ItemConf"
ID: uint32
Name: "string|{unique:true}"
Num: "int32|{optional:true}"
Items:
  "@type": "map<uint32, Item>|{unique:true}"
  "@struct":
    Name: "string|{unique:true}"
ScalarList: "[int32]|{patch:PATCH_REPLACE}"
```

## Optional Fields

```yaml
# Schema
"@sheet": "@ItemConf"
ID: uint32
Num: "int32|{optional:true}"
Type: "enum<.FruitType>|{optional:true}"
OptionalStruct:
  "@type": "{Struct}|{optional:true}"
  Type: string
  Price: int32
---
# Data — optional fields simply omitted
"@sheet": ItemConf
ID: 1
# Num and Type omitted — will be null in JSON output
```

## Merger

```yaml
# Main file metasheet
"@sheet": "@TABLEAU"
"YamlMergerConf":
  Merger: "Merger*.yaml"
---
# Schema + base data in main file
"@sheet": "@YamlMergerConf"
StructMap:
  "@type": "map<uint32, Item>"
  "@struct":
    Name: string
    Num: int32
---
"@sheet": YamlMergerConf
StructMap:
  100:
    Name: apple
    Num: 1000
```

Matched files (Merger1.yaml, Merger2.yaml) contain data only:

```yaml
# Merger1.yaml
"@sheet": YamlMergerConf
StructMap:
  1:
    Name: orange
    Num: 10
```

## Patch/Overlay

```yaml
# Base file
"@sheet": "@TABLEAU"
"YamlPatchConf":
  Patch: PATCH_MERGE
  Scatter: "../overlays/*/Env.yaml"
  ScatterWithoutBookName: true
  WithParentDir: true
---
"@sheet": "@YamlPatchConf"
Env: "string"
ScalarList: "[int32]|{patch:PATCH_REPLACE}"
StructMap:
  "@type": "map<uint32, Item>"
  "@struct":
    Name: string
    Num: int32
---
"@sheet": YamlPatchConf
Env: base
ScalarList: [1, 2, 3]
StructMap:
  1: {Name: apple, Num: 10}
```

Overlay files:

```yaml
# overlays/dev/Env.yaml
"@sheet": YamlPatchConf
Env: dev

# overlays/prod/Env.yaml
"@sheet": YamlPatchConf
Env: prod
StructMap:
  1: {Num: 100}           # merges with base
  20: {Name: pineapple, Num: 200}  # new entry

# overlays/test/Env.yaml
"@sheet": YamlPatchConf
Env: test
ScalarList: [10, 20, 30]   # replaces (PATCH_REPLACE on this field)
```

## Key Rules

1. **Three-document structure**: metasheet (`@TABLEAU`) → schema (`@SheetName`) → data (`SheetName`)
2. **`@` prefix distinguishes schema from data**: `"@sheet": "@YamlConf"` is schema, `"@sheet": YamlConf` is data
3. **Type annotations use `@` keys**: `@type`, `@struct`, `@incell`, `@key`
4. **YAML native types for data**: lists use `[...]` or `- item`, maps use `key: value`
5. **Incell data is always a quoted string**: `"1, 2, 3"` or `"1:dog,2:cat"`
6. **Union reference syntax**: `"{.TypeName}"` (dot prefix for predefined types)
7. **Comments supported**: use `#` for inline documentation
8. **Multi-file**: merger/scatter patterns work the same as Excel/CSV/XML
