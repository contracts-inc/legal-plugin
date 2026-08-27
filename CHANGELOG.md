# Changelog

## [1.1.4] - 2026/08/27

### Changed

- `review-contract` スキルの「関連コメントの取得」で使用するコメント取得ツールを、非推奨の`list_task_comment`から`list_comment`に差し替え（`SKILL.md`）。`list_comment`は対象リソースの指定（`resource_type` / `resource_id`）が任意で、指定しなければタスクと契約書を横断して取得する仕様のため、**ツール名だけを差し替えると意図せず横断取得になる**。レビュータスクのコメントを取得する箇所では`resource_type="TASK"`と`resource_id`（対象タスクのID）の指定を明記した。コメント添付ファイルIDの取得元を示す注記も同様に差し替え。あわせて「ContractS CLM」MCPでは`list_task_comment`／`list_document_comment`が非推奨となり`list_comment`に統合された（旧ツールの動作は維持される）。コメント一覧の応答には条件に合致する総件数（`total_count`）が含まれるようになったが、本スキルでは未使用。

## [1.1.3] - 2026/08/13

### Changed

- `review-contract` スキルの「参照契約書の取得」を「関連契約・参照契約書の取得」に改題し、取得手順を拡張。非推奨の`search_references`を`search_documents`に差し替え、新たに手順4として`get_related_contracts`による関連契約ツリー展開（基本契約→個別契約→変更契約書＝変更履歴）を追加。渡す契約IDは手順3で選択した参照契約書のもの（`search_documents`のレスポンスに含まれる contractId）に限定し、レビュー対象自身の契約IDは不要である旨を明記（未締結のレビュー対象は契約IDを取得できず、方法Bで判明するのは documentId のため）。本文で明示的に参照されていない兄弟契約や過去の変更覚書も漏れなく把握し、レビューのインプットとする。`get_related_contracts`が関連契約を返さない場合は親子関係未登録の可能性がある旨をレビュー所見に含める注意事項を追記。
- `draft-contract` スキルの入力ソース取得（モードA・原契約検索）で使用する非推奨の`search_references`を`search_documents`に差し替え（`SKILL.md`および`references/input-sources.md`）。
- `draft-contract` スキルの後続フロー・カスタマイズ例（ContractS CLM 利用時）における原契約への紐付けツールを、非推奨の`relate_contracts`から`set_parent_contract`に差し替え。文言を「原契約（親）に子として紐付ける」に調整。
### Fixed
- `draft-contract` スキルの後続フロー「原契約への紐付け」に、**締結完了が前提である**ことを明記（`SKILL.md` ステップ10）。文書ID（documentId）と契約ID（contractId）が別体系であり、契約IDの取得手段が検索インデックス経由に限られ、インデックス登録が締結完了時にのみ行われるため、ドラフト登録直後は紐付けできない。従来はこの前提が書かれておらず、登録直後に「親子紐付けも行いますか？」と提案して契約ID取得に失敗する動作になっていた。登録直後に紐付けを提案してはならない旨、締結完了後に実行できる旨を案内する手順に修正。あわせて、**CLMの画面からも締結済みでなければ親子登録できないため締結前の回避策は存在しない**ことを明記し、画面操作を回避策として案内しないよう禁止。あわせてカスタマイズ例を「登録まで」と「締結完了後の紐付け」に分割し、`search_documents`の検索対象が`ORIGINAL`カテゴリの締結済み契約に限られるため**変更覚書（`MEMORANDUM`判定）は締結後でも自身の契約IDを取得できず、画面操作の案内が必要**である制約を追記。

## [1.1.2] - 2026/08/10

### Added

- `review-contract` スキルのレビュープロセス「3. 全体像の把握」に、契約書の添付ファイルの取得手順を追加。方法B（ContractS CLMからの取得）の場合のみ、`list_attachment_files`ツールで契約書に添付されたファイルの一覧を取得し、ファイル名から内容を推定してレビューに有用な資料（見積書、仕様書、SOW、相手方からの修正依頼、交渉経緯資料など）の候補をユーザーに提示、選択されたファイルを`download_attachment`ツールでダウンロードしてレビューのインプットに追加するフローを定義。契約書本文と添付資料の矛盾・不整合は指摘事項に含める。

### Changed

- `review-contract` スキルの「関連コメントの取得」を拡張。`list_task_comment`のレスポンスに`attachmentFiles`（`attachmentFileId` / `attachmentFileName`）が含まれる場合、`download_attachment`ツールでダウンロードしてレビューのインプットに追加する手順を追加（方法Bの場合のみ）。
- 添付ファイル取得の制約・注意事項を明記。`download_attachment`のダウンロードURLは有効期限が300秒（5分）で期限切れの場合は再取得する、`list_attachment_files`はコメントに添付されたファイルを含まない、契約書の閲覧権限がない場合は一覧が空・ダウンロードが403となる、契約書・契約書コメント・作成依頼タスクコメント以外のコメントの添付ファイルは404となり再試行しない。
- README.md の `review-contract` 機能一覧に添付ファイル連携を追記。

## [1.1.1] - 2026/07/24

### Changed

- `review-contract` スキルのレビュープロセス「3. 全体像の把握」に、関連コメントの取得手順を追加。方法B（ContractS CLMからの取得）の場合のみ、`list_task_comment`ツールでレビュータスクに紐づくコメント（交渉経緯、レビュー依頼背景、注意事項など）を取得し、レビューのインプット情報として活用するフローを定義。
- `review-contract` スキルに「5. レビュー完了コメントの投稿」セクションを新規追加。方法B（ContractS CLMからの取得）の場合のみ、レビュー完了後に`post_task_comment`ツールでタスクの依頼者に対してレビュー完了コメントを投稿するフローを定義。コメント案をユーザーに提示し投稿前の確認を必須化。既存の「5. レビュータスクの完了」は「6. レビュータスクの完了」に番号を繰り上げ。

## [1.1.0] - 2026/07/17

### Added

- `draft-contract` スキルを新規追加（refs #7116）。原契約や雛形を参照し、変更覚書を代表ユースケースとした法務文書ドラフト（.docx）を生成する。入力ソースの3択（① コネクタ取得 / ② ファイル添付 / ③ 直接入力）、原契約からの正確な引用と変更前後の対比、推測禁止・`※要確認` 明示・ドラフト注記のガードレールを定義。
- 対象類型: 変更覚書 / 各種覚書・合意書 / NDA / 業務委託等の定型契約 / 発注書・注文書 / 通知書・同意書。文書類型の判別はモデルの知識で行い、類型ごとの構成ヒントは `generation-rules.md` に集約。
- 生成モードを「既存契約の一部変更（変更覚書等）」と「雛形からの新規作成」の2つに明確化。既存契約の変更時は、コネクタ接続時に対象契約を検索して特定する手順を定義（ContractS CLM 利用時は `search_references` で候補検索）。
- 生成後の後続フロー（任意・コネクタ接続時）を定義: ドラフトのCLM登録（登録先フォルダはユーザーに確認）→ レビュー依頼 → 原契約への関連契約紐付け。スキル本体は製品非依存の記述とし、ContractS CLM の具体ツール名（`list_folder` / `get_upload_url` / `create_document_from_uploaded_file` / `relate_contracts` 等）はカスタマイズ例として分離。
- `skills/draft-contract/references/` に `input-sources.md`（入力ソース選択フロー）、`generation-rules.md`（生成アプローチ・ガードレール・類型別の構成ヒント）、`review-criteria.md`（専門家レビューの要否判定基準）を追加。
- 雛形（テンプレート）は利用者の保管場所（① コネクタ: Google Drive / Salesforce / CLM 等）から取得する設計とし、同梱の `assets/` はサンプル（例）と位置づけ（必要に応じて自社雛形を配置可）。`amendment-format.md` は廃止し、変更覚書で雛形が無い場合は同梱の `assets/amendment-template.docx` を差し込みベースに使う。
- `skills/draft-contract/scripts/fill_docx.py`（python-docx による雛形差し込み）と、`skills/draft-contract/assets/amendment-template.docx`（汎用ダミーの変更覚書雛形）を追加。

### Changed

- `plugin.json` の説明文を、契約書レビューに加えて法務文書ドラフト生成を含む内容に更新。バージョンを 1.1.0 に更新。
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
