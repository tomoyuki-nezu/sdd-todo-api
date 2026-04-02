---
name: python-lambda
description: >
  Python の Lambda 関数を生成・修正するとき、
  または src/ 以下のコードを扱うとき
allowed-tools: [Read, Write]
---

# Python Lambda Skill

## ハンドラ構造
- ファイル: src/handlers/{リソース名}.py
- 関数名: lambda_handler(event, context)
- レスポンス形式:
  {
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps(data, ensure_ascii=False)
  }

## 必須事項
- 型アノテーションを必ず付与する
- すべての関数に docstring を書く
- ログは print ではなく logger を使用する
- エラーは {"error": "メッセージ"} 形式で返す
- DynamoDB 操作は boto3 を使用する

## 禁止事項
- ハードコードされたテーブル名（環境変数から取得）
- ハードコードされた AWS リージョン
- 例外の握りつぶし（必ずログ出力）