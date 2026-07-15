# XLSX生成サンプル（openpyxl）

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Akkodisカラー
AKKODIS_DEEP_BLUE = "001F33"
AKKODIS_YELLOW    = "FFB81C"
AKKODIS_CYAN      = "00FFFF"
WHITE             = "FFFFFF"

wb = Workbook()
ws = wb.active
ws.title = "Q3 Sales"

# === 既定フォント（日本語ビジネス文書 = Meiryo UI） ===
default_font = Font(name='Meiryo UI', size=10)

# === ヘッダー行 ===
header_font = Font(name='Meiryo UI', size=10, bold=True, color=WHITE)
header_fill = PatternFill('solid', fgColor=AKKODIS_DEEP_BLUE)
header_align = Alignment(horizontal='center', vertical='center')

headers = ['期間', 'サービス', '売上', '前年比']
for col_idx, h in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align

# === データ行 ===
data = [
    ('Q3-2025', 'Consulting', 1500000000, 1.12),
    ('Q3-2025', 'Solution',   2300000000, 1.08),
    ('Q3-2025', 'Academy',     280000000, 1.25),
    ('Q3-2025', 'Talent',     5400000000, 1.05),
]
for ri, row in enumerate(data, start=2):
    for ci, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=ci, value=val)
        c.font = default_font

# === 強調セル（成長率高 = イエロー塗り） ===
yellow_fill = PatternFill('solid', fgColor=AKKODIS_YELLOW)
for ri, row in enumerate(data, start=2):
    if row[3] >= 1.20:  # 前年比+20%以上はアクセント
        ws.cell(row=ri, column=4).fill = yellow_fill
        ws.cell(row=ri, column=4).font = Font(name='Meiryo UI', size=10, bold=True)

# === 罫線（控えめに） ===
thin = Side(border_style='thin', color='999AAD')  # 濃いブルー40%トーン
border = Border(left=thin, right=thin, top=thin, bottom=thin)
for row in ws['A1:D5']:
    for cell in row:
        cell.border = border

# === 列幅 ===
for col_idx, width in enumerate([14, 18, 18, 12], start=1):
    ws.column_dimensions[get_column_letter(col_idx)].width = width

# === 数値フォーマット ===
for ri in range(2, 6):
    ws.cell(row=ri, column=3).number_format = '#,##0'
    ws.cell(row=ri, column=4).number_format = '0.0%'

wb.save("/mnt/user-data/outputs/output.xlsx")
```

## グラフ配色

```python
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.fill import ColorChoice

chart = BarChart()
chart.type = "col"
chart.title = "Q3 売上"

data_ref = Reference(ws, min_col=3, min_row=1, max_row=5, max_col=3)
cats_ref = Reference(ws, min_col=2, min_row=2, max_row=5)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)

# シリーズ色を Akkodis濃いブルーに
chart.series[0].graphicalProperties = GraphicalProperties(solidFill=AKKODIS_DEEP_BLUE)

ws.add_chart(chart, "F2")
```

## チェックポイント

- [ ] 既定フォントは Meiryo UI（日本語ビジネス文書）
- [ ] ヘッダー：濃いブルー `#001F33` 背景＋白文字
- [ ] アクセントセル：イエロー `#FFB81C` を限定的に使用
- [ ] グラフ配色：ブランド5色＋トーン内
- [ ] 罫線色：濃いブルートーン or グレー
- [ ] イエロー背景に黒/濃色文字（白文字との組み合わせは禁止）
