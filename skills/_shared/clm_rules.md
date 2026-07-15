# ContractS CLM MCP 共通ルール（legal-plugin 共通・SSoT）

1. **タスクリンクURL（固定形式）**
   `https://clm.contracts-cloud.com/ws/documents/{taskSource.taskSourceId}?nav=task`
   - `taskId` は使わない。フォールバックで別IDからURLを組み立てない。
   - `taskSource` が null または type が DOCUMENT 以外ならリンクなし。
   - `taskSource.deleted: true` はリンク生成可だが「（削除済）」と注記。
2. **list_task**：pageSize=100固定。大量取得は `created_from`/`created_to` で絞る。
3. **担当フィルタのデフォルト**：`get_me` でユーザーID取得→ `assignee[].taskAssigneeId` に含まれるもの＝自分担当。未完了＝`completedAt` キーが存在しないもの。件数指定がなければ上位5件、作成日降順のMarkdown表。
4. **大きい結果**：ファイルに保存し `jq` でフィルタしてから読み込む。全文読み込み禁止。
5. **書き込み系ツール**（`update_document_version` / `change_document_property_values` / `post_task_comment` / `complete_task` / `relate_contracts`）は必ず内容プレビュー→ユーザー承認→実行の順。
6. **デモフォールバック**：CLM MCP未接続・対象文書なしの場合は `_shared/sample_contracts/` のサンプルで続行し、「（サンプルデータで実演中）」と出力冒頭に明示。デモを止めない。
7. 出力は日本語を基本とする。
