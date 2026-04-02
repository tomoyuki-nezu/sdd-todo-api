# アーキテクチャ設計ドキュメント

次のプロジェクトでも同じアーキテクチャを再現するための設計ドキュメント。

## 仕様書ドリブン開発（SDD）の設計思想

### Single Source of Truth としての仕様書

本プロジェクトでは `spec/` ディレクトリ配下の YAML 仕様書を唯一の真実の源泉（Single Source of Truth）とする。コードは仕様書から生成され、テストは仕様書の `examples` セクションに基づく。

```
仕様書(YAML) → Claude Code → コード生成 → テスト生成 → CI/CD → デプロイ
```

### spec/ ディレクトリの構造と役割

```
spec/
├── constitution.md    # プロジェクト憲法（AI の行動制約）
└── api/
    └── tasks.yaml     # タスク管理 API の仕様書
```

- **仕様書 (api/*.yaml)**: エンドポイント定義、リクエスト/レスポンススキーマ、エラーコード、テスト例を構造化して記述
- **constitution.md**: AI エージェントの行動範囲を Green/Yellow/Red Zone で定義

### constitution.md の役割

AI エージェント（Claude Code）が自律的に判断してよい範囲を制御する：

| Zone | 内容 | 例 |
|---|---|---|
| **Green** | AI が自律判断してよい | コード生成、テスト修正、ドキュメント生成 |
| **Yellow** | Human の承認が必要 | 本番デプロイ、API 破壊的変更、DynamoDB 定義変更 |
| **Red** | 絶対禁止 | 本番データ直接アクセス、シークレットのコード記述 |

## ディレクトリ構造と各ファイルの役割

```
sdd-todo-api/
├── .claude/                    # Claude Code プロジェクト設定
│   ├── settings.local.json     #   ローカル設定
│   └── skills/                 #   スキル定義
│       ├── python-lambda.md    #     Lambda コード生成ルール
│       └── sam-architect.md    #     SAM テンプレート生成ルール
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD パイプライン定義
├── .gitignore                  # Git 除外設定
├── .python-version             # pyenv 用 Python バージョン固定
├── CLAUDE.md                   # Claude Code への指示書
├── README.md                   # プロジェクト全体のドキュメント
├── docker-compose.yml          # DynamoDB Local の起動定義
├── docs/
│   ├── architecture.md         # 本ドキュメント（設計思想）
│   ├── development.md          # 環境セットアップ・実行ガイド
│   └── development-guide.md    # 新機能追加の手順書
├── env.local.json              # SAM local 用環境変数（git 管理外）
├── spec/
│   ├── constitution.md         # プロジェクト憲法
│   └── api/
│       └── tasks.yaml          # API 仕様書
├── src/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── tasks.py            # Lambda ハンドラ（CRUD 操作）
│   └── requirements.txt        # 本番用依存パッケージ
├── template.yaml               # SAM テンプレート（インフラ定義）
└── tests/
    ├── __init__.py
    ├── e2e/
    │   └── test_api.sh          # E2E テストスクリプト
    └── unit/
        ├── __init__.py
        └── test_tasks.py        # ユニットテスト
```

## Claude Code の設定

### CLAUDE.md の役割

Claude Code がプロジェクトで作業する際に従うべきルールを定義：

- **プロジェクト概要・技術スタック**: コンテキストの提供
- **命名規約・コード生成ルール**: 一貫したコード品質の維持
- **Python 環境**: venv の使用、グローバル汚染の禁止
- **Git Commit Rules**: Conventional Commits 形式の強制
- **Git Workflow**: 「コミットして」「プッシュして」で自律実行するルール
- **禁止事項**: セキュリティ上の制約

### .claude/skills/ の役割

タスク種別に応じた専門的なルールを定義：

| スキル | トリガー | 内容 |
|---|---|---|
| `python-lambda.md` | `src/` 配下のコードを扱う時 | ハンドラ構造、型アノテーション、ログ規約 |
| `sam-architect.md` | `template.yaml` を扱う時 | IAM 最小権限、環境変数注入、sam validate 必須 |

### Git コミット・プッシュの自動化ルール

CLAUDE.md の Git Workflow セクションにより：

- 「コミットして」→ `git status` → `git diff` → 変更分析 → 自動コミットメッセージ生成 → `git commit`
- 「プッシュして」→ ブランチ確認 → `git push origin <branch>`
- 複数の関心事にまたがる変更は自動的に複数コミットに分割

## AWS アーキテクチャ

### Lambda + API Gateway + DynamoDB の構成

```
クライアント → API Gateway → Lambda (TasksFunction) → DynamoDB (TasksTable)
```

- **API Gateway**: REST API として5つのエンドポイントを公開
- **Lambda**: 単一関数でルーティング（`handler` 関数がメソッド+パスで分岐）
- **DynamoDB**: パーティションキー `task_id` のシンプルなテーブル、PAY_PER_REQUEST

### SAM テンプレートの設計方針

- `Globals` セクションで共通設定（Runtime, Timeout, Tracing, 環境変数）を定義
- `DynamoDBCrudPolicy` SAM ポリシーテンプレートで IAM を最小権限に
- `DYNAMODB_ENDPOINT` 環境変数により本番/ローカルの接続先を切り替え
- `!Ref TasksTable` でテーブル名を動的に解決

### IAM 最小権限の原則

- SAM の `DynamoDBCrudPolicy` を使用し、対象テーブルを `!Ref TasksTable` で限定
- ワイルドカード (`*`) の使用禁止（`.claude/skills/sam-architect.md` で規定）
- ハードコードされた ARN・アカウント ID 禁止

### OIDC による GitHub Actions 認証の仕組み

```
GitHub Actions → OIDC トークン発行 → AWS STS AssumeRoleWithWebIdentity → 一時認証情報取得
```

- アクセスキーのハードコードが不要
- GitHub リポジトリ・ブランチで IAM ロールの信頼ポリシーを限定可能
- `aws-actions/configure-aws-credentials@v4` で透過的に処理

## ローカル開発環境の構成

### Docker Compose による DynamoDB Local

```yaml
services:
  dynamodb-local:
    image: amazon/dynamodb-local
    ports: ["8000:8000"]
    volumes:
      - dynamodb-data:/home/dynamodblocal/data  # データ永続化
```

- `-sharedDb` オプションでリージョン・認証情報に関係なく同一テーブルを共有
- Named volume `dynamodb-data` でコンテナ再起動時もデータを保持
- `docker compose down -v` でボリュームごと削除可能

### env.local.json による環境変数の切り替え

`sam local start-api --env-vars env.local.json` で Lambda に環境変数を注入：

- `DYNAMODB_ENDPOINT`: `http://host.docker.internal:8000`（Docker 内から Mac のポートへ）
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`: `dummy`（DynamoDB Local は認証不要だがキーは必須）

### DYNAMODB_ENDPOINT の or None パターン

```python
endpoint_url=os.environ.get("DYNAMODB_ENDPOINT") or None
```

- `template.yaml` で `DYNAMODB_ENDPOINT: ""` と定義（空文字がデフォルト）
- `env.local.json` でローカル用エンドポイントに上書き
- 本番環境では空文字 → `or None` により `None` → boto3 がデフォルトの AWS エンドポイントに接続
- `env.local.json` は `template.yaml` に定義済みの変数しか上書きできないため、先に空文字で定義しておく必要がある

## CI/CD パイプラインの設計

### GitHub Actions のジョブ構成

```
push to main ──▶ test ──▶ deploy
pull_request ──▶ test のみ（deploy はスキップ）
```

### test ジョブ

1. コードチェックアウト
2. Python 3.13 セットアップ
3. 依存パッケージインストール (`src/requirements.txt` + `pytest`)
4. `python -m pytest tests/unit/ -v` 実行

### deploy ジョブ

`test` 成功後、かつ `main` ブランチへの push 時のみ実行：

1. コードチェックアウト
2. Python 3.13 セットアップ
3. SAM CLI インストール (`aws-actions/setup-sam@v2`)
4. OIDC 認証 (`aws-actions/configure-aws-credentials@v4`)
5. `sam build`
6. `sam deploy --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM`
7. API Gateway URL 出力

### OIDC 認証フロー

```
GitHub Actions Runner
  ├─ OIDC トークン生成（permissions: id-token: write）
  ├─ aws-actions/configure-aws-credentials@v4
  │    ├─ role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
  │    └─ STS AssumeRoleWithWebIdentity
  └─ 一時認証情報で sam deploy 実行
```

必要な GitHub Secrets：

| Secret | 用途 |
|---|---|
| `AWS_ROLE_ARN` | OIDC で AssumeRole する IAM ロールの ARN |
| `AWS_REGION` | デプロイ先リージョン |
