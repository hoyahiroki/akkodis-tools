# 画像／SVG生成サンプル

## SVGでブランドグラデーション付き図形を作る

```python
SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" width="1200" height="675">
  <!-- 公式グラデーション定義：イエロー2/3 + 鋼青色1/3、45° -->
  <defs>
    <linearGradient id="akkodisGradient" x1="0%" y1="100%" x2="100%" y2="0%">
      <!-- 45° = 左下→右上、鋼青色を右上に配置 -->
      <stop offset="0%"   stop-color="#FFB81C"/>
      <stop offset="66%"  stop-color="#FFB81C"/>
      <stop offset="100%" stop-color="#00FFFF"/>
    </linearGradient>
  </defs>
  
  <!-- 背景：濃いブルー -->
  <rect width="1200" height="675" fill="#001F33"/>
  
  <!-- グラデーションアクセント（角の三角形） -->
  <polygon points="900,0 1200,0 1200,300" fill="url(#akkodisGradient)"/>
  
  <!-- 見出し（白色、Meiryo UI） -->
  <text x="80" y="320" font-family="Meiryo UI, Arial, sans-serif" 
        font-size="64" font-weight="bold" fill="#FFFFFF">
    驚くべきことを実現
  </text>
  
  <!-- 本文 -->
  <text x="80" y="400" font-family="Meiryo UI, Arial, sans-serif" 
        font-size="24" fill="#FFFFFF">
    テクノロジーと人財が、革新を生み出す。
  </text>
  
  <!-- ロゴをimageタグで埋め込む場合は base64 化 -->
  <!-- ロゴサイズ：画面200px以上、クリアスペース：ロゴ高の幅相当 -->
</svg>
'''

with open("/mnt/user-data/outputs/banner.svg", "w", encoding="utf-8") as f:
    f.write(SVG)
```

## PILでバナー画像を作る

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080

# 濃いブルーベース
img = Image.new('RGB', (W, H), '#001F33')
draw = ImageDraw.Draw(img)

# 公式グラデーション（45° 右上配置）を別Image合成
grad = Image.new('RGB', (W, H), '#001F33')
gdraw = ImageDraw.Draw(grad)
# 簡易：右上1/3エリアにイエロー→鋼青グラデ
import numpy as np
arr = np.array(grad)
# 対角線距離で線形補間（左下0、右上1）
yy, xx = np.mgrid[0:H, 0:W]
t = (xx / W) + (1 - yy / H)  # 0..2
t = np.clip(t / 2, 0, 1)     # 0..1
# 0..0.66 = yellow flat, 0.66..1.0 = yellow→cyan
yellow = np.array([0xFF, 0xB8, 0x1C], dtype=float)
cyan   = np.array([0x00, 0xFF, 0xFF], dtype=float)
mask_low = (t <= 0.66)[..., None]
mask_high = (~(t <= 0.66))[..., None]
t_high = ((t - 0.66) / 0.34)[..., None]
grad_arr = np.where(
    mask_low,
    yellow,
    yellow * (1 - t_high) + cyan * t_high
).astype(np.uint8)
# 右上の三角形にだけ適用
mask = Image.new('L', (W, H), 0)
mdraw = ImageDraw.Draw(mask)
mdraw.polygon([(W*0.6, 0), (W, 0), (W, H*0.5)], fill=255)
grad = Image.fromarray(grad_arr)
img.paste(grad, (0, 0), mask)

# テキスト
try:
    font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 84)
    font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
except:
    font_h = ImageFont.load_default()
    font_b = ImageFont.load_default()

draw.text((100, 380), "Engineering A Smarter Future", font=font_h, fill='white')
draw.text((100, 500), "AKKODiS Consulting", font=font_b, fill='white')

# ロゴを右下に配置（クリアスペース確保）
logo = Image.open("/mnt/skills/user/akkodis-brand-core/assets/logos/AKKODIS_Logo_RGB_WHITE.png")
logo.thumbnail((400, 400))
# クリアスペース：ロゴ「A」幅相当を四方に確保
margin = 80
img.paste(logo, (W - logo.width - margin, H - logo.height - margin), logo if logo.mode == 'RGBA' else None)

img.save("/mnt/user-data/outputs/banner.png")
```

## チェックポイント

- [ ] 背景は濃いブルー or ホワイトをベース
- [ ] グラデーションは：イエロー2/3＋鋼青色1/3、45°、鋼青色右上
- [ ] グラデーションを本文テキストに適用しない
- [ ] ロゴ配置時のクリアスペース確保
- [ ] ロゴは原本ファイル使用、改変禁止
- [ ] 白×黄 / 黄×白 の文字背景組み合わせ禁止
- [ ] ヘッダー数字 (例：64pt見出し)、本文 (24pt以上推奨)
- [ ] フォトグラフィー：自然な笑顔、目の高さ、自然光、中程度の被写界深度
