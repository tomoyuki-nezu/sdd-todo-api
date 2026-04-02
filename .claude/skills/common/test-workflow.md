---
name: test-workflow
description: >
  テストを実行するとき、または「テストして」
  「テストを実行して」などの依頼を受けたとき
allowed-tools: [Read, Bash]
---

# Test Workflow

## テスト実行の標準手順

### 1. ユニットテストの実行

```bash
pytest tests/unit/ -v
```

実行後に以下を確認：
- 全テストのパス/失敗数
- 失敗したテストのエラーメッセージ
- カバレッジ（必要な場合）

### 2. 失敗時の対応

テストが失敗した場合は error-handling Skill の
ワークフローに従うこと。

ただし以下の場合は自動修正してよい：
- 仕様書の変更に追従するだけの修正
- 明らかなタイポ・構文エラー

### 3. E2E テストの実行

ローカル環境:

```bash
docker compose up -d  # DynamoDB Local が起動していることを確認
ENV=local bash tests/e2e/test_api.sh
```

本番環境:

```bash
ENV=production bash tests/e2e/test_api.sh
```

### 4. テスト完了の報告

以下の形式で報告すること：

```
## テスト結果

### ユニットテスト
  合計: X件 / 成功: X件 / 失敗: X件

### E2E テスト（実行した場合）
  合計: X件 / 成功: X件 / 失敗: X件

### 失敗したテスト（ある場合）
  - テスト名: エラー内容

### 次のアクション
  （問題がある場合の推奨アクション）
```
