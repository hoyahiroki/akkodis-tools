# akkodis-tools

AKKODiS業務用のClaude Skill / スクリプト置き場。

このリポジトリは **Claude Code プラグイン・マーケットプレイス** として構成されており、
同梱のSkillを一度インストールすれば **すべてのリポジトリ／プロジェクト** で利用できます。

## インストール方法

Claude Code 上で以下を実行します（初回のみ）。

```
/plugin marketplace add hoyahiroki/akkodis-tools
/plugin install akkodis-skills@akkodis-tools
/plugin install dev-tools@akkodis-tools
```

- `user` スコープ（既定）でインストールすると、そのマシンの **全プロジェクト** でSkillが有効になります。
- チームで共有したい場合はプロジェクト直下の `.claude/settings.json` に登録するため、
  `--scope project` を付けてインストールし、そのリポジトリにコミットしてください。

インストール後の確認・更新：

```
/plugin list                 # 導入済みプラグインの一覧
/plugin marketplace update   # マーケットプレイスを最新化
```

## 同梱Skill（akkodis-skills プラグイン）

| Skill | 概要 |
|---|---|
| `akkodis-brand-core` | AKKODiSブランド準拠の成果物（DOCX/PPTX/XLSX/画像/SVG）生成・編集 |
| `akkodis-proofreader` | ブランド／日本語表記に基づく校正専用 |
| `notation-rules` | 表記統一辞書（約2,000語）に準拠した表記判定・校正 |
| `akkodis-insights-html` | Insights対談記事WordをSitecore用HTML断片へ変換 |
| `akkodis-careers-interviews-html` | careers/interviewsイベントレポートWordをHTML断片へ変換 |
| `akkodis-client-stories-html` | client-stories事例記事WordをHTML断片へ変換 |
| `hcux-audit` | サイト/ページのUX監査と優先度付き改善課題リスト出力 |
| `hcux-report-format` | HCUX Audit出力をブルー基調のA4横PDFへ整形 |
| `monthly-marketing-report-jp` | 月次マーケティングトレンドレポート生成 |
| `image-tone-match` | 複数画像の明度・彩度・色調を基準へ統一 |
| `prompt-architect` | Claude向けプロンプトの設計・改善・デバッグ |
| `output-critic` | 生成ドラフトを独立批評し重大度付き指摘を出力 |
| `spark-and-grill` | アイデア発散〜計画検証の思考パートナー |

## 同梱Skill（dev-tools プラグイン）

| Skill | 概要 |
|---|---|
| `gpt-check` | Claudeの成果物をOpenAI Codex CLI(GPT)にクロスチェックさせ、指摘を検証・反映する。事前に `codex` CLIのインストールとChatGPTアカウントでのログインが必要（環境ごとの手順はskill本文を参照） |

## リポジトリ構成

```
.claude-plugin/marketplace.json          ← マーケットプレイス定義
plugins/akkodis-skills/                  ← AKKODiS業務向けSkill
├── .claude-plugin/plugin.json           ← プラグイン定義
└── skills/<skill-name>/SKILL.md         ← 各Skill本体
plugins/dev-tools/                       ← 個人の開発ワークフロー向けSkill
├── .claude-plugin/plugin.json           ← プラグイン定義
└── skills/<skill-name>/SKILL.md         ← 各Skill本体
```

## ライセンス

Internal use only — AKKODiSコンサルティング株式会社
