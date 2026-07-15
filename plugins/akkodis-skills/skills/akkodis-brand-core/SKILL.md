---
name: akkodis-brand-core
description: "AKKODiS（AKKODiSコンサルティング株式会社）のブランド準拠成果物（DOCX/PPTX/XLSX/画像/SVG）を生成・編集する際に使用する。ブランドカラー（#001F33/#FFB81C/#00FFFF）、フォント階層（Tiempos/Roboto/Meiryo UI/Arial）、ロゴ運用（最小サイズ・クリアスペース・改変禁止）、社名表記（AKKODiSコンサルティング株式会社、サービス順序）、IOWN®表記（®/™/付属語ルール）など、ファイル生成時のビジュアル・構造・固有名詞ルールを一括適用する。トリガー：『AKKODiS』『ブランド準拠』『社内資料』『提案書』『PPT/PPTX/Word/Excel テンプレ』『IOWN』『ロゴ配置』『ブランドカラー』を含む依頼、または ユーザーが AKKODiSコンサルティング所属とわかっている場合の各種文書生成。テキスト校正（漢字開き・送り仮名・敬語）は対象外で、姉妹Skill akkodis-proofreader が担当する。"
license: Internal use only — AKKODiSコンサルティング株式会社
version: "1.1"
last_updated: "2026-05-26"
---

# AKKODiS Brand Core Skill

AKKODiSブランドガイドラインV3（2026.02.01）、ロゴ利用ガイドラインV1、フォトグラフィーガイドラインV1.0、ブランドチェックリスト完全版を統合し、ファイル生成時に確実にブランド準拠を実現するための統合スキル。

## いつ呼び出すか

以下のいずれかに該当する場合、このSkillを参照してから作業を開始する。

- 成果物生成依頼で対象が **DOCX / PPTX / XLSX / PDF / 画像 / SVG / HTML** のいずれか
- ユーザーがAKKODiSコンサルティング所属、または依頼内容にAKKODiS関連の文脈がある
- 「AKKODiS」「ブランド準拠」「社内向け」「提案書」「IOWN」「コーポレートカラー」などのキーワードが含まれる
- AKKODiSのテンプレート・ロゴ・カラー・フォントを参照する必要がある

## いつ呼び出さないか

- **テキストのみの校正・推敲**（漢字開き、送り仮名、敬語チェック等）→ `akkodis-proofreader` Skillを使用
- AKKODiSと無関係の汎用文書作成
- 個人用メモ、対話的な質問への回答

## 提供するもの

```
akkodis-brand-core/
├── SKILL.md                    ← このファイル
├── tokens/                     ← 機械可読データ（JSON）
│   ├── colors.json             ← カラーパレット正式値（HEX/RGB/CMYK/Pantone）
│   ├── fonts.json              ← フォント階層・社名ロゴ・メール署名仕様
│   ├── spacing.json            ← ロゴ最小サイズ・クリアスペース・ページ仕様
│   └── proper_nouns.json       ← 社名・サービス名・IOWN® 表記辞書
├── assets/
│   ├── logos/                  ← 公式ロゴ（SVGがマスター・PNGは後方互換用、いずれも改変禁止）
│   │   ├── AKKODIS_Logo_POS_RGB.svg       ← 【正式カラー版】白背景用 / KK黄＋他Navy
│   │   ├── AKKODIS_Logo_POS_RGB.png       ← 同上のPNG（透過・1412×420px）
│   │   ├── AKKODIS_Logo_POS_RGB.svg.b64.txt ← 同上のbase64 data URI（HTML/CSS直貼り用）
│   │   ├── AKKODIS_Logo_NEG_RGB.svg       ← 【反転カラー版】ネイビー/暗背景用 / KK黄＋他White
│   │   ├── AKKODIS_Logo_NEG_RGB.png
│   │   ├── AKKODIS_Logo_NEG_RGB.svg.b64.txt
│   │   ├── AKKODIS_Logo_RGB_BLUE.svg      ← 【モノクロNavy単色】FAX/単色印刷/カラー使用不可な場面
│   │   ├── AKKODIS_Logo_RGB_BLUE.png
│   │   ├── AKKODIS_Logo_RGB_BLUE.svg.b64.txt
│   │   ├── AKKODIS_Logo_RGB_WHITE.svg     ← 【モノクロWhite単色】暗背景でカラー使用不可な場面
│   │   ├── AKKODIS_Logo_RGB_WHITE.png
│   │   ├── AKKODIS_Logo_RGB_WHITE.svg.b64.txt
│   │   ├── AKKODIS_Logo_RGB_BLACK.svg     ← 【モノクロBlack単色】白黒印刷/コピー（fill=currentColorで色追従可）
│   │   ├── AKKODIS_Logo_RGB_BLACK.png
│   │   └── AKKODIS_Logo_RGB_BLACK.svg.b64.txt
│   └── templates/
│       ├── akkodis_pptx_template_dark.pptx  ← 公式テンプレート（37レイアウト）
│       └── akkodis_docx_template.docx       ← 公式Wordテンプレート（参照用）
├── rules/                      ← 人間可読ルールドキュメント（Markdown）
│   ├── logo_usage.md
│   ├── color_usage.md
│   ├── typography.md
│   ├── proper_nouns.md
│   ├── co_branding.md
│   ├── photography.md
│   └── output_checklist.md     ← 提出前チェックリスト
├── examples/                   ← 各成果物の生成サンプルコード
│   ├── pptx_example.md
│   ├── docx_example.md
│   ├── xlsx_example.md
│   └── image_svg_example.md
└── references/                 ← 出典PDF（読み取り専用）
    ├── brand_guideline_v3.pdf
    ├── logo_guideline_v1.pdf
    ├── photography_guideline_v1.pdf
    └── brand_checklist_v20260622.docx
```

## ロゴ運用クイックガイド

### 5バリエーション選択基準

| 用途 | 使用ファイル | 色構成 |
|---|---|---|
| **白・明色背景＋カラー使用可**（最も標準的な運用） | `POS_RGB` | KK部分=Yellow `#FFB81C`／他=Navy `#001F33` |
| **ネイビー・濃色背景＋カラー使用可** | `NEG_RGB` | KK部分=Yellow `#FFB81C`／他=White `#FFFFFF` |
| **白背景＋単色制約**（FAX、官公庁書式、印刷コスト制限等） | `RGB_BLUE` | 全Navy `#001F33` 単色 |
| **暗背景＋単色制約** | `RGB_WHITE` | 全White `#FFFFFF` 単色 |
| **白黒印刷・コピー前提** | `RGB_BLACK` | 全Black（SVGはfill=currentColor、CSSのcolorで制御可） |

### ファイル形式の選択基準

| 用途 | 推奨形式 | 理由 |
|---|---|---|
| HTML/CSS埋込（インライン） | `.svg.b64.txt` の data URI | 外部ファイル参照なしで完結、印刷時もズレなし |
| HTML（外部参照） | `.svg` | キャッシュ効率・編集容易 |
| PPTX/DOCX/XLSXに挿入 | `.svg`（Office 2019以降）／`.png`（互換性優先） | SVGはOfficeで拡大しても劣化なし |
| 古いシステム・PDF生成 | `.png`（1412×420px透過） | 縁ノイズなし・印刷高解像度耐性 |

### 不変条件（絶対遵守）

- ロゴの色を独自に変更しない（KK部分のYellow⇔他色の置換、Yellow→他色への置換は厳禁）
- ロゴの縦横比を変更しない（必ず352.7 : 104.8 = 約3.366 : 1 を維持）
- ロゴに装飾・効果（影、グラデーション、アウトライン等）を追加しない
- 最小サイズ（タグライン付き：印刷40mm / 画面200px、タグラインなし：印刷10mm / 画面50px）を下回らない
- クリアスペース：ロゴ「A」字幅分を四方に確保

## 使い方（標準ワークフロー）

### Step 1：依頼内容を読み、必要な`tokens/`を読み込む

成果物の種類に応じて、必要なJSONファイルを読み込む。

| 成果物 | 必須 | 推奨 |
|---|---|---|
| PPTX | colors, fonts, spacing | proper_nouns |
| DOCX | colors, fonts | proper_nouns, spacing |
| XLSX | colors, fonts | spacing |
| 画像/SVG | colors, spacing | fonts |
| 全般（テキスト含む） | proper_nouns | — |

### Step 2：該当する`rules/*.md`を確認

特に以下は**全成果物共通で必読**：
- `rules/output_checklist.md`（提出前チェックリスト）
- `rules/proper_nouns.md`（IOWN®含む）
- `rules/logo_usage.md`（ロゴ運用ルール）

### Step 3：`examples/*_example.md`を参考に実装

PPTXは公式テンプレートをコピーするのが最も確実（37レイアウトとAkkodisテーマが組まれている）。

### Step 4：生成後、`output_checklist.md`でセルフチェック

特に以下の致命的違反がないかを確認：
- [ ] ブランドカラー外の色を使用していない
- [ ] 白×黄／黄×白の文字背景組み合わせがない
- [ ] ロゴが改変・回転・色変更されていない
- [ ] AKKODiS（小文字 i）表記が崩れていない
- [ ] IOWN®/IOWN GLOBAL FORUM™ の表記が正しい
- [ ] 背景色に対し正しいロゴバリエーション（POS/NEG/単色）を選んでいる

## ブランド3要素クイックリファレンス

```
プライマリーカラー：
  濃いブルー  #001F33  RGB(0,31,51)     ベース・本文・背景
  イエロー    #FFB81C  RGB(255,184,28)  アクセント
  鋼青色      #00FFFF  RGB(0,255,255)   アクセント

フォント階層（Tier 1 ＞ Tier 2）：
  Tier 1（プライマリー）: Tiempos Text（英語見出し）/ Roboto（英語本文）/ ヒラギノ角ゴ・游明朝（日本語デザイン）/ Meiryo UI（日本語ビジネス文書）
  Tier 2（Office デフォルト）: Times New Roman / Arial / Meiryo UI

ロゴ最小サイズ：
  タグライン付き：印刷40mm / 画面200px
  タグラインなし：印刷10mm / 画面50px
  クリアスペース：ロゴ「A」幅分を四方に
```

## 既存Skillとの関係

| Skill | 守備範囲 |
|---|---|
| **akkodis-brand-core**（本Skill） | ファイル生成時のビジュアル・構造・固有名詞・IOWN®表記 |
| akkodis-proofreader | 既存テキストの校正（漢字開き・送り仮名・敬語・表記揺れ） |

両Skillは**併存**する。文書を生成する場合は本Skillで作成 → proofreaderで校正、の順序が推奨される。

## バージョン履歴

| Version | Date | 変更内容 |
|---|---|---|
| 1.2 | 2026-06-22 | IOWN®表記に I-10「注釈マーカーによる®省略（位置基準・初出非依存）」を追加。本文内マーカー注（IOWN®（…以下、IOWN））以降の単体IOWNの®省略を許容。出典CLを v20260501→v20260622 に改訂し §6 I-10 を正式収載。rules/proper_nouns.md・tokens/proper_nouns.json・rules/output_checklist.md・参照docx・姉妹skill proofreader を同期。 |
| 1.1 | 2026-05-26 | ロゴアセット刷新。SVGをマスター化（5バリエーション）、PNGを実体JPEG→真の透過PNG（1412×420 RGBA）に置換、base64 data URI版を追加。「POS=KK黄+他Navy／NEG=KK黄+他White／BLUE/WHITE/BLACK=単色」の運用マッピングを明文化。 |
| 1.0 | 2026-05-01 | 初版リリース。 |

## 出典

- Akkodis Brand Guidelines V3（2026.02.01）
- Akkodis ロゴ利用ガイドライン V1（2026.03.01）
- Akkodis フォトグラフィーガイドライン V1.0（2024.05.01）
- AKKODiS ブランドチェックリスト 完全版（2026.06.22修正：§6 I-10「注釈マーカーによる®省略」追加）
- 公式PowerPointテンプレート（社外向け_DARK_2025_ver2.1）
- 公式Wordテンプレート（v2）

質問・原本入手：マーケティング本部 brand.mktg-info@akkodis.co.jp
