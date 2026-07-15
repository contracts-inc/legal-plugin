# リリース運用

本リポジトリは「**1スキル ＝ 1 PR ＝ 1 リリース ＝ 1 Xポスト**」を原則として運用する。

## フロー

1. スキル単位でブランチを切り、PRを作成する（例：`feature/uc2-legal-handoff`）。相互依存が強い変更（例：`clause-review` と `review-contract` の使い分け調整）は同一PR＝同一リリースにまとめてよい。
2. PRには `.claude-plugin/plugin.json` のバージョン更新と `CHANGELOG.md` への記載（Keep a Changelog形式：Added/Changed）を含める。
3. マージ後、`vX.Y.Z` タグを打ち、GitHub Release を作成する（Releaseノート＝CHANGELOGの該当バージョンの内容）。
4. Release公開後、対応するXポストを投稿し、ReleaseノートにポストURLを追記する。

## バージョニング

- スキル追加＝minorを上げる（例：1.1.0 → 1.2.0）
- 既存スキルの修正・文言調整のみ＝patchを上げる（例：1.1.0 → 1.1.1）
