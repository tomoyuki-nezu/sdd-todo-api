"""タスク管理ハンドラのユニットテスト."""

import importlib
import json
import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_table():
    """_get_table をモックして DynamoDB テーブルを差し替える."""
    mock_tbl = MagicMock()

    with patch("src.handlers.tasks._get_table", return_value=mock_tbl):
        yield mock_tbl

    sys.modules.pop("src.handlers.tasks", None)


def _make_event(
    method: str,
    resource: str,
    body: dict | None = None,
    path_params: dict | None = None,
) -> dict:
    """テスト用の API Gateway イベントを生成する."""
    return {
        "httpMethod": method,
        "resource": resource,
        "body": json.dumps(body) if body else None,
        "pathParameters": path_params,
    }


class TestCreateTask:
    """POST /tasks のテスト."""

    def test_create_task_success(self, mock_table: MagicMock) -> None:
        """タスク作成が成功する."""
        from src.handlers.tasks import handler

        event = _make_event("POST", "/tasks", body={"title": "牛乳を買う"})
        response = handler(event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["title"] == "牛乳を買う"
        assert body["done"] is False
        assert "task_id" in body
        assert "created_at" in body
        mock_table.put_item.assert_called_once()

    def test_create_task_missing_title(self, mock_table: MagicMock) -> None:
        """title が未指定の場合 400 を返す."""
        from src.handlers.tasks import handler

        event = _make_event("POST", "/tasks", body={})
        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "MISSING_TITLE"

    def test_create_task_with_done_flag(self, mock_table: MagicMock) -> None:
        """done フラグ付きでタスクを作成できる."""
        from src.handlers.tasks import handler

        event = _make_event("POST", "/tasks", body={"title": "test", "done": True})
        response = handler(event, None)

        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["done"] is True


class TestListTasks:
    """GET /tasks のテスト."""

    def test_list_tasks_empty(self, mock_table: MagicMock) -> None:
        """タスクが0件の場合空配列を返す."""
        from src.handlers.tasks import handler

        mock_table.scan.return_value = {"Items": []}
        event = _make_event("GET", "/tasks")
        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["tasks"] == []

    def test_list_tasks_with_items(self, mock_table: MagicMock) -> None:
        """タスクが存在する場合、一覧を返す."""
        from src.handlers.tasks import handler

        mock_table.scan.return_value = {
            "Items": [
                {"task_id": "abc", "title": "牛乳を買う", "done": False, "created_at": "2026-01-01T00:00:00+00:00"}
            ]
        }
        event = _make_event("GET", "/tasks")
        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body["tasks"]) == 1
        assert body["tasks"][0]["title"] == "牛乳を買う"


class TestGetTask:
    """GET /tasks/{task_id} のテスト."""

    def test_get_task_success(self, mock_table: MagicMock) -> None:
        """存在するタスクを取得できる."""
        from src.handlers.tasks import handler

        mock_table.get_item.return_value = {
            "Item": {"task_id": "abc", "title": "牛乳を買う", "done": False, "created_at": "2026-01-01T00:00:00+00:00"}
        }
        event = _make_event("GET", "/tasks/{task_id}", path_params={"task_id": "abc"})
        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["task_id"] == "abc"

    def test_get_task_not_found(self, mock_table: MagicMock) -> None:
        """存在しないタスクは 404 を返す."""
        from src.handlers.tasks import handler

        mock_table.get_item.return_value = {}
        event = _make_event("GET", "/tasks/{task_id}", path_params={"task_id": "nonexistent"})
        response = handler(event, None)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] == "TASK_NOT_FOUND"


class TestUpdateTask:
    """PUT /tasks/{task_id} のテスト."""

    def test_update_task_done(self, mock_table: MagicMock) -> None:
        """done フラグを更新できる."""
        from src.handlers.tasks import handler

        mock_table.get_item.return_value = {
            "Item": {"task_id": "abc", "title": "牛乳を買う", "done": False, "created_at": "2026-01-01T00:00:00+00:00"}
        }
        mock_table.update_item.return_value = {
            "Attributes": {"task_id": "abc", "title": "牛乳を買う", "done": True, "created_at": "2026-01-01T00:00:00+00:00"}
        }
        event = _make_event("PUT", "/tasks/{task_id}", body={"done": True}, path_params={"task_id": "abc"})
        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["done"] is True

    def test_update_task_not_found(self, mock_table: MagicMock) -> None:
        """存在しないタスクの更新は 404 を返す."""
        from src.handlers.tasks import handler

        mock_table.get_item.return_value = {}
        event = _make_event("PUT", "/tasks/{task_id}", body={"done": True}, path_params={"task_id": "nonexistent"})
        response = handler(event, None)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] == "TASK_NOT_FOUND"

    def test_update_task_no_fields(self, mock_table: MagicMock) -> None:
        """更新フィールドが未指定の場合 400 を返す."""
        from src.handlers.tasks import handler

        event = _make_event("PUT", "/tasks/{task_id}", body={}, path_params={"task_id": "abc"})
        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "NO_UPDATE_FIELDS"


class TestDeleteTask:
    """DELETE /tasks/{task_id} のテスト."""

    def test_delete_task_success(self, mock_table: MagicMock) -> None:
        """タスクを削除できる."""
        from src.handlers.tasks import handler

        mock_table.get_item.return_value = {
            "Item": {"task_id": "abc", "title": "牛乳を買う", "done": False, "created_at": "2026-01-01T00:00:00+00:00"}
        }
        event = _make_event("DELETE", "/tasks/{task_id}", path_params={"task_id": "abc"})
        response = handler(event, None)

        assert response["statusCode"] == 200
        mock_table.delete_item.assert_called_once_with(Key={"task_id": "abc"})

    def test_delete_task_not_found(self, mock_table: MagicMock) -> None:
        """存在しないタスクの削除は 404 を返す."""
        from src.handlers.tasks import handler

        mock_table.get_item.return_value = {}
        event = _make_event("DELETE", "/tasks/{task_id}", path_params={"task_id": "nonexistent"})
        response = handler(event, None)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] == "TASK_NOT_FOUND"


class TestBasicFlow:
    """仕様書 examples: タスク作成→一覧取得→更新→削除の基本フロー."""

    def test_full_crud_flow(self, mock_table: MagicMock) -> None:
        """CRUD 一連のフローが正常に動作する."""
        from src.handlers.tasks import handler

        # Step 1: POST /tasks { title: "牛乳を買う" } → 201
        event = _make_event("POST", "/tasks", body={"title": "牛乳を買う"})
        response = handler(event, None)
        assert response["statusCode"] == 201
        created_task = json.loads(response["body"])
        task_id = created_task["task_id"]

        # Step 2: GET /tasks → 200（1件含む）
        mock_table.scan.return_value = {"Items": [created_task]}
        event = _make_event("GET", "/tasks")
        response = handler(event, None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body["tasks"]) == 1

        # Step 3: PUT /tasks/{id} { done: true } → 200
        mock_table.get_item.return_value = {"Item": created_task}
        updated_task = {**created_task, "done": True}
        mock_table.update_item.return_value = {"Attributes": updated_task}
        event = _make_event("PUT", "/tasks/{task_id}", body={"done": True}, path_params={"task_id": task_id})
        response = handler(event, None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["done"] is True

        # Step 4: DELETE /tasks/{id} → 200
        mock_table.get_item.return_value = {"Item": updated_task}
        event = _make_event("DELETE", "/tasks/{task_id}", path_params={"task_id": task_id})
        response = handler(event, None)
        assert response["statusCode"] == 200
