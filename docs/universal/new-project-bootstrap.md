# 新規プロジェクト初期化ガイド

新しいプロジェクトを開始する際の手順書。スターターキットのコピーから Claude Code による自律実行まで、5ステップで完了する。

## クイックスタート（5ステップ）

### Step 1：スターターキットをコピー

```bash
cp -r claude-code-starter/ <new-project>/
cd <new-project>/
git init
```

### Step 2：CLAUDE.md のプレースホルダーを書き換え（Cursor）

Cursor で `CLAUDE.md` を開き、プロジェクト固有設定セクションのプレースホルダーを書き換える：

| プレースホルダー | 説明 | 例 |
|---|---|---|
| `<PROJECT_NAME>` | プロジェクト名 | タスク管理 API |
| `<LANGUAGE>` | 使用言語 | Python 3.13 |
| `<FRAMEWORK>` | フレームワーク | AWS Lambda |
| `<DATASTORE>` | データストア | DynamoDB |
| `<FUNCTION_NAME>` | Lambda 関数名 | TasksFunction |

### Step 3：Claude Code に初期化プロンプトを渡す

```bash
claude
```

以下のプロンプトを渡す：

```
新しいプロジェクトを始めます。以下のドキュメントを読み込んでください：
- CLAUDE.md
- docs/universal/new-project-bootstrap.md
- docs/universal/question-document-spec.md
- .claude/questions/templates/new-project-template.md

読み込んだ後、new-project-template.md を元に本日の日付で
質問ドキュメントを .claude/questions/ に作成してください。
私が回答を記入したら『回答を読んで実行して』と伝えます。
```

### Step 4：質問ドキュメントに回答（Cursor）

Claude Code が作成した `.claude/questions/YYYYMMDD-new-project.md` を Cursor で開き、「Human の回答欄」に記入する。

質問内容（6問）：
1. プロジェクトの基本情報（名前・目的・想定ユーザー）
2. 技術スタック（言語・実行環境・データストア）
3. API 設計（エンドポイント・認証方式）
4. 環境構成（環境数・リージョン・AWS 設定の流用）
5. CI/CD の要件（デプロイトリガー・テスト要件）
6. ドキュメントの要件（言語・必要なドキュメント）

### Step 5：「回答を読んで実行して」

Claude Code に「回答を読んで実行して」と伝える。以降は Claude Code が自律的に以下を実行する：

1. 回答を読み取り、実行内容をサマリー表示
2. ユーザーの承認後、自動実行：
   - 仕様書の作成（`spec/api/<resource>.yaml`）
   - ソースコードの生成（`src/`）
   - テストコードの生成（`tests/`）
   - SAM テンプレートの作成（`template.yaml`）
   - CI/CD パイプラインの作成（`.github/workflows/deploy.yml`）
   - ローカル環境ファイルの作成（`env.local.json`, `.env.*`）
   - E2E テストスクリプトの作成（`tests/e2e/test_api.sh`）
   - README.md とプロジェクト固有ドキュメントの作成
3. テスト実行・検証
4. コミット

## Step 5 完了後に人間が行う作業

以下は Claude Code では実施できないため、手動で行う。

### GitHub リポジトリの作成と設定

1. GitHub でリポジトリを作成
2. Settings > Secrets and variables > Actions に以下を登録：

| Secret 名 | 値 |
|---|---|
| `AWS_ROLE_ARN` | OIDC で AssumeRole する IAM ロールの ARN |
| `AWS_REGION` | `ap-northeast-1` |

### AWS IAM OIDC プロバイダーの登録（AWS アカウントで初回のみ）

- IAM > ID プロバイダー > プロバイダを追加
- プロバイダのタイプ: OpenID Connect
- プロバイダの URL: `https://token.actions.githubusercontent.com`
- 対象者: `sts.amazonaws.com`

### AWS IAM Role の作成

信頼ポリシー:

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

必要なポリシー: Lambda、API Gateway、DynamoDB、CloudFormation、S3、IAM の権限

### DynamoDB Local のテーブル作成

```bash
docker compose up -d

AWS_ACCESS_KEY_ID=dummy \
AWS_SECRET_ACCESS_KEY=dummy \
aws dynamodb create-table \
  --table-name <TABLE_NAME> \
  --attribute-definitions AttributeName=<pk>,AttributeType=S \
  --key-schema AttributeName=<pk>,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1
```

### リモートリポジトリへのプッシュ

```bash
git remote add origin https://github.com/<YOUR_ORG>/<YOUR_REPO>.git
git push -u origin main
```

## 動作確認チェックリスト

すべての設定が完了したら以下を確認する：

- [ ] `pytest tests/unit/` → 全テストパス
- [ ] `docker compose up -d` → DynamoDB Local 起動
- [ ] `sam build` → ビルド成功
- [ ] `sam local start-api --env-vars env.local.json` → 起動成功
- [ ] `ENV=local bash tests/e2e/test_api.sh` → 全テストパス
- [ ] `git push` → GitHub Actions 成功
- [ ] `ENV=production bash tests/e2e/test_api.sh` → 全テストパス

## 汎用ファイルと固有ファイルの分類

| ファイル | 種別 | 引き継ぎ方法 |
|---|---|---|
| `CLAUDE.md` | 半汎用 | プロジェクト固有設定を書き換える |
| `spec/constitution.md` | 汎用 | そのまま流用 |
| `.claude/skills/common/` | 汎用 | そのまま流用 |
| `.claude/skills/project/` | 固有 | スタックに合わせて修正 |
| `docker-compose.yml` | 汎用 | そのまま流用 |
| `.gitignore` | 汎用 | そのまま流用 |
| `docs/universal/` | 汎用 | そのまま流用 |
| `.github/workflows/deploy.yml` | 半汎用 | バージョン・スタック名を変更 |
| `docs/project/` | 固有 | 新規作成 |
| `README.md` | 固有 | 新規作成 |
| `tests/e2e/test_api.sh` | 固有 | エンドポイントに合わせて修正 |
