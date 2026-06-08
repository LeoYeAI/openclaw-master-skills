# Well-Known Types in Excel

Well-known types are special tableau types that map to protobuf well-known messages or custom tableau types.

---

## Datetime

### `datetime` — Full timestamp

Cell formats: `2020-01-01 10:25:00`, RFC3339 (`2020-01-01T10:25:00Z`)

Proto backing: `google.protobuf.Timestamp`

```
| BeginDatetime       | EndDatetime         | Datetime                                    |
| datetime            | datetime            | []datetime                                  |
| Begin datetime      | End datetime        | Datetime list                               |
| 2020-01-01 10:25:00 | 2022-10-10 05:10:00 | 2020-01-01 10:25:00,2022-10-10 05:10:00     |
```

Generated proto:
```protobuf
google.protobuf.Timestamp begin_datetime = 1 [(tableau.field) = {name:"BeginDatetime"}];
google.protobuf.Timestamp end_datetime   = 2 [(tableau.field) = {name:"EndDatetime"}];
repeated google.protobuf.Timestamp datetime_list = 3 [(tableau.field) = {name:"Datetime" layout:LAYOUT_INCELL}];
```

Generated JSON:
```json
{
    "beginDatetime": "2020-01-01T02:25:00Z",
    "endDatetime":   "2022-10-09T21:10:00Z",
    "datetimeList":  ["2020-01-01T02:25:00Z", "2022-10-09T21:10:00Z"]
}
```

### `date` — Date only

Cell formats: `2023-01-01`, `20230101`

Proto backing: `google.protobuf.Timestamp`

```
| BeginDate  | EndDate  | Date                |
| date       | date     | []date              |
| Begin date | End date | Date list           |
| 2020-01-01 | 20221010 | 2020-01-01,20221010 |
```

### `time` — Time of day

Cell formats: `10:25:00`, `1025` (HHMM), `10:25`

Proto backing: `google.protobuf.Duration`

```
| BeginTime  | EndTime  | Time          |
| time       | time     | []time        |
| Begin time | End time | Time list     |
| 10:25:00   | 1125     | 10:25:00,1125 |
```

Generated JSON:
```json
{ "beginTime": "37500s", "endTime": "41100s" }
```

> **Note**: `locationName` in config controls timezone for parsing/emitting datetimes.

---

## Duration

Cell format: Go duration string, e.g. `72h3m0.5s`, `300ms`, `-1.5h`, `2h45m`

Valid units: `ns`, `us`/`µs`, `ms`, `s`, `m`, `h`

Proto backing: `google.protobuf.Duration`

```
| Duration1  | Duration2  | Duration         |
| duration   | duration   | []duration       |
| Duration 1 | Duration 2 | Duration list    |
| 1h2m3s     | 4ms5us6ns  | 1h2m3s,4ms5us6ns |
```

Generated proto:
```protobuf
google.protobuf.Duration duration_1 = 1 [(tableau.field) = {name:"Duration1"}];
google.protobuf.Duration duration_2 = 2 [(tableau.field) = {name:"Duration2"}];
repeated google.protobuf.Duration duration_list = 3 [(tableau.field) = {name:"Duration" layout:LAYOUT_INCELL}];
```

Generated JSON:
```json
{ "duration1": "3723s", "duration2": "0.004005006s" }
```

---

## Fraction

Proto backing: `tableau.Fraction` (custom type with `num` and `den` fields)

| Cell input | Meaning                       |
| ---------- | ----------------------------- |
| `10%`      | 10 per-cent (num=10, den=100) |
| `10‰`      | 10 per-thousand               |
| `10‱`      | 10 per-ten-thousand           |
| `3/4`      | fraction (num=3, den=4)       |
| `0.01`     | decimal → 1/100               |

```
| MinRatio  | Ratio1     | Ratio2   | Ratio3   | Ratio4   | Ratio5   |
| fraction  | []fraction | fraction | fraction | fraction | fraction |
| min ratio | ratio list | ratio 2  | ratio 3  | ratio 4  | ratio 5  |
| 1/4       | 10%        | 10‰      | 10‱      | 10       | 0.01     |
```

Generated proto:
```protobuf
tableau.Fraction min_ratio = 1 [(tableau.field) = {name:"MinRatio"}];
repeated tableau.Fraction ratio_list = 2 [(tableau.field) = {name:"Ratio" layout:LAYOUT_HORIZONTAL}];
```

Generated JSON:
```json
{
    "minRatio": { "num": 1, "den": 4 },
    "ratioList": [
        { "num": 10, "den": 100 },
        { "num": 10, "den": 1000 },
        { "num": 10, "den": 10000 },
        { "num": 10, "den": 1 },
        { "num": 1,  "den": 100 }
    ]
}
```

---

## Comparator

Proto backing: `tableau.Comparator` (with `sign` and `value` fields)

| Cell input | Meaning                 |
| ---------- | ----------------------- |
| `==10`     | equals 10               |
| `!=1/2`    | not-equals 1/2          |
| `<10%`     | less than 10%           |
| `<=10‰`    | less-or-equal to 10‰    |
| `>10%`     | greater than 10%        |
| `>=10‱`    | greater-or-equal to 10‱ |

```
| MinRatio   | Ratio1       | Ratio2     | Ratio3     | Ratio4     | Ratio5   |
| comparator | []comparator | comparator | comparator | comparator | comparator|
| min ratio  | ratio list   | ratio 2    | ratio 3    | ratio 4    | ratio 5  |
| !=1/4      | <10%         | <=10‰      | >10‱       | >=10       | ==3/5    |
```

Generated proto:
```protobuf
tableau.Comparator min_ratio = 1 [(tableau.field) = {name:"MinRatio"}];
repeated tableau.Comparator ratio_list = 2 [(tableau.field) = {name:"Ratio" layout:LAYOUT_HORIZONTAL}];
```

---

## Version

Proto backing: `tableau.Version` (with `str`, `val`, `major`, `minor`, `patch`, `others` fields)

Default pattern: `255.255.255` (each component 0–255).

Integer encoding: `MAJOR*(MINOR_MAX+1)*(PATCH_MAX+1) + MINOR*(PATCH_MAX+1) + PATCH`

```
| Version         | CustomVersion                             | IncellVersion                              | HorizontalVersion1 | HorizontalVersion2 | HorizontalVersion3 |
| version         | version|{pattern:"99.999.99.999.99.999"}  | []version|{pattern:"999.999.999"}          | version            | version            | version            |
| default version | custom version                            | incell version list                        | horizontal v1      | horizontal v2      | horizontal v3      |
| 1.0.3           | 1.2.3.4.5.6                               | 1.2.3,4.5.6                                | 1.0.0              | 1.2.3              | 2.0.3              |
```

Generated proto:
```protobuf
tableau.Version version = 1 [(tableau.field) = {name:"Version"}];
tableau.Version custom_version = 2 [(tableau.field) = {name:"CustomVersion" prop:{pattern:"99.999.99.999.99.999"}}];
repeated tableau.Version incell_version_list = 3 [(tableau.field) = {name:"IncellVersion" layout:LAYOUT_INCELL prop:{pattern:"999.999.999"}}];
repeated tableau.Version horizontal_version_list = 4 [(tableau.field) = {name:"HorizontalVersion" layout:LAYOUT_HORIZONTAL prop:{pattern:"999.999.999"}}];
```

Generated JSON:
```json
{
    "version": { "str": "1.0.3", "val": "65539", "major": 1, "minor": 0, "patch": 3, "others": [] },
    "customVersion": { "str": "1.2.3.4.5.6", "val": "10020300405006", "major": 1, "minor": 2, "patch": 3, "others": [4, 5, 6] },
    "incellVersionList": [
        { "str": "1.2.3", "val": "1002003", "major": 1, "minor": 2, "patch": 3, "others": [] },
        { "str": "4.5.6", "val": "4005006", "major": 4, "minor": 5, "patch": 6, "others": [] }
    ]
}
```

---

## Well-Known Types in Lists and Maps

All well-known types work in lists and maps:

```
[]date                              # incell list of dates
[]duration                          # incell list of durations
map<uint32, datetime>               # map with datetime values
[]version|{pattern:"99.999.99"}     # list of versions with custom pattern
```
