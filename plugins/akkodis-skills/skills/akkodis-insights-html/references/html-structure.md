# resource-content 構造リファレンス（正本 / 実ページ準拠・サンプル表記）

AKKODiS Insights 対談記事の `<div class="resource-content">` 配下に出力するHTMLの正本。実際に公開されているSitecore出力から逆生成した正規パターン。構成順・クラス名・入れ子・空白の扱いはこのファイルを最優先で踏襲する。ここに無いクラスは作らない。

**サンプル中の `《…》` はプレースホルダ**（実原稿の値に置換する）。`[以下、…]` や class 名・タグはそのまま使う構造の一部。

## 目次
1. 出力コントラクト
2. 全体の入れ子
3. 構成順
4. 画像の4パターン（最重要）
5. 各ブロックの正規HTML
6. 話者ラベル・IOWN®・全角・リンクの規則
6.5 本文の特殊要素
7. 入力で決まる項目／編集判断になる項目
8. 画像の左右/中央の決め方
9. 出力前セルフチェック

---

## 1. 出力コントラクト

- ファイル1行目は厳密に `<div class="resource-content">`、末尾は対応する `</div>`。前後に空行・説明・コメント・Markdown・コードフェンス・BOM・引用符を置かない。
- 画像は必ず完全な `<img …>` 要素。`src` だけを裸テキストで出さない。
- `data-__outbound-listener-attached="true"` を **絶対に出力しない**（ブラウザの追跡JSが実行時に付与する属性）。

---

## 2. 全体の入れ子（参考・出力対象は内側のみ）

公開ページは次の入れ子。**生成・出力するのは最も内側の `<div class="resource-content">…</div>` だけ**。タイトルとリード文は外（別フィールド）なので断片に含めない。

```
<section class="resource-body-content">
  <p class="base mb5 mb4_tablet akkodisContent"><span>《リード文》</span></p>   ← 出力対象外
  <div class="base mb8 mb4_tablet akkodisContent">
    <div class="resource-content"> … </div>   ← ★これだけを .txt に出力
  </div>
</section>
```

---

## 3. 構成順

resource-content 直下に、原稿に存在するものだけを上から順に。

1. **MV画像**（記事先頭の集合/タイトル画像）— 中央・パターンA
2. **Index ブロック**（`mod-box`、H2から生成）
3. **本文セクション**（H2ごと。画像は**セクション先頭に限らず本文の途中にも複数挿入され得る**。各画像の位置と種別でA〜Dを選ぶ）
4. **注釈**（単一 `<p>`、`<br>`区切り）
5. **集合写真**（中央・パターンD、`mod-media-content`なし）＋ **プロフィール**（裸の`<p>`群）

本文・見出し・画像の順序は原稿どおり保持する。**1セクションに画像が2枚以上入ることがあり、その場合は左右が振り分けられる（例: 右→左）。左右/中央は §8 のとおりレイアウト資料（Word・PDF・画像・ユーザー指示）を見て決める。**

---

## 4. 画像の4パターン（最重要）

画像は必ず次の4種のいずれかで出力する。**クラスと入れ子がパターンごとに異なる**ので厳密に守る。

| パターン | 用途 | 画像クラス | 入れ子 |
|---|---|---|---|
| **A. MV** | 記事先頭の1枚（集合/タイトル） | `img-size-adjustment` | `<p><img></p>` のみ |
| **B. floated** | 本文中で**左右に配置された**写真（写っている人数は問わない） | **`media_w400`**（左右はこの幅で固定。他幅は使わない） | `mod-media mod-media_left|_right` ＞ `mod-media-media`＋`mod-media-content` |
| **C. centered（本文付き）** | 本文中で**中央/全幅に配置された**写真 | `img-size-adjustment` | ラッパー無し。`mod-media-media`（画像）と `mod-media-content`（本文）が**兄弟** |
| **D. centered（本文なし）** | 末尾の集合写真（直後がプロフィール） | `img-size-adjustment` | `mod-media-media` のみ。直後に `<p>&nbsp;</p>` → 裸の`<p>` |

- **配置（左/右/中央）は §8 のとおりレイアウト資料（Word・PDF・画像・ユーザー指示）で決める【MUST】**（XMLの`align`属性・写っている人物・人数では決めない。複数人でも中央とは限らない。ユーザーの指示があれば最優先）。
- **画像は本文の任意位置に出る。** 本文を順に出力し、各画像が原稿で現れる位置でブロックを挿入する。1セクションに複数あり得る。
- **B（floated）の本文の入れ方**: その画像の**直後に隣接する数発話（目安4〜5）だけ**を `mod-media-content` 内に入れ、**残りの発話は `mod-media` を閉じた後に通常の `<p>` として続ける**。同一セクションに2枚目のB画像があれば、その位置で再度同じことを行う。分割位置は編集判断（§7）。
- **C（centered本文付き）の本文の入れ方**: その画像が**セクション先頭**なら、そのセクションの残り発話を `mod-media-content` 内に入れる（先頭に `<p>&nbsp;</p>`）。
- **A〜Dとも、画像位置以外の発話は通常の `<p>` として本文順に出力する。**

---

## 5. 各ブロックの正規HTML

画像パスは `/-/media/Project/Akkodis/akkodis/ja/images/trends/insights/《article-slug》/img-《役割》.webp?la=ja`。**`《article-slug》` はページURLの末尾セグメントと同一**（§7）。`&hash=…` は公開時にSitecoreが付与するので生成不要。

### 5-0. ルート＋A. MV画像

```html
<div class="resource-content">
<p><img class="img-size-adjustment" alt="《記事タイトル》" src="/-/media/Project/Akkodis/akkodis/ja/images/trends/insights/《article-slug》/img-mv.webp?la=ja"></p>
```

- MV の `alt` は**記事タイトル**。
- ファイル名は意味のある名前（`img-mv`, `img-《人物役割》`, `img-talk` 等）を仮置きし §7 で要差し替えと明示。

### 5-1. Index（`mod-box`）

```html
<div class="mod-box">
<h2>Index</h2>
<ul>
<li class="mod-list-point__item"><a href="#anc-《キーワード1》" class="mod-text-link">《見出し1》</a></li>
<li class="mod-list-point__item"><a href="#anc-《キーワード2》" class="mod-text-link">《見出し2》</a></li>
<!-- H2の数だけ。href の anchor と本文 h2 の id を一致させる -->
</ul>
</div>
```

- `<a>` にはH2テキストを必ず入れる（空 `<a>` 禁止）。`href="#《slug》"` と本文 `<h2 id="《slug》">` を一致。
- アンカーは**意味スラッグ**（`anc-<英語キーワード>`）。連番ではない（§7）。
- `data-__outbound-listener-attached` は付けない。

### 5-2. B. floated（左右配置・冒頭のみ枠内）

左に配置された写真の例（クラスは `mod-media_left`。altは写っている人物で決める。下はAKKODiS側＝「氏」なしの例）:

```html
<h2 id="anc-《キーワード1》">《見出し1》</h2>

<div class="mod-media mod-media_left">
<div class="mod-media-media">
<img class="media_w400" alt="AKKODiS 《AKKODiS姓》" src="/-/media/Project/Akkodis/akkodis/ja/images/trends/insights/《article-slug》/img-《akkodis-人物》.webp?la=ja">
</div>
<div class="mod-media-content">
<p><strong>《AKKODiS氏名》 [以下、《AKKODiS姓》] ：</strong>……（冒頭の発話）</p>
<p><strong>《ゲスト氏名》氏 [以下、《ゲスト姓》]：</strong>……</p>
<p><strong>《AKKODiS姓》：</strong>……</p>
<p><strong>《ゲスト姓》：</strong>……</p>
</div>
</div>

<p><strong>《AKKODiS姓》：</strong>……（枠の後ろに続く残りの発話。全幅で流す）</p>
<p><strong>《ゲスト姓》：</strong>……</p>
```

右に配置された写真の例（クラスは `mod-media_right`。下はゲスト＝「氏」付きの例）:

```html
<div class="mod-media mod-media_right">
<div class="mod-media-media">
<img class="media_w400" alt="《ゲスト社名》 《ゲスト姓》氏" src="/-/media/Project/Akkodis/akkodis/ja/images/trends/insights/《article-slug》/img-《guest-人物》.webp?la=ja">
</div>
<div class="mod-media-content">
…
</div>
</div>
```

- 左寄せは `mod-media_left`、右寄せは `mod-media_right`。構造は同一。左右は §8 でレイアウト資料（Word・PDF・画像・ユーザー指示）を見て決める。

### 5-3. C. centered（中央/全幅配置・本文付き）

```html
<h2 id="anc-《キーワード2》">《見出し2》</h2>

<div class="mod-media-media">
<img class="img-size-adjustment" alt="《ゲスト社名》 《ゲスト姓》氏とAKKODiS 《AKKODiS姓》" src="/-/media/Project/Akkodis/akkodis/ja/images/trends/insights/《article-slug》/img-talk.webp?la=ja">
</div>
<div class="mod-media-content">
<p>&nbsp;</p>
<p><strong>《AKKODiS姓》：</strong>……</p>
<p><strong>《ゲスト姓》：</strong>……</p>
<!-- このセクションの全発話を入れる -->
</div>
```

- ラッパー `mod-media …` は**付けない**。`mod-media-media` と `mod-media-content` は兄弟。
- 2人が写る集合写真の alt は「《ゲスト社名》 《ゲスト姓》氏とAKKODiS 《AKKODiS姓》」のように、ゲストに「氏」、AKKODiS側には付けない。
- `mod-media-content` の先頭は `<p>&nbsp;</p>`。

### 5-4. 注釈（単一 `<p>` / `<br>` 区切り）

```html
<p>※１　《注釈1本文》<br>
※２　《注釈2本文》<br>
※３　《注釈3本文》　<a rel="noopener noreferrer" href="《絶対URL》" target="_blank">《リンク表示テキスト》</a></p>
```

- `mod-footnotes` div は**使わない**。1つの `<p>` に全注釈、行間は `<br>`。
- マーカーは原稿の表記を保持（全角 `※１` ＋ 全角スペースの記事と、半角 `※1` の記事がある）。
- 外部リンクは `<a rel="noopener noreferrer" href="《絶対URL》" target="_blank">…</a>`（§6 のリンク規則）。`data-` は付けない。注釈本文中の生URLも同形式でリンク化する。

### 5-5. D. 集合写真＋プロフィール（末尾）

```html
<div class="mod-media-media">
<img class="img-size-adjustment" alt="《ゲスト社名》 《ゲスト姓》氏とAKKODiS 《AKKODiS姓》" src="/-/media/Project/Akkodis/akkodis/ja/images/trends/insights/《article-slug》/img-closing.webp?la=ja">
</div>
<p>&nbsp;</p>
<p><strong>《ゲスト社名》<br>
《ゲスト肩書》<br>
《ゲスト所属》<br></strong></p>
<p><strong>《ゲスト姓》 《ゲスト名》</strong></p>
<p>《ゲストプロフィール本文》</p>
<p><strong>AKKODiSコンサルティング株式会社<br>
《AKKODiS肩書》<br>
《AKKODiS所属》<br></strong></p>
<p><strong>《AKKODiS姓》 《AKKODiS名》</strong></p>
<p>《AKKODiSプロフィール本文》</p>

</div>
```

- 集合写真はパターンD（`mod-media-media` のみ、`mod-media-content` なし）。直後に `<p>&nbsp;</p>`。
- プロフィールは `mod-profile-block`/`mod-profile` を**使わず裸の `<p>`**。
  - 社名・肩書・所属を **1つの `<strong>` に `<br>` 区切り**（各行末にも `<br>`）。
  - 氏名は `<p><strong>…</strong></p>`。サイト表示慣習として**文字間に半角スペース**（`《姓》 《名》` を `〇 〇 〇 〇` のように）。表示上の体裁（任意・要確認）。
  - 本文 `<p>`。順序は原稿準拠（社名→肩書→所属→氏名→本文）。
  - 氏名そのものに「氏」は付けない（プロフィール見出しは敬称なし。「氏」は写真altと初出ラベルのゲスト姓に付ける）。
- 末尾でルートを閉じる `</div>`。

---

## 6. 話者ラベル・IOWN®・全角・リンクの規則

- **話者ラベル（初出）**: 原稿の `氏名［以下、略称］：` を `<strong>氏名 [以下、略称] ：</strong>` として保持（全角 ［］ は半角 [ ] にしてよい）。
  - **ゲスト（非AKKODiS）の初出は氏名に「氏」を付ける**: `《ゲスト氏名》氏 [以下、《ゲスト姓》]：`。
  - **AKKODiS側は付けない**: `《AKKODiS氏名》 [以下、《AKKODiS姓》] ：`。
- **話者ラベル（2回目以降）**: 原稿どおりの略称 `<strong>《略称》：</strong>`（2回目以降は両者とも「氏」なし）。略称を勝手に作らない。
- **段落＝1発話**。発話本文中の改行（原稿の段落分け）は実ページでは1つの `<p>` にまとめられている例が多い。原稿の意味段落を尊重しつつ、1発話=1 `<p>` を基本とする。
- **IOWN®**: 原稿の `IOWNⓇ`（Ⓡ, U+24C7）/ `IOWN®` は、**® をインラインのまま** `IOWN®` とする（**`<sup>` で囲まない**）。`™`（`IOWN GLOBAL FORUM™` 等）も**インラインのまま**。`IOWN構想` `IOWN FUSION BASE` `IOWN推進室` `IOWN APN` など複合語の IOWN には®を付けない（原稿が付けていなければ付けない）。判断に迷う商標表記は `akkodis-proofreader` / `akkodis-brand-core` の固有名詞ルールに従い、原稿の付け方を保持する。
- **外部リンク**: `<a rel="noopener noreferrer" href="《絶対URL》" target="_blank">《表示テキスト》</a>`。本文中・注釈中いずれも同形式。URLは絶対URL。`data-` 属性は付けない。
- **太字/斜体**: `<strong>` / `<em>` のみ。Word由来の色span・装飾spanは捨てる。
- **`&nbsp;` スペーサー**: パターンC/D の本文先頭と集合写真直後に `<p>&nbsp;</p>` を置く（実ページ準拠）。

---

## 6.5 本文の特殊要素（記事により出現）

- **変更履歴（トラックチェンジ）**: 原稿に校正履歴があっても、HTMLは**確定版（挿入採用・削除反映後）**を使う。`extract-text <file>.docx` の既定出力が確定版。`pandoc --track-changes=all` は使わない。レンダリング画像に見え消し線が出ても出力に含めない。
- **MV直下の氏名・肩書テキスト**: 原稿でMV画像の下に登壇者の氏名・肩書がテキストで置かれていることがある。これは**MV画像内に焼き込まれている＋末尾プロフィールにも載る**情報なので、本文には**出さない**（重複回避）。除外したことは §9 で伝える。
- **パーパス/クレド等の非対話ブロック**: 話者ラベルの付かない引用・理念ブロックが本文中に挟まることがある。話者の発話とは分け、その話者の発話中に出るなら**その `<p>` 内に `<br>` 区切りで内包**、独立しているなら単独 `<p>`＋`<br>` で出す。体裁が必要そうなら §9 で要確認。勝手に別の発話へ吸収しない。
- **本文中のインライン外部リンク**: 「参考：〇〇｜…」等は §6 のリンク形式で出す。URLは `word/_rels/document.xml.rels` の `TargetMode="External"` から取得。
- **注釈内のURL**: 注釈本文の `https://…` も §6 のリンク形式でリンク化する。

---

## 7. 入力で決まる項目／編集判断になる項目

**初回プロンプトには Word原稿（.docx）と「ページURL」の両方が必要**。画像パスの `《article-slug》` は**ページURLの末尾セグメントをそのまま使う**（例: URL が `…/insights/iown-fusion-base-next-co-creation` なら slug は `iown-fusion-base-next-co-creation`）。URLが無ければ slug を確定できないので、停止して要求する。

| 項目 | 取得元 | 確認 |
|---|---|---|
| 記事スラッグ（画像パス） | **ページURLの末尾セグメント**（推測しない） | URL必須。未提供なら停止 |
| 画像の配置（左/右/中央） | **§8: レイアウト資料（Word・PDF・画像・ユーザー指示）で決定（人数では決めない・MUST）** | 原則そのまま採用 |
| 画像の alt | 画像を目視。単独=`会社 人名`（ゲストは「氏」付き／AKKODiSは無し）、2人=`《ゲスト社名》 《ゲスト姓》氏とAKKODiS 《AKKODiS姓》`、MV=タイトル | 要確認 |
| 画像ファイル名 | 役割から `img-《役割》-` を仮置き | 要差し替え |
| アンカー slug | H2の意味から `anc-<英語キーワード>` を生成 | 要確認 |
| B枠の発話分割位置 | 画像直後の隣接4〜5発話を枠内、残りを枠後に | 要確認 |
| 氏名の文字間スペース | サイト慣習で半角スペース挿入（任意） | 任意 |

**スラッグと配置は推測の編集判断ではない**（スラッグ＝URL、配置＝レイアウト資料（Word・PDF・画像・ユーザー指示）。配置は人数で決めない）。alt・ファイル名・アンカー・分割位置は推定で、最善推定＋確認提示。

---

## 8. 画像の配置（左右/中央）の決め方 ― レイアウト資料を参照【MUST】

**配置（左/右/中央）は、レイアウトが分かるもの（Wordのレンダリング／PDF／レイアウト画像／ユーザーの明示指示）で写真が「どこに置かれているか」を見て決める。これは必須。** XMLの`align`属性や「何人写っているか」では決めない。**複数人が写っていても中央とは限らない**し、単独人物が中央のこともある。配置の根拠は常にレイアウト情報であり、人数は配置に一切影響させない。

**優先順位**: ユーザーが配置を明示している（例: 「3枚目は右」「集合写真は中央」「このレイアウト画像の通り」）場合は**それを最優先**。指示が無ければ、Wordをレンダリングするか、提供されたPDF/レイアウト画像を見て、写真の寄りを採用する。

手順:
```bash
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf <file>.docx --outdir /home/claude/
pdftoppm -png -r 90 /home/claude/<file>.pdf /home/claude/page
# /home/claude/page-NN.png を順に view
```

各画像について、レンダリング上の**水平位置だけ**で配置とクラスを決める（人数は見ない）:

```
(1) 記事先頭の集合/タイトル画像 → A（MV、img-size-adjustment、alt=記事タイトル）

(2) レイアウト上の位置（必ず見た目に従う／人数は無関係）:
      ├ 左に寄っている        → B floated（mod-media_left,  media_w400）
      ├ 右に寄っている        → B floated（mod-media_right, media_w400）
      └ ページ幅いっぱい/中央 → C（img-size-adjustment, mod-media-media + mod-media-content 兄弟, 先頭<p>&nbsp;</p>）
                               ※末尾でプロフィール直前なら D（mod-media-content なし）

(3) alt にのみ「写っている人数」を反映（配置の判定には使わない）:
      ├ 単独人物 → 「会社 人名」（ゲスト＝非AKKODiSは「氏」付き／AKKODiS側は付けない）
      └ 複数人  → 「《ゲスト社名》 《ゲスト姓》氏とAKKODiS 《AKKODiS姓》」等
```

- 配置は本文の任意位置に現れ、1セクションに複数入ることがある（例: 同一セクションで右→左）。**本文を順に走査し、各画像が現れた位置でブロックを挿入**する。Bは画像直後の隣接4〜5発話を枠内に、残りは枠後へ。
- 人物特定（alt用）は、MV画像で各人の顔・服装を覚えてから各写真を照合する。`view` は埋め込みメディア（`word/media/imageN`）を直接開くと鮮明。
- 配置の根拠（写真がページのどこに寄っていたか）と人物特定は §9 で1〜2行で伝える。

---

## 9. 出力前セルフチェック（内部実行・非表示）

保存前に確認し、不一致は自動補正してから保存する（結果は表示しない）。

1. 1行目 `<div class="resource-content">`、末尾は対応する `</div>` か
2. 画像が `<img>` の外に裸で出ていないか
3. 画像クラスがパターン準拠か（**floated=`media_w400` / MV・中央=`img-size-adjustment`**）
4. B/C/Dの入れ子が正しいか（B=`mod-media mod-media_x`ラッパー有、C=ラッパー無で兄弟、D=`mod-media-content`無）
5. Index の各 `href="#…"` に対応する `<h2 id="…">` があり一致するか／`<a>` が非空か
6. 話者ラベルが初出=`氏名 [以下、略称] ：`（ゲストは氏名に「氏」付き）／2回目以降=`略称：` になっているか
7. 注釈が**単一 `<p>` + `<br>`**（`mod-footnotes` div 無し）か。外部リンクが `<a rel="noopener noreferrer" href="…" target="_blank">` 形式で、`data-` 無しか
8. プロフィールが裸の `<p>`（`mod-profile*` を使っていない）か
9. `IOWNⓇ`/`IOWN®` が `IOWN®`（**インライン**）になっているか。**`<sup>` を一切使っていないか**。`™` がインラインのままか
10. `data-__outbound-listener-attached` を出していないか
11. 画像srcの `《article-slug》` がページURLの末尾セグメントと一致しているか（URL未提供なら生成せず停止）
12. 単独人物写真の alt が、ゲスト=「会社 人名氏」／AKKODiS=「AKKODiS 人名」になっているか
13. **配置（左/右/中央）がレイアウト資料（Word・PDF・画像・ユーザー指示）由来か（写っている人数で中央化していないか・ユーザー指示があればそれを最優先したか）**
14. **画像ファイル名の拡張子前に不要な `-` を付けていないか**（`…/img-xxx.webp?la=ja`。`img-xxx-.webp` にしない）
15. インラインstyle／参照に無いクラス（`media_w400`・上記以外）／Markdown／コードフェンス／説明文が無いか
16. resource-content 内にタイトル・リード文を入れていないか

ルート要素や `<img>` を正しく生成できない場合、またはページURLが無い場合のみ、ファイルを作らずチャットで理由を述べて確認・要求する。
