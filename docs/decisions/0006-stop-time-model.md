# ADR-0006: StopTime モデルの責務

- Status: Accepted
- Date: 2026-07-19

## Context

現在、Parser は EkiJikoku レコードを直接 StopTime モデルへ変換している。

```text
EkiJikoku
    ↓
StopTime
```

StopTime はアプリケーション側で利用するドメインモデルであり、
現在は以下の情報を保持している。

- station
- order
- arrival_time
- departure_time
- is_pass
- track_index

一方、OudiaSecond の EkiJikoku レコードには、よりファイルフォーマットに近い情報が含まれている。

例

```
1;503/504$0
```

```
stop_flag = 1
arrival_time = 503
departure_time = 504
track_index = 0
```

GUI 調査の結果、

- stop_flag は停車・通過を表す
- track は EkiTrack2 のインデックスである

ことが確認できた。

## Decision

現時点では StopTime をそのままドメインモデルとして利用する。

Parser が直接 StopTime を生成する構成を維持する。

新たな中間モデルは導入しない。

## Consequences

実装はシンプルなまま維持できる。

一方で、将来的に以下のような要求が発生した場合は、中間モデルの導入を再検討する。

- OudiaSecond ファイルを完全に再現して保存する
- stop_flag の種類が増える
- Parser と Writer を共通モデルで実装したい
- OudiaSecond 独自情報を保持する必要がある

その場合は次のような構成を検討する。

```text
EkiJikoku
    ↓
StopTimeRecord
    ↓
StopTime
```

StopTimeRecord はファイルフォーマットを忠実に表現する DTO とし、
StopTime はアプリケーションが利用するドメインモデルとする。

現時点では YAGNI の原則に従い採用しない。