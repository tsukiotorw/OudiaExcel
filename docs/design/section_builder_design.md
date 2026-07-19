# SectionBuilder設計

## 目的

Tokenizerが生成したToken列から
Section構造を生成する。

SectionBuilderは
Sectionの親子関係のみを構築し、
Railway等のドメイン知識は持たない。

---

## 入力

list[Token]

---

## 出力

SectionNode

---

## SectionNode

Section名

KeyValue一覧

子Section一覧

---

## 責務

- Section開始
- Section終了
- ネスト管理
- Stack管理

---

## 行わないこと

Railway生成

Station生成

Diagram生成

Train生成

StopTime生成
