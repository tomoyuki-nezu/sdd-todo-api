#!/bin/bash
# Claude Code コマンド実行前の安全チェック
# PreToolUse フックから呼び出される

COMMAND=$(jq -r '.tool_input.command // empty' < /dev/stdin 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# rm -rf をブロック
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+[/*]'; then
  echo "Blocked: rm -rf with wildcard or root path is not allowed" >&2
  exit 2
fi

# .env ファイルへの cat をブロック
if echo "$COMMAND" | grep -qE 'cat.*\.env'; then
  echo "Blocked: Reading .env files via cat is not allowed" >&2
  exit 2
fi

# 本番環境への直接接続をブロック（prod キーワード）
if echo "$COMMAND" | grep -qE 'aws.*--profile.*(prod|production)'; then
  echo "Blocked: Direct production AWS access requires explicit permission" >&2
  exit 2
fi

exit 0
