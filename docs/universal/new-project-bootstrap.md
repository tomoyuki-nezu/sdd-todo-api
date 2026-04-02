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
| `<FRAMEWORK>` | フレームワーク | FastAPI / Express / Lambda |
| `<DATASTORE>` | データストア | PostgreSQL / DynamoDB / MongoDB |
| `<FUNCTION_NAME>` | 関数/サービス名 | TasksService |

### Step 3：Claude Code に初期化プロンプトを渡す

```bash
claude
```

以下のプロンプトを渡す（このまま貼り付けてください）：

```
新しいプロジェクトを始めます。
CLAUDE.md と .claude/skills/ と docs/universal/ を読み込んでください。
読み込んだら、.claude/questions/templates/new-project-template.md を元に
質問ドキュメントを作成してください。
```

### Step 4：質問ドキュメントに回答（Cursor）

Claude Code が作成した `.claude/questions/YYYYMMDD-new-project.md` を Cursor で開き、「Human の回答欄」に記入する。

質問内容（6問）：
1. プロジェクトの基本情報（名前・目的・想定ユーザー）
2. 技術スタック（言語・実行環境・データストア）
3. API 設計（エンドポイント・認証方式）
4. 環境構成（環境数・リージョン・クラウド設定の流用）
5. CI/CD の要件（デプロイトリガー・テスト要件）
6. ドキュメントの要件（言語・必要なドキュメント）

### Step 5：「回答を読んで実行して」

Claude Code に「回答を読んで実行して」と伝える。以降は Claude Code が自律的に以下を実行する：

1. 回答を読み取り、実行内容をサマリー表示
2. ユーザーの承認後、自動実行：
   - 仕様書の作成（`spec/api/<resource>.yaml`）
   - ソースコードの生成（`src/`）
   - テストコードの生成（`tests/`）
   - IaC 定義の作成（選択したツールに応じて）
   - CI/CD パイプラインの作成（`.github/workflows/`）
   - ローカル環境ファイルの作成
   - E2E テストスクリプトの作成（`tests/e2e/test_api.sh`）
   - README.md とプロジェクト固有ドキュメントの作成
3. テスト実行・検証
4. コミット

## プロジェクト生成後の開発フロー

初期化が完了したら、以降は以下のフレーズで Claude Code に指示できます:

| やりたいこと | Claude Code への指示 |
|---|---|
| 仕様変更の反映 | `spec/api/xxx.yaml の変更を読み込んで、コードとテストを更新して` |
| テスト実行 | `テストして` |
| エラー修正 | `エラーを解析して` |
| コミット | `コミットして` |
| プッシュ | `プッシュして` |
| ドキュメント更新 | `README を更新して` |

複雑な判断が必要な場合は Claude Code が自動的に質問ドキュメントを作成します。Cursor で回答を記入し「回答を読んで実行して」と伝えてください。

## Step 5 完了後に人間が行う作業

以下は Claude Code では実施できないため、手動で行う。

### GitHub リポジトリの作成と設定

1. GitHub でリポジトリを作成
2. Settings > Secrets and variables > Actions にデプロイ用の認証情報を登録

### クラウド環境の認証設定（使用するプロバイダーに応じて）

GitHub Actions からクラウドへのデプロイに必要な認証を設定する。

**OIDC（推奨）:** キーレス認証。GitHub Actions の OIDC トークンでクラウドの一時認証情報を取得する。

**サービスアカウントキー:** GitHub Secrets にキーを登録する。

具体的な設定手順はクラウドプロバイダーのドキュメントを参照すること。

### ローカルデータストアのセットアップ

```bash
docker compose up -d
# プロジェクトに応じてテーブル作成やマイグレーションを実行
```

### リモートリポジトリへのプッシュ

```bash
git remote add origin https://github.com/<YOUR_ORG>/<YOUR_REPO>.git
git push -u origin main
```

## 動作確認チェックリスト

すべての設定が完了したら以下を確認する：

- [ ] `pytest tests/unit/` → 全テストパス
- [ ] `docker compose up -d` → ローカルサービス起動
- [ ] ビルド成功（使用するビルドツールで確認）
- [ ] ローカルサーバー起動成功
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
