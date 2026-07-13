# Tokenizer設計

## 1. 概要

TokenizerはReaderが読み込んだOudiaSecondファイルを解析し、
行単位の文字列を意味のあるTokenへ変換する。

Tokenizerは構文解析のみを担当し、
OudiaSecondの意味（RailwayやStationなど）は解釈しない。

---

# 2. 責務

Tokenizerの責務は以下とする。

- SourceFileを受け取る
- 行単位で解析する
- Tokenへ変換する
- 行番号を保持する
- 生の文字列を保持する

Tokenizerは以下を行わない。

- Railway生成
- Station生成
- Diagram生成
- Train生成
- StopTime生成
- バリデーション
- ドメイン知識の保持

---

# 3. 入出力

## 入力

SourceFile

```python
SourceFile
```

## 出力

```python
list[Token]
```

Tokenは入力ファイルの行順を保持する。

---

# 4. Token一覧

## KeyValueToken

例

```text
Name=中央線
```

生成

```python
KeyValueToken(
    key="Name",
    value="中央線"
)
```

---

## SectionStartToken

例

```text
Eki.
```

生成

```python
SectionStartToken(
    name="Eki"
)
```

---

## SectionEndToken

例

```text
.
```

生成

```python
SectionEndToken()
```

---

## BlankToken

例

```text

```

生成

```python
BlankToken()
```

---

## CommentToken

コメント構文が存在する場合のみ使用する。

現時点では未使用。

---

# 5. Token共通情報

すべてのTokenは以下を保持する。

|項目|説明|
|----|----|
|line_number|元ファイルの行番号（1始まり）|
|raw_line|元の文字列|

---

# 6. Tokenクラス構成

```
Token
 ├── KeyValueToken
 ├── SectionStartToken
 ├── SectionEndToken
 ├── BlankToken
 └── CommentToken
```

---

# 7. Tokenizer公開API

```python
def tokenize(source: SourceFile) -> list[Token]:
    """SourceFileをToken列へ変換する。"""
```

Tokenizerが公開する関数はこれのみとする。

---

# 8. Tokenizerアルゴリズム

各行について以下の順で判定する。

1. 空行
2. コメント
3. Section終了（`.`）
4. Section開始（`Eki.`など）
5. Key=Value
6. 上記以外はTokenizerError

---

# 9. エラー

Tokenizerでは以下の場合にTokenizerErrorを送出する。

- 未知の構文
- Key=Valueとして解釈できない行
- セクション開始構文が不正

Tokenizerはドメインルールによるエラーは扱わない。

---

# 10. Parserとの責務分離

Tokenizerは

```text
Name=中央線
```

を

```text
KeyValueToken
```

へ変換するだけである。

これがRailwayのNameなのか、
StationのNameなのかはParserが判断する。

---

# 11. 将来の拡張

将来的に以下のToken追加を想定する。

- NumberToken
- BooleanToken
- CommentToken
- UnknownToken

現段階では実装しない。

---

# 12. テスト方針

最低限以下を確認する。

- Key=Valueが正しくToken化される
- Section開始が認識できる
- Section終了が認識できる
- 空行が認識できる
- 不正な行でTokenizerErrorとなる

