# CLAUDE.md

## プロジェクト概要
タスク管理 REST API（TODO CRUD）
仕様書ドリブン開発（SDD）のサンプルプロジェクト

## 技術スタック
- 言語: Python 3.13
- フレームワーク: AWS Lambda（ハンドラ形式）
- IaC: AWS SAM（template.yaml）
- データストア: DynamoDB
- テスト: pytest
- CI/CD: GitHub Actions

## ディレクトリ構成
- spec/        : 仕様書（Single Source of Truth）
- src/         : Lambda ハンドラのソースコード
- tests/       : テストコード（unit/ / integration/）
- template.yaml: SAM テンプレート（インフラ定義）
- docs/        : 開発ガイド・ドキュメント
- .github/     : GitHub Actions ワークフロー

## 命名規約
- Python: snake_case（変数・関数）/ PascalCase（クラス）
- API エンドポイント: /tasks, /tasks/{task_id}
- Lambda 関数名: TasksFunction

## コード生成ルール
- すべての関数に型アノテーションを付与すること
- すべての公開関数に docstring を付与すること
- エラーレスポンスは {"error": "メッセージ"} 形式で統一
- ログは print ではなく logger を使用すること

## Python 環境
- バージョン管理: pyenv（`pyenv local` でプロジェクト固定、`.python-version` = 3.13.12）
- 仮想環境: `.venv/`（`python -m venv .venv` で作成）
- パッケージは必ず仮想環境内にインストールすること（グローバル汚染禁止）
- テスト・コマンド実行前に仮想環境を有効化すること: `source .venv/bin/activate`
- 依存パッケージ: `src/requirements.txt`（本番用）、`pip install pytest`（テスト用）

## Git Commit Rules
- コミットメッセージは必ず英語で記述すること
- Conventional Commits 形式に従うこと:
  `<type>(<scope>): <subject>`
  `<body>（必要な場合）`
- type の種類:
  - feat: 新機能
  - fix: バグ修正
  - docs: ドキュメントのみの変更
  - refactor: リファクタリング
  - test: テストの追加・修正
  - chore: ビルド・設定ファイルの変更
- subject は動詞の原形で始めること（Add / Fix / Update など）
- subject は 50 文字以内
- body には変更の背景・理由を記載すること

## Git Workflow
- 「コミットして」「コミットをお願い」などコミットを依頼する言葉を
  受け取った場合は以下を自律的に実行すること：
  1. git status で未コミットの変更を確認
  2. git diff で変更内容を分析
  3. 変更内容から適切なコミットメッセージを英語で自動生成
  4. 変更が複数の関心事にまたがる場合は複数コミットに分割
  5. git commit を実行
  6. コミット完了をレポートする
  ※ コミット前にメッセージの確認は不要。自律的に判断して実行すること
- 「プッシュして」「プッシュをお願い」などプッシュを依頼する言葉を
  受け取った場合は以下を自律的に実行すること：
  1. git status で未プッシュのコミットを確認
  2. 現在のブランチ名を git branch --show-current で取得
  3. git push origin <現在のブランチ名> を実行
  4. プッシュ完了をレポートする

## 禁止事項
- ハードコードされた AWS アカウント ID・ARN
- ハードコードされたシークレット・パスワード
- テストコード内の実際の AWS リソースへのアクセス