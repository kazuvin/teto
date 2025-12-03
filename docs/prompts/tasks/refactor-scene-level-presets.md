# シーン毎のプリセット設定機能

> **Status**: ✅ 完了（2024-12）

## 概要

現在の `LayerPreset` は動画全体に適用される設計だが、シーン毎に異なるプリセット（エフェクト、トランジション）を適用できるようにリファクタリングする。

### 実装完了後の変更点

1. **`LayerPreset` → `ScenePreset` にリネーム**
2. **`get_output_config()` / `get_subtitle_style()` をプリセットから削除**
3. **`Script` モデルに `output` / `subtitle_style` フィールドを追加**

## 背景と目的

### 現状の問題

現在の実装では、`ScriptCompiler` が1つの `LayerPreset` を受け取り、全シーンに同じ設定を適用している：

```python
# compiler.py:215-246
def _build_video_layers(self, script, scene_timings):
    for scene, timing in zip(script.scenes, scene_timings):
        effects = self._preset.get_image_effects()  # 全シーン共通
        transition = self._preset.get_transition()  # 全シーン共通
```

### ユースケース

1. **タイトルシーン**: エフェクトなし、フェードイン
2. **コンテンツシーン**: Ken Burns エフェクト、クロスフェード
3. **強調シーン**: ズームエフェクト、スライドトランジション
4. **エンディング**: フェードアウト

### 要件

- シーン毎に異なるプリセットを指定できる
- プリセット未指定のシーンにはデフォルトプリセットを適用
- 出力設定（解像度、FPS）は動画全体で統一
- 既存のプリセット（default, minimal, bold_subtitle, vertical）を活用

---

## アーキテクチャ

### 設計方針

既存の `LayerPreset` を維持しつつ、シーン毎のプリセット指定を追加する。

```
┌─────────────────────────────────────────────────────────────┐
│                         Script                               │
├─────────────────────────────────────────────────────────────┤
│  default_preset: "default"  ← 動画全体のデフォルト           │
├─────────────────────────────────────────────────────────────┤
│  scenes:                                                     │
│    ├─ Scene 1: preset=null     → default を使用             │
│    ├─ Scene 2: preset="minimal" → minimal を使用            │
│    ├─ Scene 3: preset=null     → default を使用             │
│    └─ Scene 4: preset="bold_subtitle" → bold_subtitle を使用│
└─────────────────────────────────────────────────────────────┘
```

### プリセットの適用範囲

| 設定項目 | 適用単位 | 取得元 |
|---------|---------|--------|
| 出力設定（解像度、FPS） | 動画全体 | **`Script.output`** |
| 字幕スタイル | 動画全体 | **`Script.subtitle_style`** |
| 画像/動画エフェクト | **シーン毎** | シーンの `preset` または `default_preset` |
| トランジション | **シーン毎** | シーンの `preset` または `default_preset` |

---

## データモデル変更

### Scene モデル（変更）

**ファイル**: `packages/core/teto_core/script/models.py`

```python
class Scene(BaseModel):
    """シーン（台本の基本単位）"""

    narrations: list[NarrationSegment] = Field(...)
    visual: Visual = Field(...)
    duration: float | None = Field(...)
    pause_after: float = Field(...)
    note: str | None = Field(...)

    # 追加: シーン毎のプリセット指定
    preset: str | None = Field(
        None,
        description="このシーンに適用するプリセット名（未指定時はデフォルトプリセットを使用）"
    )
```

### Script モデル（変更）

**ファイル**: `packages/core/teto_core/script/models.py`

```python
class Script(BaseModel):
    """台本（AI生成用の抽象データ構造）"""

    title: str = Field(...)
    scenes: list[Scene] = Field(...)
    voice: VoiceConfig = Field(...)
    timing: TimingConfig = Field(...)
    bgm: BGMConfig | None = Field(...)
    subtitle_styles: dict[str, PartialStyle] = Field(...)
    description: str | None = Field(...)

    # 追加: デフォルトプリセット指定
    default_preset: str = Field(
        "default",
        description="シーンにプリセット指定がない場合に使用するデフォルトプリセット名"
    )

    # 追加: 出力設定（動画全体で統一）
    output: OutputSettings = Field(
        default_factory=OutputSettings,
        description="出力設定（解像度、FPSなど）"
    )

    # 追加: 字幕スタイル設定（動画全体で統一）
    subtitle_style: SubtitleStyleConfig = Field(
        default_factory=SubtitleStyleConfig,
        description="字幕スタイル設定"
    )
```

---

## ScriptCompiler 変更

### 変更方針

1. コンストラクタから `layer_preset` パラメータを削除
2. `Script.default_preset` と `Scene.preset` からプリセットを解決
3. `LayerPresetRegistry` を使用してプリセットを取得

### 変更後のインターフェース

**ファイル**: `packages/core/teto_core/script/compiler.py`

```python
class ScriptCompiler:
    """Script → Project 変換"""

    def __init__(
        self,
        tts_provider: TTSProvider,
        asset_resolver: AssetResolver,
        output_dir: str = "./output",
    ):
        """ScriptCompilerを初期化する

        Args:
            tts_provider: TTSプロバイダー
            asset_resolver: アセット解決プロバイダー
            output_dir: 出力ディレクトリ

        Note:
            - 出力設定と字幕スタイルは Script から直接取得
            - シーン毎のエフェクト・トランジションは Scene.preset または Script.default_preset から取得
        """
        self._tts = tts_provider
        self._assets = asset_resolver
        self._output_dir = output_dir

    def _get_preset_for_scene(self, script: Script, scene: Scene) -> ScenePreset:
        """シーンに適用するプリセットを取得

        Args:
            script: 台本（デフォルトプリセット情報を含む）
            scene: シーン

        Returns:
            ScenePreset: 適用するプリセット
        """
        preset_name = scene.preset or script.default_preset
        return ScenePresetRegistry.get(preset_name)
```

### _build_video_layers の変更

```python
def _build_video_layers(
    self,
    script: Script,
    scene_timings: list[SceneTiming],
) -> list[Union[VideoLayer, ImageLayer]]:
    """映像レイヤーを構築"""
    layers: list[Union[VideoLayer, ImageLayer]] = []

    for scene, timing in zip(script.scenes, scene_timings):
        # シーン毎にプリセットを取得
        preset = self._get_preset_for_scene(script, scene)

        asset_path = self._assets.resolve(scene.visual)
        duration = timing.end_time - timing.start_time

        if scene.visual.type == AssetType.VIDEO:
            effects = preset.get_video_effects()
            layer: Union[VideoLayer, ImageLayer] = VideoLayer(
                path=asset_path,
                duration=duration,
                effects=effects,
                transition=preset.get_transition(),
            )
        else:
            effects = preset.get_image_effects()
            layer = ImageLayer(
                path=asset_path,
                duration=duration,
                effects=effects,
                transition=preset.get_transition(),
            )

        layers.append(layer)

    return layers
```

### _build_subtitle_layers の変更

```python
def _build_subtitle_layers(
    self,
    script: Script,
    scene_timings: list[SceneTiming],
) -> list[SubtitleLayer]:
    """字幕レイヤーを構築"""
    # 字幕スタイルは Script から直接取得（動画全体で統一）
    style = script.subtitle_style

    # styles の優先順位: Script.subtitle_styles > Script.subtitle_style.styles
    styles = script.subtitle_styles if script.subtitle_styles else style.styles

    return [
        SubtitleLayer(
            items=items,
            styles=styles,
            font_size=style.font_size,
            font_color=style.font_color,
            google_font=style.google_font,
            font_weight=style.font_weight,
            # ... 以下同様
        )
    ]
```

### _assemble_project の変更

```python
def _assemble_project(
    self,
    script: Script,
    video_layers: list[Union[VideoLayer, ImageLayer]],
    audio_layers: list[AudioLayer],
    subtitle_layers: list[SubtitleLayer],
    output_path: str,
) -> Project:
    """Project を組み立て"""
    # 出力設定は Script から直接取得（動画全体で統一）
    output_config = OutputConfig.from_settings(script.output, output_path)

    return Project(
        output=output_config,
        timeline=Timeline(
            video_layers=video_layers,
            audio_layers=audio_layers,
            subtitle_layers=subtitle_layers,
        ),
    )
```

---

## JSON スキーマ例

### シーン毎のプリセット指定

```json
{
  "title": "シーン毎プリセットのサンプル",
  "default_preset": "default",
  "output": {
    "width": 1920,
    "height": 1080,
    "fps": 30
  },
  "subtitle_style": {
    "font_size": "lg",
    "font_color": "white",
    "google_font": "Noto Sans JP",
    "appearance": "shadow",
    "position": "bottom"
  },
  "scenes": [
    {
      "narrations": [],
      "visual": { "path": "assets/title.png" },
      "duration": 3.0,
      "preset": "minimal",
      "note": "タイトル画面（エフェクトなし）"
    },
    {
      "narrations": [
        { "text": "こんにちは！" }
      ],
      "visual": { "path": "assets/intro.png" },
      "note": "イントロ（デフォルトプリセット）"
    },
    {
      "narrations": [
        { "text": "ここが重要なポイントです！" }
      ],
      "visual": { "path": "assets/highlight.png" },
      "preset": "bold_subtitle",
      "note": "強調シーン（bold_subtitle プリセット）"
    },
    {
      "narrations": [],
      "visual": { "path": "assets/ending.png" },
      "duration": 4.0,
      "preset": "minimal",
      "note": "エンディング（エフェクトなし）"
    }
  ],
  "voice": {
    "provider": "google",
    "language_code": "ja-JP"
  }
}
```

---

## タスク詳細

### Phase 1: モデル変更

- [x] `Scene` モデルに `preset: str | None` フィールドを追加
- [x] `Script` モデルに `default_preset: str` フィールドを追加
- [x] `Script` モデルに `output: OutputSettings` フィールドを追加
- [x] `Script` モデルに `subtitle_style: SubtitleStyleConfig` フィールドを追加
- [x] バリデーション追加（存在しないプリセット名のチェック）

### Phase 2: ScriptCompiler 変更

- [x] `__init__` から `layer_preset` パラメータを削除
- [x] `_get_preset_for_scene()` メソッドを追加
- [x] `_build_video_layers()` をシーン毎のプリセット対応に変更
- [x] `_build_subtitle_layers()` を Script.subtitle_style 使用に変更
- [x] `_assemble_project()` を Script.output 使用に変更

### Phase 3: プリセットリファクタリング

- [x] `LayerPreset` を `ScenePreset` にリネーム
- [x] `get_output_config()` メソッドを削除
- [x] `get_subtitle_style()` メソッドを削除
- [x] 後方互換性エイリアスを追加

### Phase 4: テスト更新

- [x] 既存テストの修正（コンストラクタ変更に対応）
- [x] シーン毎プリセット指定のテスト追加
- [x] デフォルトプリセットフォールバックのテスト追加
- [x] 存在しないプリセット名のエラーテスト追加
- [x] Script.output / Script.subtitle_style のテスト追加

### Phase 5: CLI更新

- [x] `script-presets` コマンドを更新（ScenePresetRegistry 使用）
- [x] `script-init` コマンドを更新（output, subtitle_style 追加）

### Phase 6: サンプル更新

- [x] `examples/scripts/04_script_scene_presets.json` を更新

### Phase 7: ドキュメント更新

- [x] プリセット機能のドキュメント更新

---

## 設計上の考慮事項

### 1. 後方互換性

- `default_preset` のデフォルト値は `"default"` なので、既存の Script JSON は変更なしで動作する
- `Scene.preset` は `None` がデフォルトなので、既存の Scene JSON も変更なしで動作する

### 2. プリセット解決の優先順位

```
1. Scene.preset が指定されている → そのプリセットを使用
2. Scene.preset が None → Script.default_preset を使用
3. Script.default_preset が未指定 → "default" プリセットを使用
```

### 3. 出力設定の一貫性

出力設定（解像度、FPS、コーデック）はシーン毎に変えることができない。
これは技術的制約であり、動画全体で統一する必要がある。

### 4. 字幕スタイルの一貫性

字幕スタイルも動画全体で統一する。
シーン毎に字幕スタイルを変えるには `SubtitleLayer` の設計変更が必要になるため、
今回のスコープ外とする。

### 5. マークアップ（部分スタイル）との組み合わせ

#### 実装後の動作

マークアップスタイルは以下の2箇所で定義可能：

1. **`Script.subtitle_styles`** - スクリプト全体で定義
2. **`Script.subtitle_style.styles`** - 字幕スタイル設定内で定義

`compiler.py` では以下の優先順位で適用：

```python
# styles の優先順位: Script.subtitle_styles > Script.subtitle_style.styles
styles = script.subtitle_styles if script.subtitle_styles else style.styles
```

#### 動作

マークアップスタイルは**動画全体で統一**され、シーン毎のプリセット指定には影響されない。

```
優先順位:
1. Script.subtitle_styles が定義されている → それを使用
2. Script.subtitle_styles が空 → Script.subtitle_style.styles を使用
```

#### 理由

- 字幕レイヤー（`SubtitleLayer`）は動画全体で1つ
- 全字幕アイテムに同じスタイル定義が適用される
- シーン毎にマークアップスタイルを変えるには `SubtitleLayer` の分割が必要

#### JSON 例：マークアップとシーン毎プリセットの組み合わせ

```json
{
  "title": "マークアップとプリセットの組み合わせ",
  "default_preset": "default",
  "subtitle_style": {
    "font_size": "lg",
    "appearance": "shadow"
  },
  "subtitle_styles": {
    "emphasis": { "font_color": "red", "font_weight": "bold" },
    "highlight": { "font_color": "yellow" }
  },
  "scenes": [
    {
      "narrations": [
        { "text": "<emphasis>重要:</emphasis> イントロダクション" }
      ],
      "visual": { "path": "assets/intro.png" },
      "note": "default プリセット + マークアップ"
    },
    {
      "narrations": [
        { "text": "ここが<highlight>ポイント</highlight>です！" }
      ],
      "visual": { "path": "assets/point.png" },
      "preset": "bold_subtitle",
      "note": "bold_subtitle プリセット（エフェクト/トランジション）+ 同じマークアップスタイル"
    }
  ]
}
```

上記の例では：
- **エフェクト/トランジション**: シーン毎に異なる（default → bold_subtitle）
- **字幕スタイル**: 全シーン共通（`Script.subtitle_style` から取得）
- **マークアップスタイル**: 全シーン共通（`emphasis`, `highlight` は両シーンで同じ見た目）

#### 注意事項

- シーン毎に異なるマークアップスタイルを使いたい場合は、今後の拡張で対応予定

---

## 今後の拡張案

- [ ] シーン毎の字幕スタイル変更対応（SubtitleLayer の分割）
- [ ] シーン毎のマークアップスタイル変更対応
- [ ] カスタムプリセットの JSON 定義対応
- [ ] プリセットの継承・合成機能

---

## 参考ファイル

- `packages/core/teto_core/script/models.py` - Script, Scene モデル
- `packages/core/teto_core/script/compiler.py` - ScriptCompiler
- `packages/core/teto_core/script/presets/base.py` - ScenePreset インターフェース, SubtitleStyleConfig
- `packages/core/teto_core/script/presets/registry.py` - ScenePresetRegistry
- `packages/core/teto_core/output_config/models.py` - OutputConfig, OutputSettings

---

> **Note**: ✅ このタスクは完了しました（2024-12）
