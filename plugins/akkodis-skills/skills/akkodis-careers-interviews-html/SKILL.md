---
name: akkodis-careers-interviews-html
description: "AKKODiS careers/interviews 配下のイベントレポート記事のWord原稿（.docx）を、Sitecore の resource-content 構造に準拠したHTML断片へ変換するスキル。実際の公開ページ（akkodis-award / international-womens-day / internal-hackathon 系）から逆生成した正規パターンに従い、MV画像・H2〜H4見出し・本文・イベント概要テーブル（mod-table）・箇条書き・登壇者紹介・受賞/チーム列挙・講評・インタビューQ&A・中央/floated画像・末尾注釈を組み立てる。見出しレベルは原稿の手書きマーカー（H2/H3等の接頭辞 or 欄ラベル）から判定し足場を剥がす。画像配置の既定は中央/全幅、横寄せportraitはレイアウト資料（Word・PDF・画像・ユーザー指示）が示す場合のみ floated に振る（人数では決めない）。画像ファイル名は拡張子直前にダッシュを付けない。末尾に定型注釈「※インタビュー内容、所属は取材当時のものです。」を必ず入れる。ハッシュタグ・Promo（「…とは」誘導）・採用タイルは出力しない。trends/insights の対談記事は別スキル（akkodis-insights-html）。トリガー：『careers/interviews』『イベントレポートをHTML化』『AKKODiS Award/社内ハッカソン/International Women's Day のレポートをHTMLに』『採用インタビューのWordをCMS用HTMLに』『resource-content（careers）』、またはAKKODiSの careers/interviews 記事WordをCMS投入用HTMLにしたい依頼。要約・原稿の再出力・Markdown・JSONは誤答で、必ず resource-content の断片HTMLのみをファイルで返す。alt・ファイル名・配置は推定の上で確認ポイントを併せて提示する。ブランド表記（AKKODiS / IOWN®）は akkodis-brand-core・akkodis-proofreader に従う。"
license: Internal use only — AKKODiSコンサルティング株式会社
---

# AKKODiS careers/interviews HTML 変換スキル

Word原稿（careers/interviews のイベントレポート記事）を、当該ページの `<div class="resource-content">` 配下構造に変換し、**HTML断片を .txt で出力する**。構造は実際の公開ページ（`internal-hackathon-2025` / `international-womens-day-2026` 等）から逆生成した正規パターンに準拠する。要約・リライト・解説・Markdown・JSONは出さない。

## いつ呼ぶか

- AKKODiS の **careers/interviews 配下のイベントレポート記事**原稿（.docx）を、Sitecore投入用HTMLにしたい依頼
- 「careers/interviews の HTML にして」「イベントレポートをHTML化」「Award/ハッカソン/IWD のレポートを resource-content に」などの指示
- AKKODiS の採用系イベント記事Word（タイトル＋リード＋H2〜H4＋本文＋テーブル＋画像＋受賞列挙＋Q&A 構成）をCMS用HTMLにする場面

## いつ呼ばないか

- **trends/insights の対談・インタビュー記事**（→ `akkodis-insights-html`。Index/`mod-box`・見出しアンカー・話者ラベル本文・`trends/insights` パスを使う別構造）
- HTMLではなく要約・議事録・原稿リライトが欲しい場合
- DOCX/PPTX/XLSX等の成果物作成（→ `akkodis-brand-core`）／テキスト校正のみ（→ `akkodis-proofreader`）
- careers/interviews 以外のページ構造（このスキルは当該構造に依存）

## 入出力の前提

| 項目 | 内容 |
|---|---|
| 入力（必須2点） | ① Word原稿（.docx, `/mnt/user-data/uploads/`） ② **ページURL**（画像パスの `《slug》` に使う。URLの末尾セグメント＝slug。未提供なら生成せず要求する） |
| 出力（主） | `resource-content` 断片HTMLの **.txt**（`/mnt/user-data/outputs/`） |
| 出力（副） | タイトル/リード文/画像差し替え一覧/見出しレベル対応/確認ポイントを**チャットで**提示（断片には入れない） |
| 断片の契約 | 1行目が厳密に `<div class="resource-content">`、末尾が対応する `</div>`。前後に空行・コメント・Markdown・コードフェンス・BOM・引用符なし |

**構成順・ブロック別の正規HTML・見出しレベルの読み取り・画像規則・話者規則・除外物・セルフチェックは、すべて `references/html-structure.md` にある。変換前に必ず読むこと。**

## ワークフロー

### Step 1: 入力を確認し、原稿テキストを読む

**まずページURLがあるか確認する。** 画像パスの `《slug》` は**ページURLの末尾セグメントをそのまま使う**（例: `…/careers/interviews/internal-hackathon-2025` → `internal-hackathon-2025`）。URLが無ければ slug を確定できないので、生成せずユーザーに要求する。

`docx` スキルの手順で本文・順序を把握する。本文順序の保持が最優先。

```bash
extract-text /mnt/user-data/uploads/<file>.docx
```

ここで拾うもの:
- **入稿フィールド**（`タイトル(以下、入力ください)`・`Meta description`・`公開URL`・`タグカテゴリ`・`公開日`・`OG画像`・`本文(以下、入力ください)` 等）— これらは**本文ではない**。タイトル＝H1、`本文` 直後の段落＝リード文として控え、断片には入れない。
- **見出しと階層マーカー**（`## **H2…**` の接頭辞型、または `**H2(以下、入力ください)**`＋次行 の欄ラベル型）— `references/html-structure.md` §6 のとおりマーカー/足場を剥がしレベルを確定。マーカー無しの太字見出し（`アイデアソンの流れ` 等）は入れ子から推定。
- **本文・テーブル・箇条書き・登壇者紹介・審査員・受賞/チーム列挙・講評・インタビューQ&A・末尾注釈（`※`、複数可）・外部リンク**。
- 変更履歴があっても `extract-text` の既定出力＝確定版を使う。

> **公開ページは構造の正本であって本文一致の対象ではない**（編集者が文言・見出し・配置を改変している）。**Word原稿の内容**を §3〜§5 の構造へ忠実に変換する。

### Step 2: 画像の配置を「レイアウト資料」で決める

**配置はWordのXMLからは正しく取れない。** `references/html-structure.md` §7 のとおり、**既定は中央/全幅**（`<p><img class="img-size-adjustment">`）。**横寄せ portrait は、レイアウトが分かるもの（Wordのレンダリング／PDF／レイアウト画像／ユーザーの明示指示）が横配置を示す場合のみ** floated（§5-10）にする。**ユーザーが配置を明示していればそれを最優先**。指示が無くWordしか無い場合は、下記でWordをページ画像にレンダリングして写真の寄りを見る。

```bash
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf /mnt/user-data/uploads/<file>.docx --outdir /home/claude/
pdftoppm -png -r 90 /home/claude/<file>.pdf /home/claude/page   # page-01.png … を view で開く
python /mnt/skills/public/docx/scripts/office/unpack.py /mnt/user-data/uploads/<file>.docx /home/claude/unpacked/  # word/media/imageN を alt の人物特定に使う
```

判定:
- 先頭の集合/タイトル画像 → **A. MV**（中央・`img-size-adjustment`・alt=記事タイトル）
- 段落間に全幅で入るイベント写真 → **C 既定**（`<p><img class="img-size-adjustment">`）
- レイアウト上で**左右に寄っている** portrait → **B floated**（`mod-media mod-media_left|_right` ＋ 画像`media_w400`、本文は `mod-media-content` で包む。サブ見出しは `mod-txt-em`）
- **配置（中央/左右）は写真の寄りだけで決める。写っている人数は見ない【MUST】**
- alt は配置と別に、写っている人物・直近見出し・キャプションで決める（社外＝「氏」付き／AKKODiS＝無し／装飾＝空alt）

**画像は本文の途中にも複数出る**（ハッカソンのコメント節で右→左など）。本文を順に走査し、各画像が現れた位置でブロックを挿入する。横寄せの根拠は必ず**レイアウト資料**（人数では決めない。ユーザー指示があれば最優先）。

### Step 3: HTML断片を組み立てる

`references/html-structure.md` の正規スニペットで組む。**実ページのオーサリングバグ（閉じ過ぎ div・孤立 `mod-media-content`）は再現せず、クリーンな入れ子で出力する。** 厳守事項:

- **見出しは `<h2>`〜`<h4>` のプレーン**（id・class 無し）。原稿のマーカー/足場を剥がす。
- **画像クラスは 中央/MV＝`img-size-adjustment`、floated（左右）＝`media_w400`【MUST】**。floated本文は `mod-media-content` で包む。
- **画像srcの `《slug》` はページURL末尾**、パスセグメントは **`careers/interviews`**、**拡張子直前に `-` を付けない【MUST】**（`img-mv.webp`）。
- **イベント概要**は原稿が表＝`mod-table mod-table-1row_narrow`、`■`行＝1つの `<p>`。
- **箇条書きは無印 `<ul>`/`<li>`**。
- **Q&A** の質問は `<p><strong>―…</strong></p>`（`――` でも `―` 1つに正規化）、回答ラベルは**複数話者のセクションのみ** `<strong>姓：</strong>`（単独インタビュイーは無し）。
- **注釈は単一 `<p>` + `<br />`**（複数注釈も同一 `<p>`。`mod-footnotes` div は使わない）。**末尾に `※インタビュー内容、所属は取材当時のものです。` を必ず入れる【MUST】**（原稿に無くても）。
- **外部リンクは `<a rel="noopener noreferrer" href="絶対URL" target="_blank">…</a>`**（本文中・注釈中とも。URLは rels から）。
- **除外【MUST】**: ハッシュタグ・Promo（「…とは」誘導）・採用タイルは**出さない**。
- `data-__outbound-listener-attached` は出さない。参照に無いクラスは作らない。インラインstyle禁止。IOWN® はインライン（`<sup>` 不可）。

### Step 4: .txt として保存する

`/mnt/user-data/outputs/<slug>-resource-content.txt`（slugはURL由来）。内容は断片HTMLのみ。

### Step 5: セルフチェックして引き渡す

`references/html-structure.md` §10 を内部実行（非表示）、不一致は保存前に補正。その後チャットで提示:

1. `present_files` で .txt
2. **タイトル / リード文**（Sitecoreの別フィールド貼付用。原稿のH1・`本文` 欄から）
3. **見出しレベル対応**（マーカー無しで推定した見出しのレベル）
4. **確認ポイント**: 各画像の**中央/左右の根拠（写真の寄り）と写っている人物**、alt（社外は「氏」付き・装飾は空alt）、ファイル名（`img-…`・**末尾dash無し**）、floated節の発話/サブ見出し分割。slugはURL由来・配置はレイアウト資料採用、それ以外は推定である旨を明記
5. **除外/特殊処理の申告**: ハッシュタグ／Promo／採用タイルを除外した／イベント概要をテーブル or `■`-`<p>` のどちらで出したか／注釈本数（定型クロージングは必須付与）／Word由来のゼロ幅スペース等を軽微補正、など

## 設計判断（実ページ検証＋ユーザー指示で確定／すべて上書き可）

ユーザーが明示指示で覆した場合は指示を優先する。

1. **画像の配置（中央/左右）はレイアウト資料で決める【MUST】。既定は中央/全幅。** 横寄せ portrait は資料が横配置を示す場合のみ floated。XMLの`align`・写っている人物・人数では決めない。ユーザー指示があれば最優先。alt・ファイル名・分割は推定＋確認提示。
2. **画像は本文の任意位置に複数現れる**。本文順に走査し出現位置でブロック挿入。
3. **画像クラスは 中央/MV＝`img-size-adjustment`、floated（左右）＝`media_w400`【MUST】**。
4. **floated（B）の本文・サブ見出しは `mod-media-content` で包む【MUST】**。サブ見出しは `<p class="mod-txt-em">`。
5. **見出しは H2〜H4 のプレーン**（id・class・アンカー無し。Index/`mod-box` は使わない）。レベルは原稿のマーカーから（§6）。
6. **イベント概要は2形式**（テーブル `mod-table mod-table-1row_narrow` ／ `■`行を1 `<p>`）。原稿の書式に従う。
7. **箇条書きは無印 `<ul>`/`<li>`**（Index 用 `mod-list-point__item` は使わない）。
8. **Q&A の回答ラベルは複数話者セクションのみ** `<strong>姓：</strong>`。単独インタビュイー（導入で1名名指し）は付けない。質問は `<p><strong>―…</strong></p>`（`――` でも `―` 1つに正規化）。
9. **記事スラッグ（画像パス）はページURLの末尾セグメント**（推測しない。URL未提供なら停止）。パスセグメントは `careers/interviews`。
10. **画像ファイル名は拡張子直前に `-` を付けない【MUST】**。実アセット名は揺れるため仮置き＋要差し替え。
11. **注釈は単一 `<p>` + `<br />`（複数対応）**。マーカーは原稿の全角/半角を保持。**末尾に `※インタビュー内容、所属は取材当時のものです。` を必ず付与【MUST】**（原稿に無くても）。
12. **除外【MUST】**: ハッシュタグ・Promo（「…とは」誘導）・採用タイルは断片に入れない。
13. **タイトル・日付・リード文・MV直下の氏名キャプション等は resource-content の外/非掲載**。
14. **写真altの敬称**: 社外人物＝「会社 人名氏」、AKKODiS人物＝「AKKODiS 人名」。装飾画像は空alt。
15. **IOWN®はインライン**（`IOWNⓇ`/`IOWN®`→`IOWN®`。`<sup>` を使わない）。`™`・複合語IOWNは原稿どおり。
16. **変更履歴は確定版**（`extract-text` 既定出力）。`--track-changes=all` は使わない。

## 禁止事項

- 要約・リライト・解説・Markdown・JSON・コードフェンスを**ファイルに**出すこと
- 参照に無いクラスの創作（`mod-media`/`mod-media_left|_right`/`mod-media-media`/`mod-media-content`/`media_w400`/`img-size-adjustment`/`mod-table`/`mod-table-1row_narrow`/`mod-wide-30per`/`mod-txt-em` は参照済み。それ以外の新規クラスは不可）
- **floated画像を `media_w400` 以外に、中央/MV画像を `img-size-adjustment` 以外にすること**
- 見出しに `id`・class を付けること、Index/`mod-box` を作ること
- **ハッシュタグ・Promo（「…とは」）・採用タイルを出力すること**
- **画像ファイル名の拡張子直前に `-` を付けること**
- `data-__outbound-listener-attached` 等の実行時JS属性の出力
- インラインstyle、Word由来の色span・装飾span乱立
- 画像パスを `<img>` の外に裸で出すこと（必ず `src` 値としてのみ）
- 実ページのオーサリングバグ（閉じ過ぎ div・`mod-media` の外に孤立した `mod-media-content`）の再現
- Sitecore ID形式リンク、原稿に無い見出し・本文・注釈の補完
- Wordの`align`属性や「写っている人物/人数」で配置を決めること（レンダリングして写真の寄りを見て決める）
- **`IOWN®` を `<sup>` で囲むこと**（インラインのまま）
- **記事スラッグを推測で決めること**（ページURLの末尾セグメントを使う。URL未提供なら停止して要求）
- **外部リンクに `rel="noopener noreferrer"` を付け忘れること**

変換不能時（記事構造でない、画像を分類できない、ページURL未提供 等）は、ファイルを作らずチャットで理由を述べて確認・要求する。

## 既存スキルとの関係

| Skill | 守備範囲 |
|---|---|
| **akkodis-careers-interviews-html**（本Skill） | careers/interviews のイベントレポートWord → resource-content 断片HTML への構造変換 |
| akkodis-insights-html | trends/insights の対談記事Word → resource-content 断片HTML（別構造: Index・話者ラベル本文・`media_w400`） |
| akkodis-brand-core | DOCX/PPTX/XLSX/画像/SVG 生成時のブランド準拠・固有名詞・IOWN®表記 |
| akkodis-proofreader | テキスト校正（漢字開き・送り仮名・敬語・表記揺れ） |

本文の社名・サービス名・IOWN® 表記に疑義があれば `akkodis-proofreader` / `akkodis-brand-core` の固有名詞ルールに従う（このスキルは原稿の文言を保持し、勝手に直さない）。
