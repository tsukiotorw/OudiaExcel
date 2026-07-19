# OudiaExcel

OudiaSecond (*.oud2) の解析ライブラリ。

## Documentation

本プロジェクトの設計・調査資料は `docs/` 配下に整理しています。

### Architecture

システム全体および各コンポーネントの構成を説明します。

|ファイル|内容|
|---|---|
|`docs/architecture/architecture.md`|システム全体のアーキテクチャ|
|`docs/architecture/parser_architecture.md`|Parserコンポーネントのアーキテクチャ|

---

### Design

実装前に作成した設計資料です。

|ファイル|内容|
|---|---|
|`docs/design/domain_model.md`|ドメインモデル設計|
|`docs/design/parser_design.md`|Parser設計|
|`docs/design/tokenizer_design.md`|Tokenizer設計|
|`docs/design/section_builder_design.md`|SectionBuilder設計|
|`docs/design/parser_workflow.md`|Parser全体の処理フロー|

---

### Research

OudiaSecondファイルフォーマットの調査結果をまとめています。

|ファイル|内容|
|---|---|
|`docs/research/oud2_notes.md`|OudiaSecondファイルフォーマット調査メモ|

調査資料では、実データから確認できた内容と推測を明確に区別しています。

---

### Architecture Decision Records (ADR)

設計上の重要な判断と、その理由を記録しています。

|フォルダ|内容|
|---|---|
|`docs/decisions/`|Architecture Decision Records (ADR)|

各ファイルは `0001-xxxx.md` の形式で管理しています。

---

### AI Development Guide

AIアシスタント向けの開発ガイドです。

|ファイル|内容|
|---|---|
|`docs/agents_ja.md`|AI向け開発ルール・コーディングガイドライン|

---

## Documentation Workflow

本プロジェクトでは、以下の流れで開発を進めます。

```text
Research
    ↓
Design
    ↓
Test
    ↓
Implementation
```

1. **Research**
   - 実データを調査し、仕様を確認する
   - 調査結果は `docs/research/` に記録する

2. **Design**
   - 実装前に設計を整理する
   - 設計書は `docs/design/` に記録する

3. **Test**
   - pytest によるテストを先に作成する（TDD）

4. **Implementation**
   - テストを満たす最小限の実装を行う
   - 必要に応じてリファクタリングを実施する

重要な設計判断は `docs/decisions/` に ADR として記録します。


## Development Philosophy

本プロジェクトでは、保守性と拡張性を重視し、以下の原則に従って開発を行います。

- ドメインモデル中心の設計
- 責務の明確な分離
- Test Driven Development (TDD)
- 実データに基づく仕様調査
- 小さな単位でのコミットとリファクタリング