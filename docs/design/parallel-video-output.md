# Parallel Video Output - 並列動画出力の設計

## 概要

複数フォーマットで動画を出力する際、現在は直列処理（シーケンシャル）で実行されているため、フォーマット数に比例して処理時間が増加します。本設計では、`concurrent.futures.ProcessPoolExecutor` を使用して複数フォーマットの処理を並列化し、出力時間を短縮します。

## 現状分析

### 現在の処理フロー

```
generate_multi([config1, config2, config3])
│
├─ config1: パイプライン実行 → エンコード → クリーンアップ  [時間: T]
├─ config2: パイプライン実行 → エンコード → クリーンアップ  [時間: T]
└─ config3: パイプライン実行 → エンコード → クリーンアップ  [時間: T]

合計時間: 3T（直列）
```

### 問題点

1. **直列処理**: 各フォーマットが順番に処理される
2. **グローバル状態の変更**: `self.project.output` を上書きしている
3. **リソースの非効率な使用**: CPU/GPUが1フォーマットずつしか使われない

## 設計方針

### アプローチ: ProcessPoolExecutor による並列化

各フォーマットの処理を独立したプロセスで実行し、マルチコアCPUを活用します。

```
generate_multi_parallel([config1, config2, config3])
│
├─ Process 1: config1 パイプライン → エンコード  ─┐
├─ Process 2: config2 パイプライン → エンコード  ─┼─→ 結果収集
└─ Process 3: config3 パイプライン → エンコード  ─┘

合計時間: T（並列、最大3倍高速化）
```

### 選定理由

| 選択肢 | メリット | デメリット |
|--------|----------|------------|
| **ProcessPoolExecutor** | GILの制約なし、CPUバウンド処理に最適 | プロセス間通信のオーバーヘッド |
| ThreadPoolExecutor | 軽量、メモリ共有 | GILでCPU処理が並列化されない |
| asyncio | I/Oバウンド処理に最適 | MoviePyが非対応 |

**結論**: 動画エンコードはCPUバウンド処理のため、`ProcessPoolExecutor` が最適です。

## 詳細設計

### 1. 新規メソッド追加

`VideoGenerator` クラスに `generate_multi_parallel()` メソッドを追加します。

```python
def generate_multi_parallel(
    self,
    output_configs: list,
    max_workers: int | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> list[str]:
    """複数のアスペクト比で動画を並列生成

    Args:
        output_configs: 出力設定のリスト
        max_workers: 最大並列数（デフォルト: CPU コア数）
        progress_callback: 進捗コールバック関数

    Returns:
        出力ファイルパスのリスト
    """
```

### 2. ワーカー関数の設計

プロセス間で実行可能なトップレベル関数を定義します。

```python
def _generate_single_output(
    project_dict: dict,
    output_config_dict: dict,
) -> str:
    """単一出力を生成するワーカー関数

    Note:
        ProcessPoolExecutor で使用するため、
        シリアライズ可能な dict を引数に取る
    """
    from teto_core import Project, VideoGenerator
    from teto_core.output_config import OutputConfig

    # Project を再構築
    project = Project(**project_dict)
    project.output = OutputConfig(**output_config_dict)

    # VideoGenerator を作成して実行
    generator = VideoGenerator(project)
    return generator.generate()
```

### 3. 並列実行の実装

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def generate_multi_parallel(
    self,
    output_configs: list,
    max_workers: int | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> list[str]:
    from .output_config.models import OutputConfig
    from pathlib import Path

    # 前処理フックを実行
    for hook in self._pre_hooks:
        hook(self.project)

    # 出力設定を正規化
    normalized_configs = []
    for config in output_configs:
        if isinstance(config, dict):
            config = OutputConfig(**config)
        Path(config.path).parent.mkdir(parents=True, exist_ok=True)
        normalized_configs.append(config)

    # プロジェクトをシリアライズ
    project_dict = self.project.model_dump()

    # 並列実行
    output_paths = [None] * len(normalized_configs)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # タスクを投入
        future_to_index = {
            executor.submit(
                _generate_single_output,
                project_dict,
                config.model_dump(),
            ): i
            for i, config in enumerate(normalized_configs)
        }

        # 結果を収集
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            config = normalized_configs[index]

            try:
                output_path = future.result()
                output_paths[index] = output_path

                if progress_callback:
                    progress_callback(
                        f"完了 ({sum(1 for p in output_paths if p)}/"
                        f"{len(normalized_configs)}): {config.path}"
                    )

                # 後処理フックを実行
                for hook in self._post_hooks:
                    hook(output_path, self.project)

            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate {config.path}: {e}"
                ) from e

    return output_paths
```

### 4. ファイル構成

```
packages/core/teto_core/
├── video_generator.py          # generate_multi_parallel() 追加
└── generator/
    └── parallel.py             # _generate_single_output() 定義（新規）
```

## シーケンス図

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Client    │     │  VideoGenerator  │     │ProcessPool  │
└──────┬──────┘     └────────┬─────────┘     └──────┬──────┘
       │                     │                      │
       │ generate_multi_parallel([c1,c2,c3])        │
       │────────────────────>│                      │
       │                     │                      │
       │                     │ submit(c1)           │
       │                     │─────────────────────>│
       │                     │ submit(c2)           │
       │                     │─────────────────────>│
       │                     │ submit(c3)           │
       │                     │─────────────────────>│
       │                     │                      │
       │                     │    ┌────────────────────────┐
       │                     │    │ Process 1: generate c1 │
       │                     │    │ Process 2: generate c2 │
       │                     │    │ Process 3: generate c3 │
       │                     │    └────────────────────────┘
       │                     │                      │
       │                     │<─────────────────────│ result(c2)
       │                     │<─────────────────────│ result(c1)
       │                     │<─────────────────────│ result(c3)
       │                     │                      │
       │<────────────────────│                      │
       │  [path1, path2, path3]                     │
```

## 考慮事項

### メモリ使用量

並列実行時は、各プロセスが独自のメモリ空間を持つため、メモリ使用量が増加します。

```
直列処理:   ~2GB（1プロセス）
並列処理:   ~6GB（3プロセス × 2GB）
```

**対策**: `max_workers` パラメータでシステムリソースに応じて並列数を制限可能。

### エラーハンドリング

1つのプロセスが失敗しても、他のプロセスは継続実行されます。
すべての結果収集後に、失敗したタスクがあれば例外を発生させます。

### 進捗表示

各プロセスは独立しているため、詳細な進捗（%）の共有は困難です。
完了したタスク数ベースの進捗表示を採用します。

### 後方互換性

既存の `generate_multi()` メソッドは変更せず、新しい `generate_multi_parallel()` メソッドを追加します。これにより、既存コードに影響を与えません。

## テスト計画

### ユニットテスト

```python
def test_generate_multi_parallel_produces_all_outputs():
    """すべての出力ファイルが生成されることを確認"""

def test_generate_multi_parallel_respects_max_workers():
    """max_workers パラメータが正しく適用されることを確認"""

def test_generate_multi_parallel_handles_errors():
    """エラー時に適切な例外が発生することを確認"""

def test_generate_multi_parallel_maintains_order():
    """出力パスのリストが入力順序を維持することを確認"""
```

### パフォーマンステスト

```python
def test_parallel_is_faster_than_sequential():
    """並列処理が直列処理より高速であることを確認"""
```

## 実装ステップ

1. `generator/parallel.py` にワーカー関数を実装 ✅
2. `video_generator.py` に `generate_multi_parallel()` メソッドを追加 ✅
3. `ProcessingContext` に `verbose` フラグを追加（MoviePy ログ抑制用）✅
4. `VideoOutputStep` で `verbose` フラグに対応 ✅
5. CLI で Rich Progress を使った並列進捗表示を実装 ✅
6. ユニットテストを作成・実行 ✅

## 期待される効果

| フォーマット数 | 直列処理 | 並列処理（3コア） | 高速化率 |
|---------------|---------|-----------------|---------|
| 1             | 1T      | 1T              | 1x      |
| 2             | 2T      | 1T              | 2x      |
| 3             | 3T      | 1T              | 3x      |
| 4             | 4T      | 1.33T           | 3x      |

※ T = 1フォーマットの処理時間、並列数は `max_workers` で制御可能
