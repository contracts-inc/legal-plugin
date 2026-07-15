# Changelog

## [1.2.0] - 2026/07/15

### Added

- 交渉担当者向けスキル第2弾 `legal-handoff`（UC2）を追加。社内法務へのレビュー依頼を「往復ゼロ」にする依頼パッケージ（背景・取引スキーム・論点4点セット・関連法令条文）を生成し、CLMタスクコメントとして投稿。e-Gov法令MCPによる実条文引用に対応。

## [1.1.0] - 2026/07/15

### Added

- 交渉担当者（事業部門）向けスキル第1弾 `clause-review`（UC1）を追加。業種別プレイブック照合による赤黄緑判定＋レッドライン＋交渉トーク・譲歩ライン生成。業種別プレイブック3本（商社・製薬・人材）を同梱。
- `skills/_shared/` に共有アセット（SSoT）を追加。
  - `industry_presets.md`：業種プリセット（trading/pharma/staffing）。業種はパラメータ化し、業種別のスキル複製はしない。
  - `clm_rules.md`：ContractS CLM MCP共通ルール（タスクURL固定形式・pageSize=100・書き込みは承認後）。
  - `sample_contracts/`：逸脱条項を仕込んだデモ用サンプル契約書3本＋仕込み一覧README（期待判定の突合表付き）。CLM未接続時はサンプルにフォールバックし、デモを止めない。
- `RELEASING.md` を追加。「1スキル＝1PR＝1リリース＝1Xポスト」のリリース運用を明文化。

### Changed

- `review-contract` と `clause-review` の使い分けを明確化。`review-contract` は法務担当者向け・曖昧なレビュー依頼のデフォルト、`clause-review` は事業部門の交渉担当者向け（業種指定・交渉トーク文脈）としてトリガー文言の重複を解消。両SKILL.mdとREADMEに使い分け表を追加。
- README.mdを再構成。「法務担当者向け」「交渉担当者向け」の2ペルソナでスキルを整理し、ディレクトリ構成・カスタマイズガイドを更新。

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
