# Excel Styling

Always apply this standard style when creating or modifying `.xlsx` files for tableau. Use `openpyxl` with the helpers below.

## Color Palette

| Constant         | Hex        | Applied To                                                                           |
| ---------------- | ---------- | ------------------------------------------------------------------------------------ |
| `CLR_BLUE`       | `FF4472C4` | `@TABLEAU` header row · data sheet **namerow** / **typerow** (blue, white bold text) |
| `CLR_LIGHT_BLUE` | `FF9DC3E6` | Type-name row in enum/struct/union sheets (light blue, black bold text)              |
| `CLR_NOTE_GREEN` | `FFB1CF95` | Data sheet **noterow** (light green)                                                 |
| `CLR_DATA_ODD`   | `FFFFFFFF` | Odd data rows (white)                                                                |
| `CLR_DATA_EVEN`  | `FFEDEDED` | Even data rows (light grey)                                                          |

## Style Helpers

```python
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

ALIGN_WRAP     = Alignment(wrap_text=True,  vertical='top',    horizontal='center')   # union field cells & noterow
ALIGN_NO_WRAP  = Alignment(wrap_text=False, vertical='center', horizontal='center')  # all other rows
THIN   = Side(style='thin', color='FFB0B0B0')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Color constants
CLR_BLUE       = 'FF4472C4'
CLR_LIGHT_BLUE = 'FF9DC3E6'
CLR_NOTE_GREEN = 'FFB1CF95'
CLR_DATA_ODD   = 'FFFFFFFF'
CLR_DATA_EVEN  = 'FFEDEDED'

def fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)

def auto_col_width(ws, min_col, max_col, extra=2, max_width=40):
    """Calculate max content length per column and set width explicitly."""
    for col in range(min_col, max_col + 1):
        best = 8
        for row in ws.iter_rows(min_col=col, max_col=col):
            for cell in row:
                if cell.value:
                    lines = str(cell.value).split('\n')
                    best = max(best, max(len(line) for line in lines))
        col_letter = get_column_letter(col)
        ws.column_dimensions[col_letter].width = min(best + extra, max_width)

def auto_row_height(ws, min_row, max_row, line_height=15, padding=6):
    for row in range(min_row, max_row + 1):
        max_lines = 1
        for cell in ws[row]:
            if cell.value:
                max_lines = max(max_lines, str(cell.value).count('\n') + 1)
        ws.row_dimensions[row].height = max_lines * line_height + padding
```

- **Column width**: iterate all cells, take the longest line per column + `extra` padding, capped at `max_width`.
- **Row height**: `(max newline count + 1) × line_height + padding`. Field cells with 3 lines auto-expand to ~51 pt.

---

## Row Color Rules (applies to all sheet types)

| Row type        | Fill color       | Font                      | Alignment       |
| --------------- | ---------------- | ------------------------- | --------------- |
| Type-name row   | `CLR_LIGHT_BLUE` | bold, black text, size 12 | `ALIGN_NO_WRAP` |
| Header row      | `CLR_BLUE`       | bold, white text, size 12 | `ALIGN_NO_WRAP` |
| Data row (odd)  | `CLR_DATA_ODD`   | default                   | `ALIGN_NO_WRAP` |
| Data row (even) | `CLR_DATA_EVEN`  | default                   | `ALIGN_NO_WRAP` |

All cells get `BORDER`. Row heights: type-name/header = 22 pt, data = 21 pt, field rows = `lines × 15 + 6` pt.

---

## @TABLEAU Sheet

```python
# Header row: CLR_BLUE bg + white bold text
for ci, h in enumerate(['Sheet', 'Alias', 'Mode'], 1):
    c = ws.cell(row=1, column=ci, value=h)
    c.font = Font(bold=True, color='FFFFFFFF', size=12)
    c.alignment = ALIGN_NO_WRAP; c.fill = fill(CLR_BLUE); c.border = BORDER

# Data rows: no fill, no wrap
for ci, v in enumerate(['MySheet', '', 'MODE_XXX'], 1):
    c = ws.cell(row=2, column=ci, value=v)
    c.alignment = ALIGN_NO_WRAP; c.border = BORDER
```

---

## Data Sheet (Mode = default/empty)

Header rows use `namerow / typerow / noterow / datarow` layout.

| Row      | Color                                        | Style                      |
| -------- | -------------------------------------------- | -------------------------- |
| namerow  | `CLR_BLUE`                                   | bold, white text, centered |
| typerow  | `CLR_BLUE`                                   | bold, white text, centered |
| noterow  | `CLR_NOTE_GREEN`                             | default, centered          |
| datarow+ | alternating `CLR_DATA_ODD` / `CLR_DATA_EVEN` | left-aligned               |

```python
def style_data_sheet(ws, namerow=1, typerow=2, noterow=3, datarow=4,
                     nameline=0, typeline=0, noteline=0, total_cols=None):
    """
    nameline/typeline/noteline:
      0  = whole cell is dedicated to that header (default, no wrap needed)
      >0 = that header is packed into a shared cell with \n separators (wrap required)
    When all three are >0, namerow==typerow==noterow (packed into one row).
    """
    if total_cols is None:
        total_cols = ws.max_column or 1

    # namerow: wrap only if packed (nameline > 0)
    name_align = ALIGN_WRAP if nameline > 0 else ALIGN_NO_WRAP
    for ci in range(1, total_cols + 1):
        c = ws.cell(namerow, ci)
        c.font = Font(bold=True, color='FFFFFFFF', size=12)
        c.alignment = name_align; c.fill = fill(CLR_BLUE); c.border = BORDER

    # typerow: wrap only if packed (typeline > 0)
    type_align = ALIGN_WRAP if typeline > 0 else ALIGN_NO_WRAP
    for ci in range(1, total_cols + 1):
        c = ws.cell(typerow, ci)
        c.font = Font(bold=True, color='FFFFFFFF', size=12)
        c.alignment = type_align; c.fill = fill(CLR_BLUE); c.border = BORDER

    # noterow: always wrap (note text can be long); packed row inherits from namerow styling above
    note_align = ALIGN_WRAP
    for ci in range(1, total_cols + 1):
        c = ws.cell(noterow, ci)
        c.font = Font(size=12)
        c.alignment = note_align; c.fill = fill(CLR_NOTE_GREEN); c.border = BORDER

    for ri in range(datarow, ws.max_row + 1):
        row_fill = fill(CLR_DATA_ODD) if (ri - datarow) % 2 == 0 else fill(CLR_DATA_EVEN)
        for ci in range(1, total_cols + 1):
            c = ws.cell(ri, ci)
            c.alignment = ALIGN_NO_WRAP; c.fill = row_fill; c.border = BORDER
        ws.row_dimensions[ri].height = 21

    auto_col_width(ws, 1, total_cols)
    auto_row_height(ws, namerow, ws.max_row)
```

When `nameline/typeline/noteline > 0` (packed into one row), pass the line values so alignment is set correctly:
```python
# All three packed into row 1
style_data_sheet(ws, namerow=1, typerow=1, noterow=1, datarow=2,
                 nameline=1, typeline=2, noteline=3)
```

---

## Type-Definition Sheets (Enum / Struct / Union)

### Column Sets

| Mode                     | Columns                                           | Type-name row?  |
| ------------------------ | ------------------------------------------------- | --------------- |
| `MODE_ENUM_TYPE`         | `Name`, `Number`(opt), `Alias`(opt)               | No              |
| `MODE_ENUM_TYPE_MULTI`   | same                                              | **Yes** (green) |
| `MODE_STRUCT_TYPE`       | `Name`, `Type`, `Alias`(opt)                      | No              |
| `MODE_STRUCT_TYPE_MULTI` | same                                              | **Yes** (green) |
| `MODE_UNION_TYPE`        | `Name`, `Alias`(opt), `Field1`…`FieldN`           | No              |
| `MODE_UNION_TYPE_MULTI`  | `Number`(opt), `Name`, `Alias`, `Field1`…`FieldN` | **Yes** (green) |

### Layout Pattern

**Single-type** (`MODE_*_TYPE`): starts directly with header row (CLR_AMBER).

**Multi-type** (`MODE_*_TYPE_MULTI`): each block = type-name row (CLR_LIGHT_BLUE) + header row (CLR_BLUE) + data rows. Blocks separated by 1 blank row.

### Field Cell Format (union only)

Each field is a 3-line cell (`\n`-separated): `FieldName\ntype\nnote`. Apply `ALIGN_WRAP`.

### Complete Example — `write_union_block` (Multi-type pattern)

```python
def write_union_block(ws, start_row, type_name, type_note, rows):
    """
    rows: list of (number, name, alias, [field_strings...])
    Each field_string: "FieldName\ntype\nnote"
    Returns next available row after block + 1 blank separator.
    """
    r = start_row
    max_fields = max((len(row[3]) for row in rows), default=0)
    total_cols = 3 + max_fields

    # type-name row (CLR_LIGHT_BLUE)
    ws.cell(r, 1, type_name).font = Font(bold=True, color='FF000000', size=12)
    ws.cell(r, 2, type_note)
    for c in range(1, total_cols + 1):
        cell = ws.cell(r, c)
        cell.fill = fill(CLR_LIGHT_BLUE); cell.alignment = ALIGN_NO_WRAP; cell.border = BORDER
    ws.row_dimensions[r].height = 22
    r += 1

    # header row (CLR_BLUE)
    for ci, h in enumerate(['Number', 'Name', 'Alias'] + [f'Field{i+1}' for i in range(max_fields)], 1):
        c = ws.cell(r, ci, h)
        c.font = Font(bold=True, color='FFFFFFFF', size=12); c.alignment = ALIGN_NO_WRAP
        c.fill = fill(CLR_BLUE); c.border = BORDER
    ws.row_dimensions[r].height = 22
    r += 1

    # data rows
    for idx, (number, name, alias, fields) in enumerate(rows):
        row_fill = fill(CLR_DATA_ODD) if idx % 2 == 0 else fill(CLR_DATA_EVEN)
        for ci, v in enumerate([number, name, alias], 1):
            c = ws.cell(r, ci, v)
            c.alignment = ALIGN_NO_WRAP; c.fill = row_fill; c.border = BORDER
        for fi, fval in enumerate(fields):
            c = ws.cell(r, 4 + fi, fval)
            c.font = Font(size=12)
            c.alignment = ALIGN_WRAP; c.fill = row_fill; c.border = BORDER
        for fi in range(len(fields), max_fields):
            c = ws.cell(r, 4 + fi); c.fill = row_fill; c.border = BORDER
        max_lines = max((str(f).count('\n') + 1 for f in fields), default=1)
        ws.row_dimensions[r].height = max_lines * 15 + 6
        r += 1

    return r + 1  # +1 blank separator row
```

> For single-type modes, omit the type-name row block and start directly with the header row. For enum/struct, replace field columns with `Number`/`Alias` or `Type`/`Alias` accordingly.

---

## Usage Pattern

```python
# Enum single (MODE_ENUM_TYPE)
ws = wb.create_sheet('FruitType')
# header row: CLR_AMBER, cols: Name / Number / Alias
# data rows: alternating CLR_DATA_ODD / CLR_DATA_EVEN

# Enum multi (MODE_ENUM_TYPE_MULTI)
ws = wb.create_sheet('Enum')
r = 1
r = write_enum_block(ws, r, 'FruitType', '水果类型', [
    (1, 'FRUIT_TYPE_APPLE',  '苹果'),
    (2, 'FRUIT_TYPE_ORANGE', '橙子'),
])
r = write_enum_block(ws, r, 'ColorType', '颜色类型', [
    (1, 'COLOR_TYPE_RED', '红色'), (2, 'COLOR_TYPE_BLUE', '蓝色'),
])
auto_col_width(ws, 1, 3)

# Struct multi (MODE_STRUCT_TYPE_MULTI)
ws = wb.create_sheet('Struct')
r = 1
r = write_struct_block(ws, r, 'Item',   'Item type',   [('ID','uint32',''), ('Name','string','')])
r = write_struct_block(ws, r, 'Reward', 'Reward type', [('ItemID','uint32',''), ('Num','int32','')])
auto_col_width(ws, 1, 3)

# Union single (MODE_UNION_TYPE)
ws = wb.create_sheet('Target')
write_union_single(ws, [
    ('Login',    '', ['Days\nint32\n登录天数']),
    ('Logout',   '', []),
    ('GameOver', '', ['FightType\n[]int32\n战斗类型', 'Score\nint32\n游戏分数']),
])

# Union multi (MODE_UNION_TYPE_MULTI)
ws = wb.create_sheet('Union')
r = 1
r = write_union_block(ws, r, 'Target', 'Target note', [
    (1, 'Login',    '', ['Days\nint32\n登录天数']),
    (2, 'Logout',   '', []),
    (3, 'GameOver', '', ['FightType\n[]int32\n战斗类型', 'Score\nint32\n游戏分数']),
])
r = write_union_block(ws, r, 'Condition', 'Condition note', [
    (10, 'PlayerLevel', '', ['Level\nint32\n等级']),
    (15, 'Login',       '', ['Days\nint32\n登录天数']),
])
auto_col_width(ws, 1, ws.max_column)
```
