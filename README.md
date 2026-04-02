# Task Management API (TODO CRUD)

## プロジェクト概要

仕様書ドリブン開発（SDD）で構築するタスク管理 REST API。

- **目的**: SDD + AI マルチエージェント + CI/CD を組み合わせた開発フローの実践
- **アーキテクチャ**: Cursor で仕様書を作成し、Claude Code がコード生成・テスト・Git 操作を自律実行。GitHub Actions が CI/CD を担い、AWS にサーバーレスアプリケーションをデプロイする
- **設計思想**: `spec/` 配下の仕様書を Single Source of Truth とし、コードはすべて仕様書から生成する

### 技術スタック

| カテゴリ | 技術 | 役割 |
|---|---|---|
| 言語 | Python 3.13 | Lambda ランタイム |
| コンピュート | AWS Lambda | API ハンドラの実行 |
| API | Amazon API Gateway | REST エンドポイントの公開 |
| データストア | Amazon DynamoDB | タスクデータの永続化 |
| IaC | AWS SAM | インフラ定義・ビルド・デプロイ |
| CI/CD | GitHub Actions | 自動テスト・自動デプロイ |
| テスト | pytest / シェルスクリプト | ユニットテスト / E2E テスト |
| ローカル DB | DynamoDB Local (Docker) | ローカル開発用のデータストア |
| 仕様書管理 | Cursor | YAML 仕様書の編集 |
| コード生成 | Claude Code | コード生成・Git 操作の自律実行 |

## システム構成図

```
┌─────────────────────────────────────────────────────────┐
│                    開発環境 (Mac)                         │
│                                                         │
│  ┌──────────┐    ┌─────────────┐    ┌────────────────┐  │
│  │  Cursor   │───▶│ spec/*.yaml │───▶│  Claude Code   │  │
│  │(仕様書編集)│    │ (仕様書)     │    │(コード生成/Git) │  │
│  └──────────┘    └─────────────┘    └───────┬────────┘  │
│                                             │           │
│  ┌──────────────────┐    ┌──────────────┐   │           │
│  │  Docker           │    │  SAM CLI     │   │           │
│  │  ┌──────────────┐ │    │  (ローカル    │   │           │
│  │  │DynamoDB Local │ │◀──│   API実行)   │   │           │
│  │  └──────────────┘ │    └──────────────┘   │           │
│  └──────────────────┘                        │           │
└──────────────────────────────────────────────┼───────────┘
                                               │ git push
                                               ▼
                                        ┌──────────────┐
                                        │   GitHub      │
                                        │   (VCS)       │
                                        └──────┬───────┘
                                               │ trigger
                                               ▼
                                    ┌────────────────────┐
                                    │  GitHub Actions     │
                                    │  ┌──────┐ ┌──────┐ │
                                    │  │ test │─▶│deploy│ │
                                    │  └──────┘ └──┬───┘ │
                                    └──────────────┼─────┘
                                                   │ OIDC
                                                   ▼
                                    ┌────────────────────┐
                                    │    AWS              │
                                    │  ┌──────────────┐  │
                                    │  │ API Gateway   │  │
                                    │  └──────┬───────┘  │
                                    │         ▼          │
                                    │  ┌──────────────┐  │
                                    │  │   Lambda      │  │
                                    │  └──────┬───────┘  │
                                    │         ▼          │
                                    │  ┌──────────────┐  │
                                    │  │  DynamoDB     │  │
                                    │  └──────────────┘  │
                                    └────────────────────┘
```

## 前提条件

以下のツールがインストールされていること：

| ツール | バージョン | 用途 | インストール |
|---|---|---|---|
| Python | 3.13 | ランタイム | `pyenv install 3.13.12` |
| Node.js | 18+ | Claude Code CLI | [公式サイト](https://nodejs.org/) |
| Docker Desktop | 最新 | DynamoDB Local / SAM local | [公式サイト](https://www.docker.com/products/docker-desktop/) |
| AWS CLI | v2 | AWS 操作・SSO 認証 | `brew install awscli` |
| AWS SAM CLI | >= 1.157 | ビルド・デプロイ | `brew install aws-sam-cli` |
| Claude Code | 最新 | コード生成・Git 操作 | `npm install -g @anthropic-ai/claude-code` |
| Cursor | 最新 | 仕様書の編集 | [公式サイト](https://cursor.sh/) |
| jq | 最新 | E2E テストの JSON 解析 | `brew install jq` |
| git | 最新 | バージョン管理 | `brew install git` |
| pyenv | 最新 | Python バージョン管理 | `brew install pyenv` |

## 初回セットアップ手順（ゼロから始める場合）

### 1. リポジトリのクローン

```bash
git clone https://github.com/<YOUR_USER>/sdd-todo-api.git
cd sdd-todo-api
```

### 2. Python 仮想環境の作成

```bash
# pyenv local により .python-version で Python 3.13.12 が自動選択される
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
pip install pytest
```

### 3. Claude Code のインストールとログイン

```bash
npm install -g @anthropic-ai/claude-code
claude login
```

### 4. AWS SSO の設定

```bash
aws configure sso
```

プロンプトに従い入力：

| 項目 | 値 |
|---|---|
| SSO session name | `development-<yourname>` |
| SSO start URL | `<YOUR_SSO_URL>` |
| SSO region | `ap-northeast-1` |
| CLI default client Region | `ap-northeast-1` |
| CLI default output format | `json` |
| CLI profile name | `<YOUR_PROFILE_NAME>` |

ログイン確認：

```bash
aws sts get-caller-identity --profile <YOUR_PROFILE_NAME>
```

### 5. GitHub Secrets の設定

リポジトリの Settings > Secrets and variables > Actions に以下を登録：

| Secret 名 | 値 |
|---|---|
| `AWS_ROLE_ARN` | IAM Role の ARN（OIDC 用） |
| `AWS_REGION` | `ap-northeast-1` |

### 6. Docker Desktop の設定

1. Docker Desktop を起動
2. Settings > Advanced > 「Allow the default Docker socket to be used」を ON

### 7. DOCKER_HOST の設定（Mac の場合）

```bash
# ~/.zshrc に追記
export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
source ~/.zshrc
```

### 8. env.local.json の作成（ローカル SAM 用・git 管理外）

```json
{
  "TasksFunction": {
    "TABLE_NAME": "TasksTable",
    "DYNAMODB_ENDPOINT": "http://host.docker.internal:8000",
    "AWS_DEFAULT_REGION": "ap-northeast-1",
    "AWS_ACCESS_KEY_ID": "dummy",
    "AWS_SECRET_ACCESS_KEY": "dummy"
  }
}
```

### 9. .env ファイルの作成（E2E テスト用・git 管理外）

`.env.local`:

```
BASE_URL=http://127.0.0.1:3000
```

`.env.production`:

```
BASE_URL=https://<YOUR_API_ID>.execute-api.ap-northeast-1.amazonaws.com/Prod
```

## ローカル開発のワークフロー

### 1. DynamoDB Local の起動

```bash
docker compose up -d
```

### 2. テーブルの作成（初回のみ・docker volume 削除後も必要）

```bash
AWS_ACCESS_KEY_ID=dummy \
AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb create-table \
  --table-name TasksTable \
  --attribute-definitions AttributeName=task_id,AttributeType=S \
  --key-schema AttributeName=task_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

### 3. テーブルの存在確認

```bash
AWS_ACCESS_KEY_ID=dummy \
AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb list-tables \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

### 4. SSO ログイン（トークン期限切れ時）

```bash
aws sso login --profile <YOUR_PROFILE_NAME>
```

### 5. SAM ビルドとローカル起動

```bash
sam build && \
DOCKER_HOST=unix://$HOME/.docker/run/docker.sock \
AWS_PROFILE=<YOUR_PROFILE_NAME> \
sam local start-api --env-vars env.local.json
```

### 6. ユニットテストの実行

```bash
source .venv/bin/activate
pytest tests/unit/ -v
```

### 7. E2E テストの実行（ローカル）

```bash
ENV=local bash tests/e2e/test_api.sh
```

## Claude Code を使った開発フロー

### 1. 仕様書の更新

`spec/api/tasks.yaml` を Cursor で編集

### 2. Claude Code でコード生成

```bash
claude
```

プロンプト例：

```
spec/api/tasks.yaml の変更を読み込み、
src/handlers/tasks.py を更新してください。
テストも更新してパスすることを確認してください。
```

### 3. コミット（Claude Code に依頼）

「コミットして」と入力するだけで自動コミット

### 4. プッシュ（Claude Code に依頼）

「プッシュして」と入力するだけで自動プッシュ

### 5. GitHub Actions で自動テスト・デプロイ

GitHub > Actions タブで確認

## Claude Code による自動エラー修正

### 基本的な使い方

テストが失敗した場合や実行エラーが発生した場合、Claude Code に以下のように依頼するだけでエラーの解析・修正を自動実行します：

```
テストが失敗しています。エラーを解析して修正してください
```

### ワークフロー

Claude Code は以下の手順で動作します：

1. エラーを収集・分析する
2. 推測される原因と対処方法の選択肢をユーザーに提示する
3. ユーザーが選択した方法で修正を実行する
4. テストを再実行して修正が有効か確認する
5. 修正完了をレポートする

### 重要なルール

- 自動修正の前に必ずユーザーに確認する（スキップ不可）
- 自動修正は最大 3 回まで
- 3 回で解決しない場合は手動対応を求める
- 本番環境への影響がある修正は必ず事前確認

詳細は `docs/universal/error-workflow.md` を参照。

## デプロイ後の確認

### 1. GitHub Actions の確認

GitHub > Actions タブ > 最新のワークフローを確認

### 2. CloudWatch ログの確認

```bash
aws logs tail /aws/lambda/sdd-todo-api-TasksFunction-XXXX \
  --profile <YOUR_PROFILE_NAME> \
  --since 5m
```

### 3. API Gateway URL の確認

```bash
aws cloudformation describe-stacks \
  --stack-name sdd-todo-api \
  --profile <YOUR_PROFILE_NAME> \
  --query "Stacks[0].Outputs[?OutputKey=='TasksApi'].OutputValue" \
  --output text
```

### 4. E2E テストの実行（本番）

```bash
ENV=production bash tests/e2e/test_api.sh
```

## API の動作確認

```bash
# タスク作成
curl -X POST http://127.0.0.1:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "牛乳を買う"}'

# タスク一覧取得
curl http://127.0.0.1:3000/tasks

# タスク取得
curl http://127.0.0.1:3000/tasks/{task_id}

# タスク更新
curl -X PUT http://127.0.0.1:3000/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# タスク削除
curl -X DELETE http://127.0.0.1:3000/tasks/{task_id}
```

## トラブルシューティング

### 1. DynamoDB Local の認証エラー

- **症状**: `Unable to locate credentials`
- **原因**: AWS CLI のデフォルト認証情報が未設定
- **解決**: コマンド実行時に以下を付与

```bash
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy aws dynamodb ...
```

### 2. SAM local が Docker に接続できない

- **症状**: `Error: Running AWS SAM projects locally requires a container runtime.`
- **原因**: Docker Desktop のソケットパスが異なる
- **解決**: 以下を指定して起動、または `~/.zshrc` に export して永続化

```bash
DOCKER_HOST=unix://$HOME/.docker/run/docker.sock sam local start-api ...
```

### 3. env.local.json の環境変数が Lambda に渡らない

- **症状**: `DYNAMODB_ENDPOINT=None` がログに表示される
- **原因**: `template.yaml` の `Environment/Variables` に `DYNAMODB_ENDPOINT` が未定義
- **解決**: `template.yaml` に `DYNAMODB_ENDPOINT: ""` を追加（`env.local.json` は定義済み変数の上書きのみ可能）

### 4. DynamoDB Local のテーブルが消える

- **症状**: `ResourceNotFoundException`
- **原因**: Docker コンテナ再起動でデータが消える
- **解決**: `docker compose up -d` で再起動後、テーブルを再作成する（`docker-compose.yml` にボリューム設定済みだが、`docker compose down -v` でボリュームを削除した場合は再作成が必要）

### 5. 本番環境で Invalid endpoint エラー

- **症状**: `ValueError: Invalid endpoint:`
- **原因**: `DYNAMODB_ENDPOINT` が空文字のまま boto3 に渡される
- **解決**: コード側で `os.environ.get("DYNAMODB_ENDPOINT") or None` を使用（対応済み）

### 6. SSO トークン期限切れ

- **症状**: `Token has expired`
- **解決**:

```bash
aws sso login --profile <YOUR_PROFILE_NAME>
```

### 7. GitHub Actions で S3 バケットエラー

- **症状**: `S3 Bucket not specified`
- **解決**: `sam deploy` に `--resolve-s3` を追加（対応済み）

### 8. SAM CLI が python3.13 をサポートしない

- **症状**: `'python3.13' runtime is not supported`
- **解決**: SAM CLI をアップグレード

```bash
brew upgrade aws-sam-cli
```

## AWS リソース一覧

デプロイにより以下の AWS リソースが作成されます：

| リソース | 名前/説明 | 自動管理 |
|---|---|---|
| Lambda 関数 | `TasksFunction` — CRUD ハンドラ | SAM |
| API Gateway | REST API — 5 エンドポイント | SAM |
| DynamoDB テーブル | `TasksTable` — パーティションキー: `task_id` | SAM |
| IAM ロール | Lambda 実行ロール + DynamoDB CRUD ポリシー | SAM |
| CloudWatch Logs | Lambda 関数のロググループ | AWS 自動 |
| S3 バケット | SAM デプロイ用アーティファクト格納 | SAM (`--resolve-s3`) |

## 開発効率化の設定（任意）

`~/.zshrc` に以下を追加すると、毎回の環境変数指定を省略できます：

```bash
export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
export AWS_PROFILE=<YOUR_PROFILE_NAME>
```

追加後は `source ~/.zshrc` で反映してください。
