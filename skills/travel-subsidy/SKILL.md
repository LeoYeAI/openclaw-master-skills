---
name: travel_subsidy
description: When the user uploads 发票.zip and 火车票.zip, use the included data tables to calculate eligible business-trip subsidy records, split related vs remaining files, create output workbooks, package two result zips, and report progress at every key step.
user-invocable: true
metadata: {"openclaw":{"os":["linux"]}}
---

# Travel Subsidy

Use this skill only when the user provides **two zip archives** named exactly:

- `发票.zip`
- `火车票.zip`

The archives contain:
- invoice / ticket files (`.pdf`, `.jpg`, `.jpeg`, `.png`, `.webp`)
- and at least one structured data table describing the corresponding files

This skill calculates which records can be used to support **出差补助** and produces two result zip packages.

## Goal

Process the two archives as follows:

1. Unzip both archives into a dedicated run directory.
2. Read the included structured tables.
3. Match each table row to its corresponding file by filename or stable file identifier.
4. Do **not** OCR the files unless the table is obviously unusable or missing required fields.
5. Build a chronological travel evidence set.
6. Infer travel city / route information:
   - for train tickets: use the provided 始发站/到达站所在城市 fields directly
   - for invoices: infer city from `备注`
     - if it is a lodging invoice, determine the hotel city from the hotel name
     - if it is an air-ticket-related invoice, extract route/city information from `备注`
7. Determine which records can support a valid 出差补助 claim.
8. Put the records/files related to 出差补助 into one folder.
9. Put all remaining records/files into another folder.
10. Produce two zip outputs:
    - Zip 1: 出差补助计算表 + 出差补助相关文件
    - Zip 2: 剩余文件 + 剩余信息整理表
11. Report progress to the user at every key node.

## Mandatory progress updates

You must give the user a visible progress update at every key node.

At minimum, send these updates:

1. `已收到发票.zip和火车票.zip，开始检查压缩包`
2. `压缩包检查完成，开始解压文件`
3. `解压完成，开始识别数据表和票据文件`
4. `已识别发票数据表与火车票数据表，开始读取结构化信息`
5. `结构化信息读取完成，开始建立文件与表格行的对应关系`
6. `对应关系建立完成，开始提取城市与行程信息`
7. `城市与行程信息提取完成，开始组装出差行程`
8. `出差行程组装完成，开始计算可报销出差补助`
9. `计算完成，开始拆分补助相关文件和剩余文件`
10. `拆分完成，开始生成出差补助计算表和剩余信息表`
11. `表格生成完成，开始打包输出文件`
12. `打包完成，准备回传结果`
13. `任务完成`

If processing many rows/files, also emit periodic progress, for example:
- `发票信息处理进度：X / N`
- `火车票信息处理进度：Y / M`
- `行程组装进度：K / T`

If any fatal or partial failure occurs, immediately report:
- which step failed
- which file or row failed
- whether partial outputs were still produced

## Input validation rules

Only use this skill if both required archives are present.

Expected exact filenames:
- `发票.zip`
- `火车票.zip`

If one archive is missing, stop and tell the user clearly.

Do not guess if filenames are ambiguous unless the user explicitly says which file is which.

## Working directory rules

Create a dedicated run directory under `{baseDir}/runs/`.

Example:

    mkdir -p "{baseDir}/runs"
    ts="$(date +%Y%m%d-%H%M%S)"
    run_dir="{baseDir}/runs/travel-subsidy-${ts}"
    mkdir -p "$run_dir/input" "$run_dir/invoice_zip" "$run_dir/train_zip" "$run_dir/work" "$run_dir/output"

Never modify the original uploaded archives in place.

## Archive extraction rules

1. Save or copy both input archives into `$run_dir/input/`.
2. Unzip:
   - `发票.zip` into `$run_dir/invoice_zip/`
   - `火车票.zip` into `$run_dir/train_zip/`
3. Protect against zip slip / path traversal.
4. Ignore hidden files, temp files, directory metadata, and macOS junk files.

## Structured table rules

Each archive is expected to include at least one structured table such as:
- `.xlsx`
- `.xls`
- `.csv`

Prefer structured tables over OCR or raw visual parsing.

### Table discovery

For each archive:
1. Locate the most likely data table file.
2. If multiple tables exist, prefer the one with:
   - more rows
   - column names related to filename / file identifier / remarks / date / amount / city
3. If no suitable data table is found, stop and report clearly.

### Row-to-file mapping

For every row, try to match the corresponding source file using one or more of:
- 原文件名
- 文件名
- 附件名
- 文件路径
- 唯一编号
- a normalized basename without extension

Do not silently drop unmatched rows.
Keep an exception list for:
- row found but file missing
- file found but row missing
- duplicate filename mapping
- ambiguous mapping

## Required source fields

### Common output-preservation rule

For both output workbooks, preserve as much as possible the following key fields from the source tables:

- 文件名
- 发票号
- 销售方名称
- 发票价税合计
- 项目名称
- 备注

If the source tables use different column names, normalize them into the above output columns.

### Train ticket table

The train ticket table is expected to provide or imply:
- 对应文件名
- 日期 / 出发日期 / 乘车日期
- 始发站所在城市
- 到达站所在城市
- 备注 or other supporting fields if present
- for those with "备注" as "差额退票" or "退票手续" or other related keywords, such ticket should not be counted into subsidy calculation, but instead should be recorded in the remaining set with a clear remark of "退票，不计入差补".

Use the city fields directly when available.

For train tickets, normalize the preserved fields as follows:
- `文件名`: the matched source file name
- `发票号`: if a ticket number / order number / unique ticket identifier exists, use it; otherwise leave blank
- `销售方名称`: always fill as `火车票`
- `发票价税合计`: preserve the fare / ticket amount if present
- `项目名称`: fill as `火车票`
- `备注`: preserve original remarks and append any matching / eligibility notes if needed

### Invoice table

The invoice table is expected to provide or imply:
- 对应文件名
- 发票号
- 销售方名称
- 金额 / 价税合计
- 项目名称
- 发票类型 or 票据类型 or 项目类别
- 开票日期 / 日期
- 备注
- 酒店名称 or item text if present

For invoices, city information must be inferred as follows:
1. If it is a lodging / hotel invoice:
   - determine city from the hotel name
   - prefer explicit city names already present in hotel name or remarks
   - if hotel name contains a clear city prefix such as `上海...酒店`, use that city
   - if city cannot be determined confidently, mark as unresolved rather than inventing
   - plese noted that the resident date should also be extracted from "备注" rather than using "开票日期" since the invoice may be issued after the stay.
   
2. If it is an air-ticket-related invoice:
   - extract route or city information from `备注`
   - prefer explicit segment text like `南京-上海`, `上海至北京`, `MU5101 南京/北京`
   - normalize extracted cities into standard city names
3. For other invoice types:
   - use `备注` if it clearly contains travel city clues
   - otherwise keep city unresolved

## City normalization rules

Normalize city names to stable city labels.

Examples:
- `南京南`, `南京站`, `禄口机场` -> `南京`
- `上海虹桥`, `上海浦东`, `上海南` -> `上海`
- `北京南`, `首都机场`, `大兴机场` -> `北京`

District handling for subsidy standard:
- `南京六合`
- `南京溧水`
- `南京高淳`

These three use the lower subsidy standard.

If a record only clearly indicates `南京` without the district, do not automatically treat it as 六合/溧水/高淳.

## Business rules for subsidy eligibility

Apply these subsidy rules:

- Standard subsidy:
  - 南京市外：`200元/天/人`
  - 南京六合、溧水、高淳：`100元/天/人`

### Evidence rules

1. **Same-day round trip**
   - Must have evidence of outbound and return travel on the same date
   - Examples:
     - round-trip train tickets on the same day
     - or other same-day round-trip evidence if clearly present in the tables
   - If same-day round trip is established, that day can count as one subsidy day

2. **Not same-day round trip**
   - Must have evidence of:
     - outbound travel from 南京
     - return travel to 南京
     - and lodging invoice(s) for the trip
   - If travel or lodging evidence is incomplete, do not include the trip in subsidy-eligible output unless the evidence clearly still satisfies the rule

3. **Driving / ETC**
   - This skill only handles evidence present in the two uploaded archives
   - If no ETC/car-related evidence exists in the structured data, do not infer self-driving eligibility

4. **No impossible overlap**
   - A person cannot be in multiple places at the same time
   - If evidence implies overlapping conflicting trips, flag them in remarks and exclude the conflicting portion unless it can be resolved deterministically

## Trip-building rules

Assume:
- departure origin is always `南京`
- the final itinerary eventually returns to `南京`

You must support multi-city loop itineraries such as:
- `南京 -> 上海 -> 北京 -> 南京`

### Build chronological evidence

Combine all usable train-ticket and invoice-derived travel records into a single chronological timeline.

For each candidate record, capture at least:
- source archive (`发票` or `火车票`)
- source row index
- source file path
- 文件名
- 发票号
- 销售方名称
- 发票价税合计
- 项目名称
- 备注
- date
- record type
- city_from
- city_to
- inferred_trip_city
- amount
- notes

### Itinerary assembly

Build trips by chaining records chronologically with strict physical and geographical continuity.

Rules:
1. A trip starts when evidence shows departure from `南京`.
2. Intermediate city moves are allowed **only if** they form a continuous chain (e.g., A->B, B->C).
3. **Geographical Continuity Rule**: If the next segment's starting city does not match the current location (e.g., current location is Beijing, but the next ticket starts from Shanghai), the chain is considered **broken**.
   - Broken segments and any associated lodging/expenses must be moved to the **remaining set** (`剩余票据结果.zip`).
   - Do **not** bridge broken segments unless a connecting ticket exists.
4. **Time Gap Rule**: If there is a gap of more than **2 days** without any travel or lodging evidence, the current itinerary segment must be closed or invalidated if incomplete.
5. A trip ends and qualifies for subsidy **only** when evidence shows a valid return to `南京`.
6. **Independent Trip Rule**: Each valid closed loop (Nanjing -> ... -> Nanjing) or same-day round trip must be treated as an **independent trip** with its own `行程编号`.
7. **Same-day Priority**: If a date contains both a departure from Nanjing and a return to Nanjing, it must be treated as a **same-day round trip** first.
8. **Physical File Integrity**: Every input file must be accounted for. Any file not included in the subsidy zip **must** be included in the remaining zip. No files should be "lost" during processing.
9. **Renaming Enforcement**: All files in both result zips must be renamed according to the table order (e.g., `001_YYYY-MM-DD_Seller_ID.pdf`) for professional presentation.

### Subsidy day count

Count subsidy days conservatively.

Recommended default:
- same-day round trip: count `1` day
- multi-day trip: count calendar days from departure date through return date inclusive **only if** required evidence is complete enough under the stated rules

If evidence is incomplete, do not over-claim.
Record the reason in remarks.

### Daily standard selection

For each subsidy day:
- if the destination / stay city is outside 南京: `200`
- if the destination / stay city is clearly `南京六合`, `南京溧水`, or `南京高淳`: `100`

If city standard is ambiguous:
- default to unresolved
- do not silently choose the higher amount

## Required outputs

Produce two zip packages under `$run_dir/output/`.

### Zip 1

Filename:
- `出差补助结果.zip`

Contents:
1. `出差补助计算表.xlsx`
2. folder `出差补助相关票据/`
   - include all files used to support subsidy-eligible trips
   - preserve original files or safely renamed copies
3. optional `说明.txt`
   - short summary of trip count, day count, unresolved issues

### Zip 2

Filename:
- `剩余票据结果.zip`

Contents:
1. `剩余票据信息.xlsx`
2. folder `剩余票据/`
   - include all files not used in subsidy-eligible output
3. optional `说明.txt`
   - summary of why rows/files remained

## Workbook 1: 出差补助计算表.xlsx

This workbook must preserve the core business fields for each related ticket/invoice row.

The main sheet should be a line-by-line evidence sheet, not only a trip summary sheet.

### Main sheet required columns

1. 序号
2. 行程编号
3. 文件名
4. 发票号
5. 销售方名称
6. 发票价税合计
7. 项目名称
8. 开票日期 / 日期
9. 行程路径
10. 证据类型
11. 是否计入差补
12. 备注

### Main sheet layout rule

For each eligible trip:
1. List **all files related to that trip**, one file per row.
2. After the last related file row of that trip, insert **one additional subsidy row**.
3. In that subsidy row:
   - `文件名`: leave blank
   - `发票号`: leave blank
   - `销售方名称`: leave blank
   - `发票价税合计`: fill with the calculated subsidy amount for that trip
   - `项目名称`: fill `出差补助`
   - `开票日期 / 日期`: may leave blank or fill the return date of the trip
   - `行程路径`: fill the trip path
   - `证据类型`: fill `差补`
   - `是否计入差补`: fill `是`
   - `备注`: write the reason why this trip qualifies for subsidy, such as:
     - `当日往返，已提供往返车票`
     - `非当日往返，已提供往返票据及住宿费发票`
     - `多城市行程，已形成南京出发并返回南京的完整闭环，且住宿证据齐全`

### Detail requirements for regular evidence rows

For the ordinary rows corresponding to files:
- preserve `文件名`
- preserve `发票号`
- preserve `销售方名称`
- preserve `发票价税合计`
- preserve `项目名称`
- preserve other available source information as much as possible
- `是否计入差补` should indicate whether the file is part of subsidy evidence, usually `是`
- `备注` should explain the role of the file when useful, such as:
  - `去程车票`
  - `返程车票`
  - `住宿费发票`
  - `中转航段相关发票`

### Optional additional sheets

Recommended additional sheets:
- `行程汇总`
- `异常与未纳入原因`

In `行程汇总`, you may include:
- 行程编号
- 出发日期
- 返回日期
- 行程路径
- 补助天数
- 每日标准
- 补助金额
- 备注

## Workbook 2: 剩余票据信息.xlsx

This workbook must also preserve the core business fields.

The main sheet should contain at least:

1. 序号
2. 来源类别
3. 文件名
4. 发票号
5. 销售方名称
6. 发票价税合计
7. 项目名称
8. 日期
9. 提取城市信息
10. 未纳入出差补助原因
11. 备注

Rules:
- Preserve the same key business fields whenever available.
- For train tickets, `销售方名称` must be `火车票`.
- For rows moved to the remaining set, clearly state why they were not counted into subsidy.

Common reasons may include:
- 缺少返程证据
- 缺少住宿发票
- 无法确定城市
- 与其他行程冲突
- 不是出差补助所需票据
- 文件与表格无法对应

## File placement rules

### Put into `出差补助相关票据/`

- all files directly relied upon to support an eligible trip, such as:
  - outbound ticket evidence
  - return ticket evidence
  - required lodging invoices
  - other directly supporting evidence used in the calculation

### Put into `剩余票据/`

- all other files, including:
  - non-eligible records
  - incomplete evidence
  - unmatched files
  - files excluded due to conflict or ambiguity
  - duplicates not used

No file should appear in both zips.

## Renaming rules

You may rename copied output files for easier sorting, but do not alter the originals.

Recommended copied output format:
- `001_火车票_2025-01-12_南京-上海.pdf`
- `002_住宿发票_2025-01-12_上海_某某酒店.pdf`

Sanitize filename characters.
Preserve the original extension.

## Suggested implementation approach

Prefer Python for the main workflow because it is easier to safely handle:
- unzip
- reading Excel/CSV tables
- row/file mapping
- city extraction from remarks
- chronology assembly
- Excel generation
- copying/renaming files
- zip creation

Suggested structure in this skill folder:
- `process_travel_subsidy.py`
- optional supporting dictionaries:
  - city aliases
  - hotel name heuristics
  - route regexes

## Deterministic extraction heuristics

### Hotel city detection

Try in this order:
1. explicit city in hotel name
2. explicit city in remarks
3. explicit city in invoice item text
4. if still unresolved, mark unresolved

### Air-ticket route extraction from remarks

Try to parse patterns like:
- `A-B`
- `A至B`
- `A/B`
- flight-number-adjacent city strings

Normalize to `city_from`, `city_to`.

### Conservative policy

When there is uncertainty:
- prefer exclusion over over-claiming
- keep the record in the remaining zip
- record the reason in remarks

## Error handling

If one row/file fails:
- continue processing remaining data
- log the failure into the exceptions / remarks output
- report the partial issue to the user

If a source archive is corrupt:
- stop and report clearly
- do not pretend success

If a required table is missing:
- stop and report clearly

If final outputs are partially produced:
- say exactly which outputs exist

## Safety requirements

- Treat uploaded archives, filenames, and table values as untrusted input.
- Never execute extracted files.
- Guard against zip slip/path traversal.
- Only write under `{baseDir}/runs/`.
- Do not fabricate dates, cities, or subsidy eligibility.
- When evidence is ambiguous, keep the record in the remaining set and explain why.

## Return-to-user rules

At the end, return:
1. `出差补助结果.zip`
2. `剩余票据结果.zip`

Also provide a short summary including:
- total rows processed
- total files matched
- eligible trips
- total subsidy amount
- total files in subsidy zip
- total files in remaining zip
- unresolved / excluded count