# 新規プロジェクト初期化ガイド

新しいプロジェクトを開始する際に、このドキュメントのプロンプトを Claude Code に渡すことで、同じアーキテクチャのプロジェクトを迅速に立ち上げることができる。

## このドキュメントの使い方

### Step 1：参照ドキュメントのコピー

既存プロジェクト（sdd-todo-api）から以下のファイルをコピーする：

| ファイル | 流用方法 |
|---|---|
| `CLAUDE.md` | プロジェクト名・スタックを書き換えて使う |
| `spec/constitution.md` | そのまま流用可能 |
| `.claude/skills/` | そのまま流用可能 |
| `docs/architecture.md` | 参照用 |
| `docs/development-guide.md` | 参照用 |
| `docker-compose.yml` | そのまま流用可能 |
| `.gitignore` | そのまま流用可能 |

```bash
# コピー例
NEW_PROJECT=~/projects/<NEW_PROJECT_NAME>
REFERENCE=~/projects/sdd-todo-api

mkdir -p $NEW_PROJECT
cd $NEW_PROJECT
git init

# ファイルのコピー
cp $REFERENCE/CLAUDE.md .
cp $REFERENCE/.gitignore .
cp $REFERENCE/docker-compose.yml .
mkdir -p spec && cp $REFERENCE/spec/constitution.md spec/
mkdir -p .claude/skills && cp $REFERENCE/.claude/skills/*.md .claude/skills/
mkdir -p docs && cp $REFERENCE/docs/architecture.md $REFERENCE/docs/development-guide.md docs/
```

### Step 2：Claude Code への初期化プロンプト

新しいプロジェクトのルートディレクトリで `claude` を起動し、以下のプロンプトを順番に渡す。

---

#### プロンプト 1：プロジェクト構造の初期化

```
以下のドキュメントを読み込んでください：
- CLAUDE.md
- spec/constitution.md
- docs/architecture.md
- docs/development-guide.md
- .claude/skills/ 以下のすべての Skills

読み込んだ後、以下のプロジェクト構造を作成してください：

プロジェクト名: <PROJECT_NAME>
言語: <LANGUAGE>（例: Python 3.13）
アーキテクチャ: <ARCHITECTURE>（例: Lambda + API Gateway + DynamoDB）

作成するディレクトリ・ファイル:
  spec/
    constitution.md（コピー済みのものを確認）
    api/（空ディレクトリ）
  src/
  tests/
    unit/
    e2e/
  .claude/
    skills/（コピー済みのものを確認）
  .github/
    workflows/
  docs/

CLAUDE.md を以下の内容に更新してください：
- プロジェクト名: <PROJECT_NAME>
- 技術スタック: <STACK>
- ディレクトリ構成: 上記に合わせて更新
```

---

#### プロンプト 2：仕様書の作成

```
以下の内容で仕様書を作成してください：

プロジェクト: <PROJECT_NAME>
機能概要: <FEATURE_DESCRIPTION>

spec/api/<RESOURCE>.yaml として
今回のプロジェクトの仕様書を作成してください。

仕様書には以下を含めること：
- エンドポイント定義（method / path / request / response）
- エラーコード定義
- examples セクション（BDD 形式）
- technical_constraints セクション
```

---

#### プロンプト 3：コード・インフラの生成

```
spec/api/<RESOURCE>.yaml を読み込み、
以下を生成してください：

1. src/handlers/<resource>.py
   - Lambda ハンドラ
   - DynamoDB CRUD 操作
   - エラーハンドリング

2. src/requirements.txt

3. template.yaml（SAM テンプレート）
   - Lambda 関数定義
   - API Gateway 設定
   - DynamoDB テーブル定義
   - IAM ロール（最小権限）
   - Environment Variables:
     TABLE_NAME: !Ref <Resource>Table
     DYNAMODB_ENDPOINT: ""

4. tests/unit/test_<resource>.py
   - 仕様書の examples に基づくテスト
   - DynamoDB はモックを使用

生成後、pytest tests/unit/ を実行して
全テストがパスすることを確認してください。
```

---

#### プロンプト 4：ローカル環境のセットアップ

```
以下のファイルを作成してください：

1. docker-compose.yml
   （既存のものがあれば確認・流用）

2. env.local.json
   {
     "<FunctionName>": {
       "TABLE_NAME": "<ResourceName>Table",
       "DYNAMODB_ENDPOINT": "http://host.docker.internal:8000",
       "AWS_DEFAULT_REGION": "ap-northeast-1",
       "AWS_ACCESS_KEY_ID": "dummy",
       "AWS_SECRET_ACCESS_KEY": "dummy"
     }
   }

3. .env.local
   BASE_URL=http://127.0.0.1:3000

4. .env.production
   BASE_URL=https://<YOUR_API_ID>.execute-api.ap-northeast-1.amazonaws.com/Prod

5. tests/e2e/test_api.sh
   仕様書の examples セクションに基づく E2E テストスクリプト

以下が .gitignore に含まれているか確認してください：
  env.local.json
  .env.local
  .env.production
  .aws-sam/
  __pycache__/
  .venv/
```

---

#### プロンプト 5：CI/CD の設定

```
.github/workflows/deploy.yml を作成してください。

- test ジョブ: Python <VERSION> / pytest 実行
- deploy ジョブ: OIDC 認証 / sam build / sam deploy --resolve-s3
- Python バージョン: <VERSION>（template.yaml の Runtime と一致させること）
- GitHub Secrets:
    AWS_ROLE_ARN: OIDC 用 IAM Role ARN
    AWS_REGION: ap-northeast-1

作成後、コミットしてください。
```

---

#### プロンプト 6：ドキュメントの整備

```
README.md を作成・更新してください。

以下のセクションを含めること：
- プロジェクト概要
- システム構成図
- 前提条件（ツールとバージョン）
- 初回セットアップ手順
- ローカル開発のワークフロー
- Claude Code を使った開発フロー
- デプロイ後の確認方法
- トラブルシューティング

docs/architecture.md を更新してください：
- 今回のプロジェクト固有のアーキテクチャを反映

作成後にコミット・プッシュしてください。
```

---

### Step 3：初回 AWS セットアップ（プロジェクトごとに必要）

以下は Claude Code では実施できないため、人間が手動で行う。

#### 1. GitHub リポジトリの作成

- リポジトリを作成
- Settings > Secrets and variables > Actions に以下を登録：

| Secret 名 | 値 |
|---|---|
| `AWS_ROLE_ARN` | OIDC で AssumeRole する IAM ロールの ARN |
| `AWS_REGION` | `ap-northeast-1` |

#### 2. AWS IAM OIDC プロバイダーの登録（AWS アカウントで初回のみ）

- IAM > ID プロバイダー > プロバイダを追加
- プロバイダのタイプ: OpenID Connect
- プロバイダの URL: `https://token.actions.githubusercontent.com`
- 対象者: `sts.amazonaws.com`

#### 3. AWS IAM Role の作成

- 信頼ポリシー: GitHub OIDC プロバイダーを信頼

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<YOUR_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<YOUR_ORG>/<YOUR_REPO>:*"
        }
      }
    }
  ]
}
```

- 必要なポリシー: Lambda、API Gateway、DynamoDB、CloudFormation、S3、IAM の権限

#### 4. DynamoDB Local のテーブル作成（初回のみ）

```bash
AWS_ACCESS_KEY_ID=dummy \
AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb create-table \
  --table-name <ResourceName>Table \
  --attribute-definitions AttributeName=<pk>,AttributeType=S \
  --key-schema AttributeName=<pk>,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

### Step 4：動作確認チェックリスト

新プロジェクトの初期化が完了したら以下を確認する：

- [ ] `pytest tests/unit/` → 全テストパス
- [ ] `docker compose up -d` → DynamoDB Local 起動
- [ ] `sam build` → ビルド成功
- [ ] `sam local start-api --env-vars env.local.json` → 起動成功
- [ ] `ENV=local bash tests/e2e/test_api.sh` → 全テストパス
- [ ] `git push` → GitHub Actions 成功
- [ ] `ENV=production bash tests/e2e/test_api.sh` → 全テストパス
