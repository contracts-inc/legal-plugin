# ContractS CLM MCP Legal Plugin

ContractS CLMと連動して自社基準と法令に基づく契約書レビューを実施し、あわせて法務文書のドラフト生成を支援するClaude Codeプラグインです。

## 概要

組織の契約交渉プレイブックに照らし合わせて契約書を分析し、基準からの逸脱を特定・重大度分類し、修正案（レッドライン）を生成します。ContractS CLMと連携し、割り当てられたレビュータスクから契約書を取得してレビューすることも可能です。

さらに、原契約や雛形を参照して変更覚書をはじめとする法務文書のドラフト（.docx）を生成するスキルを備えています。

## スキル

### review-contract

契約書レビュースキル。以下の機能を提供します。

- 組織のプレイブックに基づく条項ごとの分析
- リスク重大度分類（GREEN / YELLOW / RED）
- 変更履歴付き修正案（レッドライン）の生成
- レビュー指摘のWordコメント挿入
- ContractS CLMとの双方向連携（タスク取得・ドキュメント登録）

### draft-document

法務文書ドラフト生成スキル。以下の機能を提供します。

- 変更覚書を代表ユースケースとした、汎用的な法務文書ドラフト（.docx）の生成（変更覚書 / 各種覚書・合意書 / NDA / 業務委託等の定型契約 / 発注書・注文書 / 通知書・同意書）
- 入力ソースの選択（① コネクタ取得 / ② ファイル添付 / ③ 直接入力）による原契約・雛形の取り込み
- 原契約の正式名称・締結日・当事者・対象条項を正確に引用した、変更前後の対比
- 「推測で条項や数値を作らない」原則と、不足情報の `※要確認` 明示
- ドラフト注記の付与と、確定前の法務レビューを前提としたガードレール
- 生成後の後続フロー（任意・コネクタ接続時）: ドラフトのCLM登録 → レビュー依頼 → 原契約への関連契約紐付け

## ディレクトリ構成

```
.
├── .claude-plugin/
│   └── plugin.json                  # プラグインメタデータ
├── .mcp.json                        # MCP設定
├── skills/
│   ├── review-contract/
│   │   ├── SKILL.md                 # スキル定義（レビュー手順）
│   │   └── references/
│   │       ├── playbook.md          # 交渉プレイブック（カスタマイズ可能）
│   │       └── comment-format.md    # Wordコメント挿入ガイドライン
│   └── draft-document/
│       ├── SKILL.md                 # スキル定義（ドラフト生成手順）
│       ├── references/
│       │   ├── input-sources.md     # 入力ソース選択フロー（ベクトル検索含む）
│       │   ├── generation-rules.md  # 生成アプローチ・ガードレール・類型別の構成ヒント
│       │   ├── amendment-format.md  # 変更覚書の推奨フォーマットと文例
│       │   └── review-criteria.md   # 専門家レビューの要否判定基準
│       ├── scripts/
│       │   └── fill_docx.py         # python-docx による雛形差し込み
│       └── assets/
│           └── amendment-template.docx  # 汎用ダミー雛形
├── CHANGELOG.md
└── README.md
```

## セットアップ

(ヘルプサイトのURLを記載)

### draft-document の依存関係

ドラフト差し込みスクリプトは python-docx を使用します。

```sh
pip install python-docx
```

## カスタマイズ

### review-contract

`skills/review-contract/references/playbook.md` を編集することで、以下の項目を自社の基準に合わせて設定できます。

- 各条項の自社基準（許容範囲の数値・条件）
- 許容できない条件（RED判定の基準）
- フォールバック（妥協案）の範囲
- エスカレーション基準と報告先
- 交渉の優先順位（Tier 1〜3）
- 修正案のフォーマット

### draft-document

`skills/draft-document/references/` 配下を編集することで、以下を自社の運用に合わせて設定できます。

- 入力ソースの取得フローと利用コネクタ、対象契約のベクトル検索（`input-sources.md`）
- 生成アプローチの許容範囲・ガードレール・類型別の構成ヒント（`generation-rules.md`）
- 変更覚書の体裁・文例（`amendment-format.md`）
- 専門家レビューの要否判定基準（`review-criteria.md`）
- 汎用ダミー雛形（`assets/`）

同梱する雛形・サンプルはすべて汎用ダミーです。特定顧客・組織固有の情報や機密雛形は同梱しないでください。

## プライバシー / 免責

- 本プラグインはユーザーが投入する契約・雛形（機微情報）を、当該タスクの処理に限定して扱い、外部への保存・共有は行いません。
- 生成物はドラフト（草案）です。弁護士法に基づく法的な鑑定や助言（リーガルアドバイス）を提供するものではなく、確定前に必ず有資格の法務専門家によるレビューを受けてください。

## Claudeプラグインのパッケージ

カスタマイズしたスキルをzipファイルとしてプラグインをパッケージするには、プロジェクトルートで以下のコマンドを実行します。

```sh
zip -r legal-plugin.zip .claude-plugin skills .mcp.json
```

## Claudeプラグインの配布

カスタマイズしたzipパッケージか、[Releases](https://github.com/contracts-inc/legal-plugin/releases)で配布するZipファイルを使用して組織にプラグインを配布します。

Claude公式の[組織向けのclaude-coworkプラグインを管理する](https://support.claude.com/ja/articles/13837433-%E7%B5%84%E7%B9%94%E5%90%91%E3%81%91%E3%81%AEclaude-cowork%E3%83%97%E3%83%A9%E3%82%B0%E3%82%A4%E3%83%B3%E3%82%92%E7%AE%A1%E7%90%86%E3%81%99%E3%82%8B)サポートページを参考に `legal-plugin.zip` を組織に配布してください。
