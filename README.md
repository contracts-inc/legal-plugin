# ContractS CLM MCP Legal Plugin

ContractS CLMと連動して、契約書レビューから法務依頼・経理確認・稟議準備・締結後モニタリングまでをカバーするClaude Codeプラグインです。

## 概要

組織の契約交渉プレイブックに照らし合わせて契約書を分析し、基準からの逸脱を特定・重大度分類し、修正案（レッドライン）を生成します。ContractS CLMと連携し、割り当てられたレビュータスクから契約書を取得してレビューすることも可能です。

v1.1.0から、法務担当者向けの `review-contract` に加えて、事業部門の交渉担当者向けスキル（UC1〜UC5）を順次収録しています。

## スキル

### 法務担当者向け

#### review-contract

契約書レビュースキル。以下の機能を提供します。

- 組織のプレイブックに基づく条項ごとの分析
- リスク重大度分類（GREEN / YELLOW / RED）
- 変更履歴付き修正案（レッドライン）の生成
- レビュー指摘のWordコメント挿入
- ContractS CLMとの双方向連携（タスク取得・ドキュメント登録）

### 交渉担当者（事業部門）向け

契約交渉の受領〜締結〜履行の各フェーズを支援するスキル群です（UC1〜UC5を順次リリース）。業種パラメータ（`trading`：商社／`pharma`：製薬／`staffing`：人材）で挙動が切り替わります。

| スキル | フェーズ | 内容 |
|---|---|---|
| `clause-review` | ドラフト受領時 | 業種別プレイブック照合による赤黄緑判定＋レッドライン＋交渉トーク生成 |
| `legal-handoff` | 法務依頼時 | 法務レビュー依頼パッケージ生成（論点4点セット＋e-Gov法令MCPによる実条文引用） |
| `finance-impact` | 締結前 | 会計・税務インパクトの先読み（経理確認依頼シート） |

ContractS CLM未接続の環境でも、`skills/_shared/sample_contracts/` の逸脱条項入りサンプル契約書（商社・製薬・人材の3業種）でそのまま動作を試せます。

### review-contract と clause-review の使い分け

どちらも契約書レビューを行いますが、想定ユーザーと成果物が異なります。

| | `review-contract` | `clause-review` |
|---|---|---|
| 想定ユーザー | 法務担当者 | 事業部門の交渉担当者 |
| 判定基準 | 自社共通プレイブック（`references/playbook.md`） | 業種別プレイブック（trading/pharma/staffing） |
| 固有の成果物 | Wordコメント挿入によるレビュー結果 | 交渉トーク・譲歩ライン |
| 曖昧な依頼のデフォルト | ◯ | ✕ |

立場・業種の指定がない「この契約書をレビューして」のような依頼は `review-contract` に振り分けられます。`clause-review` を使いたい場合は、業種（商社／製薬／人材）を指定するか、「交渉トーク付きで」等の文言を添えてください。

## ディレクトリ構成

```
.
├── .claude-plugin/
│   └── plugin.json              # プラグインメタデータ
├── .mcp.json                    # MCP設定（ContractS CLM / e-Gov法令検索）
├── skills/
│   ├── review-contract/         # 法務向け：契約書レビュー
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── playbook.md      # 交渉プレイブック（カスタマイズ可能）
│   │       └── comment-format.md
│   ├── clause-review/           # 交渉担当者向け：条項チェック（UC1）
│   │   ├── SKILL.md
│   │   └── assets/
│   │       ├── playbook_trading.md   # 業種別プレイブック（カスタマイズ可能）
│   │       ├── playbook_pharma.md
│   │       └── playbook_staffing.md
│   ├── legal-handoff/           # 法務依頼パッケージ（UC2）
│   ├── finance-impact/          # 会計・税務論点の先読み（UC3）
│   └── _shared/                 # 共有アセット（SSoT）
│       ├── clm_rules.md         # CLM MCP共通ルール
│       ├── industry_presets.md  # 業種プリセット
│       └── sample_contracts/    # デモ用サンプル契約書3本＋仕込み一覧
├── CHANGELOG.md
└── README.md
```

## セットアップ

(ヘルプサイトのURLを記載)

## カスタマイズ

### 法務向け（review-contract）

`skills/review-contract/references/playbook.md` を編集することで、以下の項目を自社の基準に合わせて設定できます。

- 各条項の自社基準（許容範囲の数値・条件）
- 許容できない条件（RED判定の基準）
- フォールバック（妥協案）の範囲
- エスカレーション基準と報告先
- 交渉の優先順位（Tier 1〜3）
- 修正案のフォーマット

### 交渉担当者向け（clause-review ほか）

`skills/clause-review/assets/playbook_{industry}.md` が業種別プレイブックのたたき台です。自社の基準（🟢自社標準／🟡許容ライン／🔴NGライン）に書き換えてご利用ください。業種の追加は、プレイブックの追加と `skills/_shared/industry_presets.md` へのプリセット追記で行えます。

## Claudeプラグインのパッケージ

カスタマイズしたスキルをzipファイルとしてプラグインをパッケージするには、プロジェクトルートで以下のコマンドを実行します。

```sh
zip -r legal-plugin.zip .claude-plugin skills .mcp.json
```

## Claudeプラグインの配布

カスタマイズしたzipパッケージか、[Releases](https://github.com/contracts-inc/legal-plugin/releases)で配布するZipファイルを使用して組織にプラグインを配布します。

Claude公式の[組織向けのclaude-coworkプラグインを管理する](https://support.claude.com/ja/articles/13837433-%E7%B5%84%E7%B9%94%E5%90%91%E3%81%91%E3%81%AEclaude-cowork%E3%83%97%E3%83%A9%E3%82%B0%E3%82%A4%E3%83%B3%E3%82%92%E7%AE%A1%E7%90%86%E3%81%99%E3%82%8B)サポートページを参考に `legal-plugin.zip` を組織に配布してください。
