# agents_ja.md

# AIを使った開発のガイド

## プロジェクト概要
このプロジェクトは **OudiaSecond（*.oud2）** のダイヤファイルを解析し、
Microsoft Excel の駅時刻表を生成することを目的とする。

開発には以下を利用する。

- Visual Studio Code
- GitHub Copilot（Agent Mode）
- ChatGPT
- GitHub MCP

目的は「とりあえず動くもの」ではなく、保守しやすいソフトウェアを作ること。


## システム構成
Railway
 ├── Station
 └── Diagram
      └── Train
           └── StopTime

このドメインモデルが設計の中心であり、
他の処理はすべてこのモデルを利用する


## リポジトリ構成
src/
    models/
    parser/
    excel/
    tools/

docs/

examples/

tests/

役割ごとにディレクトリを分離する。


## ドメインモデルのルール
Railway が最上位オブジェクト。

Railway は
- Station
- Diagram
を保持する。

Diagram は
- Train
を保持する。

Train は
- StopTime
を保持する。

StopTime は Station を参照する。

**原則**
- 必要になるまでは逆参照を作らない
- 同じ情報を複数箇所で持たない（Single Source of Truth）
- シンプルなオブジェクト構成を優先する


## Pythonのルール
対象バージョン : 
Python 3.13

利用するもの : 
- dataclass
- pathlib
- argparse
- typing
- StrEnum
- logging

利用しないもの : 
- os.path
- グローバル変数
- ミュータブルなデフォルト引数

PEP8 に従う。


## Parserの責務
Parser が行うこと : 
- .oud2 を読む
- テキストを解析する
- ドメインモデルを生成する
- データを検証する
- 問題があれば例外を送出する

Parser が行ってはいけないこと : 
- Excel を作る
- UI を操作する
- GitHub にアクセスする
- 画面表示を行う

Parser は
**解析だけ**
を担当する。


## Excel生成
Excel生成は別モジュールで行う。
Parser に Excel の知識を持たせない。
業務ロジックとExcel書式を混在させない。


## 開発手順
実装前に
1. 仕様を理解する
2. 必要ならドキュメントを書く
3. 実装する
4. 自分でレビューする
5. 変更内容を説明する
6. コミットする


## AIとの協業ルール
AI がコードを提案するときは
必ず
- 何を変更したか
- なぜ変更したか
- メリット
- デメリット
を説明する。

**AIの禁止事項**
- 勝手にドメインモデルを変更してはいけない。
- 新しいクラスを勝手に追加してはいけない。

**AIへのお願い**
- 読みやすさを優先する
- トリッキーなコードを書かない
- 関数は小さくする
- 分からなければ推測せず質問する


## ドキュメント
コードとドキュメントは常に一致させる。
ドメインモデルを変更したら
更新するもの : 
- docs/domain_model.md
- AGENTS.md
- README.md（必要なら）

ドキュメントも実装の一部である。


## テスト
Parser の機能は最終的にユニットテストを書く。

サンプルデータ : 
examples/

テストコード : 
tests/


## ログ
print() は開発用だけ。
通常は logging を使う。


## エラー処理
意味のある例外を送出する。
None を返して失敗を表現しない。
エラーを握り潰さない。


## パフォーマンス
速度より正しさを優先する。
早すぎる最適化はしない。


## レビュー項目
コミット前に確認する。
- 設計はシンプルか
- 情報を重複していないか
- ドメインモデルを守っているか
- ドキュメントを更新したか
- 型ヒントがあるか
- 読みやすいコードか


## コミット
1つのコミットでは
1つの目的だけ変更する。
コミットメッセージは英語。
例 : 
Add domain model

Implement parser

Improve validation

Generate Excel timetable


## OudiaSecond固有ルール
一般的な鉄道システムを前提に考えない。
OudiaSecond の仕様を忠実に再現する。

Parser は
**解釈ではなく再現**
を目的とする。

解析と変換は分離する。
未知のデータを勝手に無視しない。


## 外部リソース
資産リポジトリは
**読み取り専用**
と考える。

AI は資産リポジトリを書き換えてはいけない。
GitHub MCP は
読み取りだけに利用する。
生成物は開発リポジトリだけに保存する。

