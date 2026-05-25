# ContractS CLM MCP Legal Plugin

ContractS CLMと連動して自社基準と法令に基づく契約書レビューを実施するClaude Codeプラグインです。

## 概要

組織の契約交渉プレイブックに照らし合わせて契約書を分析し、基準からの逸脱を特定・重大度分類し、修正案（レッドライン）を生成します。ContractS CLMと連携し、割り当てられたレビュータスクから契約書を取得してレビューすることも可能です。

## スキル

### review-contract

契約書レビュースキル。以下の機能を提供します。

- 組織のプレイブックに基づく条項ごとの分析
- リスク重大度分類（GREEN / YELLOW / RED）
- 変更履歴付き修正案（レッドライン）の生成
- レビュー指摘のWordコメント挿入
- ContractS CLMとの双方向連携（タスク取得・ドキュメント登録）

## ディレクトリ構成

```
.
├── .claude-plugin/
│   └── plugin.json          # プラグインメタデータ
├── .mcp.json                # MCP設定
├── skills/
│   └── review-contract/
│       ├── SKILL.md         # スキル定義（レビュー手順）
│       └── references/
│           └── playbook.md  # 交渉プレイブック（カスタマイズ可能）
├── CHANGELOG.md
└── README.md
```

## セットアップ

(ヘルプサイトのURLを記載)

## カスタマイズ

`skills/review-contract/references/playbook.md` を編集することで、以下の項目を自社の基準に合わせて設定できます。

- 各条項の自社基準（許容範囲の数値・条件）
- 許容できない条件（RED判定の基準）
- フォールバック（妥協案）の範囲
- エスカレーション基準と報告先
- 交渉の優先順位（Tier 1〜3）
- 修正案のフォーマット
