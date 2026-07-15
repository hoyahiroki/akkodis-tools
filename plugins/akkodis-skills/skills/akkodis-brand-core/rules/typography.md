# フォント運用ルール

出典：Akkodis Brand Guidelines V3 §6 / Brand Checklist §3 / Logo Guideline V1 §15.1

正式値は `tokens/fonts.json` を参照。

## フォント階層（優先度順）

### Tier 1：プライマリー（外部納品物・キャンペーン用）

| 言語 | 用途 | フォント |
|---|---|---|
| 英語 | 見出し | **Tiempos Text Regular** |
| 英語 | 本文 | **Roboto** Regular / Light / Bold |
| 日本語（デザイン） | 全般 | **ヒラギノ角ゴ** または **游明朝** |
| 日本語（ビジネス文書） | 全般 | **Meiryo UI** |

### Tier 2：デフォルト（Microsoft Office環境・フォールバック）

| 言語 | 用途 | フォント |
|---|---|---|
| 英語 | 見出し | Times New Roman Regular |
| 英語 | 本文 | Arial Regular / Bold |
| 日本語 | 全般 | Meiryo UI |

PowerPoint, Word, Excel等のMicrosoftアプリでは Tier 2 を**事前設定済みデフォルト**として使用。コアフォントと同等に扱って差し支えない。

### Tier 3：CUD/UDフォント（アクセシビリティ配慮）

| 言語 | フォント |
|---|---|
| 日本語 | **BIZ UDPゴシック** |
| 英語 | Arial（UD準拠） |

視覚障害者向け文書・アクセシビリティ配慮資料で使用。一般文書での義務はない。

## ウェイト運用ルール

- Regular / Light / Bold を**階層的に**使い分けて見出し強調を表現
- 全テキストを同一ウェイトで統一しない
- 無闇なBold多用を避ける
- Roboto での全大文字化は **強調用途のみ**。タイトル・見出し・ボディコピーへの全大文字化は禁止
- Tiempos での見出しは **語句の冒頭のみ大文字**。全大文字化禁止

## 禁止事項

- ロゴに他のフォントを使用すること
- ビジネス文書でのMS明朝・HGフォント・游ゴシック使用
- 日本語フォント（Yu Gothic, MSゴシック, MS明朝）で英語テキストを記載
- 本文テキストへのグラデーション適用

## 社名ロゴ（AKKODiSコンサルティング株式会社）

| パート | フォント | 全角/半角 |
|---|---|---|
| `AKKODiS` | Arial Bold | 半角 |
| `コンサルティング株式会社` | Meiryo UI Bold | 全角 |

- カラー：プライマリー C100/M47/Y22/K82（≒ `#001F33`）／セカンダリー K100
- クリアスペース：「a」高さ分を四方に確保
- ロゴ画像と社名表記の併記は**原則NG**（マーケティング本部承認時のみ可）

## メール署名フォーマット

詳細は `tokens/fonts.json` の `email_signature` を参照。

- 日本語版：氏名 Meiryo UI Bold 10pt、所属/役職 Meiryo UI Bold 9pt、連絡先 Meiryo UI 9pt 等
- 英語版：氏名 Arial Bold 10pt、Job Title Arial 10pt 等
- テキスト色：**Akkodis濃いブルー `#001F33`**
- バナー画像はメール署名の一部にしない（特定キャンペーンでブランドチーム許可時のみ挿入）
