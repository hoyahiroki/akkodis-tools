---
name: akkodis-insights-html
description: "AKKODiS Insights 対談・インタビュー記事のWord原稿（.docx）を、Sitecore の resource-content 構造に準拠したHTML断片へ変換するスキル。実際の公開ページから逆生成した正規パターンに従い、MV画像・Index目次・H2セクション・話者ラベル付き本文・注釈・登壇者プロフィールを組み立てる。画像の配置（左/右/中央）はレイアウト資料（Word・PDF・画像・ユーザー指示）から読み取り、左右=floated（media_w400）／中央=img-size-adjustment に振り分ける。配置は写真の寄りだけで決め、写っている人数では決めない（複数人でも中央とは限らない）。altは写っている人物から生成する。画像は本文の途中にも複数現れ得る。トリガー：『AKKODiS Insights』『記事をHTML化』『resource-content』『Sitecore用HTML』『対談原稿をHTMLに』『Word原稿をInsights記事に変換』、またはAKKODiSの対談記事WordをCMS投入用HTMLにしたい依頼。要約・原稿の再出力・Markdown・JSONは誤答で、必ず resource-content の断片HTMLのみをファイルで返す。配置はレイアウト資料（Word・PDF・画像・ユーザー指示）に従い、alt・アンカー・ファイル名・発話分割は推定の上で確認ポイントを併せて提示する。ブランド表記（AKKODiS / IOWN®）は akkodis-brand-core・akkodis-proofreader に従う。"
license: Internal use only — AKKODiSコンサルティング株式会社
---

# AKKODiS Insights HTML 変換スキル

Word原稿（対談・インタビュー記事）を、AKKODiS Insights 記事ページの `<div class="resource-content">` 配下構造に変換し、**HTML断片を .txt で出力する**。構造は実際の公開ページ（例: iown-fusion-base-next-co-creation）から逆生成した正規パターンに準拠する。要約・リライト・解説・Markdown・JSONは出さない。

## いつ呼ぶか

- AKKODiS Insights の対談/インタビュー記事原稿（.docx）を、Sitecore投入用HTMLにしたい依頼
- 「resource-content に合わせて」「Insights記事のHTMLにして」「対談原稿をHTML化」などの指示
- AKKODiSの記事系Word（タイトル＋リード＋H2セクション＋対談本文＋人物写真＋プロフィール構成）をCMS用HTMLにする場面

## いつ呼ばないか

- HTMLではなく要約・議事録・原稿リライトが欲しい場合
- DOCX/PPTX/XLSX等の成果物作成（→ `akkodis-brand-core`）／テキスト校正のみ（→ `akkodis-proofreader`）
- AKKODiS Insights 以外のページ構造（このスキルは当該構造に依存）

## 入出力の前提

| 項目 | 内容 |
|---|---|
| 入力（必須2点） | ① Word原稿（.docx, `/mnt/user-data/uploads/`） ② **ページURL**（画像パスの `<article-slug>` に使う。URLの末尾セグメント＝slug。未提供なら生成せず要求する） |
| 出力（主） | `resource-content` 断片HTMLの **.txt**（`/mnt/user-data/outputs/`） |
| 出力（副） | タイトル/リード文/アンカー対応表/画像差し替え一覧/確認ポイントを**チャットで**提示（断片には入れない） |
| 断片の契約 | 1行目が厳密に `<div class="resource-content">`、末尾が対応する `</div>`。前後に空行・コメント・Markdown・コードフェンス・BOM・引用符なし |

**構成順・画像4パターン・各ブロックの正規HTML・話者/IOWN®/全角の規則・編集判断項目・画像分類フロー・セルフチェックは、すべて `references/html-structure.md` にある。変換前に必ず読むこと。**

## ワークフロー

### Step 1: 入力を確認し、原稿テキストを読む

**まずページURLがあるか確認する。** 画像パスの `<article-slug>` は**ページURLの末尾セグメントをそのまま使う**（例: `…/insights/iown-fusion-base-next-co-creation` → `iown-fusion-base-next-co-creation`）。URLが無ければ slug を確定できないので、生成せずユーザーに要求する。

`docx` スキルの手順で本文・順序を把握する。本文順序の保持が最優先。

```bash
extract-text /mnt/user-data/uploads/<file>.docx
```

ここで拾うもの: タイトル（先頭）、リード文（タイトル直下）、H2見出し、対談本文と話者ラベル（初出 `氏名［以下、略称］：`、ゲストは氏名に「氏」付き／2回目以降 `略称：`）、注釈（※…）、外部リンク、登壇者プロフィール。変更履歴があっても `extract-text` の既定出力＝確定版を使う。

### Step 2: 画像の配置を「レイアウト資料」で決める（最重要）

**画像の配置はWordのXMLからは正しく取れない**（`align`属性は記事により付かない、自動altはゴミ）。配置は**レイアウトが分かるもの（Wordのレンダリング／PDF／レイアウト画像／ユーザーの明示指示）**で写真の寄りを見て決める。**ユーザーが配置を明示していればそれを最優先**。指示が無くWordしか無い場合は、下記でWordをページ画像にレンダリングするか、提供されたPDF/レイアウト画像を見て決める。

```bash
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf /mnt/user-data/uploads/<file>.docx --outdir /home/claude/
pdftoppm -png -r 90 /home/claude/<file>.pdf /home/claude/page   # page-01.png … を view で開く
python /mnt/skills/public/docx/scripts/office/unpack.py /mnt/user-data/uploads/<file>.docx /home/claude/unpacked/  # word/media/imageN を altの人物特定に使う
```

各ページを `view` し、`references/html-structure.md` §8 のとおり判定:
- 先頭の集合/タイトル画像 → **A. MV**（中央・`img-size-adjustment`・alt=記事タイトル）
- ページ上で**左寄せ** → **B `mod-media_left`**、**右寄せ** → **B `mod-media_right`**（`media_w400`）
- ページ幅いっぱい/中央 → **C**（本文付き）。末尾でプロフィール直前なら **D**（本文なし）
- **配置（左/右/中央）は写真の寄りだけで決める。写っている人数は見ない（複数人でも中央とは限らない）【MUST】**
- alt は配置と別に写っている人物で決める（単独=「会社 人名」ゲストは「氏」付き・AKKODiSは無し／複数=「《ゲスト社名》 《姓》氏とAKKODiS 《姓》」）

**画像は本文の途中にも複数出る**（1セクションで右→左など）。本文を順に走査し、各画像が現れた位置でブロックを挿入する。配置は必ず**レイアウト資料（Word・PDF・画像・ユーザー指示）での寄り**を採用（人物・人数では決めない。複数人でも中央とは限らない。ユーザー指示があれば最優先）。MV画像で各人の顔・服装を覚えてから単独写真を照合し、alt用に誰かを特定する。

### Step 3: HTML断片を組み立てる

`references/html-structure.md` の正規スニペットで組む。**パターンごとにクラスと入れ子が違う**点（B=`mod-media mod-media_x`ラッパー＋`media_w400`／C=ラッパー無しの兄弟＋`img-size-adjustment`／D=`mod-media-content`無し）を厳守。**画像は本文順の出現位置に挿入**し、Bは画像直後の隣接4〜5発話を枠内、残りは枠後に全幅で流す（1セクションに複数画像可）。**画像srcの `<article-slug>` はページURLの末尾セグメント**。アンカーは意味スラッグ `anc-<英語>`。**`IOWNⓇ`/`IOWN®` は `IOWN®`（インライン、`<sup>`で囲まない）**。`™`・複合語IOWNはそのまま。**外部リンクは `<a rel="noopener noreferrer" href="絶対URL" target="_blank">…</a>`**（本文中・注釈中とも。URLは rels から）。**ゲストの初出ラベルは氏名に「氏」**。**変更履歴は確定版**（`extract-text` 既定出力）。MV直下の氏名・肩書テキストは本文に出さない。パーパス等の非対話ブロックは `<p>`+`<br>` で。`data-__outbound-listener-attached` は出さない。参照に無いクラスは作らない。インラインstyle禁止。

### Step 4: .txt として保存する

`/mnt/user-data/outputs/<article-slug>-resource-content.txt`（slugはURL由来）。内容は断片HTMLのみ。

### Step 5: セルフチェックして引き渡す

`references/html-structure.md` §9 を内部実行（非表示）、不一致は保存前に補正。その後チャットで提示:

1. `present_files` で .txt
2. **タイトル / リード文**（Sitecoreの別フィールド貼付用）
3. **アンカー対応表**（H2 ↔ `anc-…`）
4. **確認ポイント**: 各画像の**左右/中央の根拠（写真の寄り）と写っている人物**、alt（ゲストは「氏」付き）、ファイル名（`img-…`）、B枠の発話分割位置。slugはURL由来・配置はレイアウト資料（Word・PDF・画像・ユーザー指示）採用、それ以外は推定である旨を明記
5. **除外/特殊処理の申告**: MV直下キャプションを除外した／パーパス等の特殊ブロックの体裁要確認／変更履歴を確定版で反映、など

## 設計判断（実ページ検証＋ユーザー指示で確定／すべて上書き可）

ユーザーが明示指示で覆した場合は指示を優先する。

1. **画像の配置（左/右/中央）はレイアウト資料（Word・PDF・画像・ユーザー指示）で決める【MUST】。** ユーザー指示があれば最優先。XMLの`align`・写っている人物・人数では決めない（複数人でも中央とは限らない）。alt・ファイル名・発話分割は推定＋確認提示。
2. **画像は本文の任意位置に複数現れる**（1セクションで右→左など）。本文順に走査し出現位置でブロック挿入。
3. **画像は4パターン**（A:MV / B:floated＝左右配置=`media_w400` / C:中央・全幅配置 / D:末尾集合写真）。**B/Cの振り分けは写真の寄りだけで決め、人数では決めない**。**左右に振る画像の幅は `media_w400` 固定**、MV・中央は `img-size-adjustment`。
4. **floated（B）はセクション全文を入れない。** 画像直後の隣接4〜5発話のみ枠内、残りは枠後に全幅。
5. **中央（C/D）はラッパー無し**で `mod-media-media`＋`mod-media-content` を兄弟配置。本文先頭は `<p>&nbsp;</p>`。
6. **話者の初出ラベル `氏名 [以下、略称] ：` を保持**（除去しない）。**ゲスト（非AKKODiS）は初出氏名に「氏」を付ける／AKKODiSは付けない**。2回目以降は両者とも略称（氏なし）。
7. **アンカーは意味スラッグ `anc-<英語>`**（連番ではない）。
8. **記事スラッグ（画像パス）はページURLの末尾セグメント**（推測しない。URL未提供なら停止）。
9. **IOWN®はインライン**（`IOWNⓇ`/`IOWN®`→`IOWN®`。`<sup>`を使わない）。`™`・複合語IOWNは原稿どおり。
10. **外部リンクは `<a rel="noopener noreferrer" href="絶対URL" target="_blank">`**（本文中・注釈中とも）。
11. **写真altの敬称**: ゲスト人物＝「会社 人名氏」、AKKODiS人物＝「AKKODiS 人名」。
12. **注釈は単一 `<p>` + `<br>`**（`mod-footnotes` div は使わない）。マーカーは原稿の全角/半角を保持。
13. **プロフィールは裸の `<p>`**（`mod-profile*` は使わない）。集合写真はパターンD。
14. **タイトル・リード文・MV直下の氏名キャプションは resource-content の外/非掲載**。
15. **変更履歴は確定版**（挿入採用・削除反映）。`extract-text` 既定出力を使い、`--track-changes=all` は使わない。
16. **パーパス等の非対話ブロックは独立/内包の `<p>`+`<br>`** として出力し、別の発話に吸収しない。

## 禁止事項

- 要約・リライト・解説・Markdown・JSON・コードフェンスを**ファイルに**出すこと
- 参照に無いクラスの創作（`media_w400` は可。それ以外の新規クラスは不可）
- `data-__outbound-listener-attached` 等の実行時JS属性の出力
- インラインstyle、Word由来の色span・装飾span乱立
- 画像パスを `<img>` の外に裸で出すこと（必ず `src` 値としてのみ）
- Sitecore ID形式リンク、原稿に無い見出し・本文・注釈の補完
- Wordの`align`属性や「写っている人物」で左右を決めること（レンダリングして写真の寄りを見て決める）
- **`IOWN®` を `<sup>` で囲むこと**（インラインのまま）
- **記事スラッグを推測で決めること**（ページURLの末尾セグメントを使う。URL未提供なら停止して要求）
- **外部リンクに `rel="noopener noreferrer"` を付け忘れること**

変換不能時（記事構造でない、画像を分類できない、ページURL未提供 等）は、ファイルを作らずチャットで理由を述べて確認・要求する。

## 既存スキルとの関係

| Skill | 守備範囲 |
|---|---|
| **akkodis-insights-html**（本Skill） | Insights対談記事Word → resource-content 断片HTML への構造変換 |
| akkodis-brand-core | DOCX/PPTX/XLSX/画像/SVG 生成時のブランド準拠・固有名詞・IOWN®表記 |
| akkodis-proofreader | テキスト校正（漢字開き・送り仮名・敬語・表記揺れ） |

本文の社名・サービス名・IOWN® 表記に疑義があれば `akkodis-proofreader` / `akkodis-brand-core` の固有名詞ルールに従う（このスキルは原稿の文言を保持し、勝手に直さない）。
