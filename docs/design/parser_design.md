# Parser設計

## 目的

SectionBuilder が生成した SectionNode ツリーを解析し、
OudiaSecond のドメインモデルへ変換する。

Parser は OudiaSecond の仕様を知る唯一の層であり、
SectionNode の内容を Railway / Diagram / Train / Station / StopTime
へ変換する責務を持つ。

意味的な整合性チェックは Validator が担当する。

---

## 入力

SectionNode

---

## 出力

Railway

---

## 責務

- Railway を生成する
- Station を生成する
- Diagram を生成する
- Train を生成する
- StopTime を生成する

---

## 行わないこと

- ファイル読み込み
- 文字コード判定
- Token生成
- Section構造生成
- 意味チェック

---

## エラー

ParserError

例)

- 必須キーが存在しない
- 不明なSection
- 不明なキー


## TimeParserの構造
TimeParser

parse_stop_times()
    ↓
TimeParser.parse()
    ↓
_parse_record()
    ↓
_parse_time_record()
    ↓
_parse_time()