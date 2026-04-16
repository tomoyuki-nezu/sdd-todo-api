# CLAUDE.md

---

## プロジェクト固有設定

> 次のプロジェクトではこのセクションを書き換えること

### プロジェクト概要
タスク管理 REST API（TODO CRUD）
仕様書ドリブン開発（SDD）のサンプルプロジェクト

### 技術スタック
- 言語: Python 3.13
- フレームワーク: AWS Lambda（ハンドラ形式）
- IaC: AWS SAM（template.yaml）
- データストア: DynamoDB
- テスト: pytest
- CI/CD: GitHub Actions

### ディレクトリ構成
- spec/                     : 仕様書（Single Source of Truth）
- src/                      : Lambda ハンドラのソースコード
- tests/                    : テストコード（unit/ / e2e/）
- template.yaml             : SAM テンプレート（インフラ定義）
- docs/universal/            : 汎用ドキュメント（プロジェクト横断）
- docs/project/              : プロジェクト固有ドキュメント
- .claude/skills/<name>/     : Skills（Anthropic 正式仕様・各フォルダに SKILL.md）
- .github/                   : GitHub Actions ワークフロー

### 命名規約
- Python: snake_case（変数・関数）/ PascalCase（クラス）
- API エンドポイント: /tasks, /tasks/{task_id}
- Lambda 関数名: TasksFunction

### Python 環境
- バージョン管理: pyenv（`pyenv local` でプロジェクト固定、`.python-version` = 3.13.12）
- 仮想環境: `.venv/`（`python -m venv .venv` で作成）
- パッケージは必ず仮想環境内にインストールすること（グローバル汚染禁止）
- テスト・コマンド実行前に仮想環境を有効化すること: `source .venv/bin/activate`
- 依存パッケージ: `src/requirements.txt`（本番用）、`pip install pytest`（テスト用）

---

## 汎用設定

> 次のプロジェクトでもそのまま使える共通ルール

### コード生成ルール
- すべての関数に型アノテーションを付与すること
- すべての公開関数に docstring を付与すること
- エラーレスポンスは {"error": "メッセージ"} 形式で統一
- ログは print ではなく logger を使用すること

### Git Commit Rules
- コミットメッセージは必ず英語で記述すること
- Conventional Commits 形式に従うこと
- 詳細は `.claude/skills/git-workflow/SKILL.md` を参照

### Git Workflow
- 「コミットして」→ 自律的にコミットを実行（確認不要）
- 「プッシュして」→ 自律的にプッシュを実行
- 詳細は `.claude/skills/git-workflow/SKILL.md` を参照

### エラー修正ルール
- 自動修正の前に必ずユーザーに報告・確認する
- 自動修正は最大 3 回まで
- 詳細は `.claude/skills/error-handling/SKILL.md` を参照

### 質問ドキュメントのルール

複雑な判断が必要な場合は一問一答ではなく質問ドキュメントを作成すること。

**作成のトリガー（以下のいずれかに該当する場合）：**
- 質問数が 3 つ以上になる
- 質問間に依存関係がある
- 決定内容を記録として残す必要がある
- アーキテクチャ・方針に関わる重要な決定

**作成手順：**
1. `.claude/questions/YYYYMMDD-<topic>.md` を作成する
2. `docs/universal/question-document-spec.md` のテンプレートに従って記述する
3. ユーザーに以下の形式で通知する：
   「複数の決定事項があるため質問ドキュメントを作成しました。
    `.claude/questions/YYYYMMDD-topic.md`
    Cursor でファイルを開いて回答を記入してください。
    記入が完了したら『回答を読んで実行して』と伝えてください。」

**読み取りのトリガー（「回答を読んで実行して」と言われた場合）：**
1. 指定された質問ドキュメントを読み込む
2. 回答の解釈を「Claude Code が実行するアクション」欄に記入する
3. 実行内容のサマリーをユーザーに提示して確認を取る
4. 承認後に実行する
5. 完了後にステータスを「実行済み」に更新してコミットする

### 禁止事項
- ハードコードされた AWS アカウント ID・ARN
- ハードコードされたシークレット・パスワード
- テストコード内の実際の AWS リソースへのアクセス

---

## Skills の読み込み設定

各スキルは `.claude/skills/<kebab-case>/SKILL.md` に配置する（Anthropic 正式仕様）。

### 汎用 Skills
どのプロジェクトでもそのまま使える共通ルール：

| スキル | 用途 |
|---|---|
| `git-workflow/` | Git コミット・プッシュの標準ルール |
| `error-handling/` | エラー解析・修正ワークフロー |
| `test-workflow/` | テスト実行・結果報告 |
| `doc-writer/` | ドキュメント生成スタイル |
| `question-doc/` | 質問ドキュメントによる意思決定フロー |

### プロジェクト固有 Skills
このプロジェクトの技術スタックに依存するルール：

| スキル | 用途 |
|---|---|
| `python-lambda/` | Lambda ハンドラの構造・規約 |
| `sam-architect/` | SAM テンプレートの設計原則 |

---

## セキュリティ設定

### 設定ファイル
.claude/settings.json にセキュリティのベースライン設定が含まれています。
詳細は docs/universal/security-settings.md を参照してください。

### 重要なルール
- .env ファイル・シークレット・認証情報は絶対に読み取らないこと
- rm -rf コマンドは実行しないこと
- 本番 AWS 環境への操作は Human の明示的な許可が必要
- セキュリティ上の問題を発見した場合は即座に Human に報告すること

### /permissions で定期確認
セッション中に権限が蓄積していないか定期的に /permissions で確認すること。
