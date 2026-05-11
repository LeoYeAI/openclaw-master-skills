# Excel Output Template (CSV Format)

## Instructions

Generate a CSV (Comma-Separated Values) file that can be directly opened in Microsoft Excel, Google Sheets, or any spreadsheet application.

## Format Rules

1. Use **Tab-Separated Values (TSV)** for best Excel compatibility (avoids comma conflicts in data)
2. First row MUST be headers
3. Wrap fields containing commas or special characters in double quotes
4. Use UTF-8 encoding with BOM for Chinese character support
5. One program per row

## Output Structure

### Sheet 1: All Programs (Main Data)

Generate with these column headers (tab-separated):

```
University	Faculty	Program (EN)	Program (ZH)	Degree	Mode	Duration	Tuition Total (HKD)	Tuition Annual (HKD)	Application Opens	Main Deadline	Late Deadline	IELTS	TOEFL	Other English	Other Requirements	Official URL
```

Each data row follows the same order, tab-separated.

### Sheet 2: Summary by University

```
University	Total Programs	Avg Tuition (HKD)	Min Tuition (HKD)	Max Tuition (HKD)	Earliest Deadline	Latest Deadline
```

### Sheet 3: Summary by Degree Type

```
Degree Type	Count	Avg Tuition (HKD)	Universities Offering
```

### Sheet 4: English Requirements Comparison

```
University	Min IELTS	Min TOEFL	CET-6 Accepted	CET-6 Min Score
```

## Example Output

```tsv
University	Faculty	Program (EN)	Program (ZH)	Degree	Mode	Duration	Tuition Total (HKD)	Tuition Annual (HKD)	Application Opens	Main Deadline	Late Deadline	IELTS	TOEFL	Other English	Other Requirements	Official URL
HKU	Faculty of Engineering	Master of Science in Computer Science	計算機科學理學碩士	MSc	Full-time	1 year	180000	180000	1 Sep 2025	30 Nov 2025	28 Feb 2026	6.0 (sub 5.5)	80	N/A	Bachelor's in CS or related	https://www.msc-cs.hku.hk
CUHK	Faculty of Engineering	MSc in Computer Science	計算機科學理學碩士	MSc	Full-time	1 year	210000	210000	1 Sep 2025	15 Nov 2025	28 Feb 2026	6.5	79	N/A	Bachelor's in CS or related	https://www.cse.cuhk.edu.hk/msc
```

## Delivery Instructions

Present the output in a code block with language tag `tsv`:
