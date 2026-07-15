# PPTX生成サンプル（python-pptx）

## 推奨アプローチ：公式テンプレートをコピーして使う

`assets/templates/akkodis_pptx_template_dark.pptx` には37のレイアウトと「Akkodis 2/3」テーマが組み込まれている。**このテンプレートをコピーしてからスライドを追加するのが最も確実**。

```python
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# 1. テンプレートをコピー
TEMPLATE = "/mnt/skills/user/akkodis-brand-core/assets/templates/akkodis_pptx_template_dark.pptx"
OUTPUT = "/mnt/user-data/outputs/your_deck.pptx"
shutil.copy(TEMPLATE, OUTPUT)

# 2. 開いて既存のサンプルスライドを削除し、必要なスライドを追加
prs = Presentation(OUTPUT)

# 既存スライド削除（テンプレ内のサンプルスライド16枚を消す）
# 注：単純なrelationshipの削除だけだと内部XMLファイルが残るが、
# 通常PowerPointで開く分には問題ない。完全クリーンが必要なら
# zipfileレベルで未参照XMLを削除する追加処理が必要。
xml_slides = prs.slides._sldIdLst
slides = list(xml_slides)
for slide in slides:
    xml_slides.remove(slide)

# 3. レイアウト一覧（4マスター×複数レイアウト）
# Master 0 (表紙系): Mesh Yellow & Blue / Eye Akkodis / Wave in the corners ...
# Master 1 (アジェンダ・章扉): Agenda - Computer / Chapter - Mesh Gold ...
# Master 2 (本文): Title, Subtitle and one Paragrah / Six Text Boxes / Two Paragraphs with Blue Line ...
# Master 3 (締め): Any questions? / Thank you / End

# 表紙スライド追加例
master = prs.slide_masters[0]
title_layout = master.slide_layouts[0]  # "Mesh Yellow & Blue"
slide = prs.slides.add_slide(title_layout)
# 各プレースホルダにテキスト挿入
for ph in slide.placeholders:
    if "Title" in ph.name or ph.placeholder_format.idx == 0:
        ph.text = "プレゼンテーションタイトル"
    elif "Subtitle" in ph.name:
        ph.text = "サブタイトル"

prs.save(OUTPUT)
```

## ゼロから作る場合

テンプレートを使わない場合、以下のテーマカラーとフォントを必ず明示設定。

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# Akkodisカラー定数
AKKODIS_DEEP_BLUE = RGBColor(0x00, 0x1F, 0x33)
AKKODIS_YELLOW    = RGBColor(0xFF, 0xB8, 0x1C)
AKKODIS_CYAN      = RGBColor(0x00, 0xFF, 0xFF)
WHITE             = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width  = Inches(13.333)  # 16:9 ワイドスクリーン
prs.slide_height = Inches(7.5)

# タイトルスライド
slide = prs.slides.add_slide(prs.slide_layouts[5])  # blank

# 背景を濃いブルーに
from pptx.oxml.ns import qn
from copy import deepcopy
bg = slide.background
fill = bg.fill
fill.solid()
fill.fore_color.rgb = AKKODIS_DEEP_BLUE

# タイトルテキスト
from pptx.util import Emu
left, top, width, height = Inches(0.7), Inches(2.5), Inches(11), Inches(1.5)
tb = slide.shapes.add_textbox(left, top, width, height)
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "プレゼンテーションタイトル"
run = p.runs[0]
run.font.name = "Meiryo UI"  # 日本語ビジネス文書
run.font.size = Pt(40)
run.font.bold = True
run.font.color.rgb = WHITE

# ロゴを右下に配置（クリアスペース確保）
LOGO = "/mnt/skills/user/akkodis-brand-core/assets/logos/AKKODIS_Logo_RGB_WHITE.png"
# 画面200px以上を確保（200px ≒ 2.08in @96dpi、PPT実寸では十分大きく）
slide.shapes.add_picture(LOGO, Inches(10.5), Inches(6.7), width=Inches(2.5))

prs.save("/mnt/user-data/outputs/output.pptx")
```

## グラデーション図形の作成

```python
from pptx.oxml.ns import qn
from lxml import etree

def add_brand_gradient(shape):
    """イエロー2/3＋鋼青色1/3、45°のAkkodis公式グラデーション"""
    sppr = shape.fill._xPr
    # 既存fillを削除
    for child in sppr.findall(qn('a:solidFill')) + sppr.findall(qn('a:gradFill')) + sppr.findall(qn('a:noFill')):
        sppr.remove(child)
    
    grad_xml = '''
    <a:gradFill rotWithShape="1" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
        <a:gsLst>
            <a:gs pos="0"><a:srgbClr val="FFB81C"/></a:gs>
            <a:gs pos="66000"><a:srgbClr val="FFB81C"/></a:gs>
            <a:gs pos="100000"><a:srgbClr val="00FFFF"/></a:gs>
        </a:gsLst>
        <a:lin ang="13500000" scaled="1"/>
    </a:gradFill>
    '''
    # 13500000 = 135° (PPTX angle in 60000ths of a degree, 45° from top-right)
    sppr.insert(0, etree.fromstring(grad_xml))
```

## チェックポイント

- [ ] テーマカラー「Akkodis 2」or「Akkodis 3」が theme XML に組まれているか
- [ ] 全テキストが Meiryo UI（日本語）または Arial / Roboto（英語）か
- [ ] ロゴはクリアスペース確保＋最小サイズ200px以上か
- [ ] グラデーションは 0/66/100% 停止、135°（右上方向）か
- [ ] 白×黄の文字背景組み合わせがないか
