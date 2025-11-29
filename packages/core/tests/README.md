# Teto Core Tests

このディレクトリには、teto-core パッケージのテストが含まれています。

## ディレクトリ構造

```
tests/
├── conftest.py              # 共通のフィクスチャと設定
├── unit/                    # ユニットテスト
│   ├── test_constants.py   # 定数モジュールのテスト
│   └── test_generator.py   # VideoGeneratorのテスト
└── integration/             # 統合テスト
    └── test_generator_integration.py
```

## テストの実行

### 全てのテストを実行

```bash
cd packages/core
uv run pytest
```

### ユニットテストのみ実行

```bash
uv run pytest -m unit
```

### 統合テストのみ実行

```bash
uv run pytest -m integration
```

### 遅いテストを除外

```bash
uv run pytest -m "not slow"
```

### カバレッジレポート付きで実行

```bash
uv run pytest --cov=teto_core --cov-report=html
```

カバレッジレポートは `htmlcov/index.html` で確認できます。

## テストマーカー

- `@pytest.mark.unit` - ユニットテスト
- `@pytest.mark.integration` - 統合テスト
- `@pytest.mark.slow` - 実行に時間がかかるテスト

## フィクスチャ

`conftest.py` には以下の共通フィクスチャが定義されています:

- `temp_dir` - テスト用の一時ディレクトリ
- `sample_image_path` - テスト用のサンプル画像
- `sample_output_path` - テスト出力用のパス

## テストの追加

新しいテストを追加する場合:

1. ユニットテストは `tests/unit/` 配下に `test_*.py` として作成
2. 統合テストは `tests/integration/` 配下に `test_*_integration.py` として作成
3. 適切なマーカーを使用してテストを分類
4. 必要に応じて `conftest.py` に新しいフィクスチャを追加
