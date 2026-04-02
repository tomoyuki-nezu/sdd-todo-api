"""タスク管理 Lambda ハンドラ."""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _get_table() -> Any:
    """DynamoDB テーブルリソースを取得する.

    環境変数を毎回読み直し、DYNAMODB_ENDPOINT が設定されている場合は
    そのエンドポイントに接続する。

    Returns:
        DynamoDB テーブルリソース
    """
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=os.environ.get("DYNAMODB_ENDPOINT"),
        region_name=os.environ.get("AWS_DEFAULT_REGION", "ap-northeast-1"),
    )
    return dynamodb.Table(os.environ.get("TABLE_NAME", "TasksTable"))


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    """HTTP レスポンスを生成する.

    Args:
        status_code: HTTP ステータスコード
        body: レスポンスボディ

    Returns:
        API Gateway 形式のレスポンス辞書
    """
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def list_tasks(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """タスク一覧を取得する.

    Args:
        event: API Gateway イベント
        context: Lambda コンテキスト

    Returns:
        タスク一覧のレスポンス
    """
    logger.info(f"DYNAMODB_ENDPOINT={os.environ.get('DYNAMODB_ENDPOINT')}")
    logger.info(f"TABLE_NAME={os.environ.get('TABLE_NAME')}")
    logger.info(f"AWS_DEFAULT_REGION={os.environ.get('AWS_DEFAULT_REGION')}")
    logger.info("Listing all tasks")
    table = _get_table()
    result = table.scan()
    tasks = result.get("Items", [])
    return _response(200, {"tasks": tasks})


def create_task(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """新しいタスクを作成する.

    Args:
        event: API Gateway イベント
        context: Lambda コンテキスト

    Returns:
        作成されたタスクのレスポンス
    """
    logger.info("Creating a new task")
    body = json.loads(event.get("body") or "{}")
    title = body.get("title")

    if not title:
        return _response(400, {"error": "MISSING_TITLE"})

    if len(title) > 200:
        return _response(400, {"error": "MISSING_TITLE"})

    task = {
        "task_id": str(uuid.uuid4()),
        "title": title,
        "done": body.get("done", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    table = _get_table()
    table.put_item(Item=task)
    logger.info("Task created: %s", task["task_id"])
    return _response(201, task)


def get_task(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """特定のタスクを取得する.

    Args:
        event: API Gateway イベント
        context: Lambda コンテキスト

    Returns:
        タスクのレスポンス
    """
    task_id = event["pathParameters"]["task_id"]
    logger.info("Getting task: %s", task_id)

    table = _get_table()
    result = table.get_item(Key={"task_id": task_id})
    item = result.get("Item")

    if not item:
        return _response(404, {"error": "TASK_NOT_FOUND"})

    return _response(200, item)


def update_task(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """タスクを更新する.

    Args:
        event: API Gateway イベント
        context: Lambda コンテキスト

    Returns:
        更新されたタスクのレスポンス
    """
    task_id = event["pathParameters"]["task_id"]
    logger.info("Updating task: %s", task_id)

    body = json.loads(event.get("body") or "{}")

    update_fields: dict[str, Any] = {}
    if "title" in body:
        if len(body["title"]) > 200:
            return _response(400, {"error": "MISSING_TITLE"})
        update_fields["title"] = body["title"]
    if "done" in body:
        update_fields["done"] = body["done"]

    if not update_fields:
        return _response(400, {"error": "NO_UPDATE_FIELDS"})

    table = _get_table()

    # タスクの存在確認
    result = table.get_item(Key={"task_id": task_id})
    if "Item" not in result:
        return _response(404, {"error": "TASK_NOT_FOUND"})

    update_expr_parts: list[str] = []
    expr_values: dict[str, Any] = {}
    expr_names: dict[str, str] = {}

    for key, value in update_fields.items():
        placeholder = f":val_{key}"
        name_placeholder = f"#attr_{key}"
        update_expr_parts.append(f"{name_placeholder} = {placeholder}")
        expr_values[placeholder] = value
        expr_names[name_placeholder] = key

    update_expression = "SET " + ", ".join(update_expr_parts)

    updated = table.update_item(
        Key={"task_id": task_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names,
        ReturnValues="ALL_NEW",
    )

    return _response(200, updated["Attributes"])


def delete_task(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """タスクを削除する.

    Args:
        event: API Gateway イベント
        context: Lambda コンテキスト

    Returns:
        削除結果のレスポンス
    """
    task_id = event["pathParameters"]["task_id"]
    logger.info("Deleting task: %s", task_id)

    table = _get_table()

    # タスクの存在確認
    result = table.get_item(Key={"task_id": task_id})
    if "Item" not in result:
        return _response(404, {"error": "TASK_NOT_FOUND"})

    table.delete_item(Key={"task_id": task_id})
    logger.info("Task deleted: %s", task_id)
    return _response(200, {"message": f"Task {task_id} deleted"})


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda エントリポイント. HTTP メソッドとパスに基づいてルーティングする.

    Args:
        event: API Gateway イベント
        context: Lambda コンテキスト

    Returns:
        API Gateway 形式のレスポンス
    """
    http_method = event.get("httpMethod", "")
    resource = event.get("resource", "")

    logger.info("Received %s %s", http_method, resource)

    routes: dict[tuple[str, str], Any] = {
        ("GET", "/tasks"): list_tasks,
        ("POST", "/tasks"): create_task,
        ("GET", "/tasks/{task_id}"): get_task,
        ("PUT", "/tasks/{task_id}"): update_task,
        ("DELETE", "/tasks/{task_id}"): delete_task,
    }

    handler_fn = routes.get((http_method, resource))
    if not handler_fn:
        return _response(404, {"error": "Not Found"})

    return handler_fn(event, context)
