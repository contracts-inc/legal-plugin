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

## Claudeプラグインのパッケージ

カスタマイズしたスキルをzipファイルとしてプラグインをパッケージするには、プロジェクトルートで以下のコマンドを実行します。

```sh
zip -r legal-plugin.zip .claude-plugin skills .mcp.json
```

## Claudeプラグインの配布

カスタマイズしたzipパッケージか、[Releases](https://github.com/contracts-inc/legal-plugin/releases)で配布するZipファイルを使用して組織にプラグインを配布します。

Claude公式の[組織向けのclaude-coworkプラグインを管理する](https://support.claude.com/ja/articles/13837433-%E7%B5%84%E7%B9%94%E5%90%91%E3%81%91%E3%81%AEclaude-cowork%E3%83%97%E3%83%A9%E3%82%B0%E3%82%A4%E3%83%B3%E3%82%92%E7%AE%A1%E7%90%86%E3%81%99%E3%82%8B)サポートページを参考に `legal-plugin.zip` を組織に配布してください。
