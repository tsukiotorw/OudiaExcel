railway.pyを以下の設計方針でリファクタリングしてください。

【変更内容】

1. DiagramにDirectionとTrain一覧を持たせる
2. RailwayからTrain一覧を削除する
3. TrainからDirectionを削除する
4. StopTimeに通過駅を表す is_pass: bool = False を追加する
5. DirectionはEnumではなくStrEnumを使用する

【制約】

・dataclassを維持すること
・型ヒントを維持すること
・default_factoryを適切に使用すること
・将来的にOudiaSecondのParserから利用することを考慮すること
・不要なコードは削除すること
・PEP8に従うこと


変更後は

・何を変更したか
・なぜ変更したか
・設計上のメリット

を最後に説明してください。