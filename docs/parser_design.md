# Parser Design

## 目的

Parserを作る前に .oud2 ファイルの構造を調査する。
本ツールはParserではなく、調査用ツールである。

---

## inspect_oud2.py の責務

- CLIからファイルを受け取る
- 文字コードを判定する
- 行番号付きで内容を表示する

Parserは呼ばない。

---

## 非機能要件

- Python 3.13
- argparse
- pathlib
- logging
- 型ヒント
- PEP8

---

## 対応文字コード

優先順位

1. UTF-8 BOM
2. UTF-8
3. CP932

---

## Parserとの違い

inspect_oud2.py

目的：
ファイルを観察する

Parser

目的：
Domain Modelを構築する

---

## 今後追加予定

- Section抽出
- Key=Value解析
- Domain Model生成

