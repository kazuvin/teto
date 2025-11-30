# packages/core ディレクトリ構成リファクタリングタスク

## 概要

`packages/core/teto_core` のディレクトリ構成を、基本ドメイン毎にディレクトリ・ファイルをフラットに管理しつつ、共通で使う model, types, enums などを core 配下に配置するよう整理する。

## 現状の構成

```
packages/core/teto_core/
├── __init__.py
├── constants.py                    # 共通定数
├── types.py                        # 共通型定義
├── video_generator.py              # メインジェネレーター
├── models/                         # ドメインモデル
│   ├── __init__.py
│   ├── project.py                  # プロジェクト
│   ├── layers.py                   # レイヤー（Video, Image, Audio, Subtitle, Stamp）
│   ├── output.py                   # 出力設定
│   ├── effects.py                  # エフェクト
│   ├── tts.py                      # TTS関連モデル
│   └── builders/                   # Builderパターン
│       ├── __init__.py
│       ├── project.py
│       ├── video_layer.py
│       ├── image_layer.py
│       ├── audio_layer.py
│       ├── subtitle_layer.py
│       ├── stamp_layer.py
│       └── tts.py
├── generator/                      # 生成パイプライン
│   ├── __init__.py
│   ├── context.py
│   ├── pipeline.py
│   └── steps/
│       ├── __init__.py
│       ├── video_layer.py
│       ├── audio_layer.py
│       ├── subtitle.py
│       ├── stamp_layer.py
│       ├── audio_merge.py
│       ├── output.py
│       └── cleanup.py
├── processors/                     # プロセッサー（ドメインロジック）
│   ├── __init__.py
│   ├── base.py
│   ├── video.py
│   ├── audio.py
│   ├── subtitle.py
│   ├── subtitle_renderers.py
│   ├── tts.py
│   └── effect/
│       ├── __init__.py
│       └── strategies/
│           ├── __init__.py
│           ├── slide.py
│           ├── zoom.py
│           ├── blur.py
│           ├── motion.py
│           └── color.py
├── tts/                            # TTS統合
│   ├── __init__.py
│   └── utils/
└── utils/                          # ユーティリティ
    ├── __init__.py
    ├── image_utils.py
    ├── font_utils.py
    ├── size_utils.py
    ├── time_utils.py
    └── color_utils.py
```

## 問題点

1. **models/ と processors/ の境界が曖昧**
   - `models/` にはデータクラス、`processors/` にはビジネスロジックがあるが、階層が深く関係性が分かりづらい
2. **builders/ が models/ 配下にある**
   - Builderパターンは構築ロジックだが、models配下に配置されている
3. **effect/ が processors/ 配下にネストしている**
   - エフェクトは独自ドメインとして扱うべきでは？
4. **共通型・定数が分散している**
   - `constants.py`, `types.py` がルート直下で管理されているが、コアドメインとして明示的に分離されていない

## リファクタ後の目指す構成

### 設計方針

1. **ドメイン毎にフラットに配置**
   - 各ドメイン（project, layer, effect, tts, generator など）を `teto_core/` 直下にフラットに配置
   - ドメイン内では `models.py`, `processors.py`, `builders.py` のように機能別ファイルで分割
2. **共通要素を core/ に集約**
   - `core/` ディレクトリを新設し、共通で使う `types.py`, `enums.py`, `constants.py` を配置
3. **utils は現状維持**
   - `utils/` は現状のままユーティリティ関数群として維持
4. **generator と video_generator の整理**
   - `video_generator.py` はエントリーポイントとして残す
   - `generator/` はパイプライン処理として `generator/` ディレクトリに統合

### リファクタ後の構成案

```
packages/core/teto_core/
├── __init__.py                     # パッケージエントリーポイント（現状の公開APIを維持）
├── video_generator.py              # VideoGeneratorクラス（メインエントリーポイント）
│
├── core/                           # 共通コア要素
│   ├── __init__.py
│   ├── types.py                    # 共通型定義（ResponsiveSize など）
│   ├── enums.py                    # 共通Enum定義（必要に応じて追加）
│   └── constants.py                # 共通定数（BASE_HEIGHT, SIZE_SCALE_MAP, COLOR_MAP など）
│
├── project/                        # プロジェクトドメイン
│   ├── __init__.py
│   ├── models.py                   # Project, Timeline データクラス
│   └── builders.py                 # ProjectBuilder
│
├── layer/                          # レイヤードメイン
│   ├── __init__.py
│   ├── models.py                   # VideoLayer, ImageLayer, AudioLayer, SubtitleLayer, SubtitleItem, StampLayer
│   ├── builders.py                 # VideoLayerBuilder, ImageLayerBuilder, AudioLayerBuilder, SubtitleLayerBuilder, StampLayerBuilder, SubtitleItemBuilder
│   └── processors.py               # 各レイヤー処理ロジック（video, audio, subtitle など）
│
├── effect/                         # エフェクトドメイン
│   ├── __init__.py
│   ├── models.py                   # AnimationEffect データクラス
│   ├── processors.py               # エフェクト適用処理の基底クラス
│   └── strategies/                 # 各種エフェクト戦略
│       ├── __init__.py
│       ├── slide.py
│       ├── zoom.py
│       ├── blur.py
│       ├── motion.py
│       └── color.py
│
├── tts/                            # TTSドメイン
│   ├── __init__.py
│   ├── models.py                   # GoogleTTSVoiceConfig, GoogleTTSAudioConfig, TTSRequest, TTSResult, TTSSegment
│   ├── builders.py                 # TTSBuilder
│   ├── processors.py               # TTS処理ロジック
│   └── utils/                      # TTS固有ユーティリティ（あれば）
│
├── output/                         # 出力設定ドメイン
│   ├── __init__.py
│   └── models.py                   # OutputConfig
│
├── generator/                      # 動画生成パイプライン
│   ├── __init__.py
│   ├── context.py                  # GeneratorContext
│   ├── pipeline.py                 # パイプライン制御
│   └── steps/                      # パイプラインステップ
│       ├── __init__.py
│       ├── video_layer.py
│       ├── audio_layer.py
│       ├── subtitle.py
│       ├── stamp_layer.py
│       ├── audio_merge.py
│       ├── output.py
│       └── cleanup.py
│
└── utils/                          # 汎用ユーティリティ
    ├── __init__.py
    ├── image_utils.py
    ├── font_utils.py
    ├── size_utils.py
    ├── time_utils.py
    └── color_utils.py
```

## タスク詳細

### Phase 1: 事前準備と調査

#### 1.1 依存関係の調査
- [ ] 各モジュール間のimport関係を洗い出す
- [ ] 循環参照がないか確認
- [ ] 外部パッケージへの依存関係を確認

#### 1.2 テストの確認
- [ ] 既存のテストコードを確認（tests/ ディレクトリ）
- [ ] リファクタ後もテストが通るようにする準備

#### 1.3 公開APIの確認
- [ ] `teto_core/__init__.py` で公開されているAPIを確認
- [ ] リファクタ後も同じAPIを維持する（後方互換性）

### Phase 2: core/ ディレクトリの作成

#### 2.1 core/ ディレクトリとファイルの作成
- [ ] `teto_core/core/` ディレクトリを作成
- [ ] `teto_core/core/__init__.py` を作成
- [ ] `constants.py` を `teto_core/core/constants.py` に移動
- [ ] `types.py` を `teto_core/core/types.py` に移動
- [ ] 必要に応じて `enums.py` を追加

#### 2.2 core/ の公開API設定
- [ ] `teto_core/core/__init__.py` で必要な要素をエクスポート
  ```python
  from .types import ResponsiveSize
  from .constants import (
      BASE_HEIGHT,
      SIZE_SCALE_MAP,
      COLOR_MAP,
      BASE_FONT_SIZE,
      # ... 必要な定数をすべてエクスポート
  )

  __all__ = [
      "ResponsiveSize",
      "BASE_HEIGHT",
      "SIZE_SCALE_MAP",
      # ...
  ]
  ```

### Phase 3: ドメインディレクトリの作成（並行作業可能）

#### 3.1 project/ ドメインの作成
- [ ] `teto_core/project/` ディレクトリを作成
- [ ] `models/project.py` → `project/models.py` に移動
  - `Project`, `Timeline` クラスを移動
- [ ] `models/builders/project.py` → `project/builders.py` に移動
  - `ProjectBuilder` クラスを移動
- [ ] `project/__init__.py` で公開APIを設定
  ```python
  from .models import Project, Timeline
  from .builders import ProjectBuilder

  __all__ = ["Project", "Timeline", "ProjectBuilder"]
  ```

#### 3.2 layer/ ドメインの作成
- [ ] `teto_core/layer/` ディレクトリを作成
- [ ] `models/layers.py` → `layer/models.py` に移動
  - `VideoLayer`, `ImageLayer`, `AudioLayer`, `SubtitleLayer`, `SubtitleItem`, `StampLayer` を移動
- [ ] `models/builders/` の各レイヤービルダーを `layer/builders.py` に統合
  - `VideoLayerBuilder`, `ImageLayerBuilder`, `AudioLayerBuilder`, `SubtitleLayerBuilder`, `StampLayerBuilder`, `SubtitleItemBuilder` を統合
- [ ] `processors/video.py`, `processors/audio.py`, `processors/subtitle.py`, `processors/subtitle_renderers.py` を `layer/processors.py` に統合または分割
  - 統合する場合: すべてを `layer/processors.py` に集約
  - 分割する場合: `layer/processors/` ディレクトリを作成し、`video.py`, `audio.py`, `subtitle.py`, `subtitle_renderers.py` として配置
- [ ] `layer/__init__.py` で公開APIを設定

#### 3.3 effect/ ドメインの作成
- [ ] `teto_core/effect/` ディレクトリを作成
- [ ] `models/effects.py` → `effect/models.py` に移動
  - `AnimationEffect` クラスを移動
- [ ] `processors/effect/` → `effect/strategies/` に移動
  - strategies 配下のファイルはそのまま
- [ ] `processors/base.py` のエフェクト関連クラスを `effect/processors.py` に移動
  - エフェクト処理の基底クラスがあれば移動
- [ ] `effect/__init__.py` で公開APIを設定

#### 3.4 tts/ ドメインの作成
- [ ] `teto_core/tts/` ディレクトリは既に存在するため、再構成
- [ ] `models/tts.py` → `tts/models.py` に移動
  - `GoogleTTSVoiceConfig`, `GoogleTTSAudioConfig`, `TTSRequest`, `TTSResult`, `TTSSegment` を移動
- [ ] `models/builders/tts.py` → `tts/builders.py` に移動
  - `TTSBuilder` を移動
- [ ] `processors/tts.py` → `tts/processors.py` に移動
  - TTS処理ロジックを移動
- [ ] 既存の `tts/utils/` はそのまま維持
- [ ] `tts/__init__.py` で公開APIを設定

#### 3.5 output/ ドメインの作成
- [ ] `teto_core/output/` ディレクトリを作成
- [ ] `models/output.py` → `output/models.py` に移動
  - `OutputConfig` クラスを移動
- [ ] `output/__init__.py` で公開APIを設定

### Phase 4: generator/ の整理

#### 4.1 generator/ の確認
- [ ] `generator/` ディレクトリは現状維持
- [ ] `generator/steps/` も現状維持
- [ ] import文を新しい構成に合わせて更新

#### 4.2 video_generator.py の更新
- [ ] `video_generator.py` のimport文を新しい構成に合わせて更新
- [ ] クラス本体のロジックは変更しない

### Phase 5: utils/ とその他の整理

#### 5.1 utils/ の確認
- [ ] `utils/` は現状維持
- [ ] import文を新しい構成に合わせて更新

#### 5.2 processors/base.py の扱い
- [ ] `processors/base.py` にエフェクト以外の共通基底クラスがある場合
  - `core/base.py` に移動するか、各ドメインに分散するか検討
- [ ] エフェクト関連は `effect/processors.py` に移動済み

### Phase 6: import文の一括更新

#### 6.1 全ファイルのimport文を更新
- [ ] `from teto_core.models import XXX` → `from teto_core.layer.models import XXX`
- [ ] `from teto_core.constants import XXX` → `from teto_core.core.constants import XXX`
- [ ] `from teto_core.types import XXX` → `from teto_core.core.types import XXX`
- [ ] `from teto_core.models.builders import XXX` → `from teto_core.layer.builders import XXX`
- [ ] `from teto_core.processors.effect import XXX` → `from teto_core.effect.strategies import XXX`
- [ ] その他すべてのimport文を新しい構成に合わせて更新

#### 6.2 相対importから絶対importへの統一（オプション）
- [ ] 必要に応じて相対import (`from .xxx import yyy`) を絶対import (`from teto_core.xxx import yyy`) に統一

### Phase 7: 公開APIの維持（後方互換性）

#### 7.1 teto_core/__init__.py の更新
- [ ] 現在の公開APIを維持するため、新しい構成からre-export
  ```python
  from .project.models import Project, Timeline
  from .layer.models import (
      VideoLayer,
      ImageLayer,
      AudioLayer,
      SubtitleLayer,
      SubtitleItem,
      StampLayer,
  )
  from .output.models import OutputConfig
  from .effect.models import AnimationEffect
  from .tts.models import (
      GoogleTTSVoiceConfig,
      GoogleTTSAudioConfig,
      TTSRequest,
      TTSResult,
      TTSSegment,
  )
  from .project.builders import ProjectBuilder
  from .layer.builders import (
      VideoLayerBuilder,
      ImageLayerBuilder,
      AudioLayerBuilder,
      SubtitleLayerBuilder,
      SubtitleItemBuilder,
      StampLayerBuilder,
  )
  from .tts.builders import TTSBuilder
  from .video_generator import VideoGenerator

  __all__ = [
      "Project",
      "Timeline",
      "VideoLayer",
      "ImageLayer",
      "AudioLayer",
      "SubtitleLayer",
      "SubtitleItem",
      "StampLayer",
      "OutputConfig",
      "AnimationEffect",
      "GoogleTTSVoiceConfig",
      "GoogleTTSAudioConfig",
      "TTSRequest",
      "TTSResult",
      "TTSSegment",
      "ProjectBuilder",
      "VideoLayerBuilder",
      "ImageLayerBuilder",
      "AudioLayerBuilder",
      "SubtitleLayerBuilder",
      "SubtitleItemBuilder",
      "StampLayerBuilder",
      "TTSBuilder",
      "VideoGenerator",
  ]
  ```

### Phase 8: 旧ディレクトリ・ファイルの削除

#### 8.1 移動完了後のクリーンアップ
- [ ] 空になった `models/` ディレクトリを削除
- [ ] 空になった `models/builders/` ディレクトリを削除
- [ ] 空になった `processors/` ディレクトリを削除
- [ ] 空になった `processors/effect/` ディレクトリを削除
- [ ] ルート直下の `constants.py`, `types.py` を削除（core/ に移動済み）

#### 8.2 __pycache__ のクリーンアップ
- [ ] すべての `__pycache__/` ディレクトリを削除して再生成

### Phase 9: テストとビルド確認

#### 9.1 テストの実行
- [ ] すべてのテストを実行して成功することを確認
  ```bash
  cd /Users/kazuya.miura/Develop/teto/packages/core
  pytest
  ```

#### 9.2 型チェックの実行（mypyがあれば）
- [ ] 型チェックを実行してエラーがないことを確認

#### 9.3 ビルドの確認
- [ ] パッケージがビルドできることを確認

### Phase 10: ドキュメントの更新

#### 10.1 README.md の更新
- [ ] `packages/core/README.md` にディレクトリ構成の説明を追加
- [ ] リファクタ内容を記載

#### 10.2 docstringの追加・更新
- [ ] 各ドメインの `__init__.py` にdocstringを追加
- [ ] モジュールレベルのドキュメントを整備

## 注意点

### import の循環参照に注意
- ドメイン間で相互にimportする場合、循環参照が発生しないように注意
- 必要に応じて型ヒントに `from __future__ import annotations` を使用

### テストコードの更新
- テストコード内のimport文も同様に更新が必要
- `tests/` ディレクトリ内のすべてのファイルを確認

### 段階的なリファクタ
- 一度にすべて変更せず、ドメイン毎に段階的に進める
- 各フェーズごとにテストを実行して動作確認

### 公開APIの維持
- `teto_core/__init__.py` で現在の公開APIを維持することで、外部パッケージ（api, cli）への影響を最小化

## マイルストーン

1. **Week 1**: Phase 1-2（準備とcore/の作成）
2. **Week 2**: Phase 3.1-3.3（project, layer, effect ドメインの作成）
3. **Week 3**: Phase 3.4-3.5, Phase 4（tts, output, generator の整理）
4. **Week 4**: Phase 5-7（utils, import更新、公開API維持）
5. **Week 5**: Phase 8-10（クリーンアップ、テスト、ドキュメント）

## 成功基準

- [ ] すべてのテストがパスする
- [ ] 型チェックでエラーが出ない
- [ ] `teto_core` の公開APIが変わらない（後方互換性）
- [ ] 各ドメインが独立してimportできる
  - `from teto_core.layer import VideoLayer`
  - `from teto_core.core import BASE_HEIGHT`
  - `from teto_core.effect.strategies import SlideEffect`
- [ ] ディレクトリ構成がフラットで見通しが良い

## 参考: リファクタ前後のimport比較

### リファクタ前
```python
from teto_core.models import VideoLayer, Project
from teto_core.models.builders import VideoLayerBuilder
from teto_core.constants import BASE_HEIGHT
from teto_core.types import ResponsiveSize
from teto_core.processors.effect.strategies import SlideEffect
```

### リファクタ後
```python
# 公開APIからのimport（推奨）
from teto_core import VideoLayer, Project, VideoLayerBuilder

# ドメイン別のimport（明示的）
from teto_core.layer import VideoLayer
from teto_core.layer.builders import VideoLayerBuilder
from teto_core.project import Project
from teto_core.core import BASE_HEIGHT, ResponsiveSize
from teto_core.effect.strategies import SlideEffect
```

## 次のステップ

1. **Phase 1** から順次実施
2. 各Phaseごとに動作確認とテスト実行
3. 問題があれば都度修正
4. 最終的に全体テストを実行して完了
