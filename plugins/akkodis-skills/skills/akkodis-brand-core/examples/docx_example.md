# DOCX生成サンプル（python-docx）

## 基本テンプレート

```python
from docx import Document
from docx.shared import Pt, RGBColor, Mm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Akkodisカラー
AKKODIS_DEEP_BLUE = RGBColor(0x00, 0x1F, 0x33)
AKKODIS_YELLOW    = RGBColor(0xFF, 0xB8, 0x1C)

doc = Document()

# === ページ設定 ===
section = doc.sections[0]
section.page_height = Mm(297)
section.page_width  = Mm(210)
section.top_margin    = Mm(25.4)
section.bottom_margin = Mm(25.4)
section.left_margin   = Mm(25.4)
section.right_margin  = Mm(25.4)

# === 既定フォント設定（日本語＋英語） ===
style = doc.styles['Normal']
style.font.name = 'Arial'  # 英語デフォルト（Office Tier 2）
style.font.size = Pt(10.5)
# 日本語フォント（rFonts/eastAsia）を Meiryo UI に
rPr = style.element.get_or_add_rPr()
rFonts = rPr.find(qn('w:rFonts')) or OxmlElement('w:rFonts')
rFonts.set(qn('w:eastAsia'), 'Meiryo UI')
rFonts.set(qn('w:ascii'), 'Arial')
rFonts.set(qn('w:hAnsi'), 'Arial')
if rFonts.getparent() is None:
    rPr.append(rFonts)

# === タイトル ===
title = doc.add_heading('提案書タイトル', level=0)
for run in title.runs:
    run.font.name = 'Meiryo UI'
    run.font.size = Pt(28)
    run.font.color.rgb = AKKODIS_DEEP_BLUE
    run.font.bold = True
    rPr = run.element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), 'Meiryo UI')
    rPr.append(rFonts)

# === 見出し1 ===
def add_h1(text):
    h = doc.add_heading(text, level=1)
    for run in h.runs:
        run.font.name = 'Meiryo UI'
        run.font.size = Pt(16)
        run.font.color.rgb = AKKODIS_DEEP_BLUE
        run.font.bold = True
        rPr = run.element.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:eastAsia'), 'Meiryo UI')
        rPr.append(rFonts)
    return h

add_h1('1. はじめに')

# === 本文 ===
def add_body(text):
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(10.5)
        rPr = run.element.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:eastAsia'), 'Meiryo UI')
        rPr.append(rFonts)
    return p

add_body('AKKODiSコンサルティング株式会社は、テクノロジーと人財の融合により…')

# === 表（ヘッダー：濃いブルー背景＋白文字） ===
def add_brand_table(headers, rows):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    # ヘッダー
    hdr = table.rows[0]
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = text
        # 背景色
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), '001F33')
        tcPr.append(shd)
        # 文字色を白に
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.bold = True
                run.font.name = 'Meiryo UI'
    # データ行
    for ri, row_data in enumerate(rows, start=1):
        for ci, val in enumerate(row_data):
            table.rows[ri].cells[ci].text = str(val)
    return table

add_brand_table(
    headers=['項目', '内容'],
    rows=[['サービス', 'Consulting'], ['提供価値', '融合']]
)

# === ロゴをヘッダーに配置 ===
LOGO = "/mnt/skills/user/akkodis-brand-core/assets/logos/AKKODIS_Logo_RGB_BLUE.png"
header = section.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = hp.add_run()
run.add_picture(LOGO, width=Mm(40))  # 印刷時最小40mm（タグライン付き想定）

doc.save("/mnt/user-data/outputs/output.docx")
```

## メール署名のフォーマット例

```python
# Meiryo UI Bold 10pt = 名前
# Meiryo UI Bold 9pt  = 役職省略形
# Meiryo UI 9pt       = 連絡先
# Meiryo UI Bold 8pt  = 会社名
# Meiryo UI 8pt       = 住所/URL/法的定型文
# 文字色：#001F33

p = doc.add_paragraph()
def signature_line(p, text, size, bold=False, color=AKKODIS_DEEP_BLUE):
    run = p.add_run(text + '\n')
    run.font.name = 'Meiryo UI'
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), 'Meiryo UI')
    run.element.get_or_add_rPr().append(rFonts)

signature_line(p, '※※本部 ※※部 役職', 9, bold=True)
signature_line(p, '森本 直之', 10, bold=True)
signature_line(p, 'T +03-1234-5678', 9)
signature_line(p, 'E naoyuki.morimoto@akkodis.co.jp', 9)
signature_line(p, 'AKKODiSコンサルティング株式会社', 8, bold=True)
signature_line(p, '〒108-0023 東京都港区芝浦3丁目4番1号 グランパークタワー3F', 8)
signature_line(p, 'https://www.akkodis.com/ja', 8)
```

## チェックポイント

- [ ] 日本語フォント eastAsia に Meiryo UI を明示設定（既定の游ゴシックを上書き）
- [ ] 英語フォントに Arial（Office Tier 2）または Roboto（Tier 1）
- [ ] 見出し色は `#001F33`、または `#000000`
- [ ] 表のヘッダー：濃いブルー背景＋白文字
- [ ] ロゴは 40mm以上、クリアスペース確保
- [ ] テキスト校正は `akkodis-proofreader` Skillと併用すること
