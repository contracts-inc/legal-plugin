# ContractS CLM MCP Legal Plugin

ContractS CLMと連動して自社基準と法令に基づく契約書レビューを実施し、あわせて法務文書のドラフト生成を支援するClaude Codeプラグインです。

## 概要

組織の契約交渉プレイブックに照らし合わせて契約書を分析し、基準からの逸脱を特定・重大度分類し、修正案（レッドライン）を生成します。ContractS CLMと連携し、割り当てられたレビュータスクから契約書を取得してレビューすることも可能です。

さらに、原契約や雛形を参照して変更覚書をはじめとする法務文書のドラフト（.docx）を生成するスキルと、レビューの判断基準となる交渉プレイブック自体を構築・更新するスキルを備えています。

## スキル

### build-playbook

交渉プレイブック構築スキル。`review-contract` が参照するプレイブック（`playbook.md`）を整備します。

- 3つのモード（新規構築 / 更新・改訂（規程・方針ドリブン） / 更新・改訂（レビュー実績ドリブン））。品質点検は独立モードではなく出力前セルフチェックとしてA/B共通で必ず実施
- 「棚卸ししたい」という依頼も更新・改訂として受け付け、改訂候補0件なら「改訂不要」と報告して終了
- 6系統の根拠情報の収集（ヒアリング / 社内規程・契約書雛形 / 過去契約・交渉実績 / インシデント事例 / 法令 / レビュー実績・版更新記録）
- 契約書雛形からの類型特定と事実上の自社基準の抽出（雛形がある類型・無い類型、立場別の雛形差、雛形の陳腐化を検出）
- プレイブック冒頭のメタデータブロック（版数・最終更新日時・承認者・承認日・次回見直し予定・対象範囲）。最終更新日時を改訂時の情報収集の起点として使用
- ヒアリングは「決定項目（何を決めるか）」で定義し、質問文と選択肢はモデルが組み立てる（契約実務の一般知識をスキルに列挙しない）
- 回答は標準スケール（要否 / 可否 / 数値 / 個別選択肢）で番号回答でき、一括フォームにもそのまま転記可能
- 見落としやすい規制フック（下請法の適用判定・書面交付、フリーランス法の条件明示、派遣法の抵触日通知、越境移転の根拠、独禁法の拘束条件など）は明示的に保持
- プレイブックを適切な大きさに保つ（基準は削らず、大きくなったら**契約類型ごとに分割**。分割の判定は出力時にスキルが行い、ユーザーにファイル構成を質問しない。立場では分割せず同一類型内で書き分け、共通部分は全ファイルで同一に保つ）
- 法令の条文・数値はプレイブックに転記せずe-Govで都度取得（法改正での陳腐化を防ぐ）
- すべての質問・判断依頼をフォーム形式に統一（番号で回答、常に「保留」を用意、1フォーム7問まで、確認事項が8件以上なら記入用フォームをファイルで配布）
- 質問文の自己完結（現行プレイブック・規程・レビュー記録・法令の引用や条番号・節番号の参照を質問に含めず、判断材料は件数などの数値のみ）
- セクション・契約類型・立場ごとに1つずつ完結させる進行と、長い一覧（実績集計・セルフチェックの継続課題・差分・確認事項・本文）のファイル出力
- 実績レンジの集計による許容範囲・フォールバックの裏付け（契約管理システム・契約管理台帳・ファイル添付・メールのいずれの経路にも対応し、出所と件数を明示）
- インシデント・トラブル事例（事例集・監査報告・インシデント台帳）からの「許容できない条件」「エスカレーション基準」「RED判定」の導出
- ContractS CLMの過去のレビュー記録・版更新の変更理由の分析による、明文化されていない論点の検出とルールの追加・変更
- 「推測で基準値を作らない」原則と、根拠（出所）の明示・不足情報の `※要確認` 明示
- レビュー時の根拠参照（「プレイブック §2.1」）を壊さないセクション番号の固定
- 取引先名・案件名・個人名を残さない匿名化と、法務責任者の承認を前提としたガードレール
- ファイル構成・配置先・ビルド手順をユーザーに質問せず、スキル側で判断（法務的な判断のみをユーザーに委ねる）
- 初回・新規構築時に「用意すると良いインプット」を提示（所在・効果・無い場合の代替を明示。すべて任意で、ヒアリングのみでも作成可能）
- 人がレビューしやすいWord出力（`playbook.docx`）と、Wordが使えない場合のフォールバックとしてのレビューシート（`review-sheet.csv`）、`review-contract` 連携用の `playbook.md` を常に出力
- レビュー観点を3点程度に絞って依頼し、返却されたWordコメント・変更履歴・レビューシートを抽出スクリプトで機械的に回収して反映

### review-contract

契約書レビュースキル。以下の機能を提供します。

- 組織のプレイブックに基づく条項ごとの分析
- リスク重大度分類（GREEN / YELLOW / RED）
- 変更履歴付き修正案（レッドライン）の生成
- レビュー指摘のWordコメント挿入
- ContractS CLMとの双方向連携（タスク取得・ドキュメント登録）
- 添付ファイル連携（契約書・タスクコメントの添付資料をレビューのインプットに取り込み、本文との整合性を検証）

### draft-contract

法務文書ドラフト生成スキル。以下の機能を提供します。

- 変更覚書を代表ユースケースとした、汎用的な法務文書ドラフト（.docx）の生成（変更覚書 / 各種覚書・合意書 / NDA / 業務委託等の定型契約 / 発注書・注文書 / 通知書・同意書）
- 入力ソースの選択（① コネクタ取得 / ② ファイル添付 / ③ 直接入力）による原契約・雛形の取り込み
- 原契約の正式名称・締結日・当事者・対象条項を正確に引用した、変更前後の対比
- 「推測で条項や数値を作らない」原則と、不足情報の `※要確認` 明示
- ドラフト注記の付与と、確定前の法務レビューを前提としたガードレール
- 生成後の後続フロー（任意・コネクタ接続時）: ドラフトのCLM登録 → レビュー依頼 → 原契約への関連契約紐付け

## ディレクトリ構成

配布物は `src/` を編集し、`scripts/build.py` でプラットフォーム別に `dist/<platform>/` へ生成します。

```
.
├── src/                                 # 配布物のソース（ここを編集する）
│   ├── .claude-bundle/              # claudeビルド専用
│   │   └── plugin.json              # プラグインメタデータ
│   ├── .chatgpt-bundle/             # chatgptビルド専用
│   │   └── plugin.json              # プラグインメタデータ
│   ├── .copilot-bundle/             # copilotビルド専用（中身をパッケージルートへ展開）
│   │   ├── manifest.json            # Teamsアプリマニフェスト
│   │   ├── color.png                # アイコン（カラー）
│   │   └── outline.png              # アイコン（アウトライン）
│   ├── .mcp.json                    # MCP設定（copilotビルドでは除外）
│   └── skills/
│       ├── build-playbook/
│       │   ├── SKILL.md             # スキル定義（7ステップ・3モード）
│       │   ├── references/
│       │   │   ├── interaction-format.md # 対話フォーマット規約（フォーム形式・引用禁止・出力量）
│       │   │   ├── playbook-schema.md   # 既定セクション構成・根拠・匿名化・分割規則
│       │   │   ├── interview-guide.md   # 決定項目（何を決めるか）・回答スケール・規制フック
│       │   │   ├── evidence-sources.md  # 根拠情報の収集フロー（6系統）
│       │   │   ├── review-output.md     # レビュー用出力の体裁・観点の絞り方・FB取り込み
│       │   │   └── update-policy.md     # 改訂トリガー・差分提示・セルフチェック・実績分析
│       │   ├── scripts/
│       │   │   └── extract_review_feedback.py # Wordコメント・変更履歴・レビューシートの抽出
│       │   └── assets/
│       │       ├── interview-form.md    # 一括フォームの書式
│       │       └── playbook-template.md # プレイブックの骨格と記入例
│       ├── review-contract/
│       │   ├── SKILL.md             # スキル定義（レビュー手順）
│       │   └── references/
│       │       ├── playbook.md      # 交渉プレイブック（カスタマイズ可能）
│       │       └── comment-format.md    # Wordコメント挿入ガイドライン
│       └── draft-contract/
│           ├── SKILL.md             # スキル定義（ドラフト生成手順）
│           ├── references/
│           │   ├── input-sources.md     # 入力ソース選択フロー（ベクトル検索・雛形保管場所）
│           │   ├── generation-rules.md  # 生成アプローチ・ガードレール・構成ヒント
│           │   └── review-criteria.md   # 専門家レビューの要否判定基準
│           ├── scripts/
│           │   └── fill_docx.py     # python-docx による雛形差し込み
│           └── assets/
│               └── amendment-template.docx  # 変更覚書のサンプル雛形（例。自社雛形の配置も可）
├── scripts/
│   └── build.py                     # src/ からプラットフォーム別バンドルを生成
├── .github/workflows/
│   └── package-plugin.yml           # ビルドとZIPパッケージのCI
├── dist/                            # ビルド出力（gitignore対象）
├── CHANGELOG.md
└── README.md
```

### プラットフォーム別ビルド

`src/` 配下のMarkdownはJinja2テンプレートとして扱われ、`platform` 変数で分岐できます。

```markdown
{% if platform == 'copilot' %}
（copilot向けの記述）
{% else %}
（その他のプラットフォーム向けの記述）
{% endif %}
```

対応プラットフォームは `chatgpt` / `claude` / `copilot` です。

### プラットフォーム専用ディレクトリ

`src/` 直下の `*-bundle/` ディレクトリは、対象プラットフォームのビルドにのみ含まれます。配置先は `build.py` の `PLATFORM_DIRS` で定義しています。

| ソース | 対象 | バンドル内の配置先 |
| --- | --- | --- |
| `src/.claude-bundle/` | `claude` | `.claude-plugin/` |
| `src/.chatgpt-bundle/` | `chatgpt` | `.codex-plugin/` |
| `src/.copilot-bundle/` | `copilot` | パッケージルート直下（ディレクトリ名を除去） |

`copilot` で中身をルートに展開するのは、Teamsアプリマニフェストが `icons` や `agentSkills` をパッケージルート基準の相対パス（`color.png` / `./skills/review-contract`）で参照するためです。生成後のバンドルは次の構成になります。

```
dist/copilot/
├── manifest.json
├── color.png
├── outline.png
└── skills/
    ├── review-contract/
    └── draft-contract/
```

ルート直下へ展開するため、`.copilot-bundle/` 内のファイル名が `src/` 直下のファイル名と衝突する場合はビルドが失敗します。

### バージョン管理

バージョンの唯一の情報源は **`CHANGELOG.md` の最新見出し**です。`build.py` が最上部の `## [x.y.z] - YYYY/MM/DD` を読み取り、各マニフェストの `version` にビルド時へ埋め込みます。

| 埋め込み先（ソース） | 対象 |
| --- | --- |
| `src/.claude-bundle/plugin.json` | `claude` |
| `src/.chatgpt-bundle/plugin.json` | `chatgpt` |
| `src/.copilot-bundle/manifest.json` | `copilot` |

そのため、リリース時に編集するのは `CHANGELOG.md` だけです。`src/` 側マニフェストの `version` はビルド時に必ず上書きされるプレースホルダで、値を更新する必要はありません（更新しても無視されます）。

CIのリリースタグも同じ値を使います。ローカルで確認する場合は次のコマンドを実行します。

```sh
python scripts/build.py --print-version
```

`CHANGELOG.md` の最新バージョンが `x.y.z` 形式でない場合、またはマニフェストが見つからない場合はビルドが失敗します（Copilotの `manifest.json` が3桁のsemverを要求するため）。

### プラットフォーム別の除外ファイル

`build.py` の `PLATFORM_EXCLUDED_FILES` で、特定プラットフォームのバンドルから除外するファイルを指定できます。

| ソース | 除外対象 | 理由 |
| --- | --- | --- |
| `src/.mcp.json` | `copilot` | `manifest.json` の `agentConnectors` でMCPサーバーを宣言するため二重定義になる |

`copilot` 向けにMCPサーバーを追加する場合は、`src/.mcp.json` ではなく `src/.copilot-bundle/manifest.json` の `agentConnectors` に定義してください。

## セットアップ

(ヘルプサイトのURLを記載)

### draft-contract の依存関係

ドラフト差し込みスクリプトは python-docx を使用します。

```sh
pip install python-docx
```

## カスタマイズ

### build-playbook

本スキルは**カスタマイズせずにそのまま利用する前提**です。決定項目（何を決めるか）、回答スケール、規制フック、実績集計や改訂候補判定のしきい値、改訂トリガー、出力前セルフチェックの項目はスキル内に既定値として作り込まれており、組織固有の運用はヒアリングで聴取して反映します。質問文と選択肢はモデルがその場で組み立てるため、質問票としてのカスタマイズも不要です（凍結した質問票が必要な場合は、組織側の資産として別に管理してください）。

評価シナリオは配布バンドルに含めず `evals/build-playbook.md` に置いています。スキルを変更した際の動作確認に使います。

成果物である `playbook.md` が組織固有の基準を担うため、カスタマイズはそちら（`review-contract` 側）で行います。`build-playbook` が生成した `playbook.md` を `src/skills/review-contract/references/playbook.md` に置き換えて再ビルドすると、組織全体に同一のレビュー基準を配布できます。

### review-contract

`src/skills/review-contract/references/playbook.md` を編集することで、以下の項目を自社の基準に合わせて設定できます。

- 各条項の自社基準（許容範囲の数値・条件）
- 許容できない条件（RED判定の基準）
- フォールバック（妥協案）の範囲
- エスカレーション基準と報告先
- 交渉の優先順位（Tier 1〜3）
- 修正案のフォーマット

### draft-contract

`src/skills/draft-contract/references/` 配下を編集することで、以下を自社の運用に合わせて設定できます。

- 入力ソースの取得フローと利用コネクタ、対象契約のベクトル検索、雛形の保管場所（Google Drive / Salesforce / CLM 等）（`input-sources.md`）
- 生成アプローチの許容範囲・ガードレール・類型別の構成ヒント（`generation-rules.md`）
- 専門家レビューの要否判定基準（`review-criteria.md`）
- 雛形のサンプル（`assets/`。例として同梱。必要に応じて自社雛形を配置可。実運用の雛形は原則コネクタの保管場所から取得）

同梱する雛形・サンプルはすべて汎用ダミーです。特定顧客・組織固有の情報や機密雛形は同梱しないでください。

## プライバシー / 免責

- 本プラグインはユーザーが投入する契約・雛形（機微情報）を、当該タスクの処理に限定して扱い、外部への保存・共有は行いません。
- 生成物はドラフト（草案）です。弁護士法に基づく法的な鑑定や助言（リーガルアドバイス）を提供するものではなく、確定前に必ず有資格の法務専門家によるレビューを受けてください。

## Claudeプラグインのパッケージ

カスタマイズしたスキルをzipファイルとしてパッケージするには、プロジェクトルートで以下のコマンドを実行します。ビルドにはJinja2が必要です。

```sh
pip install Jinja2
python scripts/build.py claude
cd dist/claude && zip -r ../../claude-skill-bundle.zip .
```

`zip` の対象は `./*` ではなく `.` を指定してください。`./*` はドットファイルにマッチしないため、`.claude-plugin/plugin.json` と `.mcp.json` が取りこぼされ、マニフェストのない不正なパッケージになります。

### 配布ZIPの構成要件

インストーラは **アーカイブ直下** のマニフェストを見てプラグインかどうかを判定します。次のエラーはこの構成が崩れている場合に出ます。

```
Plugin archive must contain .codex-plugin/plugin.json, .agent-plugin/plugin.json,
.claude-plugin/plugin.json, or plugin content such as skills/*/SKILL.md, .mcp.json, or .app.json
```

よくある原因は次の2つです。

1. **二重ZIP** — GitHub Actionsのアーティファクトはそれ自体がZIPです。ビルド済みZIPをアーティファクトにすると、ダウンロード時に「ZIPの中にZIP」になり拒否されます。CIではバンドルの中身をアーティファクトにしているため、ダウンロードしたZIPをそのままアップロードできます
2. **余計なトップレベルディレクトリ** — 親ディレクトリからZIPを作ると `my-plugin/` のような階層で包まれ、マニフェストが直下に来ません

構成は次のコマンドで検証できます（二重ZIP・余計な階層・必須ファイルの欠落を検出）。

```sh
python scripts/build.py claude --verify-archive claude-skill-bundle.zip
```

CIのリリースジョブでもZIP作成後に同じ検証を実行します。

### CIのビルド成果物

`package-plugin.yml` は2種類の入手経路を用意しています。どちらもアーカイブ直下がプラグインルートになっており、そのままインストーラにアップロードできます。

| 入手経路 | 内容 |
| --- | --- |
| Actionsのアーティファクト（`<platform>-skill-bundle`） | ダウンロードすると `<platform>-skill-bundle.zip` が得られ、その直下がバンドル |
| Releasesのアセット（`<platform>-skill-bundle.zip`） | `main` へのpush時に、`CHANGELOG.md` の最新バージョンをタグとして作成 |

## Claudeプラグインの配布

カスタマイズしたzipパッケージか、[Releases](https://github.com/contracts-inc/legal-plugin/releases)で配布するZipファイルを使用して組織にプラグインを配布します。

Claude公式の[組織向けのclaude-coworkプラグインを管理する](https://support.claude.com/ja/articles/13837433-%E7%B5%84%E7%B9%94%E5%90%91%E3%81%91%E3%81%AEclaude-cowork%E3%83%97%E3%83%A9%E3%82%B0%E3%82%A4%E3%83%B3%E3%82%92%E7%AE%A1%E7%90%86%E3%81%99%E3%82%8B)サポートページを参考に `legal-plugin.zip` を組織に配布してください。
