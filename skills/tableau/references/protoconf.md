# Protoconf Annotation Reference

Protoconf is tableau's dialect of proto3, extended with custom options. These options encode the spreadsheet binding so confgen knows how to parse each workbook and worksheet.

## File-Level: `(tableau.workbook)`

```protobuf
option (tableau.workbook) = {
  name: "HelloWorld.xlsx"   // Relative path of the source workbook
  namerow: 1                // Override global namerow
  typerow: 2                // Override global typerow
  noterow: 3                // Override global noterow
  datarow: 4                // Override global datarow
};
```

## Message-Level: `(tableau.worksheet)`

```protobuf
message ItemConf {
  option (tableau.worksheet) = {
    name: "ItemConf"         // Sheet name in the workbook
    namerow: 1               // Per-sheet header overrides
    typerow: 2
    noterow: 3
    datarow: 4
    transpose: false         // Swap rows <-> columns
    nested: false            // Use dot-separated column prefixes for nesting
    merger: ""               // Glob/list of workbooks to merge
    scatter: ""              // Glob/list for scatter output
    adjacent_key: false      // Carry-down key cells
    field_presence: false    // Use `optional` on all basic fields
    optional: false          // All fields may be absent
    patch: PATCH_NONE        // Sheet-level patch type
    ordered_map: false       // Generate OrderedMap accessor
    index: ""                // Index accessor spec
    ordered_index: ""        // OrderedIndex accessor spec
  };

  // fields...
}
```

## Message-Level: Custom Type Definitions

### Struct type defined in a sheet
```protobuf
message Item {
  option (tableau.struct) = {name:"Item" note:"Optional note"};
  // fields...
}
```

### Union type defined in a sheet
```protobuf
message Target {
  option (tableau.union) = {name:"Target"};
  // fields + oneof...
}
```

### Enum type (for MODE_ENUM_TYPE_MULTI)
```protobuf
enum CatType {
  option (tableau.etype) = {name:"EnumType" note:"CatType note"};
  CAT_TYPE_INVALID = 0;
  CAT_TYPE_RAGDOLL = 1 [(tableau.evalue).name = "Ragdoll"];
}
```

## Field-Level: `(tableau.field)`

```protobuf
// Scalar
uint32 id = 1 [(tableau.field) = {name:"ID"}];

// Vertical map (default for struct map)
map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];

// Horizontal map
map<uint32, Item> item_map = 1 [(tableau.field) = {name:"Item" key:"ID" layout:LAYOUT_HORIZONTAL}];

// Incell map
map<uint32, string> item_map = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_INCELL}];

// Horizontal list
repeated Item item_list = 1 [(tableau.field) = {name:"Item" layout:LAYOUT_HORIZONTAL}];

// Vertical list
repeated Item item_list = 1 [(tableau.field) = {layout:LAYOUT_VERTICAL}];

// Incell list
repeated int32 param_list = 1 [(tableau.field) = {name:"Param" layout:LAYOUT_INCELL}];

// Incell struct
Property prop = 2 [(tableau.field) = {name:"Prop" span:SPAN_INNER_CELL}];

// With field properties
repeated Item item_list = 1 [(tableau.field) = {
  name: "Item"
  layout: LAYOUT_HORIZONTAL
  prop: {
    fixed: true
    size: 5
    range: "1,100"
    refer: "ItemConf.ID"
    sequence: 1
    default: "0"
    form: FORM_JSON
    json_name: "customField"
    present: true
    optional: true
    patch: PATCH_MERGE
    sep: "|"
    subsep: ";"
    pattern: "255.255.255"
    unique: true
    cross: 2
  }
}];
```

## Layout Enum

| Value | Meaning |
|-------|---------|
| `LAYOUT_DEFAULT` | Auto-detect (incell for scalars, vertical for structs in maps, horizontal for structs in lists) |
| `LAYOUT_VERTICAL` | Each item = one row |
| `LAYOUT_HORIZONTAL` | Each item = one column group (requires digit suffix on column names) |
| `LAYOUT_INCELL` | All items in one cell (comma-separated) |

## Span Enum

| Value | Meaning |
|-------|---------|
| `SPAN_DEFAULT` | Auto (cross-cell for struct, inner for scalar) |
| `SPAN_CROSS_CELL` | Data spans multiple cells |
| `SPAN_INNER_CELL` | Data is entirely in one cell (incell struct) |

## Form Enum

| Value | Meaning |
|-------|---------|
| `FORM_TEXT` | Cell contains protobuf text format |
| `FORM_JSON` | Cell contains JSON format |

Example in typerow: `{.Transform}|{form:FORM_JSON}` or `{.Transform}|{form:FORM_TEXT}`

Cell data examples:
- FORM_JSON: `{"id": 1, "name": "Apple"}`
- FORM_TEXT: `id:1 name:"Apple"`

## Enum Value Annotation

```protobuf
enum FruitType {
  FRUIT_TYPE_INVALID = 0;
  FRUIT_TYPE_APPLE   = 1 [(tableau.evalue).name = "Apple"];   // alias "Apple" in cell
  FRUIT_TYPE_ORANGE  = 2 [(tableau.evalue) = {name:"Orange"}];
}
```

The alias allows using `Apple` (instead of `FRUIT_TYPE_APPLE` or `1`) in spreadsheet cells.

## Oneof Annotation (union)

```protobuf
message Target {
  option (tableau.union) = {name:"Target"};

  Type type = 9999 [(tableau.field) = {name:"Type"}];
  oneof value {
    option (tableau.oneof) = {field:"Field"};
    Pvp   pvp   = 1;
    Pve   pve   = 2;
    Story story = 3;
  }
  enum Type {
    TYPE_NIL   = 0;
    TYPE_PVP   = 1 [(tableau.evalue) = {name:"PVP"}];
    TYPE_PVE   = 2 [(tableau.evalue) = {name:"PVE"}];
    TYPE_STORY = 3 [(tableau.evalue) = {name:"Story"}];
  }
  message Pvp   { ... }
  message Pve   { ... }
  message Story { ... }
}
```

## Complete Protoconf Example

```protobuf
syntax = "proto3";
package protoconf;

import "tableau/protobuf/tableau.proto";
import "common.proto";   // contains predefined types

option go_package = "github.com/myorg/proto";
option (tableau.workbook) = {name:"HelloWorld.xlsx"};

message ItemConf {
  option (tableau.worksheet) = {name:"ItemConf" ordered_map:true};

  map<uint32, Item> item_map = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];

  message Item {
    uint32 id   = 1 [(tableau.field) = {name:"ID"}];
    string name = 2 [(tableau.field) = {name:"Name"}];
    string desc = 3 [(tableau.field) = {name:"Desc"}];
    FruitType fruit = 4 [(tableau.field) = {name:"Fruit"}];
    repeated int32 params = 5 [(tableau.field) = {name:"Param" layout:LAYOUT_INCELL}];
  }
}

message HeroConf {
  option (tableau.worksheet) = {name:"HeroConf" transpose:true};
  uint32 id    = 1 [(tableau.field) = {name:"ID"}];
  string name  = 2 [(tableau.field) = {name:"Name"}];
}

enum FruitType {
  FRUIT_TYPE_INVALID = 0;
  FRUIT_TYPE_APPLE   = 1 [(tableau.evalue).name = "Apple"];
  FRUIT_TYPE_ORANGE  = 2 [(tableau.evalue).name = "Orange"];
}
```

## Field Number Stability

By default tableau auto-assigns proto field numbers. Enable `preserveFieldNumbers: true` in `proto.output` to keep numbers stable when the spreadsheet schema changes (adds/removes/reorders columns).

## Keyed List in Proto

```protobuf
// Scalar keyed list
repeated uint32 id_list = 1 [(tableau.field) = {name:"ID" key:"ID" layout:LAYOUT_INCELL}];

// Struct keyed list
repeated Item item_list = 1 [(tableau.field) = {key:"ID" layout:LAYOUT_VERTICAL}];
```

The `key` field on a `repeated` (not `map`) marks it as a keyed list — unique key constraint without map semantics.
