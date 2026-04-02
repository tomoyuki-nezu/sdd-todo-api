---
name: question-doc
description: >
  複数の質問や方向性の確認が必要なとき、
  一問一答では非効率な場合に質問ドキュメントを作成して
  ユーザーに回答を求めるワークフロー。
  「回答を読んで実行して」と言われたときに
  質問ドキュメントを読み取って実行する。
allowed-tools: [Read, Write, Edit]
---

# Question Document Workflow

## 仕様

詳細な仕様は `docs/universal/question-document-spec.md` を参照すること。

## いつ使うか

- 質問数が 3 つ以上になる場合
- 質問間に依存関係がある場合
- 決定内容を記録として残す必要がある場合
- アーキテクチャ・方針に関わる重要な決定

## いつ使わないか

- Yes/No で答えられる単一の質問
- 明確な二択・三択の選択（1〜2問）
- 即座に回答が得られる事実確認

## 作成フロー

1. `.claude/questions/YYYYMMDD-<topic>.md` を作成する
2. `docs/universal/question-document-spec.md` のテンプレートに従って記述する
3. テンプレートがある場合は `.claude/questions/templates/` から利用する
4. ユーザーに通知する：
   「複数の決定事項があるため質問ドキュメントを作成しました。
    `.claude/questions/YYYYMMDD-topic.md`
    Cursor でファイルを開いて回答を記入してください。
    記入が完了したら『回答を読んで実行して』と伝えてください。」

## 読み取りフロー

「回答を読んで実行して」と言われた場合：

1. 質問ドキュメントを読み込む
2. 全回答を確認する（未回答があれば指摘する）
3. 回答の解釈を「Claude Code が実行するアクション」欄に記入する
4. 実行内容のサマリーをユーザーに提示して確認を取る
5. 承認後に実行する
6. 完了後にステータスを「実行済み」に更新する
7. 実行結果を「実行結果」欄に記入する
8. コミットする

## 注意事項

- 質問ドキュメントは `.gitignore` に追加しない（記録として保管する）
- 実行済みのものも削除しない
- 新規プロジェクト開始時は `.claude/questions/templates/new-project-template.md` を利用する
