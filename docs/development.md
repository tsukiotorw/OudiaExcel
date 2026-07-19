# Development Guide

## Purpose

本ドキュメントは OudiaExcel プロジェクトの開発ルールを定義します。

本プロジェクトでは、保守性・拡張性・可読性を重視し、小さな単位で品質を積み上げる開発を目指します。

---

# Development Workflow

基本的な開発フローは以下のとおりです。

```text
Research
    ↓
Design
    ↓
Test
    ↓
Implementation
    ↓
Refactor
    ↓
Commit
```

## 1. Research

実データを調査し、仕様を整理します。

成果物

- docs/research/

調査結果では以下を明確に区別します。

- 確認済み事項
- 推測
- 未解決事項

推測のみで実装してはいけません。

---

## 2. Design

実装前に設計を行います。

成果物

- docs/design/

以下を明確にします。

- 責務
- 入出力
- クラス構成
- データフロー

設計変更が発生した場合は、設計書を先に更新します。

---

## 3. Test

Test Driven Development (TDD) を採用します。

基本サイクル

```
Red
↓
Green
↓
Refactor
```

pytest によるテストを先に作成し、最小限の実装でテストを通します。

---

## 4. Implementation

実装では以下を重視します。

- 責務を分離する
- 小さな関数を作る
- 型ヒントを記述する
- Docstringを書く

---

## 5. Refactor

動作を変更せず、コード品質のみを改善します。

以下を優先します。

- 関数分割
- 命名改善
- 重複削除
- 可読性向上

リファクタリング後は必ず pytest を実行します。

---

## 6. Commit

コミット前には必ず

```bash
pytest
```

を実行し、すべてのテストが成功していることを確認します。

コミットは小さく行います。

例

```
feat(parser): parse train
feat(time_parser): parse arrival time
refactor(time_parser): extract _parse_record
docs: update parser design
```

---

# Coding Standards

## Python

対象バージョン

- Python 3.13

### 型ヒント

すべての関数に型ヒントを記述します。

```python
def parse(value: str) -> Railway:
```

Optional は

```python
str | None
```

を使用します。

---

### dataclass

ドメインモデルは dataclass を使用します。

---

### match文

複数条件の分岐では match を優先します。

```python
match child.name:
    case "Dia":
        ...
```

---

### Docstring

公開・非公開を問わず関数には Docstring を記述します。

説明は「何をするか」を記述し、「どう実装するか」は書きません。

---

### staticmethod

インスタンス状態 (`self`) やクラス状態 (`cls`) を使用しないメソッドは、
原則として `@staticmethod` とします。

目的

- インスタンス状態への依存がないことを明示する
- 関数の責務を明確にする
- 将来、別クラスや別モジュールへ移動しやすくする

例

```python
class TimeParser:

    @staticmethod
    def _detect_record_type(record: str) -> RecordType:
        ...
```
---


### 関数

関数はできるだけ単一責務とします。

長くなったら積極的に分割します。

---

# Documentation Rules

## research

実データから分かった事実を記録します。

推測は「推測」と明記します。

---

## design

実装方法を記述します。

実装変更時は先に更新します。

---

## decisions

重要な設計判断を ADR として記録します。

以下を含めます。

- Decision
- Reason
- Consequences

---

# Project Philosophy

本プロジェクトでは以下を重視します。

- ドメインモデル中心設計
- 責務の分離
- TDD
- 小さなコミット
- 継続的リファクタリング
- 実データによる仕様調査
  
  