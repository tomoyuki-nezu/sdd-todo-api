# 開発ガイド

新しいエンドポイントや機能を追加する際の手順書。

## 新しいエンドポイントを追加する手順

### 1. spec/api/tasks.yaml に仕様を追記

Cursor で仕様書を編集し、新しいエンドポイントを定義する：

```yaml
  - id: search-tasks
    method: GET
    path: /tasks/search
    description: "タスクを検索する"
    request:
      query_params:
        q: { type: string, required: true }
    response:
      success:
        status: 200
        schema:
          tasks:
            type: array
            items:
              task_id: { type: string }
              title: { type: string }
              done: { type: boolean }
      errors:
        - status: 400
          code: MISSING_QUERY
```

### 2. Claude Code でコード生成

```
spec/api/tasks.yaml の変更を読み込み、
src/handlers/tasks.py を更新してください。
テストも更新してパスすることを確認してください。
```

Claude Code が以下を自動実行する：

- `src/handlers/tasks.py` にハンドラ関数を追加
- `handler()` のルーティングテーブルに新エンドポイントを追加
- `template.yaml` に API Gateway イベントを追加
- `tests/unit/test_tasks.py` にテストケースを追加

### 3. ユニットテストがパスすることを確認

```bash
source .venv/bin/activate
pytest tests/unit/ -v
```

### 4. コミット・プッシュ

Claude Code に「コミットして」「プッシュして」と依頼。

### 5. GitHub Actions でデプロイ確認

GitHub > Actions タブで test → deploy ジョブの成功を確認。

### 6. E2E テストで動作確認

新しいエンドポイントの動作確認を `tests/e2e/test_api.sh` に追加した後：

```bash
ENV=production bash tests/e2e/test_api.sh
```

## 仕様書の書き方ガイド

### 自然言語から構造化 YAML への移行方法

まず自然言語で要件を整理し、YAML に変換する：

```
自然言語: 「タスクにタグを付けられるようにしたい。
           タグは複数付けられて、タグで検索もしたい。」

↓ 構造化

endpoints:
  - id: add-tag
    method: POST
    path: /tasks/{task_id}/tags
    description: "タスクにタグを追加する"
    request:
      schema:
        tag: { type: string, required: true, max_length: 50 }
    response:
      success:
        status: 201
```

### examples セクションの書き方（BDD 形式）

仕様書の `examples` セクションはテスト生成の元になる。ステップを順序立てて記述する：

```yaml
examples:
  - name: "タグの追加と検索のフロー"
    steps:
      - POST /tasks { title: "買い物" } → 201
      - POST /tasks/{id}/tags { tag: "urgent" } → 201
      - GET /tasks?tag=urgent → 200（1件含む）
      - DELETE /tasks/{id}/tags/urgent → 200

  - name: "存在しないタスクへのタグ追加"
    steps:
      - POST /tasks/nonexistent/tags { tag: "test" } → 404
```

### エラーコードの定義方法

エラーコードは大文字スネークケースで、具体的に命名する：

```yaml
errors:
  - status: 400
    code: MISSING_TAG          # 必須パラメータ不足
  - status: 404
    code: TASK_NOT_FOUND       # リソースが存在しない
  - status: 409
    code: TAG_ALREADY_EXISTS   # 重複
```

対応するレスポンス形式（CLAUDE.md で統一済み）：

```json
{"error": "MISSING_TAG"}
```

## テストの追加方法

### ユニットテストの追加場所と命名規則

| 項目 | 規則 |
|---|---|
| ファイル | `tests/unit/test_{リソース名}.py` |
| クラス名 | `Test{操作名}` （例: `TestSearchTasks`） |
| メソッド名 | `test_{操作}_{条件}` （例: `test_search_tasks_success`） |
| docstring | テストの意図を日本語で記述 |

### テストの基本構造

```python
class TestSearchTasks:
    """GET /tasks/search のテスト."""

    def test_search_tasks_success(self, mock_table: MagicMock) -> None:
        """検索クエリに一致するタスクを返す."""
        from src.handlers.tasks import handler

        mock_table.scan.return_value = {
            "Items": [
                {"task_id": "abc", "title": "牛乳を買う", "done": False}
            ]
        }
        event = _make_event("GET", "/tasks/search",
                           query_params={"q": "牛乳"})
        response = handler(event, None)

        assert response["statusCode"] == 200

    def test_search_tasks_missing_query(self, mock_table: MagicMock) -> None:
        """クエリパラメータが未指定の場合 400 を返す."""
        from src.handlers.tasks import handler

        event = _make_event("GET", "/tasks/search")
        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "MISSING_QUERY"
```

### DynamoDB のモックパターン

本プロジェクトでは `_get_table()` 関数をモックして DynamoDB を差し替える：

```python
@pytest.fixture(autouse=True)
def mock_table():
    """_get_table をモックして DynamoDB テーブルを差し替える."""
    mock_tbl = MagicMock()
    with patch("src.handlers.tasks._get_table", return_value=mock_tbl):
        yield mock_tbl
```

主要な DynamoDB 操作のモック例：

```python
# scan（一覧取得）
mock_table.scan.return_value = {"Items": [...]}

# get_item（単一取得）
mock_table.get_item.return_value = {"Item": {...}}  # 存在する場合
mock_table.get_item.return_value = {}                # 存在しない場合

# put_item（作成）
mock_table.put_item.assert_called_once()

# update_item（更新）
mock_table.update_item.return_value = {"Attributes": {...}}

# delete_item（削除）
mock_table.delete_item.assert_called_once_with(Key={"task_id": "abc"})
```

### E2E テストスクリプトへの追加方法

`tests/e2e/test_api.sh` に新しいステップを追加する：

```bash
# Step N: 新しいエンドポイントのテスト
echo "--- Step N: Search tasks ---"
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/tasks/search?q=test")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
assert_status "GET /tasks/search?q=test" 200 "$HTTP_CODE"
echo "$BODY" | jq .
echo ""
```

`assert_status` 関数が自動的に PASS/FAIL をカウントし、サマリーに反映される。
