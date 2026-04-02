---
name: doc-writer
description: >
  ドキュメントを作成・更新するとき、または
  「ドキュメントを書いて」「READMEを更新して」
  などの依頼を受けたとき
allowed-tools: [Read, Write, Edit]
---

# Document Writer

## ドキュメント生成の基本ルール

### 言語
- ドキュメントは日本語で記述すること
- コミットメッセージは英語（git-workflow Skill に従う）

### 機密情報の取り扱い
- AWS アカウント ID → `<YOUR_ACCOUNT_ID>`
- IAM Role ARN → `<YOUR_ROLE_ARN>`
- SSO URL → `<YOUR_SSO_URL>`
- API Gateway URL → `https://<YOUR_API_ID>.execute-api.ap-northeast-1.amazonaws.com/Prod`
- プロファイル名 → `<YOUR_PROFILE_NAME>`

### ドキュメントの種類と配置

| 種類 | 配置先 | 説明 |
|---|---|---|
| 汎用ドキュメント | `docs/universal/` | どのプロジェクトでも使える |
| プロジェクト固有 | `docs/project/` | このプロジェクト専用 |
| README | ルート | プロジェクトの入口 |

### README.md の標準セクション
1. プロジェクト概要
2. システム構成図
3. 前提条件
4. 初回セットアップ手順
5. ローカル開発のワークフロー
6. Claude Code を使った開発フロー
7. デプロイ後の確認方法
8. トラブルシューティング
9. AWS リソース一覧

### 記述スタイル
- 箇条書きとテーブルを活用する
- コマンド例は必ずコードブロックで記載
- トラブルシューティングは「症状→原因→解決」の形式
- システム構成図はテキスト図（ASCII art）で表現
