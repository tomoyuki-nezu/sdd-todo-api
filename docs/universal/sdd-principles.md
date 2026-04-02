# SDD（仕様書ドリブン開発）の設計思想・原則

## SDD とは

仕様書ドリブン開発（Specification-Driven Development）は、構造化された仕様書を Single Source of Truth とし、AI エージェントがコード・テスト・インフラを自動生成する開発手法。

## 基本原則

### 1. 仕様書が唯一の真実の源泉

```
仕様書(YAML) → コード生成 → テスト生成 → インフラ生成
```

- コードは仕様書から生成される
- テストは仕様書の `examples` セクションに基づく
- インフラ定義は仕様書の `technical_constraints` に基づく
- 仕様書が変わればコードが変わる（逆ではない）

### 2. AI エージェントの行動制約（constitution.md）

AI の自律性と安全性を両立するため、行動範囲を3段階で制御する：

| Zone | 説明 | AI の動作 |
|---|---|---|
| Green | 自律判断してよい | コード生成、テスト修正、ドキュメント |
| Yellow | Human の承認が必要 | デプロイ、破壊的変更、テーブル定義変更 |
| Red | 絶対禁止 | 本番データ直接アクセス、シークレット記述 |

### 3. エスカレーション条件

以下の場合は AI が処理を中断し、Human に通知する：

- 仕様書の解釈が複数に分かれる場合
- テスト修正ループが 3 回を超えた場合
- Red Zone の操作が必要と判断された場合

## 仕様書の構造

### ディレクトリ構成

```
spec/
├── constitution.md       # プロジェクト憲法（AI の行動制約）
└── api/
    └── <resource>.yaml   # API 仕様書
```

### API 仕様書の標準フォーマット

```yaml
metadata:
  feature: <feature-name>
  version: 1.0.0
  status: approved

overview:
  description: "<機能の説明>"
  base_path: /<resource>

endpoints:
  - id: <operation-id>
    method: <HTTP_METHOD>
    path: /<resource>
    description: "<操作の説明>"
    request:
      schema:
        <field>: { type: <type>, required: <bool> }
    response:
      success:
        status: <code>
        schema: { ... }
      errors:
        - status: <code>
          code: <ERROR_CODE>

examples:
  - name: "<シナリオ名>"
    steps:
      - <METHOD> <path> <body> → <status>

technical_constraints:
  runtime: <runtime>
  datastore: <datastore>
  table_name: <TableName>
  partition_key: <pk>
```

## SDD のワークフロー

### 新機能の追加

1. **仕様書を書く**（Cursor で `spec/api/<resource>.yaml` を編集）
2. **コード生成を依頼**（Claude Code に仕様書を渡す）
3. **テストを確認**（自動生成されたテストがパスすることを確認）
4. **コミット・プッシュ**（Claude Code に依頼）
5. **CI/CD で自動デプロイ**
6. **E2E テストで動作確認**

### 既存機能の変更

1. **仕様書を変更**
2. **差分を反映**（Claude Code に「仕様書の変更を反映して」と依頼）
3. **テストの更新を確認**
4. **コミット・プッシュ**

## マルチエージェント構成

SDD では複数の AI ツールが役割分担する：

| ツール | 役割 | 担当する作業 |
|---|---|---|
| Cursor | 仕様書エディタ | YAML 仕様書の編集・レビュー |
| Claude Code | コード生成エージェント | コード・テスト・インフラの生成、Git 操作 |
| GitHub Actions | CI/CD | 自動テスト・自動デプロイ |
