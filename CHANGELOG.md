# Changelog

## [1.6.0] - 2026/07/17

### Added

- `draft-contract` スキルを新規追加（refs #7116）。原契約や雛形を参照し、変更覚書を代表ユースケースとした法務文書ドラフト（.docx）を生成する。入力ソースの3択（① コネクタ取得 / ② ファイル添付 / ③ 直接入力）、原契約からの正確な引用と変更前後の対比、推測禁止・`※要確認` 明示・ドラフト注記のガードレールを定義。
- 対象類型: 変更覚書 / 各種覚書・合意書 / NDA / 業務委託等の定型契約 / 発注書・注文書 / 通知書・同意書。文書類型の判別はモデルの知識で行い、類型ごとの構成ヒントは `generation-rules.md` に集約。
- 生成モードを「既存契約の一部変更（変更覚書等）」と「雛形からの新規作成」の2つに明確化。既存契約の変更時は、コネクタ接続時にベクトル検索（意味検索）で対象契約を特定する手順を定義（具体ツールはカスタマイズ例として分離）。
- 生成後の後続フロー（任意・コネクタ接続時）を定義: ドラフトのCLM登録 → レビュー依頼 → 原契約への関連契約紐付け。スキル本体は製品非依存の記述とし、ContractS CLM の具体ツール名（`create_document_from_uploaded_file` / `relate_contracts` 等）はカスタマイズ例として分離。
- `skills/draft-contract/references/` に `input-sources.md`（入力ソース選択フロー）、`generation-rules.md`（生成アプローチ・ガードレール・類型別の構成ヒント）、`amendment-format.md`（変更覚書の推奨フォーマットと文例）、`review-criteria.md`（専門家レビューの要否判定基準）を追加。
- `skills/draft-contract/scripts/fill_docx.py`（python-docx による雛形差し込み）と、`skills/draft-contract/assets/amendment-template.docx`（汎用ダミーの変更覚書雛形）を追加。

### Changed

- `plugin.json` の説明文を、契約書レビューに加えて法務文書ドラフト生成を含む内容に更新。バージョンを 1.6.0 に更新。
- README.md にドラフト生成スキルの概要・ディレクトリ構成・カスタマイズ手順・プライバシー/免責を追記。

## [1.0.9] - 2026/07/09

### Changed

- `SKILL.md` のレビュープロセス「3. 全体像の把握」に、参照契約書の取得手順を追加。レビュー対象の契約書が基本契約等の他の文書を参照している場合、`search_references`ツールでContractS CLM上の候補を検索し、ユーザー選択後に`download_document`でダウンロードしてレビューのインプットに追加するフローを定義。

## [1.0.8] - 2026/05/27

### Added

- `references/comment-format.md` を新規作成。Wordコメント（吹き出し）挿入に特化したガイドライン（挿入位置のルール、含める情報、フォーマット例、禁止事項）を定義。

### Changed

- `SKILL.md` のステップ8を再構成。基本方針・変更履歴付き修正案の書き込み・禁止事項はSKILL.mdに残し、コメント挿入のフォーマットは `references/comment-format.md` を参照する構成に変更。

## [1.0.7] - 2026/05/25

### Changed

- GitHub公開リポジトリ（contracts-inc/legal-plugin）での配布に向け、単独リポジトリに移行。
- README.mdを追加し、セットアップ手順・配布方法・カスタマイズガイドを整備。

## [1.0.6] - 2026/05/22

### Changed

- `contract-review` スキルの構成をリファクタリング。SKILL.mdを普遍的なレビュー手順（プロセス）に特化し、各社固有の基準（チェックポイント、許容範囲、重大度分類、交渉優先順位など）を `references/playbook.md` に分離。
- CLM登録時（ケースA・ケースB共通）に、レビュー前の文書からの変更意図および要点を4,000文字以内で詳細にまとめた更新コメントを付与するステップを追加。

### Added

- `references/playbook.md` に各社でカスタマイズ可能なサンプルプレイブックを新規作成。基本方針、類型別チェックポイント（自社基準/許容できない条件/フォールバック）、リスク重大度分類、交渉優先順位、修正案作成ガイドライン、カスタマイズガイドを含む。

## [1.0.5] - 2026/05/12

### Changed

- `contract-review` スキルのレビュープロセスにユーザー確認ステップ（Step 9）を追加。総合評価完了後、Wordファイル作成に進む前にレビュー結果をユーザーに提示し承認を得ることを必須化。
- Wordファイル作成時の指摘事項の記載方法を厳格化。すべての指摘は既存文書の該当箇所にWordコメント（吹き出し）として挿入し、文書末尾へのサマリー追加を禁止。

## [1.0.4] - 2026/05/12

### Added

- レビュータスクの完了機能を追加。ContractS CLMから取得した契約書のレビュー完了後、`complete_task`ツールでレビュータスクを完了にするステップを追加。

### Changed

- 契約書ダウンロード時のパラメータを明確化（`type: "docx"`, `finalized_review_download: false`を明示）。
- 契約書ダウンロードとファイル確認のステップを1つに統合。

## [1.0.2] - 2026/05/11

### Added

- ContractS CLM連携機能を追加。`list_task`によるレビュータスク一覧取得、`download_document`による契約書ダウンロード機能を実装。
- レビュー対象の契約書取得方法として「方法A: ユーザーによるファイル添付」と「方法B: ContractS CLMからの取得」の2パターンを定義。
- レビュー結果のContractS CLMへの登録機能を追加（`update_document_version`によるバージョン更新、`create_document_from_uploaded_file`による新規登録）。

### Changed

- プラグインの説明文を「ContractS CLMと連動して自社基準と法令に基づく契約書レビューを実施するスキル」に変更。
- MCP設定にContractS CLM（`contracts-clm`）を追加。
- スキル名を`contract-review`に変更し、説明文にCLM連携の記述を追加。

## [1.0.1] - 2026/05/07

### Changed

- Gmail MCPのURLを`https://gmailmcp.googleapis.com/mcp/v1`に更新。

## [1.0.0] - 2026/03/24

### Added

- Legalプラグイン初版リリース。
- `contract-review`スキルを追加。組織の交渉プレイブックに基づく契約書レビュー、リスク重大度分類（GREEN/YELLOW/RED）、修正案（レッドライン）生成機能を実装。
