---
name: git-workflow
description: >
  「コミットして」「プッシュして」など
  Git 操作を依頼されたとき
allowed-tools: [Read, Bash]
---

# Git Workflow

## コミットのルール
- コミットメッセージは必ず英語で記述すること
- Conventional Commits 形式に従うこと:
  `<type>(<scope>): <subject>`
  `<body>（必要な場合）`
- type の種類:
  - feat: 新機能
  - fix: バグ修正
  - docs: ドキュメントのみの変更
  - refactor: リファクタリング
  - test: テストの追加・修正
  - chore: ビルド・設定ファイルの変更
- subject は動詞の原形で始めること（Add / Fix / Update など）
- subject は 50 文字以内
- body には変更の背景・理由を記載すること

## コミットの実行手順
「コミットして」と依頼された場合：
1. git status で未コミットの変更を確認
2. git diff で変更内容を分析
3. 変更内容から適切なコミットメッセージを英語で自動生成
4. 複数の関心事にまたがる場合は複数コミットに分割
5. git commit を実行
6. コミット完了をレポートする
※ コミット前のメッセージ確認は不要

## プッシュの実行手順
「プッシュして」と依頼された場合：
1. git status で未プッシュのコミットを確認
2. git branch --show-current で現在のブランチを取得
3. git push origin <現在のブランチ名> を実行
4. プッシュ完了をレポートする

## 禁止事項
- force push は Human の明示的な許可なしに禁止
- main ブランチへの直接コミットは禁止
  （feature ブランチを作成して PR 経由で）
- 機密情報を含むファイルのコミットは禁止
