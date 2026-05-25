# Changelog

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
