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
- .claude/skills/common/     : 汎用 Skills（プロジェクト横断）
- .claude/skills/project/    : プロジェクト固有 Skills
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
- 詳細は `.claude/skills/common/git-workflow.md` を参照

### Git Workflow
- 「コミットして」→ 自律的にコミットを実行（確認不要）
- 「プッシュして」→ 自律的にプッシュを実行
- 詳細は `.claude/skills/common/git-workflow.md` を参照

### エラー修正ルール
- 自動修正の前に必ずユーザーに報告・確認する
- 自動修正は最大 3 回まで
- 詳細は `.claude/skills/common/error-handling.md` を参照

### 禁止事項
- ハードコードされた AWS アカウント ID・ARN
- ハードコードされたシークレット・パスワード
- テストコード内の実際の AWS リソースへのアクセス

---

## Skills の読み込み設定

### 汎用 Skills（`.claude/skills/common/`）
どのプロジェクトでもそのまま使える共通ルール：

| スキル | 用途 |
|---|---|
| `git-workflow.md` | Git コミット・プッシュの標準ルール |
| `error-handling.md` | エラー解析・修正ワークフロー |
| `test-workflow.md` | テスト実行・結果報告 |
| `doc-writer.md` | ドキュメント生成スタイル |

### プロジェクト固有 Skills（`.claude/skills/project/`）
このプロジェクトの技術スタックに依存するルール：

| スキル | 用途 |
|---|---|
| `python-lambda.md` | Lambda ハンドラの構造・規約 |
| `sam-architect.md` | SAM テンプレートの設計原則 |
