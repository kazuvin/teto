# Teto

解説系動画を簡単に作成するシステム

## プロジェクト構成

このプロジェクトは uv workspace と pnpm を使用したモノリポ構成です。

```
teto/
├── packages/          # Python パッケージ
│   ├── core/         # コア動画生成ライブラリ
│   ├── api/          # FastAPI サーバー
│   └── cli/          # CLI ツール
├── apps/
│   └── desktop/      # Electron デスクトップアプリ
├── docs/             # ドキュメント
└── scripts/          # スクリプト
```

## 必要な環境

- Python 3.11+
- Node.js 18+
- uv (Python パッケージマネージャー)
- pnpm (Node.js パッケージマネージャー)

## MVP 機能

現在実装されている機能:

- ✅ 動画・画像の連結
- ✅ 音声ファイルの追加（複数トラック対応）
- ✅ 字幕の追加（焼き込み / SRT / VTT 出力）
- ✅ タイムラインベースの編集
- ✅ JSON形式のプロジェクトファイル

## クイックスタート

### 1. 環境のセットアップ

```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトルートに移動
cd teto

# 依存関係のインストール
uv sync
```

### 2. CLI のインストール（推奨）

```bash
# uv tool でグローバルにインストール（推奨）
uv tool install --editable packages/cli
```

これで `teto` コマンドがどこからでも使えるようになります。

**他のインストール方法:**

```bash
# 方法A: 仮想環境を使う
uv venv
source .venv/bin/activate  # fish の場合: source .venv/bin/activate.fish
uv pip install -e packages/cli

# 方法B: エイリアスを使う（インストール不要）
# ~/.config/fish/config.fish または ~/.bashrc に追加
alias teto='uv run --package teto-cli teto'
```

### 3. 動画を作成

```bash
# 新規プロジェクトファイルを作成
teto init my_project.json

# プロジェクトファイルを編集して素材を追加
# （エディタで my_project.json を開いて編集）

# 動画を生成
teto generate my_project.json
```

## 詳細なセットアップ

### Python 環境

```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトルートで依存関係のインストール
cd teto
uv sync
```

### CLI のインストール方法の比較

| 方法 | コマンド | メリット | デメリット |
|------|---------|---------|----------|
| **uv tool** ⭐️推奨 | `uv tool install --editable packages/cli` | グローバルで使える、シンプル | - |
| 仮想環境 | `uv venv && source .venv/bin/activate.fish` | 標準的 | 毎回アクティベートが必要 |
| エイリアス | `alias teto='uv run --package teto-cli teto'` | インストール不要 | 毎回 uv run が実行される |

### Desktop アプリ（今後実装予定）

```bash
cd apps/desktop
pnpm install
```

## 開発

### API サーバー

```bash
cd packages/api
uvicorn teto_api.main:app --reload
```

### CLI ツール

```bash
# 情報表示
teto info

# 新規プロジェクト作成
teto init project.json

# プロジェクトファイルの検証
teto generate project.json --validate-only

# 動画生成
teto generate project.json
```

詳細な使い方は [docs/examples/README.md](docs/examples/README.md) を参照してください。

### Desktop アプリ

```bash
cd apps/desktop
pnpm electron:dev
```

## パッケージ

### teto-core

動画生成のコアライブラリ

### teto-api

FastAPI ベースの API サーバー。デスクトップアプリや外部システムから利用可能

### teto-cli

コマンドラインインターフェース

### teto-desktop

React + Electron デスクトップアプリケーション

## ライセンス

MIT
