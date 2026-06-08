# XML Input Format Reference

XML files encode both the metasheet and data in a single file using XML comments and elements.

## Metasheet Format

The metasheet is an XML comment block at the top of the file, wrapped in `<@TABLEAU>...</@TABLEAU>`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
<@TABLEAU>
    <Item Sheet="Sheet1" Alias="ItemConf" OrderedMap="true" Index="(ID,Type)@Item" />
    <Item Sheet="Sheet2" Alias="FruitConf" Sep="," Subsep=":" FieldPresence="true" />
    <HeroConf Sheet="HeroConf" Transpose="true" />
    <FruitType Sheet="FruitType" Mode="MODE_ENUM_TYPE" />
    <ZoneConf Sheet="ZoneConf" Merger="Merger*.xml" />
</@TABLEAU>
-->
```

Each child element configures one worksheet. Attributes map to the same options as Excel's `@TABLEAU` sheet:

| Attribute                | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `Sheet`                  | Worksheet element name (required)                             |
| `Alias`                  | Proto message name override                                   |
| `Mode`                   | `MODE_ENUM_TYPE`, `MODE_STRUCT_TYPE`, `MODE_UNION_TYPE`, etc. |
| `Sep`                    | Incell separator (default `,`)                                |
| `Subsep`                 | Incell sub-separator (default `:`)                            |
| `Transpose`              | Swap rows/columns                                             |
| `Nested`                 | Dot-separated column naming                                   |
| `OrderedMap`             | Maintain map insertion order                                  |
| `Index`                  | Index accessor spec, e.g., `"(ID,Type)@Item"`                 |
| `FieldPresence`          | Track field presence                                          |
| `Merger`                 | Glob pattern for merging files                                |
| `Scatter`                | Glob pattern for scatter output                               |
| `ScatterWithoutBookName` | Omit book name in scatter output                              |
| `WithParentDir`          | Include parent dir in path                                    |
| `Patch`                  | `PATCH_MERGE` or `PATCH_REPLACE`                              |
| `Optional`               | Allow file to be missing                                      |
| `Template`               | Mark as Jinja2 template                                       |

If the metasheet is absent or empty, the file is ignored (no code generation).

## Type Definitions in Metasheet

Unlike Excel/CSV where types go in row 2, XML defines types **inside the metasheet comment**, after the `</@TABLEAU>` block:

```xml
<!--
<@TABLEAU>
    <Item Sheet="ItemConf" />
</@TABLEAU>

<ItemConf>
    <ID>uint32</ID>
    <Name>string</Name>
    <Desc>string</Desc>
</ItemConf>
-->
```

For struct maps and lists, use attributes on elements:

```xml
<!--
<@TABLEAU>
    <Item Sheet="MapConf" />
</@TABLEAU>

<MapConf Open="bool">
    <Entry Id="map<uint32, Entry>" Value="int32" Incell="map<int32, string>" />
    <Incell>map<int32, int32></Incell>
</MapConf>
-->
```

## Data Format — Attributes vs Elements

XML uses two patterns for encoding fields:

### Scalar Fields → XML Attributes

Simple scalar values are encoded as attributes on elements:

```xml
<Item ID="1" Name="Apple" Desc="A delicious fruit" />
```

### Complex/Repeated Fields → Child Elements

Lists, maps, and nested structs use repeated child elements:

```xml
<ItemConf>
    <Item ID="1" Name="Apple">
        <Reward ID="100" Num="10" />
        <Reward ID="200" Num="20" />
    </Item>
    <Item ID="2" Name="Orange">
        <Reward ID="300" Num="5" />
    </Item>
</ItemConf>
```

### Incell Values → Element Text Content

Incell lists, maps, and structs use element text:

```xml
<Award>3, 30</Award>                      <!-- incell struct -->
<Vector>2.7182818, 3.1415926, -1</Vector> <!-- incell list -->
<Incell>1:1,2:10,3:100</Incell>           <!-- incell map -->
```

## Scalar Sheet

All scalar types supported:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
<@TABLEAU>
    <Item Sheet="ItemConf" />
</@TABLEAU>

<ItemConf>
    <ID>uint32</ID>
    <Num>int32</Num>
    <Value>uint64</Value>
    <Weight>int64</Weight>
    <Percentage>float</Percentage>
    <Ratio>double</Ratio>
    <Name>string</Name>
    <Blob>bytes</Blob>
    <OK>bool</OK>
</ItemConf>
-->

<ItemConf>
    <ID>1</ID>
    <Num>10</Num>
    <Value>20</Value>
    <Weight>30</Weight>
    <Percentage>0.5</Percentage>
    <Ratio>3.14159</Ratio>
    <Name>apple</Name>
    <Blob>VGFibGVhdQ==</Blob> <!-- base64 of "Tableau" -->
    <OK>true</OK>
</ItemConf>
```

> Note: `bytes` fields use base64 encoding in XML data.

## Enum Sheet

Using a predefined enum type `FruitType` from *common.proto*:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
<@TABLEAU>
    <Item Sheet="ItemConf" />
</@TABLEAU>

<ItemConf>
    <ID>uint32</ID>
    <Type>enum<.FruitType></Type>
    <Desc>string</Desc>
</ItemConf>
-->

<ItemConf>
    <ID>1</ID>
    <Type>FRUIT_TYPE_APPLE</Type>
    <Desc>A kind of delicious fruit.</Desc>
</ItemConf>
```

> Note: angle brackets in type syntax must be XML-escaped (`&lt;` and `&gt;`) when used as **attribute values**. When used as **element text content** (as above), no escaping is needed.

## Struct Sheet

### General struct

Fields can be attributes or child elements:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
<@TABLEAU>
    <Item Sheet="ItemConf" />
</@TABLEAU>

<ItemConf>
    <Item ID="uint32" StartTime="datetime">
      <Expiry>duration</Expiry>
    </Item>
    <Item2 ID="{OtherItem}uint32" Name="string" />
</ItemConf>
-->

<ItemConf>
    <Item ID="1" StartTime="2024-10-01 10:10:10">
      <Expiry>1h</Expiry>
    </Item>
    <Item2 ID="1" Name="gold" />
</ItemConf>
```

### Reuse same-level struct

Use `@type="{TypeName}"` or `{TypeName}firstField` to reuse a struct type:

```xml
<!--
<ItemConf>
    <Item ID="uint32" StartTime="datetime">
      <Expiry>duration</Expiry>
    </Item>
    <NewItem @type="{Item}" />
    <OtherItem ID="{Item}uint32" StartTime="datetime">
      <Expiry>duration</Expiry>
    </OtherItem>
</ItemConf>
-->
```

All three fields (`item`, `new_item`, `other_item`) share the same `Item` message type in the generated proto.

### Predefined struct

Reference a struct from *common.proto* using `@type="{.TypeName}"` or `{.TypeName}firstField`:

```xml
<!--
<ItemConf>
    <Item @type="{.Item}" />
    <Item2 ID="{.Item}int32" Num="int32" />
</ItemConf>
-->

<ItemConf>
    <Item ID="1" Num="10" />
    <Item2 ID="2" Num="20" />
</ItemConf>
```

### Incell struct

Struct fields packed into a single element's text or attribute value:

```xml
<!--
<ItemConf Item="{uint32 ID, int32 Num}Item">
    <Item2>{uint32 ID, int32 Num}OtherItem</Item2>
</ItemConf>
-->

<ItemConf Item="2, 20">
    <Item2>1, 10</Item2>
</ItemConf>
```

### Incell predefined struct

```xml
<!--
<ItemConf Item="{.Item}">
    <Item2>{.Item}</Item2>
</ItemConf>
-->

<ItemConf Item="2, 20">
    <Item2>1, 10</Item2>
</ItemConf>
```

## List Sheet

### Scalar list (repeated elements)

Each `<Item>` element becomes one list entry:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
<@TABLEAU>
    <Item Sheet="ItemConf" />
</@TABLEAU>

<ItemConf>
    <Item>[int32]</Item>
</ItemConf>
-->

<ItemConf>
    <Item>1</Item>
    <Item>2</Item>
    <Item>3</Item>
</ItemConf>
```

### Enum list

```xml
<!--
<ItemConf>
    <Fruit>[enum<.FruitType>]</Fruit>
</ItemConf>
-->

<ItemConf>
    <Fruit>FRUIT_TYPE_APPLE</Fruit>
    <Fruit>FRUIT_TYPE_ORANGE</Fruit>
    <Fruit>FRUIT_TYPE_BANANA</Fruit>
</ItemConf>
```

### Incell scalar list

All values packed into one element's text:

```xml
<!--
<ItemConf>
    <Item>[]int32</Item>
</ItemConf>
-->

<ItemConf>
    <Item>1, 2, 3</Item>
</ItemConf>
```

### Incell enum list

```xml
<!--
<ItemConf>
    <Fruit>[]enum<.FruitType></Fruit>
</ItemConf>
-->

<ItemConf>
    <Fruit>FRUIT_TYPE_APPLE, FRUIT_TYPE_ORANGE, FRUIT_TYPE_BANANA</Fruit>
</ItemConf>
```

### Struct list

```xml
<!--
<ItemConf>
    <Item ID="[Item]uint32" Num="int32"/>
</ItemConf>
-->

<ItemConf>
    <Item ID="1" Num="10"/>
    <Item ID="2" Num="20"/>
</ItemConf>
```

### Predefined struct list

```xml
<!--
<ItemConf>
    <Item @type="[.Item]"/>
</ItemConf>
-->

<ItemConf>
    <Item ID="1" Num="10"/>
    <Item ID="2" Num="20"/>
</ItemConf>
```

### List in list

Nested repeated child elements:

```xml
<!--
<ItemConf>
    <Country Country="[Country]string" Desc="string">
        <Item Name="[Item]string" Num="int32" />
    </Country>
</ItemConf>
-->

<ItemConf>
    <Country Country="USA" Desc="A country in North America.">
        <Item Name="apple" Num="10" />
        <Item Name="orange" Num="20" />
    </Country>
    <Country Country="China" Desc="A country in East Asia.">
        <Item Name="apple" Num="100" />
        <Item Name="orange" Num="200" />
    </Country>
</ItemConf>
```

### Map in list

```xml
<!--
<ItemConf>
    <Country Country="[Country]string" Desc="string">
        <Item Name="map<string, Item>" Num="int32" />
    </Country>
</ItemConf>
-->

<ItemConf>
    <Country Country="USA" Desc="A country in North America.">
        <Item Name="apple" Num="10" />
        <Item Name="orange" Num="20" />
    </Country>
    <Country Country="China" Desc="A country in East Asia.">
        <Item Name="apple" Num="100" />
        <Item Name="orange" Num="200" />
    </Country>
</ItemConf>
```

## Map Sheet

### Incell scalar map

```xml
<!--
<ItemConf>
    <Item>map<uint32, string></Item>
</ItemConf>
-->

<ItemConf>
    <Item>1:dog,2:bird,3:cat</Item>
</ItemConf>
```

### Incell enum map

```xml
<!--
<ItemConf>
    <Item>map<enum<.FruitType>, enum<.FruitFlavor>></Item>
</ItemConf>
-->

<ItemConf>
    <Item>FRUIT_TYPE_APPLE:FRUIT_FLAVOR_FRAGRANT, FRUIT_TYPE_ORANGE:FRUIT_FLAVOR_SOUR</Item>
</ItemConf>
```

### Struct map

The key attribute carries the `map<...>` type; other attributes are value fields:

```xml
<!--
<ItemConf>
    <Item Name="map<string, Item>" Num="int32" />
</ItemConf>
-->

<ItemConf>
    <Item Name="apple" Num="10" />
    <Item Name="orange" Num="20" />
    <Item Name="banana" Num="30" />
</ItemConf>
```

### Enum key struct map

```xml
<!--
<ItemConf>
    <Item Key="map<enum<.FruitType>, EnumItem>" Name="string" Num="int32" />
</ItemConf>
-->

<ItemConf>
    <Item Key="FRUIT_TYPE_APPLE" Name="apple" Num="10" />
    <Item Key="FRUIT_TYPE_ORANGE" Name="orange" Num="20" />
    <Item Key="FRUIT_TYPE_BANANA" Name="banana" Num="30" />
</ItemConf>
```

### List in map

```xml
<!--
<ItemConf>
    <Country Key="map<string, Country>" Desc="string">
        <Item Name="[Item]string" Num="int32" />
    </Country>
</ItemConf>
-->

<ItemConf>
    <Country Key="USA" Desc="A country in North America.">
        <Item Name="apple" Num="10" />
        <Item Name="orange" Num="20" />
    </Country>
    <Country Key="China" Desc="A country in East Asia.">
        <Item Name="apple" Num="100" />
        <Item Name="orange" Num="200" />
    </Country>
</ItemConf>
```

### Map in map

```xml
<!--
<ItemConf>
    <Country Key="map<string, Country>" Desc="string">
        <Item Name="map<string, Item>" Num="int32" />
    </Country>
</ItemConf>
-->

<ItemConf>
    <Country Key="USA" Desc="A country in North America.">
        <Item Name="apple" Num="10" />
        <Item Name="orange" Num="20" />
    </Country>
    <Country Key="China" Desc="A country in East Asia.">
        <Item Name="apple" Num="100" />
        <Item Name="orange" Num="200" />
    </Country>
</ItemConf>
```

## Union Sheet

### Predefined union (incell text form)

Use `@type="{.Target}"` with `|{form:FORM_TEXT}` for text-encoded union values:

```xml
<!--
<@TABLEAU>
    <Item Sheet="ItemConf" />
</@TABLEAU>

<ItemConf>
    <Target @type="{.Target}|{form:FORM_TEXT}" />
</ItemConf>
-->

<ItemConf>
    <Target>type:TYPE_PVE pve:{mission:{id:1 level:100 damage:999} heros:1 heros:2 heros:3 dungeons:{key:1 value:10} dungeons:{key:2 value:20} dungeons:{key:3 value:30}}</Target>
</ItemConf>
```

### Predefined union (cross-cell form)

Use `@type="{.Target}"` without form for cross-element union fields:

```xml
<!--
<ItemConf>
    <Target @type="{.Target}" />
</ItemConf>
-->

<ItemConf>
    <Target Type="PVP" Field1="1" Field2="10" Field3="Apple,Orange,Banana"/>
</ItemConf>
```

### Predefined union list

```xml
<!--
<ItemConf>
    <Target @type="[.Target]" />
</ItemConf>
-->

<ItemConf>
    <Target Type="Story" Field1="1001,10" Field2="1:Apple,2:Orange" Field3="Fragrant:1,Sour:2"/>
    <Target Type="Skill" Field1="1" Field2="2"/>
</ItemConf>
```

### Inline union (cross-cell)

Define the union type inline using `{.Target}enum<.Target.Type>` on the type column:

```xml
<!--
<XMLUnionConf>
    <Union Type="[.Target]enum&lt;.Target.Type&gt;" Field1="union" Field2="union" />
</XMLUnionConf>
-->

<XMLUnionConf>
    <Union Type="Story" Field1="1001,10" Field2="1:Apple,2:Orange" />
    <Union Type="Skill" Field1="1" Field2="2" />
</XMLUnionConf>
```

> Note: angle brackets in attribute values must be XML-escaped: `enum&lt;.Target.Type&gt;`

## Field Properties in XML

Append properties to type definitions in the metasheet:

```xml
<Entry Value="int32|{default:&quot;1&quot;}" />
<Item Name="string|{unique:true}" />
<ScalarList>[int32]|{patch:PATCH_REPLACE}</ScalarList>
```

> Note: quotes inside attribute values must be escaped as `&quot;`.

## Separator Configuration

Custom separators per sheet via metasheet:

```xml
<@TABLEAU>
    <Item Sheet="SepConf" Sep=";" Subsep="=" />
</@TABLEAU>
```

Data then uses `;` instead of `,`:
```xml
<SepConf number="1;2;3" />
```

## Merger and Scatter

```xml
<!-- Base file metasheet -->
<@TABLEAU>
    <Item Sheet="MergerConf" Merger="Merger*.xml" />
</@TABLEAU>
```

Matched files (Merger1.xml, Merger2.xml) contain data only — no metasheet needed:
```xml
<MergerConf>
    <Entry Id="10" Value="100" />
</MergerConf>
```

## Patch/Overlay

Base file defines schema + patch mode:
```xml
<@TABLEAU>
    <Item Sheet="PatchConf" Patch="PATCH_MERGE" Scatter="../overlays/*/Env.xml" />
</@TABLEAU>
```

Overlay files provide environment-specific overrides:
```xml
<!-- overlays/dev/Env.xml -->
<PatchConf>
    <Env>dev</Env>
    <StrictStruct ID="0" Name="" Start="2026-10-01 06:06:06" Expiry="2h" />
</PatchConf>
```

## Key Rules

1. **Metasheet required** — XML files without a metasheet comment are ignored
2. **XML escaping in attributes** — angle brackets in type attribute values must be escaped: `enum&lt;.FruitType&gt;`; in element text content, no escaping needed
3. **Quotes in attribute properties** — use `&quot;` for quoted values: `|{default:&quot;1&quot;}`
4. **Repeated elements = lists** — multiple elements with the same name create a list
5. **`@type` attribute** — shorthand for declaring the type of an element without repeating all field attributes
6. **Mixed content** — when an element has both text and child elements, the parser takes the text from the last child element
7. **Empty elements** — `<Element />` treated as zero-valued instance
