# Type System Deep Dive

This document covers all composite and special types in tableau's **typerow syntax** — format-agnostic (applies to Excel, CSV, XML, and YAML equally).

For how to *define* types and lay out columns (enum/struct/union/list/map/nesting) in each input format, see the per-format references:
- Excel: [`excel/index.md`](excel/index.md)
- CSV: [`csv/index.md`](csv/index.md)
- XML: [`xml/index.md`](xml/index.md)
- YAML: [`yaml/index.md`](yaml/index.md)

## Table of Contents

**Basic Types**
- [Scalar Types](#scalar-types)
- [Enum Types](#enum-types)
- [Struct Types](#struct-types)

**Collection Types**
- [List Types](#list-types)
- [Keyed List](#keyed-list)
- [Map Types](#map-types)

**Advanced Types**
- [Union Types](#union-types)
- [Well-Known Types](#well-known-types)
- [Predefined Types](#predefined-types)

**Patterns & Behavior**
- [Nesting Patterns](#nesting-patterns)
- [Empty Value Handling](#empty-value-handling)

---

## Scalar Types

All proto3 scalars are supported directly in the typerow:

| Typerow                         | Proto  | JSON    | Notes                             |
| ------------------------------- | ------ | ------- | --------------------------------- |
| `int32` / `sint32` / `sfixed32` | int32  | number  | Signed 32-bit                     |
| `uint32` / `fixed32`            | uint32 | number  | Unsigned 32-bit                   |
| `int64` / `sint64` / `sfixed64` | int64  | string  | Signed 64-bit (JSON as string)    |
| `uint64` / `fixed64`            | uint64 | string  | Unsigned 64-bit (JSON as string)  |
| `float`                         | float  | number  | 32-bit float                      |
| `double`                        | double | number  | 64-bit float                      |
| `bool`                          | bool   | boolean | `true`/`false` or `1`/`0` in cell |
| `string`                        | string | string  | UTF-8                             |
| `bytes`                         | bytes  | string  | Base64 in JSON                    |

---

## Enum Types

Reference an enum in typerow with `enum<.FruitType>` (dot = predefined/imported). Three accepted cell value forms: numeric (`1`), full name (`FRUIT_TYPE_APPLE`), alias (`Apple`). Works in lists (`[]enum<.FruitType>`) and maps (`map<enum<.FruitType>, int32>`).

For how to define enum types in Excel sheets (`MODE_ENUM_TYPE` / `MODE_ENUM_TYPE_MULTI`), see [`excel/enum.md`](excel/enum.md).

---

## Struct Types

### Typerow syntax variants
| Typerow                           | Description                                      |
| --------------------------------- | ------------------------------------------------ |
| `{Property}int32`                 | Cross-cell struct (columns prefixed by var name) |
| `{int32 ID, string Name}Property` | Incell struct (all fields in one cell)           |
| `.Item`                           | Predefined struct (dot = imported)               |
| `{Item(RewardItem)}int32`         | Named variant (type `Item`, var `RewardItem`)    |
| `{.Item(PredefinedItem)}int32`    | Predefined named variant                         |
| `{.Transform}\|{form:FORM_JSON}`  | Incell struct with JSON/text form                |

For layout-specific details (cross-cell, incell, predefined, nested, `MODE_STRUCT_TYPE` / `MODE_STRUCT_TYPE_MULTI`), see [`excel/struct.md`](excel/struct.md).

---

## List Types

### Scalar list variants
| Typerow              | Cell data          | Description       |
| -------------------- | ------------------ | ----------------- |
| `[]int32`            | `1,2,3`            | Scalar list       |
| `[]enum<.FruitType>` | `Apple,Orange`     | Enum list         |
| `[]<uint32>`         | _(see Keyed List)_ | Keyed scalar list |

### Struct list variants
| Typerow                       | Description                   |
| ----------------------------- | ----------------------------- |
| `[Item]uint32`                | Cross-cell struct list        |
| `[.Item]uint32`               | Predefined struct list        |
| `[]{int32 ID, int32 Num}Item` | Incell struct list            |
| `[]{.Item}`                   | Incell predefined struct list |

For layout-specific details (horizontal, vertical, incell, fixed-size, custom separator), see [`excel/list.md`](excel/list.md).

---

## Map Types

### Map type variants
| Typerow                        | Description                                |
| ------------------------------ | ------------------------------------------ |
| `map<uint32, Item>`            | Struct value map                           |
| `map<uint32, .Item>`           | Predefined struct value map                |
| `map<uint32, string>`          | Scalar value map                           |
| `map<enum<.FruitType>, int32>` | Enum-keyed map (proto uses `int32` as key) |

**Enum-keyed map note**: Protobuf doesn't allow enum map keys directly. Tableau generates `map<int32, …>` in proto but keeps the enum type as the first field of the value struct for bookkeeping.

> ⚠️ **Tableau does NOT support nested map syntax in a single typerow cell.** Never write `map<uint32, map<int32, Item>>` in one cell — this is invalid. Each map level must be declared on its own key column.

For layout-specific details (vertical, horizontal, incell, fixed-size, custom separator, nested map-in-map), see [`excel/map.md`](excel/map.md).

---

## Keyed List

A list where the first field serves as a unique key (but stays as `repeated`, not `map`). Syntax uses angle brackets around the key type: `[Item]<uint32>`, `[]<enum<.E>>`, etc.

For layout-specific details (vertical, incell, keyed list vs map comparison), see [`excel/keyedlist.md`](excel/keyedlist.md).

---

## Union Types

A tagged union (discriminated variant type). One field determines which message type is present.

Typerow for referencing a union in a data sheet: `{.Target}enum<.Target.Type>` (type column) + `union` keyword (payload columns).

For how to define union types (`MODE_UNION_TYPE` / `MODE_UNION_TYPE_MULTI`) and use them in data sheets, see [`excel/union.md`](excel/union.md).

---

## Well-Known Types

| Typerow      | Cell format examples                       | Proto backing               |
| ------------ | ------------------------------------------ | --------------------------- |
| `datetime`   | `2023-01-01 12:00:00` / RFC3339            | `google.protobuf.Timestamp` |
| `date`       | `2023-01-01` / `20230101`                  | `google.protobuf.Timestamp` |
| `time`       | `12:30:00` / `1025` / `10:25`              | `google.protobuf.Duration`  |
| `duration`   | `72h3m0.5s` (Go format)                    | `google.protobuf.Duration`  |
| `fraction`   | `10%`, `3/4`, `0.01`                       | `tableau.Fraction`          |
| `comparator` | `==10`, `<10%`, `>=10‱`                    | `tableau.Comparator`        |
| `version`    | `1.0.3` / `version\|{pattern:"99.999.99"}` | `tableau.Version`           |

All well-known types work in lists and maps: `[]date`, `map<uint32, duration>`, `[]version|{pattern:"..."}`, etc.

For cell format details, proto backing, JSON output examples, and list/map usage, see [`excel/wellknown-types.md`](excel/wellknown-types.md).

---

## Predefined Types

Types defined in a separate proto file (e.g., `common.proto`) and referenced with a `.` prefix:

| Typerow                 | Meaning                                               |
| ----------------------- | ----------------------------------------------------- |
| `.FruitType`            | Predefined enum `FruitType`                           |
| `.Item`                 | Predefined message `Item`                             |
| `.Target`               | Predefined union `Target`                             |
| `.Item(PredefinedItem)` | Predefined `Item` with variable name `PredefinedItem` |
| `[.Item]int32`          | List of predefined struct                             |
| `map<uint32, .Item>`    | Map with predefined struct value                      |

Configure which proto files to import in `config.yaml`:
```yaml
proto:
  input:
    protoFiles:
      - "common.proto"
    protoPaths:
      - "."
```

---

## Nesting Patterns

Tableau supports deep nesting. The first field of a list/map element can itself be a complex type:

```
[Reward]{Icon}int32              # list element's first field is cross-cell struct
[Cost]{.Item}uint32              # list element's first field is predefined struct
[Magic]{int32 Id, int32 Num}Ability  # list element's first field is incell struct
[Reward][Item]uint32             # list of lists
```

> ⚠️ Tableau does **not** support nested type syntax in a single typerow cell (e.g., `map<uint32, map<string, Item>>` is invalid). Each nesting level must be declared on its own key column.

For all column layout examples (struct/list/map combinations, infinite nesting with `Nested: true`), see [`excel/nesting.md`](excel/nesting.md).

---

## Empty Value Handling

| Type            | Behavior when cell is empty                                |
| --------------- | ---------------------------------------------------------- |
| Scalar          | Default proto value: `0`, `false`, `""`                    |
| Struct          | Not created if ALL its fields are empty                    |
| List element    | Not appended if it would be an empty struct                |
| Map entry       | Not inserted if value would be an empty struct             |
| Nested          | Recursive: if all children are empty, parent is also empty |
| Optional scalar | `null` in JSON output                                      |
| Optional struct | `null` if all fields empty                                 |

### Controlling empty behavior

- `emitUnpopulated: true` in `conf.output` -> zero-value scalar fields appear in JSON output
- `present: true` field property -> error if cell is empty (forces explicit data)
- `field_presence: true` worksheet option -> use proto3 `optional` to track explicit-vs-default
