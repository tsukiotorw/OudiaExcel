# Domain Model

## Railway

```text
Railway
├── name
├── stations : list[Station]
└── diagrams : list[Diagram]
```

責務
- 路線全体を表現する
- 駅一覧を保持する
- ダイヤ一覧を保持する

---

## Station

```text
Station
├── index
└── name
```

責務
- 路線上の駅を表現する
- indexは駅順を表す

---

## Diagram

```text
Diagram
├── name
├── direction
└── trains
```

責務
- 上り・下りなどの方向を持つ
- Trainを管理する

---

## Train

```text
Train
├── number
├── train_type
└── stop_times
```

責務
- 1本の列車を表現する

---

## StopTime

```text
StopTime
├── station
├── order
├── arrival_time
├── departure_time
└── is_pass
```

責務
- 各駅での停車情報
- 通過駅も表現できる

---

# 設計ルール

- Railwayが唯一Station一覧を保持する（Single Source of Truth）
- DiagramがTrain一覧を保持する
- TrainはStopTimeのみ保持する
- StopTimeはStationを参照する
- 逆参照は持たない