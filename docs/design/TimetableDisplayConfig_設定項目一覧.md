# TimetableDisplayConfig 設定項目一覧

## 1. 目的

OuDiaExcelの駅時刻表表示設定を管理する `TimetableDisplayConfig` について、設定項目とその内容を整理する。

本ドキュメントは、今後実装する表示設定プリセット機能の設計資料として使用する。

各設定項目について、以下の情報を記録する。

- Pythonのフィールド名
- 日本語名称
- 設定内容
- デフォルト値
- データ型

## 2. 基本方針

- Pythonのフィールド名は変更しない。
- 日本語名称は、設定項目の意味を人間が理解しやすくするために使用する。
- 本一覧はプリセット機能の設計・実装時の基礎資料とする。
- 公式プリセットへの採用・除外は、別途分類作業で決定する。
- 設定値や既存の動作仕様は、本ドキュメントでは変更しない。

## 3. 設定項目一覧

### 3.1 列車種別ごとの設定

| Pythonフィールド名 | 日本語名称 | 設定内容 | デフォルト値 |
|---|---|---|---|
| `train_type_colors` | 列車種別の文字色 | 列車種別ごとの文字色 | `{}` |
| `train_type_fills` | 列車種別の背景色 | 列車種別ごとの背景色 | `{}` |
| `train_type_visible` | 列車種別の表示有無 | 列車種別を表示するか | `{}` |
| `train_type_column_visible` | 列車欄の列車種別表示有無 | 列車欄に列車種別を表示するか | `{}` |

### 3.2 列車欄の表示位置・表示方式

| Pythonフィールド名 | 日本語名称 | 設定内容 | デフォルト値 |
|---|---|---|---|
| `destination_position` | 行先の表示位置 | 行先を上下どちらに配置するか | `"top"` |
| `train_type_position` | 列車種別の表示位置 | 列車種別を上下どちらに配置するか | `"top"` |
| `metadata_order` | 行先・列車種別の表示順 | 行先と列車種別の配置順 | `"destination_first"` |
| `hour_column_mode` | 時刻欄の表示方式 | 時刻欄の配置方式 | `"separate"` |
| `striped_train_fill` | 列車欄の交互背景色 | 時間帯によって背景色を交互にするか | `True` |

### 3.3 罫線設定

| Pythonフィールド名 | 日本語名称 | 設定内容 | デフォルト値 |
|---|---|---|---|
| `title_border` | タイトルの罫線 | タイトル部分の上下左右の罫線 | `BorderConfig()` |
| `header_border` | ヘッダーの罫線 | ヘッダー部分の上下左右の罫線 | `BorderConfig()` |
| `hour_border` | 時刻欄の罫線 | 時刻欄の上下左右の罫線 | `BorderConfig()` |
| `train_border` | 列車欄の罫線 | 列車欄の上下左右の罫線 | `BorderConfig()` |
| `train_separator` | 列車欄の区切り罫線 | 列車欄の区切り線 | `BorderSideConfig()` |
| `legend_border` | 凡例の罫線 | 凡例部分の上下左右の罫線 | `BorderConfig()` |

#### BorderConfig の内部設定

罫線の上下左右それぞれに `BorderSideConfig` を持つ。

| Pythonフィールド名 | 日本語名称 | 設定内容 |
|---|---|---|
| `top` | 上罫線 | 上側の罫線 |
| `bottom` | 下罫線 | 下側の罫線 |
| `left` | 左罫線 | 左側の罫線 |
| `right` | 右罫線 | 右側の罫線 |

#### BorderSideConfig の内部設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `enabled` | 罫線の有効・無効 | `bool` | `False` | その罫線を表示するか |
| `color` | 罫線の色 | `str` | `"000000"` | 罫線の色 |
| `style` | 罫線の種類 | `str` | `"thin"` | 細線などの罫線スタイル |

### 3.4 タイトル設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `title_fill` | タイトルの背景色 | `str \| None` | `None` | タイトル部分の塗りつぶし色 |
| `title_font_color` | タイトルの文字色 | `str` | `"000000"` | タイトル文字の色 |
| `title_font_name` | タイトルのフォント | `str` | `"源ノ角ゴシック JP"` | タイトル文字のフォント |
| `title_font_size` | タイトルの文字サイズ | `int` | `14` | タイトル文字の大きさ |

### 3.5 ヘッダー設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `header_fill` | ヘッダーの背景色 | `str \| None` | `None` | ヘッダー部分の塗りつぶし色 |
| `header_font_color` | ヘッダーの文字色 | `str` | `"FAFAFA"` | ヘッダー文字の色 |
| `header_font_name` | ヘッダーのフォント | `str` | `"源ノ角ゴシック JP Heavy"` | ヘッダー文字のフォント |
| `header_font_size` | ヘッダーの文字サイズ | `int` | `12` | ヘッダー文字の大きさ |

### 3.6 時刻表本体の設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `timetable_fill` | 時刻表の基本背景色 | `str` | `"FAFAFA"` | 時刻表本体の基本色 |
| `timetable_alt_fill` | 時刻表の交互背景色 | `str` | `"C8E6C9"` | 交互表示に使用する背景色 |
| `timetable_border_color` | 時刻表の標準罫線色 | `str` | `"FAFAFA"` | 時刻表本体の標準罫線色 |
| `timetable_border_width` | 時刻表の標準罫線幅 | `str` | `"thin"` | 時刻表本体の標準罫線幅 |

### 3.7 時刻欄の設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `hour_fill` | 時刻欄の背景色 | `str \| None` | `None` | 時刻欄の塗りつぶし色 |
| `hour_font_color` | 時刻欄の文字色 | `str` | `"000000"` | 時刻の文字色 |
| `hour_font_name` | 時刻欄のフォント | `str` | `"源ノ角ゴシック JP Heavy"` | 時刻のフォント |
| `hour_font_size` | 時刻欄の文字サイズ | `int` | `10` | 時刻の文字の大きさ |

### 3.8 列車欄の設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `train_fill` | 列車欄の背景色 | `str \| None` | `None` | 列車欄の基本背景色 |
| `train_font_color` | 列車欄の基本文字色 | `str` | `"000000"` | 列車欄の基本文字色 |
| `minute_font_color` | 分の文字色 | `str \| None` | `None` | 分の数字に使用する文字色 |
| `use_train_type_short_name` | 列車種別の略称使用 | `bool` | `False` | 列車種別の略称を使用するか |
| `show_destination` | 行先の表示有無 | `bool` | `True` | 列車欄に行先を表示するか |
| `show_destination_legend` | 行先凡例の表示有無 | `bool` | `True` | 行先凡例を表示するか |

### 3.9 列車欄のフォント設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `metadata_font_name` | 行先・列車種別の基本フォント | `str` | `"源ノ角ゴシック JP"` | 行先・列車種別の基本フォント |
| `metadata_font_size` | 行先・列車種別の基本文字サイズ | `int` | `6` | 行先・列車種別の基本文字サイズ |
| `minute_font_name` | 分のフォント | `str` | `"源ノ角ゴシック JP"` | 分の数字のフォント |
| `minute_font_size` | 分の文字サイズ | `int` | `10` | 分の数字の大きさ |
| `destination_font_name` | 行先のフォント | `str \| None` | `None` | 行先専用のフォント |
| `destination_font_size` | 行先の文字サイズ | `int \| None` | `None` | 行先専用の文字サイズ |
| `destination_font_color` | 行先の文字色 | `str \| None` | `None` | 行先専用の文字色 |
| `destination_font_mode` | 行先のフォント設定方式 | `str` | `"independent"` | 他の項目のフォント設定を参照するか |
| `train_type_font_name` | 列車種別のフォント | `str \| None` | `None` | 列車種別専用のフォント |
| `train_type_font_size` | 列車種別の文字サイズ | `int \| None` | `None` | 列車種別専用の文字サイズ |
| `train_type_font_color` | 列車種別の文字色 | `str \| None` | `None` | 列車種別専用の文字色 |
| `train_type_font_mode` | 列車種別のフォント設定方式 | `str` | `"independent"` | 他の項目のフォント設定を参照するか |
| `minute_font_mode` | 分のフォント設定方式 | `str` | `"independent"` | 他の項目のフォント設定を参照するか |

### 3.10 凡例設定

| Pythonフィールド名 | 日本語名称 | 型 | デフォルト値 | 設定内容 |
|---|---|---|---|---|
| `legend_label_fill` | 凡例ラベルの背景色 | `str` | `"000000"` | 「凡例」ラベル部分の背景色 |
| `legend_fill` | 凡例本体の背景色 | `str` | `"FAFAFA"` | 凡例部分の背景色 |
| `legend_font_color` | 凡例本体の文字色 | `str` | `"000000"` | 凡例内容の文字色 |
| `legend_label_font_name` | 凡例ラベルのフォント | `str` | `"源ノ角ゴシック JP Heavy"` | 「凡例」ラベルのフォント |
| `legend_font_name` | 凡例本体のフォント | `str` | `"源ノ角ゴシック JP"` | 凡例内容のフォント |
| `legend_label_font_size` | 凡例ラベルの文字サイズ | `int` | `8` | 「凡例」ラベルの文字サイズ |
| `legend_font_size` | 凡例本体の文字サイズ | `int` | `8` | 凡例内容の文字サイズ |
| `legend_label_font_color` | 凡例ラベルの文字色 | `str` | `"FAFAFA"` | 「凡例」ラベルの文字色 |
| `legend_row_height` | 凡例の行の高さ | `float` | `24.2` | 凡例1行あたりの高さ |

## 4. メソッド（JSON保存対象外）

以下は `TimetableDisplayConfig` が持つメソッドであり、設定フィールドではないため、JSON保存対象には含めない。

| メソッド名 | 内容 |
|---|---|
| `get_train_type_color()` | 指定した列車種別の文字色を取得する |
| `get_entry_font_settings()` | 列車欄の項目に適用するフォント名・サイズ・色を取得する |
| `get_entry_fill()` | 列車欄の基本背景色を取得する |

## 5. プリセット設計に関する今後の検討事項

本ドキュメント作成時点では、以下の事項は未決定である。

- 公式プリセットで共通化する設定項目
- 列車種別に依存するため公式プリセットから除外する設定項目
- ユーザープリセットに保存する設定項目
- JSONへのシリアライズ・デシリアライズ方法
- 既存設定との互換性の扱い

これらは今後の設計・実装手順で決定する。

## 6. 開発状況

| 項目 | 状態 |
|---|---|
| `TimetableDisplayConfig` のフィールド確認 | 完了 |
| 設定項目の日本語名称整理 | 完了 |
| 設定項目の公式プリセット採用・除外分類 | 未着手 |
| プリセット機能のWeb画面実装 | 未着手 |
| JSON保存・読み込み・復元テスト | 未着手 |
| 京王電鉄風デザインの具体的な設定値決定 | 未着手 |
| JR東日本風デザインの具体的な設定値決定 | 未着手 |
| 公式プリセットJSONの確定 | 未着手 |

---

**本ドキュメントは、表示設定プリセット機能の設計に使用する設定項目の基礎資料とする。**
