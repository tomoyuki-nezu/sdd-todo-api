# 開発環境セットアップ・実行ガイド

## 前提条件

| ツール | 用途 | バージョン確認 |
|---|---|---|
| pyenv | Python バージョン管理 | `pyenv --version` |
| Python 3.13.12 | ランタイム | `python --version` |
| AWS SAM CLI >= 1.157 | ローカルテスト・デプロイ | `sam --version` |
| Docker Desktop | SAM ローカル実行・DynamoDB Local | `docker --version` |
| AWS CLI v2 | AWS 認証・操作 | `aws --version` |

## 初回セットアップ

```bash
# 1. Python バージョンの設定（pyenv local により .python-version で固定済み）
pyenv install 3.13.12  # 未インストールの場合

# 2. 仮想環境の作成
python -m venv .venv

# 3. 仮想環境の有効化
source .venv/bin/activate

# 4. 依存パッケージのインストール
pip install pytest boto3
```

## 日常の開発作業

### 仮想環境の有効化（毎回のターミナル起動時）

```bash
source .venv/bin/activate
```

### ユニットテストの実行

```bash
# 全テスト実行
python -m pytest tests/unit/ -v

# 特定のテストクラスのみ
python -m pytest tests/unit/test_tasks.py::TestCreateTask -v

# 特定のテストケースのみ
python -m pytest tests/unit/test_tasks.py::TestCreateTask::test_create_task_success -v
```

### SAM テンプレートの検証

```bash
sam validate --region ap-northeast-1
```

## ローカル開発（SAM + DynamoDB Local）

### 1. DynamoDB Local の起動

```bash
docker compose up -d
```

### 2. テーブルの作成（初回のみ）

```bash
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb create-table \
  --table-name TasksTable \
  --attribute-definitions AttributeName=task_id,AttributeType=S \
  --key-schema AttributeName=task_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

### 3. SSO ログイン

```bash
aws sso login --profile <YOUR_PROFILE_NAME>
```

### 4. SAM ビルドとローカル API サーバーの起動

```bash
sam build

DOCKER_HOST=unix://$HOME/.docker/run/docker.sock \
AWS_PROFILE=<YOUR_PROFILE_NAME> \
sam local start-api --env-vars env.local.json
```

### 5. API の動作確認

```bash
# タスク作成
curl -X POST http://127.0.0.1:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "テストタスク"}'

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

### 単一関数の呼び出し

```bash
sam local invoke TasksFunction --event events/event.json
```

## 環境変数ファイル

### env.local.json（SAM local 用、.gitignore 済み）

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

> `env.local.json` は `template.yaml` の `Environment/Variables` に定義済みの変数のみ上書き可能です。新しい環境変数を追加する場合は、先に `template.yaml` にも定義してください。

## 開発効率化の設定（任意）

`~/.zshrc` に以下を追加すると、毎回の環境変数指定を省略できます：

```bash
export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
export AWS_PROFILE=<YOUR_PROFILE_NAME>
```

追加後は `source ~/.zshrc` で反映。

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| `ModuleNotFoundError: No module named 'pytest'` | 仮想環境が有効化されていない | `source .venv/bin/activate` |
| `Cannot connect to the Docker daemon` | Docker ソケットパスが異なる | `DOCKER_HOST=unix://$HOME/.docker/run/docker.sock` を指定 |
| `NoRegionError` | AWS リージョンが未設定 | `aws configure` または `--region` オプションを指定 |
| `pyenv: command not found` | pyenv が未インストール | `brew install pyenv` |
| `Token has expired` | SSO トークン期限切れ | `aws sso login --profile <YOUR_PROFILE_NAME>` |
| DynamoDB Local のテーブルが消えた | `docker compose down -v` でボリューム削除された | テーブル作成コマンドを再実行（上記「テーブルの作成」参照） |
| DynamoDB Local 認証エラー | ダミー認証情報が未設定 | `env.local.json` に `AWS_ACCESS_KEY_ID: dummy` を設定 |
| `'python3.13' runtime is not supported` | SAM CLI が古い | `brew upgrade aws-sam-cli` でアップグレード |
