# config.yaml / options.Options Reference

> **⚠️ MUST DO FIRST**: Before running any `tableauc` command that involves both protogen and confgen, **always check whether a `config.yaml` exists** in the working directory. If it does not exist, **create it immediately** using the minimal template in the [Default `config.yaml`](#default-configyaml-for-cli-usage) section below — before invoking `tableauc`. Skipping this step causes confgen to silently produce no output because it cannot locate the generated `.proto` files.

Run `tableauc -s` to dump a full sample config to stdout.

## Top-Level Fields

```yaml
lang: en                    # BCP 47: "en" or "zh"
locationName: Local         # IANA timezone (e.g. "Asia/Shanghai", "UTC")
acronyms:                   # Custom word -> acronym mappings
  K8s: k8s                  #   PascalCase "K8sID" -> snake "k8s_id"
log:
  mode: SIMPLE              # SIMPLE or FULL (full includes file/line)
  level: INFO               # DEBUG, INFO, WARN, ERROR
  sink: CONSOLE             # CONSOLE, FILE, MULTI
  filename: ""              # Path to log file (FILE/MULTI only)
proto: ...                  # See proto section below
conf: ...                   # See conf section below
```

## `proto` Section (protogen options)

```yaml
proto:
  input:
    header:
      namerow: 1            # Row number for column names
      typerow: 2            # Row number for column types
      noterow: 3            # Row number for notes
      datarow: 4            # First data row
      nameline: 0           # Line in cell for name (0 = whole cell)
      typeline: 0           # Line in cell for type (0 = whole cell)
      noteline: 0           # Line in cell for note (0 = whole cell)
      sep: ","              # Default incell separator
      subsep: ":"           # Default incell sub-separator
    protoPaths:             # Proto import search paths
      - "."
    protoFiles:             # Glob patterns for pre-existing (predefined) proto files
      - "common.proto"
    formats:                # Filter input formats (empty = all)
      - xlsx
      - csv
    subdirs:                # Only process these subdirectory prefixes
      - "excel"
    subdirRewrites:         # Rewrite subdir paths in generated proto workbook names
      "live": "test"
    followSymlink: false    # Follow symbolic links (can cause infinite loops)
    metasheetName: "@TABLEAU"   # Override metasheet name (must start with @)
    firstPassMode: ""       # "" | "normal" | "advanced"
    messagerPattern: ""     # Regexp for validating generated message names
  output:
    subdir: ""              # Subdirectory for generated .proto files
    filenameWithSubdirPrefix: false  # Replace "/" in filename with "__"
    filenameSuffix: ""      # Append suffix to proto filenames (e.g. "_pb")
    fileOptions:            # Proto file-level options
      go_package: "github.com/myorg/myrepo/proto"
      csharp_namespace: "MyOrg.Proto"
    enumValueWithPrefix: false  # Prepend ENUM_TYPE_ prefix to enum values
    preserveFieldNumbers: false  # Keep field numbers stable on re-generation
```

### `firstPassMode`

Controls type discovery (enums/structs/unions) before the main parse pass:

| Value          | Behavior                                                     |
| -------------- | ------------------------------------------------------------ |
| `""` (default) | Scan only workbooks in the current generation call           |
| `"normal"`     | Scan all workbooks in the input directory first              |
| `"advanced"`   | Reuse previously generated `.proto` files for type discovery |

Use `"advanced"` when predefined types are spread across many workbooks and you want them all discoverable without regenerating everything.

### `preserveFieldNumbers`

When enabled, proto field numbers are kept stable across re-generations. This is important for binary format compatibility when the spreadsheet schema changes (adds/removes/reorders columns).

### `subdirRewrites`

Rewrites subdirectory paths in generated proto workbook names. Useful when you want to map live data paths to test paths:
```yaml
subdirRewrites:
  "live": "test"    # live/ItemConf.xlsx -> test/ItemConf.xlsx in proto
```

## `conf` Section (confgen options)

```yaml
conf:
  input:
    protoPaths:             # Proto import search paths
      - "."
    protoFiles:             # Glob patterns for proto files to load
      - "*.proto"
    excludedProtoFiles:     # Glob patterns to exclude
      - "common.proto"
    formats:                # Filter source data formats (empty = all)
      - xlsx
    subdirs:                # Only process workbooks under these subdirs
      - "excel"
    subdirRewrites:
      "live": "test"
    ignoreUnknownWorkbook: false  # Don't error if workbook not found
  output:
    subdir: ""              # Subdirectory for generated config files
    formats:                # Output formats (can enable multiple)
      - json
      # - binpb
      # - txtpb
    messagerFormats:        # Per-messager format overrides
      ItemConf: [json, binpb]
    pretty: true            # Multiline + indented output
    emitUnpopulated: false  # Emit zero-value fields in JSON
    emitTimezones: false    # Include timezone offset in timestamp strings
    useProtoNames: false    # Use snake_case keys (false = lowerCamelCase)
    useEnumNumbers: false   # Emit enum values as integers (false = string names)
    dryRun: ""              # "" | "patch" (preview scatter/patch merges)
```

### Output Format Details

| Format  | File Extension | Description                    |
| ------- | -------------- | ------------------------------ |
| `json`  | `.json`        | JSON format (most common)      |
| `txtpb` | `.txtpb`       | Protocol Buffers text format   |
| `binpb` | `.binpb`       | Protocol Buffers binary format |

### `messagerFormats`

Override output formats for specific messages:
```yaml
messagerFormats:
  ItemConf: [json, binpb]     # ItemConf gets both JSON and binary
  HeroConf: [txtpb]           # HeroConf only gets text proto
```

### `emitUnpopulated`

When `true`, zero-value scalar fields appear in JSON output. Default `false` omits them for cleaner output.

### `useProtoNames`

When `true`, JSON keys use `snake_case` proto field names. When `false` (default), uses `lowerCamelCase`.

## Default `config.yaml` for CLI Usage

When no `--config` / `-c` flag is provided, `tableauc` uses built-in defaults
(see `tableauc -s`). If you need to customise behaviour — especially to make
`confgen` find the `.proto` files that `protogen` just wrote — create a
`config.yaml` in the project root.

### Minimal default config (two-step workflow)

The most common pattern is:

1. **protogen** reads workbooks from the CWD, writes `.proto` to `<CWD>/output/proto/`.
2. **confgen** reads those `.proto` files from `<CWD>/output/proto/`, reads workbooks
   from the CWD, writes JSON to `<CWD>/output/conf/`.

```yaml
lang: en
log:
  mode: SIMPLE
  level: INFO
  sink: CONSOLE

proto:
  input:
    protoPaths:
      - "."          # search path for imported .proto files
  output:
    subdir: "output/proto"  # proto files are written to <CWD>/output/proto/

conf:
  input:
    protoPaths:
      - "output/proto"    # must match proto.output.subdir
    protoFiles:
      - "output/proto/*.proto"   # glob to pick up all generated protos
  output:
    subdir: "output/conf"   # JSON files are written to <CWD>/output/conf/
    formats:
      - json
    pretty: true
```

> **Why `conf.input.protoPaths: ["./output/proto"]`?**
> `protoPaths` is resolved relative to the CWD. It must match
> `proto.output.subdir` so confgen can find the `.proto` files that protogen wrote.

### Invocation with this config

```bash
# Step 1 – generate .proto files (written to ./output/proto/)
tableauc -c config.yaml -m proto

# Step 2 – generate JSON config files (written to ./output/conf/)
tableauc -c config.yaml -m conf

# Or both in one shot (default mode)
tableauc -c config.yaml
```

### When to auto-generate this file

**Always** create `config.yaml` before running `tableauc` if it does not already exist and the task involves both protogen and confgen. Place it in the same directory from which `tableauc` is invoked.
