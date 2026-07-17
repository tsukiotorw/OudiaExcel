# OudiaSecond ファイル調査メモ

## 調査対象

| 項目 | 内容 |
|------|------|
| ファイル名 | つきうさぎ.oud2 |
| 調査日 | 2026-07-11 |
| 調査者 | 月音鉄道 |

---

# 基本情報

## 文字コード

utf-8-sig

## 改行コード

CRLF

## ファイルサイズ

52kb

---

# サンプル断片

## Railway

```text
   2: Rosen.
   3: Rosenmei=
   4: KudariDiaAlias=
   5: NoboriDiaAlias=

```

### 読み取り結果

- Railwayクラスを生成する
- name に対応する

---

## Station

```text
  50: Eki.
  51: Ekimei=月音駅ＧＲ口
  52: Ekijikokukeisiki=Jikokukeisiki_Hatsu
  53: Ekikibo=Ekikibo_Ippan
  54: DownMain=0
  55: UpMain=1
  56: EkiTrack2Cont.
  57: EkiTrack2.
  58: TrackName=1番線
  59: TrackRyakusyou=1
  60: .
  61: EkiTrack2.
  62: TrackName=2番線
  63: TrackRyakusyou=2
  64: .
  65: .
  66: JikokuhyouTrackOmit=1
  67: JikokuhyouJikokuDisplayKudari=0,1
  68: JikokuhyouJikokuDisplayNobori=0,1
  69: JikokuhyouSyubetsuChangeDisplayKudari=0,0,0,0,1
  70: JikokuhyouSyubetsuChangeDisplayNobori=0,0,0,0,1
  71: DiagramColorNextEki=0
  72: JikokuhyouOuterDisplayKudari=0,0
  73: JikokuhyouOuterDisplayNobori=0,0
```

### 読み取り結果

- Stationクラスを生成する
- index を設定する
- name を設定する

---

## Diagram

```text
 234: Dia.
 235: DiaName=Ver01
 236: MainBackColorIndex=0
 237: SubBackColorIndex=1
 238: BackPatternIndex=0
 239: Kudari.
 240: Ressya.
 241: Houkou=Kudari
 242: Syubetsu=0
 243: EkiJikoku=1;500$0,1;503/504$0,1;507/508$0,1;512/513$1,1;517/518$1,1;521/522$1,1;527/528$1,1;532/533$0,1;536/$1
 244: Operation0B=3/459$/TN008
 245: Operation8A=5/$0
```

### 読み取り結果

- Diagramクラスを生成する
- direction を設定する
---

## Train

```text
 247: Ressya.
 248: Houkou=Kudari
 249: Syubetsu=0
 250: EkiJikoku=1;510$0,1;513/514$0,1;517/518$0,1;522/523$1,1;527/528$1,1;531/532$1,1;537/538$1,1;542/543$0,1;546/$1
 251: Operation0B=5/$
 252: Operation8A=5/$0
```

### 読み取り結果

- Trainクラスを生成する
- train_type を設定する
- stop_times を設定する
---



# ファイル全体の構造

現時点で確認できた構造

```
ファイル
 ├─ Railway
 ├─ Station
 ├─ Diagram
 │    ├─ Train
 │    └─ ...
 └─ ...
```

※ あくまで現時点での推測。
今後の調査で変更される可能性がある。

---

# セクション一覧

| セクション名 | 用途 | 備考 |
|--------------|------|------|
| Railway | 路線全体 | |
| Station | 駅情報 | |
| Diagram | ダイヤ | |
| Train | 列車 | |
| ... | | |

---

# データの記述形式

多くのデータは

```
キー=値
```

の形式で記述されている。

例

```
Name=中央線
```

---

# ネスト構造

現在確認できている構造

```
Railway
 ├─ Station
 └─ Diagram
      └─ Train
```

ネストの表現方法については引き続き確認する。

---

# 調査で確認できたこと

- UTF-8で読み込み可能
- 空行は区切りとして使われているように見える
- セクションは一定の順番で出現する
- Train は Diagram の配下に存在する

---

# 未確認事項

- Diagram は必ず存在するか
- Train の順序保証はあるか
- Station の Index は必ず連番か
- Version による違いはあるか

---

# Parser設計への影響

現時点では以下の構成が適切と考える。

```
Reader
    ↓
Tokenizer
    ↓
Parser
    ↓
Domain Model
```

理由

- ファイル構造とドメインモデルを分離できる
- Parser の責務を単純化できる
- 将来の仕様変更に対応しやすい

---

# 気付き・メモ

（自由記述）

例

- UnknownSection が存在する。
- コメント行らしきものは見当たらない。
- 空文字列を持つ項目がある。
- TrainName が未設定でも列車は存在する。

---

# Parser実装時の注意点

- 未知のキーは無視せずログへ出力する。
- Parser は Excel を生成しない。
- Parser は Domain Model の生成だけを担当する。
- 調査結果と異なるデータが見つかった場合は、このドキュメントを更新する。

---

# 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-07-11 | 初版作成 |
