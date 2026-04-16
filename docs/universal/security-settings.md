# Claude Code セキュリティ設定ガイド

## 概要

Claude Code はターミナルコマンドの実行・ファイルの読み書きが
できるため、セキュリティ設定が重要です。
本ガイドではスターターキットに含まれるセキュリティ設定の
内容と、プロジェクト固有のカスタマイズ方法を説明します。

## 設定ファイルの優先順位

Claude Code の設定は以下の優先順位で適用されます：

1. Managed Settings（組織管理者が設定・上書き不可）
2. User Settings（~/.claude/settings.json）
3. Project Settings（.claude/settings.json）← このキットの設定

## .claude/settings.json の主要設定

### サンドボックス（sandbox）

Claude Code が実行する Bash コマンドを OS レベルで隔離します。

- macOS: Seatbelt による隔離
- Linux: Bubble Wrap による隔離

有効化後は /sandbox コマンドで状態を確認できます。

allowedDomains に含まれていない URL への curl などは失敗します。
プロジェクトで必要なドメインを追加してください：

例：AWS を使うプロジェクトの場合
"allowedDomains" に追加：
  "*.amazonaws.com"
  "*.execute-api.ap-northeast-1.amazonaws.com"

### 拒否ルール（permissions.deny）

以下のパターンをデフォルトでブロックしています：
- .env ファイルへの読み取り・編集・書き込み
- .pem / .key ファイルへの読み取り
- rm -rf コマンド
- chmod 777 コマンド

ルールの評価順序：deny → ask → allow
deny ルールは最優先で適用されます。

### フック（hooks）

PreToolUse フックで Bash コマンド実行前に
.claude/hooks/validate-command.sh が実行されます。

プロジェクト固有のチェックはこのスクリプトに追加してください。
exit 2 でコマンドをブロック、exit 0 で許可します。

## プロジェクト固有のカスタマイズ

### 許可ドメインの追加

プロジェクトで使う外部サービスのドメインを追加する：

.claude/settings.json の sandbox.network.allowedDomains に追加：
  "*.your-service.com"

### 追加の deny ルール

プロジェクト固有のブロックルールを追加する：

.claude/settings.json の permissions.deny に追加：
  "Bash(your-dangerous-command *)"

### フックの拡張

.claude/hooks/validate-command.sh に追加チェックを記述する：

例：特定の環境変数が設定されている場合のみ許可
if [ -z "$ALLOWED_ENV" ]; then
  echo "Blocked: ALLOWED_ENV is not set" >&2
  exit 2
fi

## チーム・組織での利用

チーム開発では Managed Settings による一括管理が推奨されます。

Managed Settings の配置先：
- macOS: /Library/Application Support/ClaudeCode/managed-settings.json
- Linux: /etc/claude-code/managed-settings.json

Managed Settings は Claude for Teams / Enterprise プランで
リモート配信（Server-managed settings）も可能です。

## /permissions コマンドで定期確認

セッション中に許可した「Always allow」ルールが
蓄積していないか定期的に確認してください：

/permissions  # 現在の権限設定を一覧表示
/status       # 読み込まれている設定ファイルを確認
