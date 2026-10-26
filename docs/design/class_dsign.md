# クラス関連図

この資料は、`src/` の実装に基づくクラスと主要なモジュール間の関係を示します。編集可能な図は [class_dsign.drawio](./class_dsign.drawio) です。draw.ioで開くと、全体構成、ドメインモデル、運用情報、Parser、アプリケーション/UIの各ページを確認できます。

## 図の範囲と記法

- 実装されているクラス、列挙型、主要な手続き型モジュールを対象にしています。手続き型モジュールは `«module»` として示します。
- `*--` は所有・包含（コンポジション）、`-->` は参照または処理上の依存を示します。矢印に付した多重度と名前は、実装上のフィールドや処理を表します。
- Parserの処理は `read_file` → `tokenize` → `build_sections` → `Parser.parse` の順です。画面操作は `MainWindow` がアプリケーション関数を呼び出して処理します。
- UIやExcel出力から参照するドメイン型は、ページ間で図が分断されないよう、関係先のページにも必要な型名を記載しています。

## 全体の処理フロー

1. `application.oud2_loader` がファイル読込、トークン化、Sectionツリー構築、ドメインモデル化を順に実行します。
2. `Railway` を `StationTimetableGenerator` に渡し、指定駅の `StationTimetable` を生成します。
3. `ExcelWriter` が `StationTimetable` と表示設定を受け取り、`.xlsx` を作成します。
4. `MainWindow` は上記の処理と駅名・表示設定の保存/読込を接続し、`TimetablePreview` でプレビューを表示します。

## ドメインモデル

| クラス | 主な属性 | 役割・関係 |
|---|---|---|
| `Railway` | `name`, `stations`, `train_types`, `diagrams` | 路線の集約ルート。駅、列車種別、ダイヤを所有します。 |
| `Station` | `index`, `name`, `short_name`, `is_no_mark` | 駅。`display_name` は略称があれば略称を返します。 |
| `TrainType` | `index`, `name`, `short_name` | 路線内の列車種別。 |
| `Diagram` | `name`, `direction`, `trains` | 方向別ダイヤ。列車を所有します。 |
| `Train` | `number`, `train_type_index`, `stop_times`, `operations` | 列車。停車時刻と運用レコードを所有します。列車種別はIDで参照します。 |
| `StopTime` | `station`, `order`, `arrival_time`, `departure_time`, `is_pass`, `track_index` | 列車の駅ごとの時刻。`Station` を参照します。 |
| `Direction` (`railway.py`) | `UP`, `DOWN` | `Diagram` の方向を表し、Parserと時刻表生成で使用します。 |
| `Direction` (`direction.py`) | `UP`, `DOWN` | `models` パッケージから公開される別定義の列挙型です。現行の主要処理は `railway.py` 側の型を参照します。 |
| `TimetableEntry` | `minute`, `destination`, `train_type`, `train_number` | 駅時刻表に掲載する1列車の情報。 |
| `TimetableHour` | `hour`, `entries` | 1時間分の時刻表エントリを保持します。 |
| `StationTimetable` | `station_name`, `down`, `up`, `train_types` | 指定駅の上下方向の時刻表データ。 |

### ドメイン上の所有・参照

- `Railway` は `Station`、`TrainType`、`Diagram` のリストを保持します。
- `Diagram` は `Train` を、`Train` は `StopTime` と `OperationRecord` を保持します。
- `StopTime` は駅一覧の単一ソースである `Station` を参照します。`Station` から `StopTime` への逆参照はありません。
- `Train.train_type_index` は `Railway.train_types` 内の列車種別を指す整数です。`Train` から `TrainType` へのオブジェクト参照ではありません。
- `StationTimetable` は `TimetableHour` を方向別に保持し、各時間は `TimetableEntry` を保持します。エントリは行先 `Station` と `TrainType` を参照します。

## 運用情報モデル

`OperationRecord` は駅の `order` と `is_before` に結び付く運用情報のまとまりです。配下の `Operation` は `OperationType` と、次のいずれかの詳細データを持ちます。増解結などの入れ子は `before_children` / `after_children` で表現します。

| クラス | 主な属性 | 関連 |
|---|---|---|
| `OperationType` | `SHUNT`, `CONNECT`, `RELEASE`, `OUT_IN`, `OUTER`, `JUNCTION`, `NUMBER_CHANGE` | 作業種別の列挙型。 |
| `Operation` | `type`, `detail`, `before_children`, `after_children` | 1件の作業。子作業を再帰的に保持します。 |
| `OperationRecord` | `order`, `is_before`, `operations` | 駅順序・Before/After単位の作業列。 |
| `ShuntDetail` | `linked_track_index`, `departure_time`, `arrival_time`, `show_arrival` | 入換の詳細。 |
| `ConnectDetail` | `connect_position`, `connect_time` | 増結の詳細。 |
| `ReleaseDetail` | `release_position`, `release_count`, `release_time` | 解結の詳細。 |
| `OutInDetail` | `time`, `train_number` | 出区・入区の詳細。 |
| `OuterDetail` | `outer_station_index`, `departure_time`, `arrival_time`, `train_number` | 路線外始発・終着の詳細。 |
| `JunctionDetail` | `time`, `value` | 前後列車接続の詳細。 |
| `NumberChangeDetail` | `train_number` | 運用番号変更の詳細。 |

## Parserクラス

| クラス | 主な属性・入出力 | 役割・関係 |
|---|---|---|
| `SourceFile` | `path`, `encoding`, `lines` | Readerが読み込んだファイル情報。 |
| `Token` | `line_number`, `raw_line` | トークンの基底データ型。 |
| `KeyValueToken` | `key`, `value` | `Token` の派生型。 |
| `SectionStartToken` | `name` | `Token` の派生型。 |
| `SectionEndToken` | - | `Token` の派生型。 |
| `BlankToken` | - | `Token` の派生型。 |
| `CommentToken` | - | `Token` の派生型。現状のTokenizerでは生成されません。 |
| `SectionNode` | `line_number`, `name`, `key_values`, `children` | セクション構文木。子ノードを再帰的に保持します。 |
| `Parser` | `_stations` | `SectionNode` を `Railway` に変換し、時間・運用パーサーを利用します。 |
| `OperationParser` | `parse(tokens)` | `Operation` キー群を `OperationRecord` に変換します。 |
| `TimeParser` | `parse(record, station, order)` | 1駅分の時刻レコードを `StopTime` に変換します。 |
| `RecordType` | `EMPTY`, `TIME` | 時刻レコードの種類。 |
| `ReaderError`, `TokenizerError`, `SectionBuilderError`, `ParserError`, `OperationParserError`, `TimeParserError` | 例外型 | 各Parser段階の失敗を表します。 |

Reader、Tokenizer、SectionBuilder、時刻解析関数は独立した関数として実装されています。クラスではありませんが、処理関係を図に含めるため `«module»` として示しています。

## アプリケーション、UI、Excel出力

| クラス / モジュール | 主な関係・責務 |
|---|---|
| `MainWindow` | `Railway`、選択中の `Station`、`StationTimetable`、`TimetableDisplayConfig` を画面状態として保持します。ファイル読込、時刻表生成、設定保存、Excel出力をアプリケーション関数経由で呼び出します。 |
| `StationTimetableGenerator` | `Railway` と選択駅を使って `StationTimetable` を生成します。 |
| `TimetablePreview` | `StationTimetable` と `TimetableDisplayConfig` を使ってプレビューを描画し、編集対象に応じて `DisplayConfigDialog` を開きます。Tkinterの `Frame` 派生クラスです。 |
| `DisplayConfigDialog` | `PreviewItem`、表示設定、列車種別を受け取る設定ダイアログ。Tkinterの `Toplevel` 派生クラスです。 |
| `TimetableView` | `StationTimetable` をテキスト表示する独立UI部品です。 |
| `BorderSideConfig` | 罫線の有効状態、色、線種を保持します。 |
| `BorderConfig` | 上下左右の `BorderSideConfig` を保持します。 |
| `TimetableDisplayConfig` | 表示色、フォント、罫線、表示オプションを保持し、罫線設定を所有します。 |
| `PreviewItem` | プレビュー内のタイトル、見出し、時刻、列車、凡例を表す列挙型。 |
| `ExcelWriter` (`src/timetable/excel_writer.py`) | `StationTimetable` と `TimetableDisplayConfig` を `.xlsx` に出力します。 |
| `ExcelWriter` (`src/excel/writer.py`) | ファイル名を表示するだけの別実装です。旧 `src/main.py` から参照されるスタブで、現行UIの出力経路では使われません。 |

次の機能はクラスではなく関数として提供されています。図ではモジュールとして表記しています。

| モジュール | 主な関数 |
|---|---|
| `application.oud2_loader` | `load_oud2` |
| `application.station_timetable` | `generate_station_timetable` |
| `application.excel_export` | `export_station_timetable` |
| `application.station_alias_settings` | 駅名、非表示記号、表示設定の読込・保存 |

## draw.ioファイル

図の編集には [class_dsign.drawio](./class_dsign.drawio) を使用してください。ページ構成は「全体構成」「ドメインモデル」「運用情報」「Parser」「アプリケーション/UI」です。
