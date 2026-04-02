---
name: sam-architect
description: >
  SAM template.yaml を生成・修正するとき、
  または AWS インフラ定義を扱うとき
allowed-tools: [Read, Write, Bash]
---

# SAM Architect Skill

## 設計原則
- IAM は最小権限。Action は具体的に列挙する
- すべてのリソースに Environment タグを付与
- 環境変数でテーブル名・リージョンを注入する
- Lambda メモリは 256MB から開始する
- CloudWatch Logs の保持期間は 30 日

## 禁止事項
- IAM の Action に * ワイルドカード使用禁止
- ハードコードされた ARN・アカウント ID 禁止
- 本番環境の手動変更禁止（すべて IaC 経由）

## 検証
- 生成後は必ず sam validate を実行すること