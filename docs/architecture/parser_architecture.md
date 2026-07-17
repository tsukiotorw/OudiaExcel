# OudiaSecond Parser Architecture

## 概要

OudiaSecond Parserは、OudiaSecond(.oud2)ファイルを
ドメインモデルへ変換するライブラリである。

責務ごとに以下の4層へ分離する。

Reader
    ↓
Tokenizer
    ↓
SectionBuilder
    ↓
Parser
    ↓
Domain Model


## Reader

### 責務
    - ファイルの読み込み
    - 文字コード判定
    - SourceFile生成

### 入力
    Path

### 出力
    SourceFile

    @dataclass
    class SourceFile:
        lines: list[str]
        encoding: str
        path: Path


## Tokenizer

### 責務
    - 行をTokenへ変換する
    - Tokenizerは意味を理解しない

### 入力
    SourceFile

### 出力
    Token[] 

    生成するToken
    - SectionStartToken
    - SectionEndToken
    - KeyValueToken
    - BlankToken
  

## SectionBuilder

### 責務
    Token列からSectionツリーを構築する。

### 入力
    Token[]

### 出力
    SectionNode

    例
    Rosen
    ├── Eki
    ├── Eki
    └── Dia
        ├── Kudari
        └── Nobori

## Parser
### 責務
    - Sectionツリーをドメインモデルへ変換する。
    - ファイル構造とドメインモデルの違いを吸収する。

### 入力
    SectionNode

### 出力
    Railway

### Parserの構成
    parse()

    _parse_railway()

    _parse_station()

    _parse_dia()

    _parse_direction()

    _parse_train()

    _parse_stop_times()

### Diaの変換
    OudiaSecond
        Dia
        ├── Kudari
        └── Nobori
     ↓
    Domain Model
        Diagram(Direction.DOWN)
        Diagram(Direction.UP)
    - Dia自体はDiagramではない
    - Parserが上下2つのDiagramへ変換する。

### Trainの変換
    Ressya
     ↓
    Train

    現時点では
    - Syubetsh
    - Ekijikoku
    のみ解析対象とする。
    Operation系は対象外。

### StopTime
    Ekijikokuの解析はParser本体から分離し、
    time_perser.py
    へ実装する。

### Validator
    Parser終了後に事項する。

#### 責務
    - Staion参照整合性
    - Diagram整合性
    - Train整合性
    - StopTime整合性



## 設計変更履歴

### 2026-07-18

#### Diaの扱いを変更

当初はDiaをDiagramへ1対1で変換する設計としていた。

実際の.oud2ファイルを調査した結果、

Dia
├── Kudari
└── Nobori

という構造であることを確認した。

そのためParserでは

Diagram(Direction.DOWN)
Diagram(Direction.UP)

の2つへ変換する設計へ変更した。

理由:
ドメインモデルではDiagramが方向を保持するため。

