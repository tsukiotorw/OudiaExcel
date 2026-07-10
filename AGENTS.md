# Domain Model Rules

- RailwayはStationとDiagramを保持する
- DiagramはTrainを保持する
- TrainはDirectionを保持しない
- StopTimeはStationを参照する
- 時刻は文字列で保持する