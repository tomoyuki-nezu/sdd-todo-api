# Task Management API (TODO CRUD)

仕様書ドリブン開発（SDD）で構築するタスク管理 REST API

## 技術スタック

| カテゴリ | 技術 |
|---|---|
| 言語 | Python 3.13 |
| フレームワーク | AWS Lambda (ハンドラ形式) |
| IaC | AWS SAM (template.yaml) |
| データストア | Amazon DynamoDB |
| テスト | pytest |
| ローカル DB | DynamoDB Local (Docker) |

## 前提条件

以下のツールがインストールされていること：

| ツール | バージョン確認 | インストール |
|---|---|---|
| pyenv | `pyenv --version` | `brew install pyenv` |
| Python 3.13.12 | `python --version` | `pyenv install 3.13.12` |
| AWS SAM CLI >= 1.157 | `sam --version` | `brew install aws-sam-cli` |
| Docker Desktop | `docker --version` | [公式サイト](https://www.docker.com/products/docker-desktop/) |
| AWS CLI v2 | `aws --version` | `brew install awscli` |

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd sdd-todo-api
```

### 2. Python 仮想環境の作成と依存パッケージのインストール

```bash
# pyenv local により .python-version で Python 3.13.12 が自動選択される
python -m venv .venv
source .venv/bin/activate
pip install pytest boto3
```

### 3. AWS SSO の設定

```bash
aws configure sso
```

プロンプトに従い、以下を入力：

| 項目 | 値 |
|---|---|
| SSO session name | 任意の名前 |
| SSO start URL | 管理者から共有された URL |
| SSO region | ap-northeast-1 |
| CLI default client Region | ap-northeast-1 |
| CLI default output format | json |
| CLI profile name | 任意のプロファイル名 |

### 4. DynamoDB Local のセットアップ

```bash
# DynamoDB Local を起動
docker compose up -d

# テーブルの作成（初回のみ）
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb create-table \
  --table-name TasksTable \
  --attribute-definitions AttributeName=task_id,AttributeType=S \
  --key-schema AttributeName=task_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

### 5. SAM ローカル実行用の環境変数ファイルの作成

`env.local.json` を作成（.gitignore 済み）：

```json
{
  "TasksFunction": {
    "TABLE_NAME": "TasksTable",
    "DYNAMODB_ENDPOINT": "http://host.docker.internal:8000",
    "AWS_ACCESS_KEY_ID": "dummy",
    "AWS_SECRET_ACCESS_KEY": "dummy"
  }
}
```

## ローカル開発の実行方法

### DynamoDB Local の起動

```bash
docker compose up -d
```

### SSO ログイン

```bash
aws sso login --profile <YOUR_PROFILE_NAME>
```

### SAM ビルドとローカル API サーバーの起動

```bash
source .venv/bin/activate

sam build

DOCKER_HOST=unix://$HOME/.docker/run/docker.sock \
AWS_PROFILE=<YOUR_PROFILE_NAME> \
sam local start-api --env-vars env.local.json
```

## API の動作確認

ローカル API サーバー起動後（http://127.0.0.1:3000）：

```bash
# タスク作成
curl -X POST http://127.0.0.1:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "牛乳を買う"}'

# タスク一覧取得
curl http://127.0.0.1:3000/tasks

# タスク取得（task_id は作成時のレスポンスから取得）
curl http://127.0.0.1:3000/tasks/{task_id}

# タスク更新
curl -X PUT http://127.0.0.1:3000/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# タスク削除
curl -X DELETE http://127.0.0.1:3000/tasks/{task_id}
```

## テストの実行方法

```bash
source .venv/bin/activate

# 全ユニットテスト実行
python -m pytest tests/unit/ -v

# 特定のテストクラスのみ
python -m pytest tests/unit/test_tasks.py::TestCreateTask -v

# 特定のテストケースのみ
python -m pytest tests/unit/test_tasks.py::TestCreateTask::test_create_task_success -v
```

## 開発効率化の設定（任意）

`~/.zshrc` に以下を追加すると、毎回の環境変数指定を省略できます：

```bash
export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
export AWS_PROFILE=<YOUR_PROFILE_NAME>
```

追加後は `source ~/.zshrc` で反映してください。

## トラブルシューティング

### Docker ソケットエラー (`Cannot connect to the Docker daemon`)

Docker Desktop の最新版ではソケットパスが異なる場合があります：

```bash
# ソケットパスを明示的に指定
DOCKER_HOST=unix://$HOME/.docker/run/docker.sock sam local start-api --env-vars env.local.json
```

または `~/.zshrc` に `export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock` を追加してください。

### DynamoDB Local のテーブルが消えた

Docker コンテナ再作成時にデータが消えた場合：

```bash
# テーブルを再作成
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb create-table \
  --table-name TasksTable \
  --attribute-definitions AttributeName=task_id,AttributeType=S \
  --key-schema AttributeName=task_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

> `docker compose down` ではなく `docker compose down -v` を実行するとボリュームも削除されます。データを残したい場合は `-v` を付けないでください。

### SSO トークンの期限切れ (`Token has expired`)

```bash
aws sso login --profile <YOUR_PROFILE_NAME>
```

### DynamoDB Local の認証エラー

DynamoDB Local はダミー認証情報で動作します。`env.local.json` に `AWS_ACCESS_KEY_ID` と `AWS_SECRET_ACCESS_KEY` が `dummy` で設定されていることを確認してください。
