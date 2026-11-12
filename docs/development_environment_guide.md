# OuDiaExcel 開発環境・運用手順書

最終更新：2026年11月12日

## 1. この文書の目的

OuDiaExcelの開発環境、GitHub運用、バックアップ、AIツールの利用方針を統一する。

Windows 11とLinux Mintのどちらからでも、同じ手順で開発を開始・終了できる状態を維持する。

## 2. 開発環境

### 2-1. Windows（メイン環境）

| 項目 | 設定 |
|---|---|
| OS | Windows 11 Pro |
| エディタ | Visual Studio Code |
| Python | 3.13.14 |
| 仮想環境 | プロジェクト内 `.venv` |
| 作業フォルダ | `D:\Users\tori\Documents\workspace\OudiaExcel` |
| Git | GitHub |
| ブランチ | main |

### 2-2. Linux（サブ環境）

| 項目 | 設定 |
|---|---|
| OS | Linux Mint 22.3 Zena |
| デスクトップ | Cinnamon |
| エディタ | Visual Studio Code |
| Python | 3.13.14 |
| 仮想環境 | プロジェクト内 `.venv` |
| 作業フォルダ | `~/workspace/OudiaExcel` |
| Git | GitHub |
| ブランチ | main |

### 2-3. Python仮想環境

各OSでプロジェクト専用の `.venv` を使用する。

仮想環境はOSごとに作成する。Windowsの `.venv` をLinuxにコピーして使用しない。

## 3. 開発開始手順

### 3-1. Windows

VSCodeでプロジェクトフォルダを開き、ターミナルで以下を実行する。

```powershell
cd D:\Users\tori\Documents\workspace\OudiaExcel

git status
```

未コミットの変更がないことを確認してから、最新状態を取得する。

```powershell
git pull origin main
```

仮想環境を有効化する。

```powershell
.\.venv\Scripts\Activate.ps1
```

Pythonのバージョンと仮想環境を確認する。

```powershell
python --version
where.exe python
```

### 3-2. Linux Mint

ターミナルで以下を実行する。

```bash
cd ~/workspace/OudiaExcel

git status
```

未コミットの変更がないことを確認してから、最新状態を取得する。

```bash
git pull origin main
```

仮想環境を有効化する。

```bash
source .venv/bin/activate
```

Pythonのバージョンと仮想環境を確認する。

```bash
python --version
which python
```

### 3-3. 開発環境の確認

必要に応じて依存パッケージを確認する。

```bash
python -m pip check
```

テストを実行する。

```bash
pytest -s
```

既存テストが通ることを確認してから開発を開始する。

## 4. Web版の起動

プロジェクトルートで以下を実行する。

```bash
python -m uvicorn src.web.main:app --reload
```

ブラウザでWebアプリケーションを開き、動作確認を行う。

## 5. 開発中の基本方針

- GitHubのmainブランチをソースコードの正本とする。
- WindowsとLinuxで同じファイルを同時に編集しない。
- 大きな変更を一度に行わず、小さな単位で実装・テストする。
- 既存コードを確認してから変更する。
- Windows版とWeb版の機能差を意識する。
- 既存機能を壊さないことを優先する。
- テスト結果と実際の画面・Excel出力の確認結果を区別する。

## 6. 開発終了手順

その日の作業が終了したら、以下を実行する。

### 6-1. テスト

```bash
pytest -s
```

テストが成功することを確認する。

### 6-2. GitHubへの反映

```bash
git status
git add .
git commit -m "変更内容を日本語で記述"
git push origin main
```

コミットメッセージは日本語とし、変更内容が分かる簡潔な表現にする。

例：

- `駅略称設定を追加`
- `行先凡例の表示を修正`
- `Excel出力の文字色を修正`

### 6-3. バックアップ

GitHubへの反映後、プロジェクトフォルダ全体を手動でコピーする。

バックアップ先：

1. OneDrive
2. 外付けHDD

実施タイミング：その日の作業終了時。

## 7. 別端末への切り替え

WindowsからLinux、またはLinuxからWindowsへ切り替える場合は、以下を守る。

1. 作業終了時にテストを実行する。
2. GitHubへコミット・プッシュする。
3. OneDriveと外付けHDDへバックアップする。
4. 別端末でGitHubから最新状態を取得する。
5. テストを実行してから作業を再開する。

未コミットの変更が残った状態で端末を切り替えない。

## 8. バックアップ方針

プロジェクトフォルダ全体をバックアップする。

| バックアップ先 | 方法 | タイミング |
|---|---|---|
| GitHub | Gitによる管理 | 作業終了時 |
| OneDrive | 手動コピー | 作業終了時 |
| 外付けHDD | 手動コピー | 作業終了時 |

GitHubはバージョン管理、OneDriveと外付けHDDはプロジェクト全体のバックアップとして使い分ける。

## 9. AIツールの利用方針

### ChatGPT

メインのAIツール。

- 開発方針の相談
- 設計の検討
- コード修正
- 不具合の原因分析
- テスト方針の検討
- 設計ドキュメントの整備

### GitHub Copilot

VSCode上でのコード補完とコード生成に使用する。

- 日常的なコード補完
- 新機能の初回コード生成
- 類似機能の大量修正

無料枠を考慮し、大規模なコード生成が必要な場面を優先する。

### Claude

ChatGPTとは別の視点によるレビューに使用する。

- ChatGPTのコード修正案に疑問がある場合の検証
- 設計や実装のセカンドレビュー
- 他のAIツールの無料枠が不足した場合の代替

### 共通方針

- 無料プランを基本とする。
- 必要性が明確になった場合のみ有料プランを検討する。
- Claude Code、Codexなどの専用コーディングエージェントは現時点では使用しない。
- 最終的なコードの確認・編集はVSCodeで行う。

## 10. 今後の管理方針

開発環境や運用方法に変更があった場合は、この文書を更新する。

特に以下の変更は記録する。

- Pythonのバージョン変更
- 依存パッケージの追加・変更
- Windows・Linuxの環境変更
- GitHub運用ルールの変更
- バックアップ方法の変更
- AIツールの利用方針変更

この文書と開発状況サマリーをGitHubで管理し、開発環境と開発状況の両方を把握できる状態を維持する。
