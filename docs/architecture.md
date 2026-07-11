# アーキテクチャ

## 入力

OudiaSecond (.oud2)
↓
Parser
↓
Railway Model
↓
Excel Writer
↓
Excel (.xlsx)

## レイヤー

services
    データ取得

parser
    OudiaSecond解析

models
    データモデル

excel
    Excel出力
